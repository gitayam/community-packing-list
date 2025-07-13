from django.core.management.base import BaseCommand
from packing_lists.models import Store


class Command(BaseCommand):
    help = 'Create default stores (Amazon, Walmart, Sam\'s Club)'

    def handle(self, *args, **options):
        default_stores = [
            {
                'name': 'Amazon',
                'url': 'https://amazon.com',
                'is_online': True,
                'is_in_person': False,
            },
            {
                'name': 'Walmart',
                'url': 'https://walmart.com',
                'is_online': True,
                'is_in_person': True,
            },
            {
                'name': 'Sam\'s Club',
                'url': 'https://samsclub.com', 
                'is_online': True,
                'is_in_person': True,
            },
        ]
        
        created_count = 0
        for store_data in default_stores:
            store, created = Store.objects.get_or_create(
                name=store_data['name'],
                defaults=store_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created store: {store.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Store already exists: {store.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(default_stores)} default stores. Created {created_count} new stores.')
        )