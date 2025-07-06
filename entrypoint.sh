#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to check if database tables exist
check_tables_exist() {
    python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
try:
    cursor.execute(\"SELECT COUNT(*) FROM packing_lists_packinglist\")
    print('Tables exist')
    exit(0)
except:
    print('Tables do not exist')
    exit(1)
"
}

# Wait for the database to be ready
echo "Waiting for postgres..."
while ! pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-packinglist_user} -q -d ${DB_NAME:-packinglist_dev}; do
  sleep 1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

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
if ! check_tables_exist || [ "$(python manage.py shell -c "from packing_lists.models import PackingList; print(PackingList.objects.count())")" = "0" ]; then
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

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

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

# Start server
# The CMD in Dockerfile or command in docker-compose.yml will be executed after this script.
# If you want this script to be the final command, you can start Gunicorn or runserver here.
# For example:
# exec gunicorn community_packing_list.wsgi:application --bind 0.0.0.0:8000 --workers 3

# If CMD is used in Dockerfile/docker-compose.yml to start the server,
# this script just needs to prepare the environment (like migrations).
echo "Entrypoint script finished. Docker CMD will now run."

# The `exec "$@"` line allows Docker to pass the CMD from the Dockerfile or docker-compose.yml
# to this script, and this script will execute it as the main process (PID 1).
# This is useful if you want to run migrations and then start the server using the CMD.
exec "$@"
