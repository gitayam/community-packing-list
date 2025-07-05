#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
echo "Waiting for postgres..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -q -d $DB_NAME; do
  sleep 1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

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
