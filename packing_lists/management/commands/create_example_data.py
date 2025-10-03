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
                    'address': 'Fort Moore, GA 31905',
                    'latitude': 32.3676,
                    'longitude': -84.9547
                }
            )
            if created:
                self.stdout.write(f"Created school: {school.name}")

            base, created = Base.objects.get_or_create(
                name="Fort Moore",
                defaults={
                    'address': 'Columbus, GA 31905',
                    'latitude': 32.3676,
                    'longitude': -84.9547
                }
            )
            if created:
                self.stdout.write(f"Created base: {base.name}")

            # Create example packing list
            packing_list, created = PackingList.objects.get_or_create(
                name="Ranger School Packing List 2025",
                defaults={
                    'description': 'Official packing list for Ranger School candidates (Updated January 2025). Includes all required items for RAP Week through graduation. Bring only what is authorized.',
                    'school': school,
                    'base': base,
                    'type': 'course',
                }
            )
            if created:
                self.stdout.write(f"Created packing list: {packing_list.name}")

            # Define structured items with sections
            items_data = [
                # Uniforms and Clothing
                ('Uniforms and Clothing', 'Army Combat Boots', 2, 'NSN 8430-01-514-4933', True, 'Black or coyote brown, broken in', 'Must be fully broken in. Bring 2 pairs minimum'),
                ('Uniforms and Clothing', 'OCP Uniform Set', 4, 'NSN 8415-01-645-2768', True, 'Complete with all patches sewn', 'Ranger tab location sewn on left shoulder. Name tape, rank, US Army'),
                ('Uniforms and Clothing', 'APFU (PT Uniform)', 3, 'NSN 8415-01-584-5665', True, 'Army PT uniform with reflective', 'Must be current APFU, not IPFU. Bring shorts and pants'),
                ('Uniforms and Clothing', 'PT Shoes', 2, 'NSN 8430-01-516-9301', True, 'Running shoes', 'Well broken in running shoes'),
                ('Uniforms and Clothing', 'Socks (Boot)', 12, 'NSN 8440-01-504-8208', True, 'Green or tan boot socks', 'Wool blend recommended. Change daily to prevent blisters'),
                ('Uniforms and Clothing', 'Socks (White PT)', 6, 'NSN 8440-01-641-3772', True, 'White athletic socks', 'For PT uniform'),
                ('Uniforms and Clothing', 'Underwear (Brown)', 10, 'NSN 8420-01-518-4933', True, 'Brown or tan underwear', 'No bright colors. Moisture wicking recommended'),
                ('Uniforms and Clothing', 'Undershirts (Tan 499)', 8, 'NSN 8415-01-641-6436', True, 'Tan 499 t-shirts', 'Required under OCP uniform'),
                ('Uniforms and Clothing', 'Belt (Rigger)', 2, 'NSN 8465-01-472-0918', True, 'Tan or coyote brown', 'Standard military rigger belt'),
                ('Uniforms and Clothing', 'Patrol Cap', 2, 'NSN 8415-01-645-0634', True, 'OCP patrol cap', 'With all patches sewn'),
                ('Uniforms and Clothing', 'Boonie Hat', 1, 'NSN 8415-01-655-9661', False, 'OCP boonie hat', 'Optional for field use'),
                ('Uniforms and Clothing', 'Gloves (Cold Weather)', 2, 'NSN 8415-01-626-6802', True, 'Black or OCP gloves', 'For cold weather and mountain phase'),
                ('Uniforms and Clothing', 'Watch', 1, 'NSN 6645-01-493-9878', True, 'Black, analog with indiglo', 'Must be field watch with glow hands. No smart watches'),
                
                # Field Gear and Rucksack
                ('Field Gear', 'Rucksack (Large)', 1, 'NSN 8465-01-524-7226', True, 'MOLLE II Large Rucksack', 'Main rucksack for all field exercises'),
                ('Field Gear', 'Assault Pack', 1, 'NSN 8465-01-600-7825', True, 'MOLLE II Assault Pack', 'Day pack for patrols'),
                ('Field Gear', 'Sleep System (Modular)', 1, 'NSN 8465-01-547-2577', True, 'Complete MSS with patrol bag', 'Green or woodland. Rated to -40°F'),
                ('Field Gear', 'Sleeping Pad', 1, 'NSN 8465-01-524-6274', True, 'Sleeping pad, foam', 'Therm-a-Rest or similar closed cell'),
                ('Field Gear', 'Poncho', 2, 'NSN 8405-01-628-3245', True, 'Wet weather poncho', 'One for shelter, one for wear'),
                ('Field Gear', 'Poncho Liner (Woobie)', 2, 'NSN 8405-01-547-0827', True, 'Poncho liner, nylon quilted', 'Essential for warmth. Bring 2'),
                ('Field Gear', 'Camel Bak', 1, 'NSN 8465-01-525-0585', True, '100oz hydration system', 'Keep hydrated during movements'),
                ('Field Gear', 'Canteen (1-Quart)', 4, 'NSN 8465-01-558-0307', True, 'Plastic canteen', 'With covers and cups'),
                ('Field Gear', 'Canteen Cup', 2, 'NSN 8465-00-177-1471', True, 'Stainless steel cup', 'For heating meals and water'),
                ('Field Gear', 'E-Tool (Entrenching Tool)', 1, 'NSN 5120-00-177-2836', True, 'Folding shovel with case', 'Required for digging fighting positions'),
                
                # Hygiene and Medical
                ('Hygiene and Medical', 'Toothbrush', 2, 'NSN 6515-00-159-4859', True, 'Standard toothbrush', 'Keep one in ruck, one in assault pack'),
                ('Hygiene and Medical', 'Toothpaste', 2, 'NSN 6515-00-753-4505', True, 'Travel size', 'Non-mint less attractive to bugs'),
                ('Hygiene and Medical', 'Soap (Bar)', 3, 'NSN 7930-00-133-9794', True, 'Unscented bar soap', 'For bathing. Unscented to avoid attracting insects'),
                ('Hygiene and Medical', 'Shaving Razor', 6, 'NSN 6515-01-524-5668', True, 'Disposable razors', 'Shave daily. Bring plenty'),
                ('Hygiene and Medical', 'Shaving Cream', 2, 'NSN 8510-00-264-9557', True, 'Travel size shaving cream', 'Can or foam'),
                ('Hygiene and Medical', 'Nail Clippers', 1, 'NSN 6515-00-935-7138', True, 'Finger and toe nails', 'Keep nails trimmed to prevent infection'),
                ('Hygiene and Medical', 'Foot Powder', 2, 'NSN 6505-01-314-0613', True, 'Gold Bond or similar', 'Essential for foot care. Prevents blisters'),
                ('Hygiene and Medical', 'Body Powder', 1, 'NSN 8510-00-141-5565', False, 'Anti-chafe powder', 'For hot weather and Florida phase'),
                ('Hygiene and Medical', 'Lip Balm with SPF', 3, 'NSN 6505-01-496-5000', True, 'Sun protection', 'Prevents chapped lips and sunburn'),
                ('Hygiene and Medical', 'Sunscreen (50+ SPF)', 2, 'NSN 6505-01-530-6697', True, 'Water resistant', 'Apply daily to prevent burns'),
                ('Hygiene and Medical', 'Insect Repellent', 2, 'NSN 6840-01-284-3982', True, 'DEET 30%+', 'Spray or lotion. Essential in Florida'),
                ('Hygiene and Medical', 'Individual First Aid Kit (IFAK)', 1, 'NSN 6545-01-519-7976', True, 'Personal medical kit', 'Bandages, gauze, tape, mole skin'),
                ('Hygiene and Medical', 'Ibuprofen', 1, 'NSN 6505-01-418-8672', False, '200mg tablets', 'OTC pain relief. Personal supply'),
                ('Hygiene and Medical', 'Multivitamin', 1, 'NSN 6505-01-491-4429', False, 'Daily vitamin', 'Helps maintain health during course'),
                ('Hygiene and Medical', 'Baby Wipes', 4, 'NSN 8540-01-620-3925', True, 'Unscented wipes', 'For hygiene when no shower available'),
                ('Hygiene and Medical', 'Laundry Detergent', 1, 'NSN 7930-01-598-5054', False, 'Travel size pods', 'For washing uniform during breaks'),
                
                # Navigation and Communication
                ('Navigation and Communication', 'Lensatic Compass', 1, 'NSN 6605-01-196-6971', True, 'Military lensatic compass', 'Must know how to use. Practice before arrival'),
                ('Navigation and Communication', 'Protractor', 1, 'NSN 6675-01-457-7373', True, 'GTA 5-2-12 protractor', 'For plotting coordinates and bearings'),
                ('Navigation and Communication', 'Waterproof Map Case', 1, 'NSN 8465-01-580-1316', True, 'Clear waterproof case', 'Protect maps and overlays'),
                ('Navigation and Communication', 'Mechanical Pencils', 4, 'NSN 7510-01-524-1754', True, '0.7mm or 0.9mm lead', 'For map marking. Bring extra lead'),
                ('Navigation and Communication', 'Pencil Sharpener', 1, 'NSN 7510-00-543-4141', True, 'Small sharpener', 'For regular pencils'),
                ('Navigation and Communication', 'Waterproof Notebook', 2, 'NSN 7530-01-600-1687', True, 'Rite in Rain or similar', 'For OPORD, notes, and planning'),
                ('Navigation and Communication', 'Black/Red Pens', 4, 'NSN 7520-01-512-1228', True, 'Fine point pens', 'For writing orders and notes'),
                ('Navigation and Communication', 'Pace Count Beads', 1, 'NSN 6675-01-509-3265', True, 'Ranger beads', 'For land navigation. Know your pace count'),
                ('Navigation and Communication', 'Red Lens Flashlight', 1, 'NSN 6230-01-536-2629', True, 'Red lens or filter', 'For reading maps at night'),

                # Food and Water
                ('Food and Water', 'Water Purification Tablets', 2, 'NSN 6850-01-349-5462', True, 'Iodine or chlorine tablets', 'For field water purification'),
                ('Food and Water', 'Electrolyte Mix', 3, 'NSN 6505-01-519-2358', False, 'Hydration packets', 'Helps maintain electrolytes during training'),
                ('Food and Water', 'Protein Bars', 10, 'NSN 8970-01-533-8969', False, 'High protein bars', 'Supplemental calories. Don\'t rely on these'),
                ('Food and Water', 'MRE Spoon', 2, 'NSN 8970-01-413-3003', True, 'Long handle spoon', 'For eating MREs and hot meals'),
                ('Food and Water', 'P-38 Can Opener', 3, 'NSN 7340-00-162-0316', True, 'Small can opener', 'Backup can opener. Attach to dog tags'),

                # Tools and Equipment
                ('Tools and Equipment', 'Multi-Tool / Gerber', 1, 'NSN 5110-01-457-4457', True, 'Leatherman or Gerber', 'Essential for gear maintenance and repairs'),
                ('Tools and Equipment', '100-mph Tape (Duct Tape)', 1, 'NSN 7510-01-363-6594', True, 'OD Green duct tape', 'For all repairs. Wrap around canteen'),
                ('Tools and Equipment', '550 Cord (Paracord)', 1, 'NSN 4020-00-159-4404', True, '100 feet minimum', 'Type III 550 cord. Many uses'),
                ('Tools and Equipment', 'Headlamp', 1, 'NSN 6230-01-563-7914', True, 'LED headlamp with red light', 'Hands-free light. Red light for tactical'),
                ('Tools and Equipment', 'Extra Batteries (AA)', 12, 'NSN 6135-01-559-6373', True, 'Lithium batteries preferred', 'For headlamp, GPS, etc. Lithium lasts longer'),
                ('Tools and Equipment', 'Ziplock Bags', 20, 'NSN 8105-01-588-8154', True, 'Quart and gallon sizes', 'Keep gear dry. Various sizes'),
                ('Tools and Equipment', 'Carabiners', 4, 'NSN 8465-01-517-2147', True, 'Non-climbing carabiners', 'For attaching gear to ruck'),
                ('Tools and Equipment', 'Sewing Kit', 1, 'NSN 8315-01-450-0682', True, 'Needle, thread, buttons', 'For uniform repairs'),
                ('Tools and Equipment', 'Safety Pins', 10, 'NSN 8315-00-205-6789', True, 'Assorted sizes', 'For quick uniform fixes'),
                ('Tools and Equipment', 'Dummy Cord', 1, 'NSN 8315-01-458-9827', True, 'Small dummy cord', 'Secure small items to prevent loss'),

                # Administrative and Personal
                ('Administrative', 'Copies of Orders', 3, 'N/A', True, 'Orders in plastic bag', 'Keep multiple copies of PCS/TDY orders dry'),
                ('Administrative', 'ID Card / CAC', 1, 'N/A', True, 'Military ID', 'Carry at all times. Keep secure'),
                ('Administrative', 'Dog Tags', 2, 'NSN 8465-01-562-3610', True, 'Metal dog tags', 'Wear at all times. Bring spare set'),
                ('Administrative', 'Copy of DA 5500', 1, 'N/A', False, 'Body composition form', 'If applicable. Keep with orders'),
                ('Administrative', 'Cash', 1, 'N/A', True, '$200-300 in small bills', 'For phone cards, laundry, necessities'),
                ('Administrative', 'Calling Card / Phone Card', 2, 'N/A', False, 'Prepaid phone cards', 'For calling home during breaks'),

                # Optional Comfort Items
                ('Optional Items', 'Energy Drinks', 6, 'NSN 8970-01-589-4793', False, 'Caffeine drinks', 'For energy during long days. Use wisely'),
                ('Optional Items', 'Instant Coffee', 5, 'NSN 8970-01-457-3892', False, 'Instant coffee packets', 'For early mornings'),
                ('Optional Items', 'Hand Warmers', 20, 'NSN 8415-01-563-7945', False, 'Chemical hand warmers', 'For mountains phase in winter'),
                ('Optional Items', 'Small Bible / Religious Text', 1, 'N/A', False, 'Religious materials', 'If desired for personal faith'),
                ('Optional Items', 'Photos from Home', 1, 'N/A', False, 'Laminated photos', 'Motivation during tough times'),
                ('Optional Items', 'Pre-Stamped Envelopes', 10, 'NSN 7530-01-442-0951', False, 'Addressed envelopes', 'For writing home during breaks'),
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