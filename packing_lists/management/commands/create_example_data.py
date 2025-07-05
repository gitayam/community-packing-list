from django.core.management.base import BaseCommand
from django.db import transaction
from packing_lists.models import School, Base, PackingList, Item, PackingListItem


class Command(BaseCommand):
    help = 'Creates example packing list data for demonstration'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Create example school and base
            school, created = School.objects.get_or_create(
                name="Ranger School",
                defaults={
                    'city': 'Fort Benning',
                    'state': 'GA',
                    'zip_code': '31905',
                    'latitude': 32.3676,
                    'longitude': -84.9547
                }
            )
            if created:
                self.stdout.write(f"Created school: {school.name}")

            base, created = Base.objects.get_or_create(
                name="Fort Benning",
                defaults={
                    'city': 'Columbus',
                    'state': 'GA',
                    'zip_code': '31905',
                    'latitude': 32.3676,
                    'longitude': -84.9547
                }
            )
            if created:
                self.stdout.write(f"Created base: {base.name}")

            # Create example packing list
            packing_list, created = PackingList.objects.get_or_create(
                name="Ranger School Packing List",
                defaults={
                    'description': 'Comprehensive packing list for Ranger School candidates. This list includes all required items organized by category.',
                    'school': school,
                    'base': base,
                    'type': 'course',
                }
            )
            if created:
                self.stdout.write(f"Created packing list: {packing_list.name}")

            # Define structured items with sections
            items_data = [
                # Clothing and Personal Items
                ('Clothing and Personal Items', 'Combat Boots', 1, 'NSN 8430-01-123-4567', True, 'Must be broken in', 'Ensure boots are properly broken in before arrival'),
                ('Clothing and Personal Items', 'ACU Uniform Set', 4, 'NSN 8415-01-234-5678', True, 'Complete set with patches', 'All patches must be properly sewn on'),
                ('Clothing and Personal Items', 'PT Uniform', 3, 'NSN 8415-01-345-6789', True, 'Army PT uniform', 'Must be regulation Army PT uniform'),
                ('Clothing and Personal Items', 'Socks', 12, 'NSN 8415-01-456-7890', True, 'Wool or synthetic blend', 'Bring extra pairs for field training'),
                ('Clothing and Personal Items', 'Underwear', 8, 'NSN 8415-01-567-8901', True, 'Moisture wicking', 'Comfortable for extended wear'),
                ('Clothing and Personal Items', 'Watch', 1, 'NSN 6645-01-678-9012', True, 'Waterproof, analog', 'Must be able to read in low light'),
                
                # Field Gear
                ('Field Gear', 'Rucksack', 1, 'NSN 8465-01-789-0123', True, 'Large ALICE or MOLLE', 'Must be able to carry 50+ lbs'),
                ('Field Gear', 'Sleeping Bag', 1, 'NSN 8465-01-890-1234', True, 'Cold weather rated', 'Rated for 0 degrees Fahrenheit'),
                ('Field Gear', 'Sleeping Pad', 1, 'NSN 8465-01-901-2345', True, 'Closed cell foam', 'Provides insulation from ground'),
                ('Field Gear', 'Poncho', 1, 'NSN 8405-01-012-3456', True, 'Waterproof', 'Can be used as shelter'),
                ('Field Gear', 'Poncho Liner', 1, 'NSN 8405-01-123-4567', True, 'Wool blanket alternative', 'Lightweight and warm'),
                
                # Hygiene and Medical
                ('Hygiene and Medical', 'Toothbrush', 2, 'NSN 6515-01-234-5678', True, 'Travel size', 'Keep one in main pack, one in assault pack'),
                ('Hygiene and Medical', 'Toothpaste', 2, 'NSN 6515-01-345-6789', True, 'Travel size', 'Non-mint flavor recommended'),
                ('Hygiene and Medical', 'Soap', 2, 'NSN 7930-01-456-7890', True, 'Bar soap', 'Unscented preferred'),
                ('Hygiene and Medical', 'Razor', 3, 'NSN 6515-01-567-8901', True, 'Disposable', 'Keep clean shaven'),
                ('Hygiene and Medical', 'First Aid Kit', 1, 'NSN 6545-01-678-9012', True, 'Personal size', 'Include bandages, antiseptic'),
                ('Hygiene and Medical', 'Ibuprofen', 1, 'NSN 6505-01-789-0123', False, '200mg tablets', 'For pain management'),
                
                # Navigation and Communication
                ('Navigation and Communication', 'Compass', 1, 'NSN 6605-01-890-1234', True, 'Lensatic compass', 'Must be able to take bearings'),
                ('Navigation and Communication', 'Map Case', 1, 'NSN 8465-01-901-2345', True, 'Waterproof', 'Protect maps from elements'),
                ('Navigation and Communication', 'Protractor', 1, 'NSN 6675-01-012-3456', True, 'Military protractor', 'For map reading'),
                ('Navigation and Communication', 'Pencil', 3, 'NSN 7520-01-123-4567', True, 'Mechanical pencil', 'For map marking'),
                ('Navigation and Communication', 'Notebook', 1, 'NSN 7530-01-234-5678', True, 'Waterproof paper', 'For notes and planning'),
                
                # Food and Water
                ('Food and Water', 'Canteen', 2, 'NSN 8465-01-345-6789', True, '1-quart capacity', 'Stay hydrated'),
                ('Food and Water', 'Canteen Cup', 1, 'NSN 8465-01-456-7890', True, 'Stainless steel', 'For heating water'),
                ('Food and Water', 'MREs', 10, 'NSN 8970-01-567-8901', True, 'Meals Ready to Eat', 'High calorie meals for energy'),
                ('Food and Water', 'Water Purification Tablets', 1, 'NSN 6850-01-678-9012', True, 'Iodine tablets', 'For water purification'),
                
                # Tools and Equipment
                ('Tools and Equipment', 'Multi-tool', 1, 'NSN 5110-01-789-0123', True, 'Leatherman or similar', 'Versatile tool for repairs'),
                ('Tools and Equipment', 'Duct Tape', 1, 'NSN 7510-01-890-1234', True, 'Roll of tape', 'For gear repairs'),
                ('Tools and Equipment', '550 Cord', 1, 'NSN 4020-01-901-2345', True, '100 feet', 'For shelter building and repairs'),
                ('Tools and Equipment', 'Headlamp', 1, 'NSN 6230-01-012-3456', True, 'LED with red light', 'Hands-free lighting'),
                ('Tools and Equipment', 'Batteries', 4, 'NSN 6135-01-123-4567', True, 'AA batteries', 'For headlamp and other devices'),
                
                # Optional Items
                ('Optional Items', 'Camera', 1, 'NSN 6730-01-234-5678', False, 'Disposable camera', 'Capture memories if allowed'),
                ('Optional Items', 'Book', 1, 'NSN 7520-01-345-6789', False, 'Small paperback', 'For downtime reading'),
                ('Optional Items', 'Energy Bars', 5, 'NSN 8970-01-456-7890', False, 'High protein', 'Quick energy boost'),
                ('Optional Items', 'Hand Warmers', 10, 'NSN 8415-01-567-8901', False, 'Disposable', 'For cold weather training'),
            ]

            # Create items and add to packing list
            created_count = 0
            for section, item_name, quantity, nsn_lin, required, notes, instructions in items_data:
                item, item_created = Item.objects.get_or_create(
                    name=item_name,
                    defaults={'description': f'{item_name} for Ranger School'}
                )
                if item_created:
                    self.stdout.write(f"Created item: {item_name}")

                pli, pli_created = PackingListItem.objects.get_or_create(
                    packing_list=packing_list,
                    item=item,
                    defaults={
                        'section': section,
                        'quantity': quantity,
                        'nsn_lin': nsn_lin,
                        'required': required,
                        'notes': notes,
                        'instructions': instructions,
                    }
                )
                if pli_created:
                    created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created example data:\n'
                    f'- School: {school.name}\n'
                    f'- Base: {base.name}\n'
                    f'- Packing List: {packing_list.name}\n'
                    f'- Items added: {created_count}'
                )
            ) 