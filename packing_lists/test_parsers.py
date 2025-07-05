from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
import io

from .parsers import parse_csv, parse_excel, parse_pdf, parse_text


class CSVParserTests(TestCase):
    """Test CSV parsing functionality"""
    
    def test_parse_csv_standard_headers(self):
        """Test parsing CSV with standard headers"""
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
        """Test parsing CSV with alternative headers"""
        csv_data = "product,qty,description\nSocks,5,Wool\nShoes,1,Size 10"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'Socks')
        self.assertEqual(items[0]['quantity'], 5)
        self.assertEqual(items[0]['notes'], 'Wool')
    
    def test_parse_csv_missing_quantity_column(self):
        """Test parsing CSV without quantity column"""
        csv_data = "Item Name,Notes\nShirt,Blue\nPants,Khaki"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['quantity'], 1)  # Default quantity
        self.assertEqual(items[1]['quantity'], 1)
    
    def test_parse_csv_missing_notes_column(self):
        """Test parsing CSV without notes column"""
        csv_data = "Item Name,Quantity\nShirt,2\nPants,1"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['notes'], '')
        self.assertEqual(items[1]['notes'], '')
    
    def test_parse_csv_missing_item_column(self):
        """Test parsing CSV without item name column"""
        csv_data = "Quantity,Notes\n2,Blue\n1,Khaki"
        items, error = parse_csv(csv_data)
        
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
        self.assertIn("Could not determine the item name column", error)
    
    def test_parse_csv_empty_file(self):
        """Test parsing empty CSV file"""
        csv_data = ""
        items, error = parse_csv(csv_data)
        
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
    
    def test_parse_csv_only_headers(self):
        """Test parsing CSV with only headers"""
        csv_data = "Item Name,Quantity,Notes\n"
        items, error = parse_csv(csv_data)
        
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
        self.assertIn("No items found", error)
    
    def test_parse_csv_with_empty_rows(self):
        """Test parsing CSV with empty rows"""
        csv_data = "Item Name,Quantity,Notes\nShirt,2,Blue\n\nPants,1,Khaki\n"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)  # Empty rows should be skipped
    
    def test_parse_csv_with_whitespace(self):
        """Test parsing CSV with whitespace in data"""
        csv_data = "Item Name,Quantity,Notes\n  Shirt  , 2 ,  Blue  \nPants,1,Khaki"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'Shirt')
        self.assertEqual(items[0]['quantity'], 2)
        self.assertEqual(items[0]['notes'], 'Blue')
    
    def test_parse_csv_invalid_quantity(self):
        """Test parsing CSV with invalid quantity values"""
        csv_data = "Item Name,Quantity,Notes\nShirt,invalid,Blue\nPants,1.5,Khaki\nSocks,0,Test"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['quantity'], 1)  # Default for invalid
        self.assertEqual(items[1]['quantity'], 1)  # Default for float
        self.assertEqual(items[2]['quantity'], 0)  # Zero is valid
    
    def test_parse_csv_unicode_characters(self):
        """Test parsing CSV with unicode characters"""
        csv_data = "Item Name,Quantity,Notes\nT-shirt,2,Blå\nPants,1,Khaki"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'T-shirt')
        self.assertEqual(items[0]['notes'], 'Blå')


