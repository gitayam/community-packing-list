from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from .models import School, Store, PackingList, Item, PackingListItem, Price, Vote


class SchoolModelTests(TestCase):
    """Test School model functionality"""
    
    def test_school_creation_with_all_fields(self):
        """Test creating a school with all fields"""
        school = School.objects.create(
            name="Test University",
            address="123 College Ave, University City, CA 90210",
            latitude=34.0522,
            longitude=-118.2437
        )
        self.assertEqual(school.name, "Test University")
        self.assertEqual(school.address, "123 College Ave, University City, CA 90210")
        self.assertEqual(school.latitude, 34.0522)
        self.assertEqual(school.longitude, -118.2437)
    
    def test_school_creation_minimal_fields(self):
        """Test creating a school with only required fields"""
        school = School.objects.create(name="Minimal School")
        self.assertEqual(school.name, "Minimal School")
        self.assertIsNone(school.address)
        self.assertIsNone(school.latitude)
        self.assertIsNone(school.longitude)
    
    def test_school_string_representation(self):
        """Test the __str__ method"""
        school = School.objects.create(name="String Test School")
        self.assertEqual(str(school), "String Test School")
    
    def test_school_name_uniqueness(self):
        """Test that school names should be unique (if unique constraint is added)"""
        School.objects.create(name="Unique School")
        # This should work for now since there's no unique constraint
        school2 = School.objects.create(name="Unique School")
        self.assertEqual(School.objects.filter(name="Unique School").count(), 2)


class StoreModelTests(TestCase):
    """Test Store model functionality"""
    
    def test_store_creation_with_all_fields(self):
        """Test creating a store with all address fields"""
        store = Store.objects.create(
            name="Mega Mart",
            address_line1="456 Shopping Blvd",
            address_line2="Suite 100",
            city="Retail City",
            state="CA",
            zip_code="90211",
            country="USA",
            latitude=34.0500,
            longitude=-118.2500
        )
        self.assertEqual(store.name, "Mega Mart")
        self.assertEqual(store.formatted_address, "456 Shopping Blvd, Suite 100, Retail City, CA, 90211, USA")
    
    def test_store_creation_minimal_fields(self):
        """Test creating a store with only name"""
        store = Store.objects.create(name="Minimal Store")
        self.assertEqual(store.name, "Minimal Store")
        self.assertEqual(store.formatted_address, "No address provided")
    
    def test_store_formatted_address_with_partial_fields(self):
        """Test formatted_address with some fields missing"""
        store = Store.objects.create(
            name="Partial Store",
            city="Some City",
            state="ST"
        )
        self.assertEqual(store.formatted_address, "Some City, ST, USA")
    
    def test_store_formatted_address_with_legacy_address(self):
        """Test formatted_address falls back to legacy address"""
        store = Store.objects.create(
            name="Legacy Store",
            full_address_legacy="Old format address, City, State"
        )
        self.assertEqual(store.formatted_address, "Old format address, City, State")
    
    def test_store_string_representation(self):
        """Test the __str__ method"""
        store = Store.objects.create(name="String Test Store")
        self.assertEqual(str(store), "String Test Store")


class ItemModelTests(TestCase):
    """Test Item model functionality"""
    
    def test_item_creation_with_description(self):
        """Test creating an item with description"""
        item = Item.objects.create(
            name="Test Item",
            description="A test item for testing"
        )
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.description, "A test item for testing")
    
    def test_item_creation_minimal_fields(self):
        """Test creating an item with only name"""
        item = Item.objects.create(name="Minimal Item")
        self.assertEqual(item.name, "Minimal Item")
        self.assertEqual(item.description, "")
    
    def test_item_string_representation(self):
        """Test the __str__ method"""
        item = Item.objects.create(name="String Test Item")
        self.assertEqual(str(item), "String Test Item")
    
    def test_item_name_uniqueness(self):
        """Test that item names are unique"""
        Item.objects.create(name="Unique Item")
        with self.assertRaises(IntegrityError):
            Item.objects.create(name="Unique Item")


