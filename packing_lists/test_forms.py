from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import School, Store, Item, PackingList
from .forms import PackingListForm, PriceForm, BulkPriceForm


class PackingListFormTests(TestCase):
    """Test PackingListForm functionality"""
    
    def setUp(self):
        self.school = School.objects.create(name="Existing School")
    
    def test_packing_list_form_valid(self):
        """Test form with valid data"""
        form_data = {
            'name': 'Test List',
            'description': 'A test list'
        }
        form = PackingListForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_packing_list_form_with_existing_school(self):
        """Test form with existing school selection"""
        form_data = {
            'name': 'Test List',
            'school': self.school.id
        }
        form = PackingListForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        packing_list = form.save()
        self.assertEqual(packing_list.school, self.school)
    
    def test_packing_list_form_with_new_school(self):
        """Test form with new school name"""
        form_data = {
            'name': 'Test List',
            'school_name': 'New School Name'
        }
        form = PackingListForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        packing_list = form.save()
        self.assertIsNotNone(packing_list.school)
        self.assertEqual(packing_list.school.name, 'New School Name')
    
    def test_packing_list_form_with_both_schools(self):
        """Test form with both existing school and new school name"""
        form_data = {
            'name': 'Test List',
            'school': self.school.id,
            'school_name': 'New School Name'
        }
        form = PackingListForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Should prefer existing school
        packing_list = form.save()
        self.assertEqual(packing_list.school, self.school)
    
    def test_packing_list_form_invalid(self):
        """Test form with invalid data"""
        form_data = {
            'name': '',  # Empty name
            'description': 'Invalid list'
        }
        form = PackingListForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_packing_list_form_school_queryset(self):
        """Test that school queryset is ordered by name"""
        # Clear existing schools to ensure clean test
        School.objects.all().delete()
        School.objects.create(name="A School")
        School.objects.create(name="Z School")
        
        form = PackingListForm()
        schools = list(form.fields['school'].queryset)
        self.assertEqual(schools[0].name, "A School")
        self.assertEqual(schools[1].name, "Z School")


