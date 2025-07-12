#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Enable debug mode if needed
if [ "$DEBUG_ENTRYPOINT" = "true" ]; then
    set -x
fi

# Determine which settings module to use
if [ "$GOOGLE_CLOUD_PROJECT" ]; then
    export DJANGO_SETTINGS_MODULE="community_packing_list.settings_gcp"
    echo "Using Google Cloud settings"
else
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-community_packing_list.settings}"
    echo "Using local/default settings"
fi

# Function to check if database is accessible
check_database() {
    python -c "
import django
import os
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('Database connection successful')
    exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"
}

# Function to check if tables exist
check_tables_exist() {
    python -c "
import django
import os
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute(\"SELECT COUNT(*) FROM packing_lists_packinglist\")
    print('Tables exist')
    exit(0)
except Exception as e:
    print('Tables do not exist or error occurred')
    exit(1)
"
}

# Wait for database to be ready (with timeout)
echo "Waiting for database to be ready..."
TIMEOUT=60
COUNTER=0

while [ $COUNTER -lt $TIMEOUT ]; do
    if check_database; then
        echo "Database is ready!"
        break
    fi
    echo "Database not ready, waiting... ($COUNTER/$TIMEOUT)"
    sleep 2
    COUNTER=$((COUNTER + 2))
done

if [ $COUNTER -ge $TIMEOUT ]; then
    echo "Database connection timeout after ${TIMEOUT} seconds"
    exit 1
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Only set up demo data in development/non-production environments
if [ "$ENVIRONMENT" != "production" ] && [ "$SKIP_DEMO_DATA" != "true" ]; then
    echo "Setting up demo data (non-production environment)..."
    
    # Clean up any existing demo data and recreate properly
    echo "Cleaning up and recreating demo data..."
    python manage.py shell -c "
from packing_lists.models import PackingList, PackingListItem
# Remove any existing demo lists
PackingList.objects.filter(name__in=['Ranger School Packing List V10', 'Ranger School Packing List']).delete()
print('Cleaned up existing demo lists')
"

    # Check if we need to create example data
    echo "Checking if example data exists..."
    DATA_COUNT=$(python manage.py shell -c "from packing_lists.models import PackingList; print(PackingList.objects.count())" 2>/dev/null || echo "0")
    if [ "$DATA_COUNT" = "0" ]; then
        echo "Creating example data..."
        python manage.py create_example_data
    else
        echo "Example data already exists, skipping creation."
    fi

    # Ensure demo packing list has the correct description
    echo "Updating demo packing list description..."
    python manage.py shell -c "
from packing_lists.models import PackingList
demo_list = PackingList.objects.filter(name='Ranger School Packing List V10').first()
if demo_list and '(DEMO)' not in demo_list.description:
    demo_list.description = 'Official Ranger School Packing List V10 as of Dec 2024 (DEMO)'
    demo_list.save()
    print('Updated demo list description')
else:
    print('Demo list already has correct description or does not exist')
"
else
    echo "Skipping demo data setup (production environment or explicitly disabled)"
fi

# Collect static files (only if not using Cloud Storage)
if [ "$USE_GCS" != "true" ] && [ "$GS_BUCKET_NAME" = "" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear
else
    echo "Using Cloud Storage for static files, skipping local collection"
fi

# Create superuser if it doesn't exist (for development)
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Creating superuser if it doesn't exist..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
fi

# Health check before starting server
echo "Performing pre-startup health check..."
python -c "
import django
django.setup()
from django.db import connection
from django.core.management import execute_from_command_line
try:
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✓ Database connection healthy')
    
    # Test Django setup
    execute_from_command_line(['manage.py', 'check', '--deploy'])
    print('✓ Django deployment check passed')
    
except Exception as e:
    print(f'✗ Health check failed: {e}')
    exit(1)
"

echo "Entrypoint script completed successfully. Starting application..."

# Execute the CMD instruction from Dockerfile
exec "$@"