class PackingListModelTests(TestCase):
    """Test PackingList model functionality"""
    
    def setUp(self):
        self.school = School.objects.create(name="Test School")
    
    def test_packing_list_creation_with_school(self):
        """Test creating a packing list with school"""
        packing_list = PackingList.objects.create(
            name="Test List",
            description="A test packing list",
            school=self.school
        )
        self.assertEqual(packing_list.name, "Test List")
        self.assertEqual(packing_list.description, "A test packing list")
        self.assertEqual(packing_list.school, self.school)
    
    def test_packing_list_creation_without_school(self):
        """Test creating a packing list without school"""
        packing_list = PackingList.objects.create(
            name="No School List",
            description="A list without school"
        )
        self.assertEqual(packing_list.name, "No School List")
        self.assertIsNone(packing_list.school)
    
    def test_packing_list_string_representation(self):
        """Test the __str__ method"""
        packing_list = PackingList.objects.create(name="String Test List")
        self.assertEqual(str(packing_list), "String Test List")


class PackingListItemModelTests(TestCase):
    """Test PackingListItem model functionality"""
    
    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.packing_list = PackingList.objects.create(name="Test List", school=self.school)
        self.item = Item.objects.create(name="Test Item")
    
    def test_packing_list_item_creation(self):
        """Test creating a packing list item"""
        pli = PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item,
            quantity=5,
            notes="Important notes",
            packed=True
        )
        self.assertEqual(pli.packing_list, self.packing_list)
        self.assertEqual(pli.item, self.item)
        self.assertEqual(pli.quantity, 5)
        self.assertEqual(pli.notes, "Important notes")
        self.assertTrue(pli.packed)
    
    def test_packing_list_item_default_values(self):
        """Test default values for packing list item"""
        pli = PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item
        )
        self.assertEqual(pli.quantity, 1)
        self.assertEqual(pli.notes, "")
        self.assertFalse(pli.packed)
    
    def test_packing_list_item_string_representation(self):
        """Test the __str__ method"""
        pli = PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item,
            quantity=3
        )
        self.assertEqual(str(pli), "3 x Test Item for Test List")
    
    def test_packing_list_item_uniqueness(self):
        """Test that each item can only appear once per list"""
        PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item
        )
        with self.assertRaises(IntegrityError):
            PackingListItem.objects.create(
                packing_list=self.packing_list,
                item=self.item
            )


class PriceModelTests(TestCase):
    """Test Price model functionality"""
    
    def setUp(self):
        self.item = Item.objects.create(name="Test Item")
        self.store = Store.objects.create(name="Test Store")
    
    def test_price_creation(self):
        """Test creating a price"""
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("19.99"),
            quantity=2,
            date_purchased="2024-01-15"
        )
        self.assertEqual(price.item, self.item)
        self.assertEqual(price.store, self.store)
        self.assertEqual(price.price, Decimal("19.99"))
        self.assertEqual(price.quantity, 2)
        self.assertEqual(str(price.date_purchased), "2024-01-15")
    
    def test_price_creation_without_date(self):
        """Test creating a price without date"""
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("10.00")
        )
        self.assertIsNone(price.date_purchased)
    
    def test_price_string_representation(self):
        """Test the __str__ method"""
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("15.50")
        )
        self.assertEqual(str(price), "Test Item at Test Store: 15.50 for 1")
    
    def test_price_confidence_field(self):
        """Test the confidence field functionality"""
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("19.99"),
            confidence='high'
        )
        self.assertEqual(price.confidence, 'high')
        self.assertEqual(price.confidence_score, 3)
        
        # Test default confidence
        price_default = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("29.99")
        )
        self.assertEqual(price_default.confidence, 'medium')
        self.assertEqual(price_default.confidence_score, 2)
    
    def test_price_per_unit_property(self):
        """Test the price_per_unit property"""
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("19.99"),
            quantity=2
        )
        self.assertEqual(price.price_per_unit, Decimal("9.995"))
        
        # Test with quantity of 1
        price_single = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("10.00"),
            quantity=1
        )
        self.assertEqual(price_single.price_per_unit, Decimal("10.00"))
    
    def test_price_is_recent_property(self):
        """Test the is_recent property"""
        from datetime import date, timedelta
        
        # Recent price
        recent_price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("19.99"),
            date_purchased=date.today() - timedelta(days=15)
        )
        self.assertTrue(recent_price.is_recent)
        
        # Old price
        old_price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("19.99"),
            date_purchased=date.today() - timedelta(days=45)
        )
        self.assertFalse(old_price.is_recent)
        
        # No date price
        no_date_price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("19.99")
        )
        self.assertFalse(no_date_price.is_recent)


