"""
Celery tasks for background processing.
Handles price score updates, cache warming, and file processing.
"""

from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def update_price_scores(self):
    """
    Background task to update price scores across all items.
    Runs every 15 minutes to keep scores fresh.
    """
    try:
        from .optimizations import bulk_update_price_scores
        updated_count = bulk_update_price_scores()
        
        logger.info(f"Updated {updated_count} price scores successfully")
        return {"status": "success", "updated_count": updated_count}
        
    except Exception as exc:
        logger.error(f"Error updating price scores: {exc}")
        self.retry(countdown=60 * 2**self.request.retries)


@shared_task
def warm_popular_items_cache():
    """
    Pre-warm cache with popular items data.
    """
    try:
        from .optimizations import get_popular_items
        
        # Warm different cache variants
        get_popular_items(limit=50)  # Top 50
        get_popular_items(limit=100) # Top 100
        
        logger.info("Successfully warmed popular items cache")
        return {"status": "success"}
        
    except Exception as exc:
        logger.error(f"Error warming popular items cache: {exc}")
        return {"status": "error", "error": str(exc)}


@shared_task
def warm_item_price_statistics_cache(item_ids):
    """
    Pre-warm price statistics cache for specific items.
    """
    try:
        from .optimizations import get_item_price_statistics
        
        warmed_count = 0
        for item_id in item_ids:
            get_item_price_statistics(item_id)
            warmed_count += 1
        
        logger.info(f"Warmed price statistics cache for {warmed_count} items")
        return {"status": "success", "warmed_count": warmed_count}
        
    except Exception as exc:
        logger.error(f"Error warming price statistics cache: {exc}")
        return {"status": "error", "error": str(exc)}


@shared_task(bind=True, max_retries=2)
def process_uploaded_file(self, file_path, packing_list_id):
    """
    Process uploaded files (CSV, Excel, PDF) in the background.
    """
    try:
        from .parsers import parse_uploaded_file
        from .models import PackingList
        
        packing_list = PackingList.objects.get(id=packing_list_id)
        result = parse_uploaded_file(file_path, packing_list)
        
        logger.info(f"Successfully processed file for packing list {packing_list_id}")
        return {"status": "success", "items_created": result.get("items_created", 0)}
        
    except Exception as exc:
        logger.error(f"Error processing uploaded file: {exc}")
        self.retry(countdown=60 * 2**self.request.retries)


@shared_task
def cleanup_old_sessions():
    """
    Clean up old session data and expired cache entries.
    """
    try:
        from django.contrib.sessions.models import Session
        from datetime import datetime, timezone as tz
        
        # Delete expired sessions
        expired_sessions = Session.objects.filter(expire_date__lt=datetime.now(tz.utc))
        deleted_count = expired_sessions.count()
        expired_sessions.delete()
        
        logger.info(f"Cleaned up {deleted_count} expired sessions")
        return {"status": "success", "cleaned_sessions": deleted_count}
        
    except Exception as exc:
        logger.error(f"Error during cleanup: {exc}")
        return {"status": "error", "error": str(exc)}


@shared_task
def calculate_store_distances_for_base(base_id, force_refresh=False):
    """
    Pre-calculate store distances for a base to improve filter performance.
    """
    try:
        from .optimizations import get_cached_store_distances
        
        if force_refresh:
            # Clear existing cache
            cache_key = f'store_distances_{base_id}_50'  # Default radius
            cache.delete(cache_key)
        
        distances = get_cached_store_distances(base_id, radius=50, cache_timeout=86400)  # 24 hours
        
        logger.info(f"Calculated distances for {len(distances)} stores from base {base_id}")
        return {"status": "success", "distances_calculated": len(distances)}
        
    except Exception as exc:
        logger.error(f"Error calculating store distances: {exc}")
        return {"status": "error", "error": str(exc)}


@shared_task
def send_notification_email(user_email, subject, message):
    """
    Send notification emails asynchronously.
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        logger.info(f"Sent notification email to {user_email}")
        return {"status": "success"}
        
    except Exception as exc:
        logger.error(f"Error sending notification email: {exc}")
        return {"status": "error", "error": str(exc)}


@shared_task
def generate_packing_list_pdf(packing_list_id):
    """
    Generate PDF of packing list in background for large lists.
    """
    try:
        from .models import PackingList
        from .views import generate_packing_list_pdf_content
        
        packing_list = PackingList.objects.get(id=packing_list_id)
        pdf_content = generate_packing_list_pdf_content(packing_list)
        
        # Store PDF in cache or file storage for later retrieval
        cache_key = f'packing_list_pdf_{packing_list_id}'
        cache.set(cache_key, pdf_content, timeout=3600)  # 1 hour
        
        logger.info(f"Generated PDF for packing list {packing_list_id}")
        return {"status": "success", "pdf_size": len(pdf_content)}
        
    except Exception as exc:
        logger.error(f"Error generating PDF: {exc}")
        return {"status": "error", "error": str(exc)}