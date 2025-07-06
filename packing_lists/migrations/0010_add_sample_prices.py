from django.db import migrations
from datetime import date

def add_sample_prices(apps, schema_editor):
    Store = apps.get_model('packing_lists', 'Store')
    Item = apps.get_model('packing_lists', 'Item')
    Price = apps.get_model('packing_lists', 'Price')
    PackingList = apps.get_model('packing_lists', 'PackingList')

    # Only add prices if we have the demo packing list
    demo_list = PackingList.objects.filter(name="Ranger School Packing List V10").first()
    if not demo_list:
        return

    # Create some stores
    store1, _ = Store.objects.get_or_create(name="Ranger Supply", defaults={
        'address_line1': '123 Main St', 'city': 'Columbus', 'state': 'GA', 'zip_code': '31905', 'country': 'USA', 'is_in_person': True, 'is_online': False
    })
    store2, _ = Store.objects.get_or_create(name="Tactical Online", defaults={
        'url': 'https://tacticalonline.example.com', 'is_in_person': False, 'is_online': True
    })
    store3, _ = Store.objects.get_or_create(name="Military Surplus Store", defaults={
        'address_line1': '456 Army Ave', 'city': 'Fort Benning', 'state': 'GA', 'zip_code': '31905', 'country': 'USA', 'is_in_person': True, 'is_online': True, 'url': 'https://milsurplus.example.com'
    })

    # Add prices for items from the demo packing list
    prices = [
        ("ACH BRACKET", store1, 32.99, 1),
        ("ACH BRACKET", store2, 29.99, 1),
        ("RUCKSACK LARGE FIELD PACK MOLLE", store1, 199.99, 1),
        ("RUCKSACK LARGE FIELD PACK MOLLE", store2, 189.99, 1),
        ("RUCKSACK LARGE FIELD PACK MOLLE", store3, 175.00, 1),
        ("SUSTAINMENT POUCH", store1, 15.50, 1),
        ("SUSTAINMENT POUCH", store2, 13.99, 1),
        ("SUSTAINMENT POUCH", store3, 12.95, 1),
        ("PACK FRAME MOLLE", store1, 89.99, 1),
        ("PACK FRAME MOLLE", store2, 85.50, 1),
        ("HELMET, ADVANCED COMBAT", store1, 299.99, 1),
        ("HELMET, ADVANCED COMBAT", store2, 275.00, 1),
        ("MOLLE TACTICAL ASSAULT PANEL (TAP)", store1, 45.99, 1),
        ("MOLLE TACTICAL ASSAULT PANEL (TAP)", store3, 39.95, 1),
        ("POUCH, 1 QT CANTEEN-GENERAL", store1, 8.99, 1),
        ("POUCH, 1 QT CANTEEN-GENERAL", store2, 7.50, 1),
        ("POUCH, HAND GRENADE", store1, 12.99, 1),
        ("POUCH, M4 TWO MAGAZINE", store1, 18.99, 1),
        ("POUCH, M4 THREE MAG", store1, 22.99, 1),
        ("CANTEEN 1QT", store1, 6.99, 1),
        ("CANTEEN 1QT", store2, 5.95, 1),
        ("CANTEEN WATER 2QT", store1, 12.99, 1),
        ("PONCHO WET WEATHER or TARPAULIN", store1, 24.99, 1),
        ("PONCHO WET WEATHER or TARPAULIN", store3, 19.95, 1),
        ("SLEEPING BAG ICW (Winter-Gray)", store1, 149.99, 1),
        ("SLEEPING BAG ICW (Winter-Gray)", store2, 135.00, 1),
        ("SLEEPING BAG-(Patrol-Green)", store1, 129.99, 1),
        ("Compass, LENSATIC", store1, 45.99, 1),
        ("Compass, LENSATIC", store2, 42.50, 1),
        ("Compass, LENSATIC", store3, 38.95, 1),
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