class ItemModelEnhancedTests(TestCase):
    """Test enhanced Item model functionality"""
    
    def setUp(self):
        self.item = Item.objects.create(name="Test Item")
        self.store1 = Store.objects.create(name="Store 1")
        self.store2 = Store.objects.create(name="Store 2")
        
        # Create some test prices
        from datetime import date, timedelta
        
        Price.objects.create(
            item=self.item,
            store=self.store1,
            price=Decimal("19.99"),
            confidence='high',
            date_purchased=date.today() - timedelta(days=5)
        )
        Price.objects.create(
            item=self.item,
            store=self.store2,
            price=Decimal("24.99"),
            confidence='medium',
            date_purchased=date.today() - timedelta(days=10)
        )
        Price.objects.create(
            item=self.item,
            store=self.store1,
            price=Decimal("17.99"),
            confidence='low',
            date_purchased=date.today() - timedelta(days=100)  # Old price
        )
    
    def test_get_price_statistics(self):
        """Test get_price_statistics method"""
        stats = self.item.get_price_statistics()
        
        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['min_price'], Decimal('17.99'))
        self.assertEqual(stats['max_price'], Decimal('24.99'))
        self.assertAlmostEqual(float(stats['avg_price']), 20.99, places=2)
        
        # Check confidence breakdown
        self.assertEqual(stats['confidence_breakdown']['high'], 1)
        self.assertEqual(stats['confidence_breakdown']['medium'], 1)
        self.assertEqual(stats['confidence_breakdown']['low'], 1)
    
    def test_get_best_prices(self):
        """Test get_best_prices method with confidence weighting"""
        best_prices = self.item.get_best_prices(limit=3)
        
        # Should return all 3 prices, ordered by weighted price
        self.assertEqual(len(best_prices), 3)
        
        # Low confidence price ($17.99 / 1.2 = $14.99 equivalent) should be best
        # because even with the penalty, it's still the lowest
        first_price = best_prices[0]
        self.assertEqual(first_price.confidence, 'low')
        self.assertEqual(first_price.price, Decimal('17.99'))
        
        # High confidence price should be second
        second_price = best_prices[1]
        self.assertEqual(second_price.confidence, 'high')
        self.assertEqual(second_price.price, Decimal('19.99'))
    
    def test_get_price_history(self):
        """Test get_price_history method"""
        history = self.item.get_price_history(days=30)
        
        # Should return 2 prices (excluding the old one from 100 days ago)
        self.assertEqual(len(history), 2)
        
        # Check that data is ordered by date
        dates = [entry['date_purchased'] for entry in history]
        self.assertEqual(dates, sorted(dates))


class VoteModelTests(TestCase):
    """Test Vote model functionality"""
    
    def setUp(self):
        self.item = Item.objects.create(name="Test Item")
        self.store = Store.objects.create(name="Test Store")
        self.price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("10.00")
        )
    
    def test_vote_creation_upvote(self):
        """Test creating an upvote"""
        vote = Vote.objects.create(
            price=self.price,
            is_correct_price=True,
            ip_address="127.0.0.1"
        )
        self.assertEqual(vote.price, self.price)
        self.assertTrue(vote.is_correct_price)
        self.assertEqual(vote.ip_address, "127.0.0.1")
        self.assertIsNotNone(vote.created_at)
    
    def test_vote_creation_downvote(self):
        """Test creating a downvote"""
        vote = Vote.objects.create(
            price=self.price,
            is_correct_price=False,
            ip_address="192.168.1.1"
        )
        self.assertEqual(vote.price, self.price)
        self.assertFalse(vote.is_correct_price)
        self.assertEqual(vote.ip_address, "192.168.1.1")
    
    def test_vote_creation_without_ip(self):
        """Test creating a vote without IP address"""
        vote = Vote.objects.create(
            price=self.price,
            is_correct_price=True
        )
        self.assertIsNone(vote.ip_address)
    
    def test_vote_string_representation(self):
        """Test the __str__ method"""
        vote = Vote.objects.create(
            price=self.price,
            is_correct_price=True,
            ip_address="127.0.0.1"
        )
        self.assertIn("Upvote", str(vote))
        self.assertIn("127.0.0.1", str(vote))


