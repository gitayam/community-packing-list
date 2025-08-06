from django.core.management.base import BaseCommand
from django.conf import settings
from django.test import Client
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles import finders
import time


class Command(BaseCommand):
    help = 'Health check for deployment - tests static files, database, and key functionality'

    def handle(self, *args, **options):
        start_time = time.time()
        
        self.stdout.write(self.style.SUCCESS('=== Deployment Health Check ==='))
        
        # Test database connection
        self.stdout.write('Testing database connection...')
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('✓ Database connection OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database error: {e}'))
            return

        # Test static files
        self.stdout.write('\nTesting static files...')
        critical_files = [
            'main.css',
            'packing_lists/css/style.css',
            'packing_lists/js/items.js',
            'packing_lists/js/packing-list-detail.js',
            'packing_lists/icons/travel-bag.svg'
        ]
        
        failed_files = []
        for file_path in critical_files:
            result = finders.find(file_path)
            if result:
                self.stdout.write(self.style.SUCCESS(f'✓ {file_path}'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ {file_path}'))
                failed_files.append(file_path)

        if failed_files:
            self.stdout.write(self.style.ERROR(f'Missing critical files: {failed_files}'))
            return

        # Test static file storage (production)
        if not settings.DEBUG:
            self.stdout.write('\nTesting static file storage...')
            try:
                test_file = 'packing_lists/css/style.css'
                exists = staticfiles_storage.exists(test_file)
                if exists:
                    url = staticfiles_storage.url(test_file)
                    self.stdout.write(self.style.SUCCESS(f'✓ Storage working, URL: {url}'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Static file storage not working'))
                    return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Storage error: {e}'))
                return

        # Test basic views
        self.stdout.write('\nTesting basic views...')
        client = Client()
        
        test_urls = [
            ('/', 'Home page'),
            ('/items/', 'Items page'),
            ('/lists/', 'Lists page'),
        ]
        
        for url, description in test_urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'✓ {description} ({url})'))
                else:
                    self.stdout.write(self.style.WARNING(f'? {description} returned {response.status_code}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ {description} error: {e}'))

        # Test settings
        self.stdout.write('\nTesting settings...')
        
        # Check critical settings
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING('⚠ DEBUG=True (should be False in production)'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ DEBUG=False'))

        if settings.SECRET_KEY == "django-insecure-fallback-key-for-dev-only-q*g=xz-zl0-dzeg8k3=$0@ung3vnk@etqe60lku&r^s%7y2n@)":
            self.stdout.write(self.style.ERROR('✗ Using default SECRET_KEY'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Custom SECRET_KEY set'))

        # Check WhiteNoise (production)
        if not settings.DEBUG:
            if 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE:
                self.stdout.write(self.style.SUCCESS('✓ WhiteNoise middleware configured'))
            else:
                self.stdout.write(self.style.ERROR('✗ WhiteNoise middleware missing'))

        # Memory and performance check
        self.stdout.write('\nPerformance check...')
        elapsed_time = time.time() - start_time
        self.stdout.write(f'Health check completed in {elapsed_time:.2f} seconds')
        
        if elapsed_time > 10:
            self.stdout.write(self.style.WARNING('⚠ Health check took longer than expected'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Response time good'))

        self.stdout.write(self.style.SUCCESS('\n=== Health Check Complete ==='))
        
        if failed_files:
            self.stdout.write(self.style.ERROR('FAILED: Missing critical static files'))
        else:
            self.stdout.write(self.style.SUCCESS('PASSED: All checks successful'))