class PriceFormTests(TestCase):
    """Test PriceForm functionality"""
    
    def setUp(self):
        self.store = Store.objects.create(name="Existing Store")
        self.item = Item.objects.create(name="Test Item")
    
    def test_price_form_valid(self):
        """Test form with valid data"""
        form_data = {
            'store': self.store.id,
            'price': '19.99',
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_price_form_with_new_store(self):
        """Test form with new store name"""
        form_data = {
            'store_name': 'New Store Name',
            'price': '15.50',
            'quantity': 2
        }
        form = PriceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        price = form.save(item_instance=self.item)
        self.assertEqual(price.store.name, 'New Store Name')
        self.assertEqual(price.item, self.item)
    
    def test_price_form_with_both_stores(self):
        """Test form with both existing store and new store name"""
        form_data = {
            'store': self.store.id,
            'store_name': 'New Store Name',
            'price': '10.00',
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Should prefer existing store
        price = form.save(item_instance=self.item)
        self.assertEqual(price.store, self.store)
    
    def test_price_form_neither_store(self):
        """Test form with neither existing store nor new store name"""
        form_data = {
            'price': '10.00',
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Please select an existing store or provide a new store name.', str(form.errors))
    
    def test_price_form_enhanced_validation(self):
        """Test enhanced price validation"""
        # Test negative price
        form_data = {
            'store': self.store.id,
            'price': '-5.00',
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        
        # Test very high price
        form_data['price'] = '15000.00'
        form = PriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        
        # Test zero quantity
        form_data['price'] = '19.99'
        form_data['quantity'] = 0
        form = PriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
    
    def test_price_form_with_confidence(self):
        """Test form with confidence field"""
        form_data = {
            'store': self.store.id,
            'price': '19.99',
            'quantity': 1,
            'confidence': 'high'
        }
        form = PriceForm(data=form_data, item_instance=self.item)
        self.assertTrue(form.is_valid())
        price = form.save(item_instance=self.item)
        self.assertEqual(price.confidence, 'high')
    
    def test_price_form_price_per_unit_validation(self):
        """Test price per unit validation"""
        form_data = {
            'store': self.store.id,
            'price': '0.05',  # 5 cents for 10 items = 0.5 cents per unit (less than 1 cent)
            'quantity': 10
        }
        form = PriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Price per unit cannot be less than $0.01', str(form.errors))


class BulkPriceFormTests(TestCase):
    """Test BulkPriceForm functionality"""
    
    def setUp(self):
        self.store = Store.objects.create(name="Test Store")
    
    def test_bulk_price_form_valid(self):
        """Test form with valid bulk data"""
        form_data = {
            'store': self.store.id,
            'confidence': 'medium',
            'price_data': 'Compass, 19.99, 1\nSleeping Bag, 89.99, 1\nFirst Aid Kit, 24.99, 1'
        }
        form = BulkPriceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_bulk_price_form_invalid_format(self):
        """Test form with invalid CSV format"""
        form_data = {
            'store': self.store.id,
            'confidence': 'medium',
            'price_data': 'Compass, 19.99\nSleeping Bag, 89.99, 1, extra'  # Wrong number of fields
        }
        form = BulkPriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price_data', form.errors)
    
    def test_bulk_price_form_invalid_prices(self):
        """Test form with invalid price values"""
        form_data = {
            'store': self.store.id,
            'confidence': 'medium',
            'price_data': 'Compass, -19.99, 1\nSleeping Bag, not_a_price, 1'
        }
        form = BulkPriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price_data', form.errors)
    
    def test_bulk_price_form_save(self):
        """Test saving bulk price data"""
        form_data = {
            'store': self.store.id,
            'confidence': 'high',
            'price_data': 'Compass, 19.99, 1\nSleeping Bag, 89.99, 1'
        }
        form = BulkPriceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        created_prices, created_items = form.save()
        
        self.assertEqual(len(created_prices), 2)
        self.assertEqual(len(created_items), 2)
        
        # Check that items were created
        self.assertTrue(Item.objects.filter(name='Compass').exists())
        self.assertTrue(Item.objects.filter(name='Sleeping Bag').exists())
        
        # Check that prices were created
        compass_price = Price.objects.get(item__name='Compass')
        self.assertEqual(compass_price.price, Decimal('19.99'))
        self.assertEqual(compass_price.confidence, 'high')
        self.assertEqual(compass_price.store, self.store)
    
    def test_bulk_price_form_with_new_store(self):
        """Test bulk form with new store creation"""
        form_data = {
            'store_name': 'New Bulk Store',
            'confidence': 'medium',
            'price_data': 'Test Item, 9.99, 1'
        }
        form = BulkPriceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        created_prices, created_items = form.save()
        
        self.assertEqual(len(created_prices), 1)
        self.assertEqual(len(created_items), 1)
        
        # Check that new store was created
        self.assertTrue(Store.objects.filter(name='New Bulk Store').exists())
        new_store = Store.objects.get(name='New Bulk Store')
        
        # Check that price is associated with new store
        test_price = Price.objects.get(item__name='Test Item')
        self.assertEqual(test_price.store, new_store)
        form_data = {
            'store': self.store.id,
            'price': 'invalid_price',
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
    
    def test_price_form_negative_quantity(self):
        """Test form with negative quantity"""
        form_data = {
            'store': self.store.id,
            'price': '10.00',
            'quantity': -1
        }
        form = PriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
    
    def test_price_form_save_without_item_instance(self):
        """Test form save without item instance"""
        form_data = {
            'store': self.store.id,
            'price': '10.00',
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        with self.assertRaises(ValueError):
            form.save()
    
    def test_price_form_store_queryset(self):
        """Test that store queryset is ordered by name"""
        # Clear existing stores to ensure clean test
        Store.objects.all().delete()
        Store.objects.create(name="A Store")
        Store.objects.create(name="Z Store")
        
        form = PriceForm()
        stores = list(form.fields['store'].queryset)
        self.assertEqual(stores[0].name, "A Store")
        self.assertEqual(stores[1].name, "Z Store")


class FormEdgeCaseTests(TestCase):
    """Test edge cases and error conditions in forms"""
    
    def test_packing_list_form_very_long_name(self):
        """Test form with very long name"""
        long_name = 'A' * 201  # Exceeds max_length of 200
        form_data = {'name': long_name}
        form = PackingListForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_price_form_very_high_price(self):
        """Test form with very high price"""
        high_price = '999999.99'  # Should be within max_digits=10
        form_data = {
            'store_name': 'Test Store',
            'price': high_price,
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_price_form_too_high_price(self):
        """Test form with price exceeding max_digits"""
        too_high_price = '9999999999.99'  # Exceeds max_digits=10
        form_data = {
            'store_name': 'Test Store',
            'price': too_high_price,
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
    
    def test_price_form_zero_price(self):
        """Test form with zero price"""
        form_data = {
            'store_name': 'Test Store',
            'price': '0.00',
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_price_form_zero_quantity(self):
        """Test form with zero quantity"""
        form_data = {
            'store_name': 'Test Store',
            'price': '10.00',
            'quantity': 0
        }
        form = PriceForm(data=form_data)
        self.assertTrue(form.is_valid())  # Zero is allowed for PositiveIntegerField
    
    def test_school_name_whitespace_handling(self):
        """Test that school names are properly stripped of whitespace"""
        form_data = {
            'name': 'Test List',
            'school_name': '  School with spaces  '
        }
        form = PackingListForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        packing_list = form.save()
        self.assertEqual(packing_list.school.name, 'School with spaces')
    
    def test_store_name_whitespace_handling(self):
        """Test that store names are properly stripped of whitespace"""
        form_data = {
            'store_name': '  Store with spaces  ',
            'price': '10.00',
            'quantity': 1
        }
        form = PriceForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        price = form.save(item_instance=Item.objects.create(name="Test Item"))
        self.assertEqual(price.store.name, 'Store with spaces') 