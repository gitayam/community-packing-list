from django.core.management.base import BaseCommand
from django.db import transaction
from packing_lists.models import Item, Store, Price, Vote


class Command(BaseCommand):
    help = 'Creates sample prices with votes to test smart sorting'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Get or create some stores
            stores = []
            store_names = ['Walmart', 'Target', 'Amazon', 'Local Army Surplus', 'Military Exchange']
            for name in store_names:
                store, created = Store.objects.get_or_create(
                    name=name,
                    defaults={'address_line1': f'{name} Store Address'}
                )
                stores.append(store)
                if created:
                    self.stdout.write(f"Created store: {store.name}")

            # Get some items to add prices to
            items = Item.objects.all()[:5]  # Get first 5 items
            
            if not items:
                self.stdout.write(self.style.WARNING("No items found. Please run create_example_data first."))
                return

            # Create sample prices with different scenarios
            sample_prices = [
                # (item_name, store_name, price, quantity, upvotes, downvotes)
                ('Combat Boots', 'Walmart', 45.99, 1, 5, 1),  # Good price, high confidence
                ('Combat Boots', 'Amazon', 39.99, 1, 8, 0),   # Best price, high confidence
                ('Combat Boots', 'Target', 52.99, 1, 2, 3),   # Higher price, low confidence
                ('Combat Boots', 'Local Army Surplus', 35.99, 1, 3, 2),  # Good price, mixed confidence
                
                ('ACU Uniform Set', 'Military Exchange', 89.99, 1, 10, 0),  # Best price, highest confidence
                ('ACU Uniform Set', 'Amazon', 95.99, 1, 6, 1),  # Good price, high confidence
                ('ACU Uniform Set', 'Walmart', 79.99, 1, 2, 4),  # Lower price, low confidence
                
                ('Rucksack', 'Local Army Surplus', 125.99, 1, 7, 1),  # Good price, high confidence
                ('Rucksack', 'Amazon', 115.99, 1, 4, 2),  # Best price, mixed confidence
                ('Rucksack', 'Target', 145.99, 1, 1, 3),  # Higher price, low confidence
                
                ('MREs', 'Military Exchange', 12.99, 10, 15, 0),  # Best price, highest confidence
                ('MREs', 'Amazon', 14.99, 10, 8, 1),  # Good price, high confidence
                ('MREs', 'Walmart', 11.99, 10, 3, 5),  # Lower price, low confidence
                
                ('Compass', 'Local Army Surplus', 25.99, 1, 9, 0),  # Good price, high confidence
                ('Compass', 'Amazon', 22.99, 1, 5, 2),  # Best price, mixed confidence
                ('Compass', 'Target', 29.99, 1, 2, 1),  # Higher price, low confidence
            ]

            created_count = 0
            for item_name, store_name, price, quantity, upvotes, downvotes in sample_prices:
                try:
                    item = Item.objects.get(name=item_name)
                    store = Store.objects.get(name=store_name)
                    
                    # Create price
                    price_obj, price_created = Price.objects.get_or_create(
                        item=item,
                        store=store,
                        defaults={
                            'price': price,
                            'quantity': quantity
                        }
                    )
                    
                    if price_created:
                        self.stdout.write(f"Created price: {item.name} at {store.name} for ${price}")
                        created_count += 1
                    
                    # Add votes
                    existing_votes = price_obj.votes.count()
                    if existing_votes == 0:  # Only add votes if none exist
                        for _ in range(upvotes):
                            Vote.objects.create(
                                price=price_obj,
                                is_correct_price=True,
                                ip_address='127.0.0.1'
                            )
                        for _ in range(downvotes):
                            Vote.objects.create(
                                price=price_obj,
                                is_correct_price=False,
                                ip_address='127.0.0.1'
                            )
                        self.stdout.write(f"Added {upvotes} upvotes and {downvotes} downvotes for {item.name} at {store.name}")
                    
                except Item.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Item '{item_name}' not found"))
                except Store.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Store '{store_name}' not found"))

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} sample prices with votes!\n'
                    f'Now you can test the smart sorting algorithm that considers:\n'
                    f'- Price per unit (70% weight)\n'
                    f'- Vote confidence (30% weight)\n'
                    f'- Best value options are highlighted with 🏆'
                )
            ) 