class ExcelParserTests(TestCase):
    """Test Excel parsing functionality"""
    
    def test_parse_excel_standard_headers(self):
        """Test parsing Excel with standard headers"""
        df_data = {
            'Item Name': ['Excel Item 1', 'Excel Item 2'],
            'Quantity': [3, 1],
            'Notes': ['From Excel', 'Test note']
        }
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile(
            "test.xlsx",
            excel_file_io.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        items, error = parse_excel(excel_file)
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'Excel Item 1')
        self.assertEqual(items[0]['quantity'], 3)
        self.assertEqual(items[0]['notes'], 'From Excel')
    
    def test_parse_excel_alternative_headers(self):
        """Test parsing Excel with alternative headers"""
        df_data = {
            'product': ['Product 1', 'Product 2'],
            'qty': [5, 2],
            'description': ['Desc 1', 'Desc 2']
        }
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read())
        items, error = parse_excel(excel_file)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'Product 1')
        self.assertEqual(items[0]['quantity'], 5)
        self.assertEqual(items[0]['notes'], 'Desc 1')
    
    def test_parse_excel_missing_quantity_column(self):
        """Test parsing Excel without quantity column"""
        df_data = {
            'Item Name': ['Item 1', 'Item 2'],
            'Notes': ['Note 1', 'Note 2']
        }
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read())
        items, error = parse_excel(excel_file)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['quantity'], 1)  # Default quantity
        self.assertEqual(items[1]['quantity'], 1)
    
    def test_parse_excel_missing_item_column(self):
        """Test parsing Excel without item name column"""
        df_data = {
            'Quantity': [2, 1],
            'Notes': ['Note 1', 'Note 2']
        }
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read())
        items, error = parse_excel(excel_file)
        
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
        self.assertIn("Could not determine the item name column", error)
    
    def test_parse_excel_empty_sheet(self):
        """Test parsing empty Excel sheet"""
        df = pd.DataFrame()
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read())
        items, error = parse_excel(excel_file)
        
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
        self.assertIn("Excel sheet is empty", error)
    
    def test_parse_excel_with_nan_values(self):
        """Test parsing Excel with NaN values"""
        df_data = {
            'Item Name': ['Item 1', 'Item 2', 'Item 3'],
            'Quantity': [1, float('nan'), 3],
            'Notes': ['Note 1', 'Note 2', float('nan')]
        }
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read())
        items, error = parse_excel(excel_file)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[1]['quantity'], 1)  # Default for NaN
        self.assertEqual(items[2]['notes'], '')  # Empty string for NaN
    
    def test_parse_excel_float_quantities(self):
        """Test parsing Excel with float quantities"""
        df_data = {
            'Item Name': ['Item 1', 'Item 2'],
            'Quantity': [2.0, 1.5],
            'Notes': ['Note 1', 'Note 2']
        }
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read())
        items, error = parse_excel(excel_file)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['quantity'], 2)  # Converted to int
        self.assertEqual(items[1]['quantity'], 1)  # Converted to int


class PDFParserTests(TestCase):
    """Test PDF parsing functionality"""
    
    def test_parse_pdf_basic_text(self):
        """Test parsing basic PDF text"""
        # Create a simple PDF-like text content
        pdf_content = "Item 1\nItem 2\nItem 3"
        
        # Mock PDF file with text content
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content.encode('utf-8'), content_type="application/pdf")
        
        items, error = parse_pdf(pdf_file)
        
        # PDF parsing is basic, so we expect it to work with simple text
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['item_name'], 'Item 1')
        self.assertEqual(items[1]['item_name'], 'Item 2')
        self.assertEqual(items[2]['item_name'], 'Item 3')
    
    def test_parse_pdf_empty_content(self):
        """Test parsing PDF with empty content"""
        pdf_content = ""
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content.encode('utf-8'), content_type="application/pdf")
        
        items, error = parse_pdf(pdf_file)
        
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
        self.assertIn("No text could be extracted", error)
    
    def test_parse_pdf_with_whitespace(self):
        """Test parsing PDF with extra whitespace"""
        pdf_content = "  Item 1  \n\n  Item 2  \n  Item 3  "
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content.encode('utf-8'), content_type="application/pdf")
        
        items, error = parse_pdf(pdf_file)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['item_name'], 'Item 1')
        self.assertEqual(items[1]['item_name'], 'Item 2')
        self.assertEqual(items[2]['item_name'], 'Item 3')
    
    def test_parse_pdf_complex_content(self):
        """Test parsing PDF with complex content"""
        pdf_content = """
        Shopping List:
        
        - Laptop, 1, Work computer
        - Mouse, 2, Wireless
        - Keyboard, 1, Mechanical
        
        Total items: 4
        """
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content.encode('utf-8'), content_type="application/pdf")
        
        items, error = parse_pdf(pdf_file)
        
        self.assertIsNone(error)
        self.assertTrue(len(items) > 0)  # Should extract some items
    
    def test_parse_pdf_error_handling(self):
        """Test PDF parsing error handling"""
        # Create a file that's not actually a PDF
        invalid_content = b"This is not a PDF file"
        pdf_file = SimpleUploadedFile("test.pdf", invalid_content, content_type="application/pdf")
        
        items, error = parse_pdf(pdf_file)
        
        # Should handle the error gracefully
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)


