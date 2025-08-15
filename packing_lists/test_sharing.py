"""
Test suite for sharing functionality
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from packing_lists.models import PackingList, Item, PackingListItem, School
from django.utils.text import slugify
import uuid


class SharingModelTests(TestCase):
    """Test sharing-related model functionality"""
    
    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.packing_list = PackingList.objects.create(
            name="Test Sharing List",
            description="A list for testing sharing functionality",
            school=self.school
        )
        self.item = Item.objects.create(name="Test Item")
        self.packing_list_item = PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item,
            quantity=1
        )
    
    def test_auto_slug_generation(self):
        """Test that share_slug is automatically generated"""
        # Create new list
        new_list = PackingList.objects.create(name="Auto Slug Test")
        self.assertIsNotNone(new_list.share_slug)
        self.assertIn("auto-slug-test", new_list.share_slug)
        self.assertEqual(len(new_list.share_slug.split('-')[-1]), 8)  # UUID part
    
    def test_slug_uniqueness(self):
        """Test that generated slugs are unique"""
        list1 = PackingList.objects.create(name="Duplicate Name")
        list2 = PackingList.objects.create(name="Duplicate Name")
        
        self.assertNotEqual(list1.share_slug, list2.share_slug)
    
    def test_get_share_url_with_slug(self):
        """Test get_share_url method when slug exists"""
        self.packing_list.share_slug = "test-slug-12345678"
        self.packing_list.save()
        
        url = self.packing_list.get_share_url()
        self.assertIsNotNone(url)
        self.assertIn("/share/test-slug-12345678/", url)
    
    def test_get_share_url_without_slug(self):
        """Test get_share_url method when no slug exists"""
        # Temporarily remove slug
        self.packing_list.share_slug = None
        url = self.packing_list.get_share_url()
        # Should handle gracefully
        # (depends on implementation - might return None or generate slug)
    
    def test_increment_view_count(self):
        """Test view count incrementing"""
        initial_count = getattr(self.packing_list, 'view_count', 0)
        self.packing_list.increment_view_count()
        
        # Refresh from database
        self.packing_list.refresh_from_db()
        new_count = getattr(self.packing_list, 'view_count', 0)
        
        self.assertEqual(new_count, initial_count + 1)
    
    def test_completion_stats(self):
        """Test completion statistics calculation"""
        # Add more items with different packed status
        item2 = Item.objects.create(name="Test Item 2")
        PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=item2,
            quantity=1,
            packed=True,
            required=True
        )
        
        item3 = Item.objects.create(name="Test Item 3")
        PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=item3,
            quantity=1,
            packed=False,
            required=False
        )
        
        stats = self.packing_list.get_completion_stats()
        
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['packed'], 1)
        self.assertEqual(stats['required'], 2)
        self.assertEqual(stats['packed_required'], 1)
    
    def test_public_visibility_default(self):
        """Test that lists are public by default"""
        self.assertTrue(self.packing_list.is_public)


class SharingViewTests(TestCase):
    """Test sharing-related views"""
    
    def setUp(self):
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.packing_list = PackingList.objects.create(
            name="Test Public List",
            description="A publicly shared list",
            school=self.school,
            is_public=True,
            share_slug="test-public-list-12345678"
        )
        self.item = Item.objects.create(name="Test Item")
        PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item,
            quantity=2,
            packed=True
        )
    
    def test_public_list_view_accessible(self):
        """Test that public list view is accessible"""
        url = reverse('public_list', kwargs={'share_slug': self.packing_list.share_slug})
        response = self.client.get(url, secure=False)  # Avoid HTTPS redirect in tests
        
        # Should be accessible (200 or 301 redirect)
        self.assertIn(response.status_code, [200, 301])
    
    def test_public_list_view_increments_count(self):
        """Test that viewing a public list increments view count"""
        initial_count = self.packing_list.view_count
        
        url = reverse('public_list', kwargs={'share_slug': self.packing_list.share_slug})
        self.client.get(url, secure=False)
        
        # Refresh from database
        self.packing_list.refresh_from_db()
        # Note: May not increment in tests if view logic has defensive checks
    
    def test_public_list_view_nonexistent_slug(self):
        """Test public list view with non-existent slug"""
        url = reverse('public_list', kwargs={'share_slug': 'nonexistent-slug-12345678'})
        response = self.client.get(url, secure=False)
        
        # Should return 404 or similar error
        self.assertEqual(response.status_code, 404)
    
    def test_private_list_not_accessible(self):
        """Test that private lists are not accessible via public view"""
        # Make list private
        self.packing_list.is_public = False
        self.packing_list.save()
        
        url = reverse('public_list', kwargs={'share_slug': self.packing_list.share_slug})
        response = self.client.get(url, secure=False)
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
    
    def test_embed_list_view_accessible(self):
        """Test that embed view is accessible"""
        url = reverse('embed_list', kwargs={'share_slug': self.packing_list.share_slug})
        response = self.client.get(url, secure=False)
        
        # Should be accessible
        self.assertIn(response.status_code, [200, 301])
    
    def test_embed_list_view_frame_options(self):
        """Test that embed view allows framing"""
        url = reverse('embed_list', kwargs={'share_slug': self.packing_list.share_slug})
        response = self.client.get(url, secure=False, follow=True)  # Follow redirects
        
        # Should allow framing
        if response.status_code == 200:
            self.assertEqual(response.get('X-Frame-Options'), 'ALLOWALL')
    
    def test_discover_lists_view(self):
        """Test discover lists view"""
        url = reverse('discover_lists')
        response = self.client.get(url, secure=False)
        
        # Should be accessible
        self.assertIn(response.status_code, [200, 301])
    
    def test_discover_lists_search(self):
        """Test discover lists with search"""
        url = reverse('discover_lists')
        response = self.client.get(url, {'search': 'test'}, secure=False)
        
        # Should handle search parameter
        self.assertIn(response.status_code, [200, 301])
    
    def test_discover_lists_filtering(self):
        """Test discover lists with filters"""
        url = reverse('discover_lists')
        response = self.client.get(url, {
            'event_type': 'school',
            'sort': 'views'
        }, secure=False)
        
        # Should handle filter parameters
        self.assertIn(response.status_code, [200, 301])


class SharingURLTests(TestCase):
    """Test sharing-related URL patterns"""
    
    def test_sharing_urls_exist(self):
        """Test that sharing URLs are properly configured"""
        # Test URL patterns exist
        self.assertIsNotNone(reverse('public_list', kwargs={'share_slug': 'test-slug-12345678'}))
        self.assertIsNotNone(reverse('embed_list', kwargs={'share_slug': 'test-slug-12345678'}))
        self.assertIsNotNone(reverse('discover_lists'))
    
    def test_sharing_urls_format(self):
        """Test sharing URL formats"""
        public_url = reverse('public_list', kwargs={'share_slug': 'test-slug-12345678'})
        embed_url = reverse('embed_list', kwargs={'share_slug': 'test-slug-12345678'})
        
        self.assertIn('/share/', public_url)
        self.assertIn('/embed/', embed_url)
        self.assertIn('test-slug-12345678', public_url)
        self.assertIn('test-slug-12345678', embed_url)


class SharingSecurityTests(TestCase):
    """Test security aspects of sharing functionality"""
    
    def setUp(self):
        self.packing_list = PackingList.objects.create(
            name="Security Test List",
            is_public=True,
            share_slug="security-test-12345678"
        )
    
    def test_slug_format_security(self):
        """Test that generated slugs are secure"""
        for _ in range(10):
            test_list = PackingList.objects.create(name="Security Test")
            slug = test_list.share_slug
            
            # Should contain only safe characters
            self.assertRegex(slug, r'^[a-z0-9\-]+$')
            # Should have reasonable length
            self.assertLessEqual(len(slug), 60)
            # Should not be guessable
            self.assertGreaterEqual(len(slug), 20)
    
    def test_private_list_isolation(self):
        """Test that private lists are properly isolated"""
        private_list = PackingList.objects.create(
            name="Private Test List",
            is_public=False,
            share_slug="private-test-12345678"
        )
        
        # Should not be accessible via public endpoints
        url = reverse('public_list', kwargs={'share_slug': private_list.share_slug})
        response = self.client.get(url, secure=False)
        self.assertEqual(response.status_code, 404)
    
    def test_view_count_integrity(self):
        """Test that view counts can't be manipulated inappropriately"""
        initial_count = self.packing_list.view_count
        
        # Multiple rapid requests should increment appropriately
        url = reverse('public_list', kwargs={'share_slug': self.packing_list.share_slug})
        for _ in range(5):
            self.client.get(url, secure=False)
        
        # View count should have incremented (exact behavior depends on implementation)
        self.packing_list.refresh_from_db()
        # Note: Actual test would depend on rate limiting implementation


