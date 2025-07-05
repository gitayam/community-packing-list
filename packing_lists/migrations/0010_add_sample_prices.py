from django.db import migrations
from datetime import date

def add_sample_prices(apps, schema_editor):
    Store = apps.get_model('packing_lists', 'Store')
    Item = apps.get_model('packing_lists', 'Item')
    Price = apps.get_model('packing_lists', 'Price')

    # Create some stores
    store1, _ = Store.objects.get_or_create(name="Ranger Supply", defaults={
        'address_line1': '123 Main St', 'city': 'Columbus', 'state': 'GA', 'zip_code': '31905', 'country': 'USA', 'is_in_person': True, 'is_online': False
    })
    store2, _ = Store.objects.get_or_create(name="Tactical Online", defaults={
        'url': 'https://tacticalonline.example.com', 'is_in_person': False, 'is_online': True
    })

    # Add prices for a few items if they exist
    item_names = ["ACH BRACKET", "RUCKSACK LARGE FIELD PACK MOLLE", "SUSTAINMENT POUCH"]
    prices = [
        ("ACH BRACKET", store1, 32.99, 1),
        ("ACH BRACKET", store2, 29.99, 1),
        ("RUCKSACK LARGE FIELD PACK MOLLE", store1, 199.99, 1),
        ("SUSTAINMENT POUCH", store1, 15.50, 1),
        ("SUSTAINMENT POUCH", store2, 13.99, 1),
    ]
    for item_name, store, price_val, qty in prices:
        try:
            item = Item.objects.get(name=item_name)
            Price.objects.get_or_create(
                item=item,
                store=store,
                defaults={
                    'price': price_val,
                    'quantity': qty,
                    'date_purchased': date.today(),
                }
            )
        except Item.DoesNotExist:
            continue

class Migration(migrations.Migration):
    dependencies = [
        ('packing_lists', '0009_create_ranger_school_packing_list'),
    ]
    operations = [
        migrations.RunPython(add_sample_prices),
    ] 