class TextParserTests(TestCase):
    """Test text parsing functionality"""
    
    def test_parse_text_simple(self):
        """Test parsing simple text"""
        text_data = "Laptop, 1, Work\nMouse\nKeyboard, 1"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['item_name'], 'Laptop')
        self.assertEqual(items[0]['quantity'], 1)
        self.assertEqual(items[0]['notes'], 'Work')
        self.assertEqual(items[1]['item_name'], 'Mouse')
        self.assertEqual(items[1]['quantity'], 1)  # Default quantity
        self.assertEqual(items[1]['notes'], '')
        self.assertEqual(items[2]['item_name'], 'Keyboard')
        self.assertEqual(items[2]['quantity'], 1)
    
    def test_parse_text_only_item_name(self):
        """Test parsing text with only item names"""
        text_data = "Single Item Line\nAnother Item"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'Single Item Line')
        self.assertEqual(items[0]['quantity'], 1)  # Default quantity
        self.assertEqual(items[0]['notes'], '')
    
    def test_parse_text_item_with_notes_no_qty(self):
        """Test parsing text with item and notes but no quantity"""
        text_data = "Item with notes, some important notes here"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['item_name'], 'Item with notes')
        self.assertEqual(items[0]['quantity'], 1)  # Default because second part is not number
        self.assertEqual(items[0]['notes'], 'some important notes here')
    
    def test_parse_text_empty(self):
        """Test parsing empty text"""
        text_data = ""
        items, error = parse_text(text_data)
        
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
        self.assertIn("Text content is empty", error)
    
    def test_parse_text_whitespace_only(self):
        """Test parsing text with only whitespace"""
        text_data = "   \n\n  \n"
        items, error = parse_text(text_data)
        
        self.assertIsNotNone(error)
        self.assertEqual(len(items), 0)
        self.assertIn("Text content is empty", error)
    
    def test_parse_text_with_quantities(self):
        """Test parsing text with explicit quantities"""
        text_data = "Laptop, 2, Work computer\nMouse, 3, Wireless\nKeyboard, 1"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['quantity'], 2)
        self.assertEqual(items[1]['quantity'], 3)
        self.assertEqual(items[2]['quantity'], 1)
    
    def test_parse_text_with_invalid_quantities(self):
        """Test parsing text with invalid quantity values"""
        text_data = "Item 1, invalid, Note 1\nItem 2, 2.5, Note 2\nItem 3, 0, Note 3"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['quantity'], 1)  # Default for invalid
        self.assertEqual(items[1]['quantity'], 2)  # Converted from float
        self.assertEqual(items[2]['quantity'], 0)  # Zero is valid
    
    def test_parse_text_with_special_characters(self):
        """Test parsing text with special characters"""
        text_data = "T-shirt, 2, Blue color\nPants, 1, Khaki style"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['item_name'], 'T-shirt')
        self.assertEqual(items[0]['notes'], 'Blue color')
    
    def test_parse_text_with_unicode(self):
        """Test parsing text with unicode characters"""
        text_data = "T-shirt, 2, Blå färg\nPants, 1, Khaki stil"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['notes'], 'Blå färg')
        self.assertEqual(items[1]['notes'], 'Khaki stil')
    
    def test_parse_text_with_empty_lines(self):
        """Test parsing text with empty lines"""
        text_data = "Item 1, 1, Note 1\n\nItem 2, 2, Note 2\n\n\nItem 3, 3, Note 3"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 3)  # Empty lines should be skipped
        self.assertEqual(items[0]['item_name'], 'Item 1')
        self.assertEqual(items[1]['item_name'], 'Item 2')
        self.assertEqual(items[2]['item_name'], 'Item 3')


