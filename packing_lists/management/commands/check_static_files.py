from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
import os


class Command(BaseCommand):
    help = 'Check static files configuration and locate files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Check specific file path'
        )
        parser.add_argument(
            '--list-all',
            action='store_true',
            help='List all found static files'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Static Files Configuration ==='))
        
        # Show configuration
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"STATIC_URL: {settings.STATIC_URL}")
        self.stdout.write(f"STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Not set')}")
        self.stdout.write(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        
        if hasattr(settings, 'STATICFILES_STORAGE'):
            self.stdout.write(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
        
        self.stdout.write('\n=== Directory Check ===')
        for static_dir in settings.STATICFILES_DIRS:
            if os.path.exists(static_dir):
                self.stdout.write(self.style.SUCCESS(f"✓ {static_dir} exists"))
                # List contents
                try:
                    for root, dirs, files in os.walk(static_dir):
                        for file in files[:5]:  # Show first 5 files
                            rel_path = os.path.relpath(os.path.join(root, file), static_dir)
                            self.stdout.write(f"  - {rel_path}")
                        if len(files) > 5:
                            self.stdout.write(f"  ... and {len(files) - 5} more files")
                        break  # Only show first level
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Error reading directory: {e}"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ {static_dir} does not exist"))

        # Check specific file
        if options['file']:
            self.stdout.write(f'\n=== Checking file: {options["file"]} ===')
            result = finders.find(options['file'])
            if result:
                self.stdout.write(self.style.SUCCESS(f"Found: {result}"))
                # Check if file exists
                if os.path.exists(result):
                    size = os.path.getsize(result)
                    self.stdout.write(f"File size: {size} bytes")
                else:
                    self.stdout.write(self.style.ERROR("File path found but file doesn't exist"))
            else:
                self.stdout.write(self.style.ERROR("File not found by Django static files system"))

        # Check key CSS and JS files
        self.stdout.write('\n=== Key Files Check ===')
        key_files = [
            'packing_lists/css/compiled.css',
            'packing_lists/css/style.css', 
            'packing_lists/js/items.js',
            'packing_lists/js/packing-list-detail.js',
            'packing_lists/icons/travel-bag.svg'
        ]
        
        for file_path in key_files:
            result = finders.find(file_path)
            if result:
                size = os.path.getsize(result) if os.path.exists(result) else 0
                self.stdout.write(self.style.SUCCESS(f"✓ {file_path} ({size} bytes)"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ {file_path}"))

        # Storage check
        if not settings.DEBUG and hasattr(staticfiles_storage, 'exists'):
            self.stdout.write('\n=== Storage Check ===')
            try:
                # Check if storage is working
                test_files = ['packing_lists/css/style.css']
                for test_file in test_files:
                    exists = staticfiles_storage.exists(test_file)
                    url = staticfiles_storage.url(test_file) if exists else 'N/A'
                    self.stdout.write(f"{test_file}: {'✓' if exists else '✗'} (URL: {url})")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Storage check failed: {e}"))

        if options['list_all']:
            self.stdout.write('\n=== All Static Files ===')
            all_files = []
            for finder in finders.get_finders():
                for path, storage in finder.list([]):
                    all_files.append(path)
            
            for file_path in sorted(all_files)[:50]:  # Show first 50
                self.stdout.write(f"  {file_path}")
            
            if len(all_files) > 50:
                self.stdout.write(f"  ... and {len(all_files) - 50} more files")
            
            self.stdout.write(f"\nTotal files found: {len(all_files)}")

        self.stdout.write(self.style.SUCCESS('\nStatic files check complete!'))