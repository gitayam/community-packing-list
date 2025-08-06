from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Setup database for production deployment'

    def handle(self, *args, **options):
        self.stdout.write('Setting up database...')
        
        # Run migrations
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=2)
        
        # Collect static files
        self.stdout.write('Collecting static files...')
        call_command('collectstatic', '--noinput', verbosity=2)
        
        self.stdout.write(
            self.style.SUCCESS('Database setup completed successfully!')
        )