class ParserEdgeCaseTests(TestCase):
    """Test edge cases and error conditions in parsers"""
    
    def test_csv_parser_very_long_item_name(self):
        """Test CSV parser with very long item name"""
        long_name = 'A' * 1000
        csv_data = f"Item Name,Quantity,Notes\n{long_name},1,Test"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['item_name'], long_name)
    
    def test_excel_parser_very_long_item_name(self):
        """Test Excel parser with very long item name"""
        long_name = 'A' * 1000
        df_data = {
            'Item Name': [long_name],
            'Quantity': [1],
            'Notes': ['Test']
        }
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read())
        items, error = parse_excel(excel_file)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['item_name'], long_name)
    
    def test_text_parser_very_long_item_name(self):
        """Test text parser with very long item name"""
        long_name = 'A' * 1000
        text_data = f"{long_name}, 1, Test"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['item_name'], long_name)
    
    def test_csv_parser_malformed_data(self):
        """Test CSV parser with malformed data"""
        csv_data = "Item Name,Quantity,Notes\nShirt,2,Blue\nPants,1,Khaki,Extra,Data"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)  # Should handle extra columns gracefully
    
    def test_excel_parser_malformed_data(self):
        """Test Excel parser with malformed data"""
        df_data = {
            'Item Name': ['Item 1', 'Item 2'],
            'Quantity': [1, 2],
            'Notes': ['Note 1', 'Note 2'],
            'Extra': ['Extra 1', 'Extra 2']  # Extra column
        }
        df = pd.DataFrame(df_data)
        excel_file_io = io.BytesIO()
        with pd.ExcelWriter(excel_file_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file_io.seek(0)
        
        excel_file = SimpleUploadedFile("test.xlsx", excel_file_io.read())
        items, error = parse_excel(excel_file)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)  # Should handle extra columns gracefully
    
    def test_parser_performance_large_files(self):
        """Test parser performance with large files"""
        # Create a large CSV file
        csv_lines = []
        for i in range(1000):
            csv_lines.append(f"Item {i}, {i % 10 + 1}, Note {i}")
        
        csv_data = "Item Name,Quantity,Notes\n" + "\n".join(csv_lines)
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 1000)
        self.assertEqual(items[0]['item_name'], 'Item 0')
        self.assertEqual(items[999]['item_name'], 'Item 999')
    
    def test_parser_encoding_issues(self):
        """Test parser handling of encoding issues"""
        # Test with UTF-8 encoded text
        text_data = "T-shirt, 2, Blå färg\nPants, 1, Khaki stil"
        items, error = parse_text(text_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['notes'], 'Blå färg')
    
    def test_parser_empty_item_names(self):
        """Test parser handling of empty item names"""
        csv_data = "Item Name,Quantity,Notes\n,2,Blue\nPants,1,Khaki\n,3,Red"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 1)  # Only 'Pants' should be included
        self.assertEqual(items[0]['item_name'], 'Pants')
    
    def test_parser_whitespace_only_item_names(self):
        """Test parser handling of whitespace-only item names"""
        csv_data = "Item Name,Quantity,Notes\n   ,2,Blue\nPants,1,Khaki\n  ,3,Red"
        items, error = parse_csv(csv_data)
        
        self.assertIsNone(error)
        self.assertEqual(len(items), 1)  # Only 'Pants' should be included
        self.assertEqual(items[0]['item_name'], 'Pants') 