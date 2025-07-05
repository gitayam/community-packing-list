from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.db import IntegrityError
from decimal import Decimal
import json

from .models import School, Store, PackingList, Item, PackingListItem, Price, Vote


class HomeViewTests(TestCase):
    """Test the home view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.packing_list = PackingList.objects.create(name="Test List", school=self.school)
    
    def test_home_view_get(self):
        """Test GET request to home view"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/home.html')
        self.assertContains(response, "Test List")
    
    def test_home_view_with_no_lists(self):
        """Test home view when no packing lists exist"""
        PackingList.objects.all().delete()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No packing lists found")


class CreatePackingListViewTests(TestCase):
    """Test the create packing list view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.school = School.objects.create(name="Existing School")
    
    def test_create_packing_list_get(self):
        """Test GET request to create packing list view"""
        response = self.client.get(reverse('create_packing_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/packing_list_form.html')
        self.assertContains(response, "Create New Packing List")
    
    def test_create_packing_list_post_valid(self):
        """Test POST request with valid data"""
        data = {
            'name': 'New Test List',
            'description': 'A new test list'
        }
        response = self.client.post(reverse('create_packing_list'), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check that the packing list was created
        packing_list = PackingList.objects.get(name='New Test List')
        self.assertEqual(packing_list.description, 'A new test list')
        self.assertIsNone(packing_list.school)
    
    def test_create_packing_list_post_with_school(self):
        """Test POST request with existing school"""
        data = {
            'name': 'List with School',
            'description': 'A list with school',
            'school': self.school.id
        }
        response = self.client.post(reverse('create_packing_list'), data)
        self.assertEqual(response.status_code, 302)
        
        packing_list = PackingList.objects.get(name='List with School')
        self.assertEqual(packing_list.school, self.school)
    
    def test_create_packing_list_post_with_new_school(self):
        """Test POST request with new school name"""
        data = {
            'name': 'List with New School',
            'school_name': 'New School Name'
        }
        response = self.client.post(reverse('create_packing_list'), data)
        self.assertEqual(response.status_code, 302)
        
        packing_list = PackingList.objects.get(name='List with New School')
        self.assertIsNotNone(packing_list.school)
        self.assertEqual(packing_list.school.name, 'New School Name')
    
    def test_create_packing_list_post_invalid(self):
        """Test POST request with invalid data"""
        data = {
            'name': '',  # Empty name should be invalid
            'description': 'Invalid list'
        }
        response = self.client.post(reverse('create_packing_list'), data)
        self.assertEqual(response.status_code, 200)  # Form re-rendered with errors
        self.assertContains(response, "This field is required")


class UploadPackingListViewTests(TestCase):
    """Test the upload packing list view functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_upload_packing_list_get(self):
        """Test GET request to upload view"""
        response = self.client.get(reverse('upload_packing_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/upload_form.html')
    
    def test_upload_csv_file(self):
        """Test uploading a CSV file"""
        csv_content = "Item Name,Quantity,Notes\nShirt,2,Blue\nPants,1,Khaki"
        csv_file = SimpleUploadedFile(
            "test.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(reverse('upload_packing_list'), {
            'file': csv_file
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect to configure
        self.assertIn('/list/upload/configure/', response.url)
        
        # Check session data
        session_key = response.url.split('/')[-2]
        self.assertIn(session_key, self.client.session)
        parsed_items = self.client.session[session_key]
        self.assertEqual(len(parsed_items), 2)
        self.assertEqual(parsed_items[0]['item_name'], 'Shirt')
    
    def test_upload_text_content(self):
        """Test uploading text content"""
        text_content = "Laptop, 1, Work\nMouse\nKeyboard, 1"
        
        response = self.client.post(reverse('upload_packing_list'), {
            'text_content': text_content
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/list/upload/configure/', response.url)
        
        # Check session data
        session_key = response.url.split('/')[-2]
        parsed_items = self.client.session[session_key]
        self.assertEqual(len(parsed_items), 3)
    
    def test_upload_invalid_file_type(self):
        """Test uploading invalid file type"""
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"Some content",
            content_type="text/plain"
        )
        
        response = self.client.post(reverse('upload_packing_list'), {
            'file': invalid_file
        })
        
        self.assertEqual(response.status_code, 200)  # Form re-rendered with errors
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Unsupported file type", str(messages[0]))
    
    def test_upload_both_file_and_text(self):
        """Test uploading both file and text (should fail)"""
        csv_file = SimpleUploadedFile("test.csv", b"content", content_type="text/csv")
        
        response = self.client.post(reverse('upload_packing_list'), {
            'file': csv_file,
            'text_content': 'Some text'
        })
        
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Please provide either a file OR text content", str(messages[0]))
    
    def test_upload_neither_file_nor_text(self):
        """Test uploading neither file nor text (should fail)"""
        response = self.client.post(reverse('upload_packing_list'), {})
        
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Please provide either a file or text content", str(messages[0]))


class PackingListDetailViewTests(TestCase):
    """Test the packing list detail view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.school = School.objects.create(name="Test School")
        self.packing_list = PackingList.objects.create(name="Test List", school=self.school)
        self.item = Item.objects.create(name="Test Item")
        self.packing_list_item = PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item,
            quantity=2,
            notes="Test notes"
        )
        self.store = Store.objects.create(name="Test Store")
        self.price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("10.00")
        )
    
    def test_packing_list_detail_get(self):
        """Test GET request to packing list detail"""
        response = self.client.get(reverse('view_packing_list', args=[self.packing_list.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/packing_list_detail.html')
        self.assertContains(response, "Test List")
        self.assertContains(response, "Test Item")
    
    def test_packing_list_detail_nonexistent(self):
        """Test accessing non-existent packing list"""
        response = self.client.get(reverse('view_packing_list', args=[99999]))
        self.assertEqual(response.status_code, 404)
    
    def test_toggle_packed_status(self):
        """Test toggling item packed status"""
        self.assertFalse(self.packing_list_item.packed)
        
        response = self.client.post(reverse('view_packing_list', args=[self.packing_list.id]), {
            'toggle_packed_item_id': self.packing_list_item.id
        })
        
        self.assertEqual(response.status_code, 302)
        self.packing_list_item.refresh_from_db()
        self.assertTrue(self.packing_list_item.packed)
        
        # Toggle back
        response = self.client.post(reverse('view_packing_list', args=[self.packing_list.id]), {
            'toggle_packed_item_id': self.packing_list_item.id
        })
        
        self.packing_list_item.refresh_from_db()
        self.assertFalse(self.packing_list_item.packed)
    
    def test_toggle_invalid_item_id(self):
        """Test toggling with invalid item ID"""
        response = self.client.post(reverse('view_packing_list', args=[self.packing_list.id]), {
            'toggle_packed_item_id': 99999
        })
        
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Item not found", str(messages[0]))


class AddPriceViewTests(TestCase):
    """Test the add price view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.item = Item.objects.create(name="Test Item")
        self.store = Store.objects.create(name="Test Store")
        self.packing_list = PackingList.objects.create(name="Test List")
    
    def test_add_price_get(self):
        """Test GET request to add price view"""
        response = self.client.get(reverse('add_price_for_item', args=[self.item.id, self.packing_list.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/price_form.html')
        self.assertContains(response, "Test Item")
    
    def test_add_price_post_valid(self):
        """Test POST request with valid price data"""
        data = {
            'store': self.store.id,
            'price': '15.99',
            'quantity': 1
        }
        
        response = self.client.post(
            reverse('add_price_for_item', args=[self.item.id, self.packing_list.id]),
            data
        )
        
        self.assertEqual(response.status_code, 302)
        price = Price.objects.get(item=self.item, store=self.store)
        self.assertEqual(price.price, Decimal("15.99"))
    
    def test_add_price_post_with_new_store(self):
        """Test POST request with new store name"""
        data = {
            'store_name': 'New Store Name',
            'price': '20.00',
            'quantity': 1
        }
        
        response = self.client.post(
            reverse('add_price_for_item', args=[self.item.id, self.packing_list.id]),
            data
        )
        
        self.assertEqual(response.status_code, 302)
        store = Store.objects.get(name='New Store Name')
        price = Price.objects.get(item=self.item, store=store)
        self.assertEqual(price.price, Decimal("20.00"))
    
    def test_add_price_post_invalid(self):
        """Test POST request with invalid data"""
        data = {
            'price': 'invalid_price',
            'quantity': 1
        }
        
        response = self.client.post(
            reverse('add_price_for_item', args=[self.item.id, self.packing_list.id]),
            data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please correct the errors below")


class VoteViewTests(TestCase):
    """Test the vote view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.item = Item.objects.create(name="Test Item")
        self.store = Store.objects.create(name="Test Store")
        self.price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("10.00")
        )
    
    def test_upvote(self):
        """Test upvoting a price"""
        response = self.client.post(reverse('handle_vote'), {
            'upvote_price_id': self.price.id
        })
        
        self.assertEqual(response.status_code, 302)
        vote = Vote.objects.get(price=self.price)
        self.assertTrue(vote.is_correct_price)
    
    def test_downvote(self):
        """Test downvoting a price"""
        response = self.client.post(reverse('handle_vote'), {
            'downvote_price_id': self.price.id
        })
        
        self.assertEqual(response.status_code, 302)
        vote = Vote.objects.get(price=self.price)
        self.assertFalse(vote.is_correct_price)
    
    def test_vote_invalid_price(self):
        """Test voting on non-existent price"""
        response = self.client.post(reverse('handle_vote'), {
            'upvote_price_id': 99999
        })
        
        self.assertEqual(response.status_code, 404)
    
    def test_vote_invalid_request(self):
        """Test vote request without proper data"""
        response = self.client.post(reverse('handle_vote'), {})
        
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Invalid vote submission", str(messages[0]))


class StoreListViewTests(TestCase):
    """Test the store list view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.school = School.objects.create(
            name="Test School",
            latitude=34.0522,
            longitude=-118.2437
        )
        self.store1 = Store.objects.create(
            name="Store 1",
            city="Los Angeles",
            state="CA",
            latitude=34.0500,
            longitude=-118.2500
        )
        self.store2 = Store.objects.create(
            name="Store 2",
            city="San Francisco",
            state="CA",
            latitude=37.7749,
            longitude=-122.4194
        )
    
    def test_store_list_get(self):
        """Test GET request to store list"""
        response = self.client.get(reverse('store_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/store_list.html')
        self.assertContains(response, "Store 1")
        self.assertContains(response, "Store 2")
    
    def test_store_list_filter_by_city(self):
        """Test filtering stores by city"""
        response = self.client.get(reverse('store_list'), {'city': 'Los Angeles'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Store 1")
        self.assertNotContains(response, "Store 2")
    
    def test_store_list_filter_by_state(self):
        """Test filtering stores by state"""
        response = self.client.get(reverse('store_list'), {'state': 'CA'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Store 1")
        self.assertContains(response, "Store 2")
    
    def test_store_list_filter_by_school(self):
        """Test filtering stores by proximity to school"""
        response = self.client.get(reverse('store_list'), {'school_id': self.school.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stores near Test School")
    
    def test_store_list_filter_by_user_location(self):
        """Test filtering stores by user GPS coordinates"""
        response = self.client.get(reverse('store_list'), {
            'user_lat': '34.0522',
            'user_lon': '-118.2437'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stores near your current location")


class ConfigureUploadedListViewTests(TestCase):
    """Test the configure uploaded list view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.session_key = "parsed_items_test"
        self.parsed_items = [
            {'item_name': 'Item 1', 'quantity': 2, 'notes': 'Note 1'},
            {'item_name': 'Item 2', 'quantity': 1, 'notes': ''}
        ]
    
    def test_configure_uploaded_list_get(self):
        """Test GET request to configure uploaded list"""
        # Set up session data
        session = self.client.session
        session[self.session_key] = self.parsed_items
        session['original_filename'] = 'test.csv'
        session.save()
        
        response = self.client.get(reverse('configure_uploaded_list', args=[self.session_key]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/configure_upload_form.html')
        self.assertContains(response, "2 item(s)")
    
    def test_configure_uploaded_list_get_no_session_data(self):
        """Test GET request without session data"""
        response = self.client.get(reverse('configure_uploaded_list', args=['nonexistent_key']))
        self.assertEqual(response.status_code, 302)  # Redirect to upload
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("No items found to configure", str(messages[0]))
    
    def test_configure_uploaded_list_post_valid(self):
        """Test POST request with valid configuration data"""
        # Set up session data
        session = self.client.session
        session[self.session_key] = self.parsed_items
        session['original_filename'] = 'test.csv'
        session.save()
        
        data = {
            'list_name': 'Configured List',
            'description': 'A configured list',
            'school_name': 'New School'
        }
        
        response = self.client.post(reverse('configure_uploaded_list', args=[self.session_key]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check that objects were created
        packing_list = PackingList.objects.get(name='Configured List')
        self.assertEqual(packing_list.description, 'A configured list')
        self.assertEqual(packing_list.school.name, 'New School')
        self.assertEqual(packing_list.items.count(), 2)
        
        # Check that session data was cleared
        self.assertNotIn(self.session_key, self.client.session)
    
    def test_configure_uploaded_list_post_duplicate_name(self):
        """Test POST request with duplicate list name"""
        # Create existing list
        PackingList.objects.create(name='Existing List')
        
        # Set up session data
        session = self.client.session
        session[self.session_key] = self.parsed_items
        session['original_filename'] = 'test.csv'
        session.save()
        
        data = {
            'list_name': 'Existing List',
            'description': 'A duplicate list'
        }
        
        response = self.client.post(reverse('configure_uploaded_list', args=[self.session_key]), data)
        self.assertEqual(response.status_code, 200)  # Form re-rendered with errors
        self.assertContains(response, "A packing list with this name already exists")


class ErrorHandlingTests(TestCase):
    """Test error handling in views"""
    
    def setUp(self):
        self.client = Client()
    
    def test_404_handling(self):
        """Test 404 error handling"""
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)
    
    def test_database_error_handling(self):
        """Test database error handling in views"""
        # This would require mocking database operations to test
        # For now, we'll test that views handle missing objects gracefully
        response = self.client.get(reverse('view_packing_list', args=[99999]))
        self.assertEqual(response.status_code, 404)
    
    def test_file_upload_error_handling(self):
        """Test file upload error handling"""
        # Test with corrupted file data
        corrupted_file = SimpleUploadedFile(
            "test.xlsx",
            b"not a real excel file",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        response = self.client.post(reverse('upload_packing_list'), {
            'file': corrupted_file
        })
        
        self.assertEqual(response.status_code, 200)  # Form re-rendered with errors
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Error processing file" in str(msg) for msg in messages)) 