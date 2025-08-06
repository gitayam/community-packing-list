"""
Security utilities for anonymous price submissions and abuse prevention.
"""
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Q
from typing import Optional, Tuple
import ipaddress

def get_client_ip(request) -> Optional[str]:
    """
    Get the real IP address from request, handling proxies and load balancers.
    Returns None if IP cannot be determined.
    """
    # Check for forwarded IP (behind proxy/load balancer)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP in the chain (original client)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # Direct connection
        ip = request.META.get('REMOTE_ADDR')
    
    # Validate IP address format
    if ip:
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            pass
    
    return None

def is_rate_limited(ip_address: str, window_minutes: int = 5, max_submissions: int = 10) -> Tuple[bool, int]:
    """
    Check if IP address is rate limited for price submissions.
    
    Args:
        ip_address: Client IP address
        window_minutes: Time window for rate limiting
        max_submissions: Maximum submissions allowed in window
        
    Returns:
        Tuple of (is_limited, seconds_until_reset)
    """
    if not ip_address:
        return True, 300  # Block if no IP
        
    cache_key = f"rate_limit_price:{ip_address}"
    current_count = cache.get(cache_key, 0)
    
    if current_count >= max_submissions:
        # Get TTL for cache key to know when limit resets
        # Note: ttl() method may not be available in all cache backends
        try:
            ttl = cache.ttl(cache_key)
            return True, ttl if ttl > 0 else 300
        except AttributeError:
            # Fallback for cache backends without ttl() method
            return True, window_minutes * 60
    
    # Increment counter with expiry
    cache.set(cache_key, current_count + 1, timeout=window_minutes * 60)
    return False, 0

def is_ip_suspicious(ip_address: str) -> bool:
    """
    Check if IP address has suspicious activity patterns.
    
    Args:
        ip_address: Client IP address
        
    Returns:
        True if IP is suspicious
    """
    if not ip_address:
        return True
        
    from .models import Price
    
    # Check recent submission patterns (last 24 hours)
    since = timezone.now() - timedelta(hours=24)
    recent_prices = Price.objects.filter(
        ip_address=ip_address,
        created_at__gte=since
    )
    
    # Suspicious patterns:
    # 1. Too many submissions in short time
    if recent_prices.count() > 50:
        return True
        
    # 2. All prices for same item/store (likely spam)
    unique_items = recent_prices.values('item').distinct().count()
    if recent_prices.count() > 10 and unique_items == 1:
        return True
        
    # 3. All prices exactly the same value (likely fake)
    if recent_prices.count() > 5:
        unique_prices = recent_prices.values('price').distinct().count()
        if unique_prices == 1:
            return True
    
    # 4. High flagged content ratio
    flagged_prices = recent_prices.filter(flagged_count__gt=0)
    if recent_prices.count() > 5 and flagged_prices.count() / recent_prices.count() > 0.3:
        return True
        
    return False

def calculate_trust_score(ip_address: str) -> float:
    """
    Calculate trust score for an IP address based on submission history.
    
    Args:
        ip_address: Client IP address
        
    Returns:
        Trust score from 0.0 (untrusted) to 1.0 (highly trusted)
    """
    if not ip_address:
        return 0.0
        
    from .models import Price, Vote
    
    # Base score for new IPs
    base_score = 0.5
    
    # Get all submissions from this IP
    prices = Price.objects.filter(ip_address=ip_address)
    total_submissions = prices.count()
    
    if total_submissions == 0:
        return base_score
    
    # Factors that increase trust:
    # 1. Number of submissions (consistency)
    consistency_bonus = min(total_submissions * 0.02, 0.3)
    
    # 2. Age of account (oldest submission)
    oldest_price = prices.order_by('created_at').first()
    if oldest_price:
        days_active = (timezone.now() - oldest_price.created_at).days
        age_bonus = min(days_active * 0.005, 0.2)
    else:
        age_bonus = 0
    
    # 3. Positive voting ratio on their prices
    total_votes = Vote.objects.filter(price__in=prices).count()
    positive_votes = Vote.objects.filter(price__in=prices, is_correct_price=True).count()
    
    if total_votes > 0:
        vote_ratio = positive_votes / total_votes
        vote_bonus = (vote_ratio - 0.5) * 0.3  # Range: -0.15 to +0.15
    else:
        vote_bonus = 0
    
    # Factors that decrease trust:
    # 1. Flagged submissions
    flagged_submissions = prices.filter(flagged_count__gt=0).count()
    flagged_penalty = (flagged_submissions / total_submissions) * 0.4
    
    # 2. Suspicious patterns
    suspicious_penalty = 0.3 if is_ip_suspicious(ip_address) else 0
    
    # Calculate final score
    trust_score = base_score + consistency_bonus + age_bonus + vote_bonus - flagged_penalty - suspicious_penalty
    
    # Clamp to valid range
    return max(0.0, min(1.0, trust_score))

def get_recommended_confidence(ip_address: str, user_selected_confidence: str) -> str:
    """
    Get recommended confidence level based on IP trust score and user selection.
    
    Args:
        ip_address: Client IP address
        user_selected_confidence: User's selected confidence level
        
    Returns:
        Recommended confidence level
    """
    trust_score = calculate_trust_score(ip_address)
    
    # High trust IPs can use any confidence level
    if trust_score >= 0.8:
        return user_selected_confidence
    
    # Medium trust IPs are limited to medium/low
    if trust_score >= 0.6:
        if user_selected_confidence == 'high':
            return 'medium'
        return user_selected_confidence
    
    # Low trust IPs are limited to low confidence
    return 'low'

def should_block_submission(ip_address: str) -> Tuple[bool, str]:
    """
    Determine if a price submission should be blocked.
    
    Args:
        ip_address: Client IP address
        
    Returns:
        Tuple of (should_block, reason)
    """
    if not ip_address:
        return True, "Invalid IP address"
    
    # Check rate limiting
    is_limited, time_left = is_rate_limited(ip_address)
    if is_limited:
        minutes = time_left // 60
        return True, f"Rate limit exceeded. Try again in {minutes} minutes."
    
    # Check if IP is suspicious
    if is_ip_suspicious(ip_address):
        return True, "Suspicious activity detected. Please try again later."
    
    # Check if IP is in blocklist (could be added later)
    blocklist_key = f"blocked_ip:{ip_address}"
    if cache.get(blocklist_key):
        return True, "IP address is temporarily blocked."
    
    return False, ""

def flag_price_as_suspicious(price_id: int, reason: str = ""):
    """
    Flag a price as suspicious and update metrics.
    
    Args:
        price_id: ID of the price to flag
        reason: Optional reason for flagging
    """
    from .models import Price
    
    try:
        price = Price.objects.get(id=price_id)
        price.flagged_count += 1
        price.save(update_fields=['flagged_count'])
        
        # If too many flags, consider blocking the IP temporarily
        if price.flagged_count >= 3 and price.ip_address:
            cache.set(f"blocked_ip:{price.ip_address}", True, timeout=3600)  # 1 hour block
            
    except Price.DoesNotExist:
        pass