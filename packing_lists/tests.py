from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model # If testing user-related features later

from .models import School, Store, PackingList, Item, PackingListItem, Price, Vote
from .forms import PackingListForm, UploadFileForm, PriceForm, ConfigureUploadListForm
from .parsers import parse_csv, parse_excel, parse_pdf, parse_text

import pandas as pd
import io

# ---- Parser Tests ----
class ParserTests(TestCase):
    def test_parse_csv_simple(self):
        csv_data = "Item Name,Quantity,Notes\nShirt,2,Blue\nPants,1,Khaki"
        items, error = parse_csv(csv_data)
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'Shirt')
        self.assertEqual(items[0]['quantity'], 2)
        self.assertEqual(items[0]['notes'], 'Blue')
        self.assertEqual(items[1]['item_name'], 'Pants')
        self.assertEqual(items[1]['quantity'], 1)
        self.assertEqual(items[1]['notes'], 'Khaki')

    def test_parse_csv_alternative_headers(self):
        csv_data = "product,qty,description\nSocks,5,Wool\nShoes,1,Size 10"
        items, error = parse_csv(csv_data)
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'Socks')
        self.assertEqual(items[0]['quantity'], 5)
        self.assertEqual(items[0]['notes'], 'Wool')

    def test_parse_csv_missing_item_column(self):
        csv_data = "Quantity,Notes\n2,Blue\n1,Khaki"
        items, error = parse_csv(csv_data)
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
        self.assertIn("Could not determine the item name column", error)

    def test_parse_csv_empty_or_no_headers(self):
        csv_data = ""
        items, error = parse_csv(csv_data)
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)

        csv_data_no_content = "Item Name,Quantity,Notes\n" # Only headers
        items, error = parse_csv(csv_data_no_content)
        self.assertIsNotNone(error) # Expects "No items found"
        self.assertEqual(len(items), 0)


    def test_parse_text_simple(self):
        text_data = "Laptop, 1, Work\nMouse\nKeyboard, 1"
        items, error = parse_text(text_data)
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['item_name'], 'Laptop')
        self.assertEqual(items[0]['quantity'], 1)
        self.assertEqual(items[0]['notes'], 'Work')
        self.assertEqual(items[1]['item_name'], 'Mouse')
        self.assertEqual(items[1]['quantity'], 1) # Default quantity
        self.assertEqual(items[1]['notes'], '')
        self.assertEqual(items[2]['item_name'], 'Keyboard')
        self.assertEqual(items[2]['quantity'], 1)

    def test_parse_text_only_item_name(self):
        text_data = "Single Item Line"
        items, error = parse_text(text_data)
        self.assertIsNone(error)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['item_name'], 'Single Item Line')
        self.assertEqual(items[0]['quantity'], 1)
        self.assertEqual(items[0]['notes'], '')

    def test_parse_text_item_with_notes_no_qty(self):
        text_data = "Item with notes, some important notes here"
        items, error = parse_text(text_data)
        self.assertIsNone(error)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['item_name'], 'Item with notes')
        self.assertEqual(items[0]['quantity'], 1) # default because second part is not number
        self.assertEqual(items[0]['notes'], 'some important notes here')

    def test_parse_text_empty(self):
        text_data = ""
        items, error = parse_text(text_data)
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)

    def test_parse_excel_simple(self):
        # Create a dummy Excel file in memory
        df_data = {'Item Name': ['Excel Item 1', 'Excel Item 2'],
                   'Quantity': [3, 1],
                   'Notes': ['From Excel', 'Test note']}
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0) # Reset pointer to the beginning of the BytesIO object

        # Wrap in SimpleUploadedFile to mimic Django's file upload handling
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        items, error = parse_excel(excel_file)
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'Excel Item 1')
        self.assertEqual(items[0]['quantity'], 3)
        self.assertEqual(items[0]['notes'], 'From Excel')
        self.assertEqual(items[1]['item_name'], 'Excel Item 2')
        self.assertEqual(items[1]['quantity'], 1)

    def test_parse_pdf_basic_extraction(self):
        # PDF parsing is very basic and highly dependent on PDF structure.
        # This test will be for simple text extraction.
        # Creating a PDF on the fly is complex for a unit test here.
        # We'd typically have a sample PDF file.
        # For now, this test will be more of a placeholder or would need a pre-made simple PDF.
        # If we had a simple PDF file named 'sample.pdf' in the test directory:
        # try:
        #     with open('path/to/your/sample.pdf', 'rb') as f:
        #         pdf_file = SimpleUploadedFile("sample.pdf", f.read(), content_type="application/pdf")
        #         items, error = parse_pdf(pdf_file)
        #         self.assertIsNone(error)
        #         # Add assertions based on the content of sample.pdf
        #         # e.g., self.assertTrue(len(items) > 0) if it has parsable lines
        # except FileNotFoundError:
        #     self.skipTest("Sample PDF file not found for testing parse_pdf.")
        pass # Skipping actual PDF test for now due to complexity of creating test PDF