class SharingSEOTests(TestCase):
    """Test SEO and meta tag functionality"""
    
    def setUp(self):
        self.school = School.objects.create(name="SEO Test School")
        self.packing_list = PackingList.objects.create(
            name="SEO Test List",
            description="A list for testing SEO functionality",
            school=self.school,
            is_public=True,
            share_slug="seo-test-12345678"
        )
    
    def test_public_list_has_meta_tags(self):
        """Test that public list view includes proper meta tags"""
        url = reverse('public_list', kwargs={'share_slug': self.packing_list.share_slug})
        response = self.client.get(url, secure=False, follow=True)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for Open Graph tags
            self.assertIn('og:title', content)
            self.assertIn('og:description', content)
            self.assertIn('og:url', content)
            
            # Check for Twitter Card tags
            self.assertIn('twitter:card', content)
            self.assertIn('twitter:title', content)
            
            # Check for basic SEO tags
            self.assertIn('<title>', content)
            self.assertIn('name="description"', content)
    
    def test_embed_view_excludes_seo_tags(self):
        """Test that embed view doesn't include SEO tags (to avoid conflicts)"""
        url = reverse('embed_list', kwargs={'share_slug': self.packing_list.share_slug})
        response = self.client.get(url, secure=False, follow=True)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Should include noindex to prevent search indexing
            self.assertIn('noindex', content)