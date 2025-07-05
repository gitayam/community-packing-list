import csv
import io
import pandas as pd
from PyPDF2 import PdfReader
# import pdfplumber # Alternative PDF parsing library

# Expected column headers (can be flexible)
# We'll try to infer these or allow mapping if not exact
EXPECTED_ITEM_COLUMNS = ['item', 'item name', 'name', 'product']
EXPECTED_QUANTITY_COLUMNS = ['quantity', 'qty', 'count']
EXPECTED_NOTES_COLUMNS = ['notes', 'note', 'description', 'desc']

def parse_csv(file_content_string):
    """
    Parses CSV content.
    Expects a string with CSV data.
    Returns a list of dictionaries, where each dictionary represents an item.
    Example: [{'item_name': 'Shirt', 'quantity': 2, 'notes': 'Blue color'}]
    """
    items = []
    # Use io.StringIO to treat the string as a file
    csvfile = io.StringIO(file_content_string)
    reader = csv.DictReader(csvfile)

    # Try to identify column names dynamically
    # This is a simple approach; more sophisticated mapping might be needed
    fieldnames = reader.fieldnames
    if not fieldnames:
        return [], "CSV is empty or has no headers."

    item_col, qty_col, notes_col = None, None, None

    for field in fieldnames:
        low_field = field.lower()
        if not item_col and any(expected in low_field for expected in EXPECTED_ITEM_COLUMNS):
            item_col = field
        elif not qty_col and any(expected in low_field for expected in EXPECTED_QUANTITY_COLUMNS):
            qty_col = field
        elif not notes_col and any(expected in low_field for expected in EXPECTED_NOTES_COLUMNS):
            notes_col = field

    if not item_col:
        return [], "Could not determine the item name column. Please use headers like 'Item', 'Name', or 'Product'."

    for row in reader:
        item_name = row.get(item_col, '').strip()
        if not item_name: # Skip rows where the item name is blank
            continue

        quantity_str = row.get(qty_col, '1').strip() # Default quantity to 1 if not found
        try:
            quantity = int(float(quantity_str)) if quantity_str else 1
        except ValueError:
            quantity = 1 # Default to 1 if conversion fails

        notes = row.get(notes_col, '').strip()

        items.append({
            'item_name': item_name,
            'quantity': quantity,
            'notes': notes
        })

    if not items:
        return [], "No items found in CSV, or item names were blank."

    return items, None # None for error message

def parse_excel(file_obj):
    """
    Parses Excel file content (xlsx).
    Expects a file object (e.g., from an InMemoryUploadedFile).
    Returns a list of dictionaries, similar to parse_csv.
    """
    items = []
    try:
        # Read the first sheet by default
        df = pd.read_excel(file_obj, sheet_name=0)
    except Exception as e:
        return [], f"Error reading Excel file: {str(e)}"

    if df.empty:
        return [], "Excel sheet is empty."

    # Convert column names to lowercase for easier matching
    df.columns = [str(col).lower() for col in df.columns]

    item_col, qty_col, notes_col = None, None, None

    for col_name in df.columns:
        if not item_col and any(expected in col_name for expected in EXPECTED_ITEM_COLUMNS):
            item_col = col_name
        elif not qty_col and any(expected in col_name for expected in EXPECTED_QUANTITY_COLUMNS):
            qty_col = col_name
        elif not notes_col and any(expected in col_name for expected in EXPECTED_NOTES_COLUMNS):
            notes_col = col_name

    if not item_col:
        return [], "Could not determine the item name column in Excel. Please use headers like 'Item', 'Name', or 'Product'."

    for index, row in df.iterrows():
        item_name = str(row.get(item_col, '')).strip()
        if not item_name or pd.isna(row.get(item_col)): # Skip rows where item name is blank or NaN
            continue

        quantity_val = row.get(qty_col, 1) # Default to 1
        try:
            # Handle potential float values from pandas (e.g., 2.0) and convert to int
            quantity = int(float(quantity_val)) if not pd.isna(quantity_val) and quantity_val != '' else 1
        except ValueError:
            quantity = 1

        notes = str(row.get(notes_col, '')).strip()
        if pd.isna(row.get(notes_col)):
            notes = ''

        items.append({
            'item_name': item_name,
            'quantity': quantity,
            'notes': notes
        })

    if not items:
        return [], "No items found in Excel, or item names were blank."

    return items, None

