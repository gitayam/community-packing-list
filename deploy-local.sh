#!/bin/bash
# Local Development Deployment Script

echo "🚀 Setting up Community Packing List locally..."

# Check Docker
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker not running. Please start Docker first."
    exit 1
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file..."
    cat > .env << EOL
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

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose --profile dev down --remove-orphans

# Start development environment
echo "🏗️ Building and starting development environment..."
docker-compose --profile dev up -d --build

# Wait for containers
echo "⏳ Waiting for containers to start..."
sleep 15

# Run setup commands
echo "🗄️ Running database migrations..."
docker-compose exec web-dev python manage.py migrate

echo "📦 Collecting static files..."
docker-compose exec web-dev python manage.py collectstatic --noinput

echo "👤 Creating admin user..."
docker-compose exec web-dev python manage.py createsuperuser --noinput || echo "Admin user already exists"

echo ""
echo "🎉 Local deployment complete!"
echo ""
echo "📋 Access Information:"
echo "   🌐 Application: http://localhost:8000"
echo "   👤 Admin Panel: http://localhost:8000/admin/"
echo "   🔐 Admin Login: admin / admin123"
echo ""
echo "🔧 Useful Commands:"
echo "   📊 Logs: docker-compose logs -f web-dev"
echo "   🛑 Stop: docker-compose --profile dev down" 
echo "   🔄 Restart: docker-compose --profile dev restart"
echo ""
echo "✅ Ready for modal testing at http://localhost:8000"
