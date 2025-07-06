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
                    'address': 'Fort Benning, GA 31905',
                    'latitude': 32.3676,
                    'longitude': -84.9547
                }
            )
            if created:
                self.stdout.write(f"Created school: {school.name}")

            base, created = Base.objects.get_or_create(
                name="Fort Benning",
                defaults={
                    'address': 'Columbus, GA 31905',
                    'latitude': 32.3676,
                    'longitude': -84.9547
                }
            )
            if created:
                self.stdout.write(f"Created base: {base.name}")

            # Create the demo packing list (V10) first
            demo_list, created = PackingList.objects.get_or_create(
                name="Ranger School Packing List V10",
                defaults={
                    'description': 'Official Ranger School Packing List V10 as of Dec 2024 (DEMO)',
                    'school': school,
                    'base': base,
                    'event_type': 'school',
                }
            )
            if created:
                self.stdout.write(f"Created demo packing list: {demo_list.name}")
            
            # Create the regular example packing list
            packing_list, created = PackingList.objects.get_or_create(
                name="Ranger School Packing List",
                defaults={
                    'description': 'Comprehensive packing list for Ranger School candidates. This list includes all required items organized by category.',
                    'school': school,
                    'base': base,
                    'event_type': 'school',
                }
            )
            if created:
                self.stdout.write(f"Created packing list: {packing_list.name}")

            # Define V10 demo items (official Ranger School list)
            v10_items_data = [
                # (name, quantity, notes, nsn_lin)
                ("RUCKSACK LARGE FIELD PACK MOLLE", 1, "LIN: DA650J", "DA650J"),
                ("PACK FRAME MOLLE", 1, "LIN: DA650F", "DA650F"),
                ("SUSTAINMENT POUCH", 2, "LIN: DA650Y", "DA650Y"),
                ("MOLDED WAIST BELT", 1, "LIN: DA657T", "DA657T"),
                ("ENHANCED FRAME SHOULDER STRAPS MOLLE", 1, "LIN: DA652Z", "DA652Z"),
                ("BUCKLE MALE SHOULDER SUSPENSION", 1, "For Molle or CIF will issue Large Rucksack on Day 3 to all personnel needing one", None),
                ("LOAD LIFTER ATTACHMENT STRAP", 2, "LIN: DA657W", "DA657W"),
                ("HELMET, ADVANCED COMBAT", 1, "LIN: H53175", "H53175"),
                ("PAD SET, SUSPENSION", 1, "Must have all 7 Suspension Pads, nothing at all/7 pads during the layout will result in being dismissed", None),
                ("ACH BRACKET", 1, "", None),
                ("CAT-EYES BAND PAGST", 1, "LIN: YN1982", "YN1982"),
                ("COVER HELMET ACH MULTICAM-OR- COVER, HELMET, CAMO PATTERN", 1, "LIN: C2175C/C82472", "C2175C/C82472"),
                ("Eye Protection APEL (Clear Lens only) (w/inserts if required)", 1, "Minimum 1 pr.", None),
                ("MOLLE TACTICAL ASSAULT PANEL (TAP)", 1, "LIN: DA6690", "DA6690"),
                ("POUCH, 1 QT CANTEEN-GENERAL", 2, "LIN: DA5589", "DA5589"),
                ("POUCH, HAND GRENADE", 2, "LIN: DA5593", "DA5593"),
                ("POUCH, M4 TWO MAGAZINE", 2, "LIN: DA5582", "DA5582"),
                ("POUCH, M4 THREE MAG", 2, "LIN: DA5582", "DA5582"),
                ("FLASH BANG GRENADE POUCH", 1, "LIN: DA5693", "DA5693"),
                ("Compass, LENSATIC", 1, "NSN 6605-01-196-6971", "6605-01-196-6971"),
                ("Magazine, M4", 7, "30 round Magazine (ATRIB and CIF do not provide this item)", None),
                ("Adapter, fitting, M4 yellow, not M16 red", 1, "", None),
                ("CANTEEN 1QT", 2, "LIN: C9636", "C9636"),
                ("CANTEEN WATER 2QT", 1, "LIN: C9399", "C9399"),
                ("COVER, CANTEEN 2QT", 1, "LIN: DA6700", "DA6700"),
                ("CARRIER, HYDRATION SYSTEM W/BLADDER, HYDRATION S", 1, "LIN: DA650Z/DA6510", "DA650Z/DA6510"),
                ("GEN III - LEVEL1 LIGHTWEIGHT CW DRAWERS", 2, "LIN: D74128", "D74128"),
                ("GEN III - LEVEL2 MID-WEIGHT CW DRAWERS", 2, "", None),
                ("GEN III - LEVEL1 LW CW UNDERSHIRT", 2, "", None),
                ("GEN III - LEVEL2 MIDWEIGHT CW UNDERSHIRT", 2, "", None),
                ("GAITER NECK", 1, "", None),
                ("MITTEN INSERTS, COLD WEATHER", 2, "", None),
                ("MITTEN SHELLS, COLD WEATHER", 2, "", None),
                ("GLOVES COMBAT", 1, "LIN: DA154H", "DA154H"),
                ("WORK GLOVES, HEAVY DUTY", 1, "LIN: J68065", "J68065"),
                ("GLOVES, MEN'S AND WOMEN'S or GLOVES Flyers or Gloves Intermediate Cold Weather", 1, "LIN: DA153A or S06171", "DA153A/S06171"),
                ("OVERSHOES VINYL", 1, "NSN: N39848", "N39848"),
                ("BOOTS, INTERMEDIATE COLD WEATHER", 1, "", None),
                ("PONCHO WET WEATHER or TARPAULIN", 1, "LIN: P17415", "P17415"),
                ("LINER WET WEATHER PONCHO", 1, "LIN: L70789", "L70789"),
                ("EXTREME WET/COLD WEATHER JACKET LEVEL VI or item #124", 1, "LIN: E42924", "E42924"),
                ("Trousers Wet Weather or ECWCS Level IV Trousers or item #125", 1, "LIN: E43367", "E43367"),
                ("STUFF SACK, LRG", 1, "LIN: DA6597", "DA6597"),
                ("STUFF SACK, SML", 1, "LIN: DA6553U", "DA6553U"),
                ("BIVY COVER, MODULAR SYSTEM", 1, "LIN: DA658R", "DA658R"),
                ("SLEEPING BAG ICW (Winter-Gray)", 1, "LIN: DA658N", "DA658N"),
                ("SLEEPING BAG-(Patrol-Green)", 1, "LIN: DA658Z", "DA658Z"),
                ("CAP, PATROL, ARMY COMBAT UNIFORM", 1, "LIN: C02082", "C02082"),
                ("Coat, ACU OCP (must have minimum of 2 winter uniforms the others can be Coat, IHWCU)", 4, "LIN: C68926", "C68926"),
                ("Trousers, ACU OCP (must have a minimum of 2 winter uniforms the others can be Trousers, IHWCU)", 4, "LIN: T057108", "T057108"),
                ("T-Shirts, S/S; Tan 499; loose fitting", 7, "", None),
                ("Belt, brown non-elastic (trigger style)", 7, "", None),
                ("Socks, cushion sole wool blend (military black, tan or green - non waterproof)", 7, "", None),
                ("Boots, Hot Weather Desert (IAW DA PAM 670-1 with no buckles)", 2, "", None),
                ("PT Uniform: Jacket, Pants, Long Sleeve Shirt, Short Sleeve Shirt, Shorts", 1, "", None),
                ("Socks, white/black (calf or above ankle only)", 2, "", None),
                ("WATCH CAP: BLACK MICRO FLEECE", 1, "LIN: C03291", "C03291"),
                ("Belt, reflective (high vis. yellow)", 1, "", None),
                ("PT Shoes", 1, "", None),
                ("Ear Plugs with Case, Triple Flange minimum", 1, "", None),
                ("Protractor", 1, "GTA 5-2-12", None),
                ("Razor, shaving (non electric)", 1, "", None),
                ("Razor Blades", 12, "", None),
                ("Alcohol Marker, permanent (4 pack multiple colors)", 1, "", None),
                ("Camouflage Stick (or like item)", 3, "NSN 6850-00-161-6204", "6850-00-161-6204"),
            ]

            # Define structured items with sections for the regular list
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

            # Create V10 demo items first
            v10_created_count = 0
            for item_name, quantity, notes, nsn_lin in v10_items_data:
                item, item_created = Item.objects.get_or_create(
                    name=item_name,
                    defaults={'description': f'{item_name} for Ranger School V10'}
                )
                if item_created:
                    self.stdout.write(f"Created V10 item: {item_name}")

                pli, pli_created = PackingListItem.objects.get_or_create(
                    packing_list=demo_list,
                    item=item,
                    defaults={
                        'quantity': quantity,
                        'notes': notes or "",
                        'nsn_lin': nsn_lin or "",
                        'required': True,
                    }
                )
                if pli_created:
                    v10_created_count += 1

            # Create items and add to regular packing list
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
                    f'- Demo Packing List: {demo_list.name} ({v10_created_count} items)\n'
                    f'- Regular Packing List: {packing_list.name} ({created_count} items)'
                )
            ) 