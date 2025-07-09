#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings')
django.setup()

from packing_lists.models import Item, Store, Price
from packing_lists.forms import PriceForm

def test_price_creation():
    print("Testing price input functionality...")
    
    # Get test data
    item = Item.objects.first()
    store = Store.objects.first()
    
    if not item or not store:
        print("No items or stores found in database")
        return
    
    print(f"Testing with item: {item.name}")
    print(f"Testing with store: {store.name}")
    
    # Test 1: Create price with existing store
    print("\nTest 1: Creating price with existing store")
    form_data = {
        'store': store.id,
        'price': '25.99',
        'quantity': 1
    }
    
    form = PriceForm(form_data)
    print(f"Form valid: {form.is_valid()}")
    
    if form.is_valid():
        try:
            price = form.save(commit=True, item_instance=item)
            print(f"✓ Price created successfully: ${price.price} for {price.quantity} at {price.store.name}")
        except Exception as e:
            print(f"✗ Error creating price: {e}")
    else:
        print(f"✗ Form errors: {form.errors}")
    
    # Test 2: Create price with new store
    print("\nTest 2: Creating price with new store")
    form_data_new_store = {
        'store': '__add_new__',
        'store_name': 'Test New Store',
        'price': '30.50',
        'quantity': 2
    }
    
    form_new_store = PriceForm(form_data_new_store)
    print(f"Form valid: {form_new_store.is_valid()}")
    
    if form_new_store.is_valid():
        try:
            price = form_new_store.save(commit=True, item_instance=item)
            print(f"✓ Price with new store created successfully: ${price.price} for {price.quantity} at {price.store.name}")
        except Exception as e:
            print(f"✗ Error creating price with new store: {e}")
    else:
        print(f"✗ Form errors: {form_new_store.errors}")
    
    # Test 3: Check total prices
    print(f"\nTest 3: Total prices in database: {Price.objects.count()}")
    print(f"Total items: {Item.objects.count()}")
    print(f"Total stores: {Store.objects.count()}")

if __name__ == "__main__":
    test_price_creation() 