# ---- Model Tests ----
class ModelCreationTests(TestCase):
    def setUp(self):
        self.school1 = School.objects.create(name="Test School A", address="123 Main St", latitude=34.0522, longitude=-118.2437)
        self.store1 = Store.objects.create(name="Test Store X", city="Testville", state="TS", latitude=34.0500, longitude=-118.2500)
        self.item1 = Item.objects.create(name="Test Item 1", description="A test item")
        self.item2 = Item.objects.create(name="Test Item 2")

    def test_school_creation(self):
        self.assertEqual(self.school1.name, "Test School A")
        self.assertIsNotNone(self.school1.latitude)

    def test_store_creation(self):
        self.assertEqual(self.store1.name, "Test Store X")
        self.assertEqual(self.store1.formatted_address, "Testville, TS, USA")

    def test_item_creation(self):
        self.assertEqual(self.item1.name, "Test Item 1")

    def test_packing_list_creation(self):
        packing_list = PackingList.objects.create(name="My Test List", school=self.school1, description="List for testing")
        self.assertEqual(packing_list.name, "My Test List")
        self.assertEqual(packing_list.school, self.school1)

    def test_packing_list_item_creation(self):
        packing_list = PackingList.objects.create(name="List with Item")
        pli = PackingListItem.objects.create(packing_list=packing_list, item=self.item1, quantity=5, notes="Important notes")
        self.assertEqual(pli.item, self.item1)
        self.assertEqual(pli.quantity, 5)
        self.assertEqual(packing_list.items.count(), 1)

    def test_price_creation(self):
        price = Price.objects.create(item=self.item1, store=self.store1, price="19.99", quantity=1)
        self.assertEqual(price.item, self.item1)
        self.assertEqual(price.store, self.store1)
        self.assertEqual(str(price.price), "19.99")

    def test_vote_creation(self):
        price = Price.objects.create(item=self.item1, store=self.store1, price="10.00")
        vote = Vote.objects.create(price=price, is_correct_price=True, ip_address="127.0.0.1")
        self.assertEqual(vote.price, price)
        self.assertTrue(vote.is_correct_price)
        self.assertEqual(vote.ip_address, "127.0.0.1")
        self.assertIsNotNone(vote.created_at)

# ---- Form Tests ----
class FormValidationTests(TestCase):
    def test_packing_list_form_valid(self):
        form_data = {'name': 'New Holiday List', 'description': 'For the holidays'}
        form = PackingListForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_packing_list_form_new_school(self):
        form_data = {'name': 'List with New School', 'school_name': 'Online University'}
        form = PackingListForm(data=form_data)
        self.assertTrue(form.is_valid())
        packing_list = form.save()
        self.assertIsNotNone(packing_list.school)
        self.assertEqual(packing_list.school.name, 'Online University')

    def test_price_form_valid(self):
        store = Store.objects.create(name="Local Mart")
        item = Item.objects.create(name="Bread")
        form_data = {'store': store.id, 'price': '2.99', 'quantity': 1}
        form = PriceForm(data=form_data)
        # PriceForm requires item_instance to be passed to save(), but not for is_valid() if item is not in fields
        self.assertTrue(form.is_valid())
        # price_instance = form.save(item_instance=item) # Test save separately if needed
        # self.assertEqual(price_instance.item, item)


