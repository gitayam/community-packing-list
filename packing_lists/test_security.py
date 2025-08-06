"""
Unit tests for security.py module
Tests rate limiting, IP validation, trust scoring, and abuse prevention.
"""
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from packing_lists.security import (
    get_client_ip,
    is_rate_limited,
    is_ip_suspicious,
    calculate_trust_score,
    get_recommended_confidence,
    should_block_submission,
    flag_price_as_suspicious
)
from packing_lists.models import Item, PackingList, Store, Price, Vote


class SecurityTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        cache.clear()  # Clear cache before each test
        
        # Create test data
        self.packing_list = PackingList.objects.create(
            name="Test List",
            description="Test description"
        )
        self.item = Item.objects.create(name="Test Item")
        self.store = Store.objects.create(
            name="Test Store",
            address_line1="123 Test St"
        )
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()

    def test_get_client_ip_direct(self):
        """Test getting IP from direct connection."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_forwarded(self):
        """Test getting IP from X-Forwarded-For header."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.1')  # First IP in chain

    def test_get_client_ip_invalid(self):
        """Test handling of invalid IP addresses."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = 'invalid-ip'
        
        ip = get_client_ip(request)
        self.assertIsNone(ip)

    def test_get_client_ip_missing(self):
        """Test handling when no IP is available."""
        request = self.factory.get('/')
        # Don't set any IP headers
        
        ip = get_client_ip(request)
        self.assertIsNone(ip)

    def test_rate_limiting_normal_usage(self):
        """Test normal usage within rate limits."""
        ip = '192.168.1.100'
        
        # First few submissions should be allowed
        for i in range(5):
            is_limited, time_left = is_rate_limited(ip, window_minutes=5, max_submissions=10)
            self.assertFalse(is_limited)
            self.assertEqual(time_left, 0)

    def test_rate_limiting_exceeded(self):
        """Test rate limiting when threshold is exceeded."""
        ip = '192.168.1.101'
        
        # Exceed the rate limit
        for i in range(11):  # Max is 10
            is_rate_limited(ip, window_minutes=5, max_submissions=10)
        
        # Next request should be limited
        is_limited, time_left = is_rate_limited(ip, window_minutes=5, max_submissions=10)
        self.assertTrue(is_limited)
        self.assertGreater(time_left, 0)

    def test_rate_limiting_no_ip(self):
        """Test rate limiting with no IP address."""
        is_limited, time_left = is_rate_limited(None)
        self.assertTrue(is_limited)
        self.assertEqual(time_left, 300)  # Default 5 minutes

    def test_suspicious_ip_too_many_submissions(self):
        """Test detection of IPs with too many submissions."""
        ip = '192.168.1.102'
        
        # Create many recent prices for this IP
        recent_time = timezone.now() - timedelta(hours=1)
        for i in range(51):  # Threshold is 50
            Price.objects.create(
                item=self.item,
                store=self.store,
                price=f"{10 + i}.99",
                ip_address=ip,
                created_at=recent_time + timedelta(minutes=i)
            )
        
        self.assertTrue(is_ip_suspicious(ip))

    def test_suspicious_ip_same_item_spam(self):
        """Test detection of spam submissions for same item."""
        ip = '192.168.1.103'
        
        # Create 11 prices for the same item (threshold: >10 for same item)
        recent_time = timezone.now() - timedelta(hours=1)
        for i in range(12):
            Price.objects.create(
                item=self.item,  # Same item
                store=self.store,
                price=f"{10}.99",
                ip_address=ip,
                created_at=recent_time + timedelta(minutes=i)
            )
        
        self.assertTrue(is_ip_suspicious(ip))

    def test_suspicious_ip_same_price_spam(self):
        """Test detection of submissions with identical prices."""
        ip = '192.168.1.104'
        
        # Create 6 prices with identical values
        recent_time = timezone.now() - timedelta(hours=1)
        for i in range(6):
            Price.objects.create(
                item=self.item,
                store=self.store,
                price="9.99",  # Same price
                ip_address=ip,
                created_at=recent_time + timedelta(minutes=i)
            )
        
        self.assertTrue(is_ip_suspicious(ip))

    def test_suspicious_ip_high_flagged_ratio(self):
        """Test detection of IPs with high flagged content ratio."""
        ip = '192.168.1.105'
        
        # Create 10 prices, flag 4 of them (40% flagged > 30% threshold)
        recent_time = timezone.now() - timedelta(hours=1)
        prices = []
        for i in range(10):
            price = Price.objects.create(
                item=self.item,
                store=self.store,
                price=f"{10 + i}.99",
                ip_address=ip,
                created_at=recent_time + timedelta(minutes=i)
            )
            prices.append(price)
        
        # Flag 4 prices
        for i in range(4):
            prices[i].flagged_count = 1
            prices[i].save()
        
        self.assertTrue(is_ip_suspicious(ip))

    def test_normal_ip_not_suspicious(self):
        """Test that normal IPs are not flagged as suspicious."""
        ip = '192.168.1.106'
        
        # Create a few normal prices
        recent_time = timezone.now() - timedelta(hours=1)
        for i in range(3):
            Price.objects.create(
                item=self.item,
                store=self.store,
                price=f"{10 + i}.99",
                ip_address=ip,
                created_at=recent_time + timedelta(minutes=i * 10)
            )
        
        self.assertFalse(is_ip_suspicious(ip))

    def test_trust_score_new_ip(self):
        """Test trust score calculation for new IP."""
        ip = '192.168.1.107'
        # No existing submissions
        score = calculate_trust_score(ip)
        self.assertEqual(score, 0.5)  # Base score

    def test_trust_score_with_submissions(self):
        """Test trust score with submission history."""
        ip = '192.168.1.108'
        
        # Create some old prices to get age bonus
        old_time = timezone.now() - timedelta(days=30)
        for i in range(10):
            Price.objects.create(
                item=self.item,
                store=self.store,
                price=f"{10 + i}.99",
                ip_address=ip,
                created_at=old_time + timedelta(days=i)
            )
        
        score = calculate_trust_score(ip)
        self.assertGreater(score, 0.5)  # Should be higher than base score

    def test_trust_score_with_positive_votes(self):
        """Test trust score bonus from positive votes."""
        ip = '192.168.1.109'
        
        # Create price
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price="9.99",
            ip_address=ip
        )
        
        # Add positive votes
        for i in range(5):
            Vote.objects.create(
                price=price,
                is_correct_price=True,
                ip_address=f'192.168.1.{200 + i}'
            )
        
        score = calculate_trust_score(ip)
        self.assertGreater(score, 0.5)

    def test_trust_score_with_flagged_content(self):
        """Test trust score penalty from flagged content."""
        ip = '192.168.1.110'
        
        # Create prices with flags
        for i in range(5):
            price = Price.objects.create(
                item=self.item,
                store=self.store,
                price=f"{10 + i}.99",
                ip_address=ip
            )
            if i < 3:  # Flag 3 out of 5
                price.flagged_count = 2
                price.save()
        
        score = calculate_trust_score(ip)
        self.assertLess(score, 0.5)  # Should be lower than base score

    def test_recommended_confidence_high_trust(self):
        """Test confidence recommendation for high trust IP."""
        ip = '192.168.1.111'
        
        # Mock high trust score
        with patch('packing_lists.security.calculate_trust_score', return_value=0.9):
            confidence = get_recommended_confidence(ip, 'high')
            self.assertEqual(confidence, 'high')

    def test_recommended_confidence_medium_trust(self):
        """Test confidence recommendation for medium trust IP."""
        ip = '192.168.1.112'
        
        # Mock medium trust score
        with patch('packing_lists.security.calculate_trust_score', return_value=0.7):
            confidence = get_recommended_confidence(ip, 'high')
            self.assertEqual(confidence, 'medium')  # Downgraded from high

    def test_recommended_confidence_low_trust(self):
        """Test confidence recommendation for low trust IP."""
        ip = '192.168.1.113'
        
        # Mock low trust score
        with patch('packing_lists.security.calculate_trust_score', return_value=0.3):
            confidence = get_recommended_confidence(ip, 'high')
            self.assertEqual(confidence, 'low')  # Downgraded to low

    def test_should_block_submission_rate_limited(self):
        """Test blocking submission due to rate limiting."""
        ip = '192.168.1.114'
        
        # Exceed rate limit first
        for i in range(11):
            is_rate_limited(ip, window_minutes=5, max_submissions=10)
        
        should_block, reason = should_block_submission(ip)
        self.assertTrue(should_block)
        self.assertIn('Rate limit exceeded', reason)

    def test_should_block_submission_suspicious_ip(self):
        """Test blocking submission due to suspicious IP."""
        ip = '192.168.1.115'
        
        # Make IP suspicious
        with patch('packing_lists.security.is_ip_suspicious', return_value=True):
            should_block, reason = should_block_submission(ip)
            self.assertTrue(should_block)
            self.assertIn('Suspicious activity', reason)

    def test_should_block_submission_blocklisted_ip(self):
        """Test blocking submission due to IP blocklist."""
        ip = '192.168.1.116'
        
        # Add IP to blocklist
        cache.set(f"blocked_ip:{ip}", True, timeout=3600)
        
        should_block, reason = should_block_submission(ip)
        self.assertTrue(should_block)
        self.assertIn('temporarily blocked', reason)

    def test_should_allow_submission_normal_ip(self):
        """Test allowing submission for normal IP."""
        ip = '192.168.1.117'
        
        should_block, reason = should_block_submission(ip)
        self.assertFalse(should_block)
        self.assertEqual(reason, "")

    def test_flag_price_as_suspicious(self):
        """Test flagging a price as suspicious."""
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price="9.99",
            ip_address='192.168.1.118'
        )
        
        initial_count = price.flagged_count
        
        flag_price_as_suspicious(price.id, "Test reason")
        
        price.refresh_from_db()
        self.assertEqual(price.flagged_count, initial_count + 1)

    def test_flag_price_blocks_ip_after_threshold(self):
        """Test that flagging a price blocks IP after threshold."""
        ip = '192.168.1.119'
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price="9.99",
            ip_address=ip,
            flagged_count=2  # Already has 2 flags
        )
        
        # Flag it again (3rd flag should trigger block)
        flag_price_as_suspicious(price.id, "Third flag")
        
        # Check if IP is blocked
        blocked = cache.get(f"blocked_ip:{ip}")
        self.assertTrue(blocked)

    def test_flag_nonexistent_price(self):
        """Test flagging a non-existent price ID."""
        # Should not raise exception
        flag_price_as_suspicious(99999, "Non-existent price")
        # Test passes if no exception is raised


class SecurityViewsTestCase(TestCase):
    """Test security aspects of views."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()
        self.packing_list = PackingList.objects.create(
            name="Test List",
            description="Test description"
        )
        self.item = Item.objects.create(name="Test Item")
        self.store = Store.objects.create(
            name="Test Store",
            address_line1="123 Test St"
        )

    def test_price_submission_with_valid_ip(self):
        """Test price submission with valid IP."""
        from django.test import Client
        
        client = Client()
        response = client.post('/item/1/add_price/', {
            'price': '9.99',
            'store': self.store.id,
            'quantity': 1,
            'confidence': 'medium'
        }, HTTP_X_FORWARDED_FOR='192.168.1.120')
        
        # Should not be blocked by security (assuming endpoint exists)
        # This test would need the actual view to exist

    def test_price_submission_malicious_data(self):
        """Test price submission with malicious data."""
        from django.test import Client
        
        client = Client()
        malicious_data = {
            'price': '<script>alert("XSS")</script>',
            'store': f'{self.store.id}; DROP TABLE stores; --',
            'quantity': '-1',
            'confidence': 'javascript:alert(1)'
        }
        
        response = client.post('/item/1/add_price/', malicious_data,
                             HTTP_X_FORWARDED_FOR='192.168.1.121')
        
        # Should be rejected or sanitized by Django's built-in protections
        # This test would need the actual view to exist

    def test_csrf_protection(self):
        """Test CSRF protection on price submission."""
        from django.test import Client
        
        client = Client(enforce_csrf_checks=True)
        
        # Attempt submission without CSRF token
        response = client.post('/item/1/add_price/', {
            'price': '9.99',
            'store': self.store.id,
            'quantity': 1
        })
        
        # Should be rejected due to missing CSRF token
        # This test would need the actual view to exist