#!/bin/bash

# Quick Local Setup Script
# Usage: ./local-setup.sh

echo "🚀 Setting up Community Packing List locally..."

# Ensure .env exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file for local development..."
    cat > .env << EOL
# Local Development Environment
DB_NAME=packinglist_dev
DB_USER=packinglist_user
DB_PASS=supersecretpassword
DB_HOST=db
DB_PORT=5432
DB_PORT_HOST=5433
DEBUG=True
SECRET_KEY=local-dev-secret-key-not-for-production
DJANGO_SETTINGS_MODULE=community_packing_list.settings
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
WEB_PORT=8000
NODE_ENV=development
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
EOL
    echo "✅ Created .env file"
fi

echo ""
echo "🐳 Starting with Docker Compose..."
echo "   Run: docker-compose --profile dev up -d --build"
echo ""
echo "🔧 After containers start, run these commands:"
echo "   docker-compose exec web-dev python manage.py migrate"
echo "   docker-compose exec web-dev python manage.py collectstatic --noinput"
echo "   docker-compose exec web-dev python manage.py createsuperuser --noinput || echo 'Superuser already exists'"
echo ""
echo "🌐 Then access: http://localhost:8000"
echo "👤 Admin: admin / admin123"