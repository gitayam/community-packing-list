from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import School, Store, Item, PackingList
from .forms import PackingListForm, PriceForm


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
        self.assertIn('__all__', form.errors)
    
    def test_price_form_invalid_price(self):
        """Test form with invalid price"""
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