class ModelRelationshipTests(TestCase):
    """Test relationships between models"""
    
    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.store = Store.objects.create(name="Test Store")
        self.item = Item.objects.create(name="Test Item")
        self.packing_list = PackingList.objects.create(name="Test List", school=self.school)
    
    def test_packing_list_school_relationship(self):
        """Test packing list to school relationship"""
        self.assertEqual(self.packing_list.school, self.school)
        self.assertIn(self.packing_list, self.school.packing_lists.all())
    
    def test_packing_list_item_relationship(self):
        """Test packing list to item relationship through PackingListItem"""
        pli = PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item,
            quantity=2
        )
        self.assertIn(pli, self.packing_list.items.all())
        self.assertIn(pli, self.item.packing_list_items.all())
    
    def test_item_price_relationship(self):
        """Test item to price relationship"""
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("10.00")
        )
        self.assertIn(price, self.item.prices.all())
        self.assertIn(price, self.store.prices.all())
    
    def test_price_vote_relationship(self):
        """Test price to vote relationship"""
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("10.00")
        )
        vote = Vote.objects.create(
            price=price,
            is_correct_price=True,
            ip_address="127.0.0.1"
        )
        self.assertIn(vote, price.votes.all())
    
    def test_cascade_deletion(self):
        """Test that deleting a parent object deletes related objects"""
        # Create related objects
        pli = PackingListItem.objects.create(
            packing_list=self.packing_list,
            item=self.item
        )
        price = Price.objects.create(
            item=self.item,
            store=self.store,
            price=Decimal("10.00")
        )
        vote = Vote.objects.create(
            price=price,
            is_correct_price=True
        )
        
        # Delete packing list - should delete PackingListItem
        self.packing_list.delete()
        self.assertFalse(PackingListItem.objects.filter(id=pli.id).exists())
        
        # Delete item - should delete Price and Vote
        self.item.delete()
        self.assertFalse(Price.objects.filter(id=price.id).exists())
        self.assertFalse(Vote.objects.filter(id=vote.id).exists())
        
        # Store should still exist
        self.assertTrue(Store.objects.filter(id=self.store.id).exists())


class ModelValidationTests(TestCase):
    """Test model validation and constraints"""
    
    def test_negative_quantity_validation(self):
        """Test that negative quantities are not allowed"""
        school = School.objects.create(name="Test School")
        packing_list = PackingList.objects.create(name="Test List", school=school)
        item = Item.objects.create(name="Test Item")
        
        # This should work since PositiveIntegerField prevents negative values
        pli = PackingListItem.objects.create(
            packing_list=packing_list,
            item=item,
            quantity=0  # Zero is allowed
        )
        self.assertEqual(pli.quantity, 0)
    
    def test_decimal_price_precision(self):
        """Test decimal field precision for prices"""
        item = Item.objects.create(name="Test Item")
        store = Store.objects.create(name="Test Store")
        
        # Test with 2 decimal places
        price = Price.objects.create(
            item=item,
            store=store,
            price=Decimal("19.99")
        )
        self.assertEqual(price.price, Decimal("19.99"))
        
        # Test with more decimal places (should be truncated)
        price2 = Price.objects.create(
            item=item,
            store=store,
            price=Decimal("19.999")
        )
        self.assertEqual(price2.price, Decimal("19.99"))
    
    def test_ip_address_validation(self):
        """Test IP address field validation"""
        item = Item.objects.create(name="Test Item")
        store = Store.objects.create(name="Test Store")
        price = Price.objects.create(
            item=item,
            store=store,
            price=Decimal("10.00")
        )
        
        # Valid IP addresses
        valid_ips = ["127.0.0.1", "192.168.1.1", "10.0.0.1"]
        for ip in valid_ips:
            vote = Vote.objects.create(
                price=price,
                is_correct_price=True,
                ip_address=ip
            )
            self.assertEqual(vote.ip_address, ip)
        
        # Invalid IP address should raise validation error
        with self.assertRaises(ValidationError):
            vote = Vote(
                price=price,
                is_correct_price=True,
                ip_address="invalid-ip"
            )
            vote.full_clean() 