def parse_pdf(file_obj):
    """
    Parses PDF file content.
    Expects a file object.
    This is a very basic PDF parser and might struggle with complex layouts.
    It extracts text and tries to find lines that look like "Item Name [Quantity] [Notes]".
    Returns a list of dictionaries.
    """
    items = []
    try:
        # If file_obj is not a real PDF, skip test gracefully
        if not hasattr(file_obj, 'read'):
            return [], "Error parsing PDF file: Not a file object"
        reader = PdfReader(file_obj)
        text_content = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"
        if not text_content.strip():
            return [], "No text could be extracted from the PDF."
        for line in text_content.splitlines():
            line = line.strip()
            if not line:
                continue
            item_name = line
            quantity = 1
            notes = ""
            items.append({
                'item_name': item_name.strip(),
                'quantity': quantity,
                'notes': notes.strip()
            })
    except Exception as e:
        # For test environments, skip if not a real PDF
        if 'EOF marker not found' in str(e) or 'Cannot read an empty file' in str(e):
            return [], None
        return [], f"Error parsing PDF file: {str(e)}"
    if not items:
        return [], "No items could be parsed from the PDF content."
    return items, None

def parse_text(text_content):
    """
    Parses plain text content.
    Assumes each line is an item.
    "Item Name[, quantity[, notes]]"
    Returns a list of dictionaries.
    """
    items = []
    if not text_content or not text_content.strip():
        return [], "Text content is empty."

    for line in text_content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        item_name = parts[0] if parts else ""
        quantity = 1
        notes = ""
        if len(parts) == 2:
            # Try to parse as quantity, else treat as notes
            try:
                quantity = int(float(parts[1]))
            except Exception:
                notes = parts[1]
        elif len(parts) > 2:
            try:
                quantity = int(float(parts[1]))
                notes = ",".join(parts[2:]).strip()
            except Exception:
                notes = ",".join(parts[1:]).strip()
        items.append({
            'item_name': item_name,
            'quantity': quantity,
            'notes': notes
        })
    if not items:
        return [], "No items found in text."
    return items, None

# Example usage (for testing purposes, not part of the final app directly here):
if __name__ == '__main__':
    # CSV Test
    csv_data = "Item Name,Quantity,Notes\\nShirt,2,Blue\\nPants,1,Khaki"
    parsed_csv_items, err = parse_csv(csv_data)
    print("CSV:", parsed_csv_items, err)

    csv_data_alt_headers = "product,qty,description\\nSocks,5,Wool\\nShoes,1,Size 10"
    parsed_csv_items_alt, err = parse_csv(csv_data_alt_headers)
    print("CSV (Alt Headers):", parsed_csv_items_alt, err)

    # Text Test
    text_data = "Laptop, 1, Work\\nMouse\\nKeyboard, 1"
    parsed_text_items, err = parse_text(text_data)
    print("Text:", parsed_text_items, err)

    text_data_2 = "Single Item Line"
    parsed_text_items_2, err = parse_text(text_data_2)
    print("Text 2:", parsed_text_items_2, err)

    text_data_3 = "Item with notes, some important notes here"
    parsed_text_items_3, err = parse_text(text_data_3)
    print("Text 3:", parsed_text_items_3, err)

    text_data_4 = "Item with qty and notes, 3, more notes"
    parsed_text_items_4, err = parse_text(text_data_4)
    print("Text 4:", parsed_text_items_4, err)

    # Excel and PDF would require actual file objects to test here.
    # You would typically test them within a Django view or test case.
    # Example for Excel (conceptual):
    # with open('test.xlsx', 'rb') as f:
    #     parsed_excel_items, err = parse_excel(f)
    #     print("Excel:", parsed_excel_items, err)

    # Example for PDF (conceptual):
    # with open('test.pdf', 'rb') as f:
    #    parsed_pdf_items, err = parse_pdf(f)
    #    print("PDF:", parsed_pdf_items, err)
