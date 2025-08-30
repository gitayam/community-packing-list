#!/bin/bash

# Local Development Deployment Script for Community Packing List
# This script sets up and runs the application locally using Docker Compose

set -e  # Exit on any error

echo "🚀 Starting Local Development Deployment for Community Packing List"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
        print_warning "Please review and update .env file with your local settings"
    else
        print_error ".env.example file not found. Cannot create .env file."
        exit 1
    fi
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose --profile dev down --remove-orphans

# Build and start the development environment
print_status "Building and starting development environment..."
docker-compose --profile dev up -d --build

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Check if web-dev container is running
if ! docker-compose ps web-dev | grep -q "Up"; then
    print_error "web-dev container failed to start. Checking logs..."
    docker-compose logs web-dev
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose exec web-dev python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose exec web-dev python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
print_status "Creating superuser (if not exists)..."
docker-compose exec web-dev python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
" || print_warning "Could not create superuser (may already exist)"

echo ""
print_success "🎉 Local deployment completed successfully!"
echo ""
echo "📋 Application Details:"
echo "   🌐 Web Application: http://localhost:8000"
echo "   🗄️  Database: PostgreSQL on localhost:5433"
echo "   👤 Admin User: admin / admin123"
echo "   🔧 Admin Panel: http://localhost:8000/admin/"
echo ""
echo "🛠️  Development Commands:"
echo "   📊 View logs:        docker-compose logs -f web-dev"
echo "   🛑 Stop services:    docker-compose --profile dev down"
echo "   🔄 Restart:          docker-compose --profile dev restart"
echo "   🧹 Clean rebuild:    docker-compose --profile dev down && docker-compose --profile dev up -d --build"
echo "   🐛 Shell access:     docker-compose exec web-dev python manage.py shell"
echo "   💾 Database shell:   docker-compose exec db psql -U packinglist_user -d packinglist_dev"
echo ""
echo "✅ Your local development environment is ready!"
echo "   Navigate to http://localhost:8000 to access the application"