# ---- View Tests ----
class ViewAccessibilityTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Test School", latitude=10, longitude=10)
        self.item = Item.objects.create(name="Sample Item")
        self.store = Store.objects.create(name="Sample Store")
        self.packing_list = PackingList.objects.create(name="Test View List", school=self.school)
        PackingListItem.objects.create(packing_list=self.packing_list, item=self.item, quantity=1)
        self.price = Price.objects.create(item=self.item, store=self.store, price="5.00")


    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/home.html')

    def test_create_packing_list_get(self):
        response = self.client.get(reverse('create_packing_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/packing_list_form.html')

    def test_packing_list_detail_view_status_code(self):
        response = self.client.get(reverse('view_packing_list', args=[self.packing_list.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/packing_list_detail.html')
        self.assertContains(response, self.packing_list.name)
        self.assertContains(response, self.item.name) # Check if item name is on page

    def test_upload_packing_list_get(self):
        response = self.client.get(reverse('upload_packing_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/upload_form.html')

    def test_add_price_for_item_get(self):
        response = self.client.get(reverse('add_price_for_item', args=[self.item.id, self.packing_list.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/price_form.html')
        self.assertContains(response, self.item.name)

    def test_store_list_view_status_code(self):
        response = self.client.get(reverse('store_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/store_list.html')
        self.assertContains(response, self.store.name)


class UploadProcessTests(TestCase):
    def test_upload_csv_redirects_to_configure(self):
        csv_data = "Item Name,Quantity\nTest Upload Item,1"
        # Create a SimpleUploadedFile
        csv_file = SimpleUploadedFile("test_upload.csv", csv_data.encode('utf-8'), content_type="text/csv")

        response = self.client.post(reverse('upload_packing_list'), {'file': csv_file})

        self.assertEqual(response.status_code, 302) # Should redirect
        self.assertIn('/list/upload/configure/', response.url)
        session_key_items = response.url.split('/')[-2] # Extract session key from redirect URL

        # Check session data
        self.assertIn(session_key_items, self.client.session)
        self.assertEqual(self.client.session[session_key_items][0]['item_name'], 'Test Upload Item')
        self.assertEqual(self.client.session['original_filename'], 'test_upload.csv')

    def test_configure_uploaded_list_get(self):
        # Simulate session data
        session = self.client.session
        session_key = f"parsed_items_testkey"
        session[session_key] = [{'item_name': 'Test Item from Session', 'quantity': 1, 'notes': ''}]
        session['original_filename'] = 'session_upload.txt'
        session.save()

        response = self.client.get(reverse('configure_uploaded_list', args=[session_key]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'packing_lists/configure_upload_form.html')
        self.assertContains(response, '1 item(s)') # Check if it shows the correct item count

    def test_configure_uploaded_list_post_creates_list_and_items(self):
        # Simulate session data
        session = self.client.session
        session_key = f"parsed_items_configure_post"
        parsed_data = [{'item_name': 'Configured Item 1', 'quantity': 2, 'notes': 'Note A'},
                       {'item_name': 'Configured Item 2', 'quantity': 1, 'notes': ''}]
        session[session_key] = parsed_data
        session['original_filename'] = 'configure_me.txt'
        session.save()

        school_name = "Config Test School"
        list_name = "My Configured List"

        response = self.client.post(reverse('configure_uploaded_list', args=[session_key]), {
            'list_name': list_name,
            'description': 'A configured list.',
            'school_name': school_name # Create new school
        })

        self.assertEqual(response.status_code, 302) # Redirects to view_packing_list

        # Verify PackingList created
        self.assertTrue(PackingList.objects.filter(name=list_name).exists())
        new_list = PackingList.objects.get(name=list_name)
        self.assertEqual(new_list.school.name, school_name)

        # Verify Items and PackingListItems created
        self.assertTrue(Item.objects.filter(name='Configured Item 1').exists())
        self.assertTrue(Item.objects.filter(name='Configured Item 2').exists())
        self.assertEqual(new_list.items.count(), 2)

        pli1 = PackingListItem.objects.get(packing_list=new_list, item__name='Configured Item 1')
        self.assertEqual(pli1.quantity, 2)
        self.assertEqual(pli1.notes, 'Note A')

        # Verify session data is cleared
        self.assertNotIn(session_key, self.client.session)
        self.assertNotIn('original_filename', self.client.session)

# More tests can be added for voting, price creation logic, store filtering, etc.
# For example, testing the Haversine function or specific filter applications in store_list view.

# To run these tests: python manage.py test packing_lists
