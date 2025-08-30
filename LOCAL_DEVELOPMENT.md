# Local Development Setup

This guide explains how to run the Community Packing List application locally using Docker Compose.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

### Option 1: Automated Setup Script

```bash
# Run the setup script
./deploy-local.sh
```

This script will:
- Check Docker availability 
- Create `.env` file if needed
- Build and start all services
- Run database migrations
- Collect static files
- Create admin user
- Display access information

### Option 2: Manual Docker Compose

```bash
# 1. Create environment file (one-time setup)
./local-setup.sh

# 2. Start the development environment
docker-compose --profile dev up -d --build

# 3. Run initial setup commands
docker-compose exec web-dev python manage.py migrate
docker-compose exec web-dev python manage.py collectstatic --noinput
docker-compose exec web-dev python manage.py createsuperuser --noinput || echo "Superuser exists"
```

## Access the Application

Once running, you can access:

- **🌐 Web Application**: http://localhost:8000
- **👤 Admin Panel**: http://localhost:8000/admin/
  - Username: `admin`
  - Password: `admin123`
- **🗄️ Database**: PostgreSQL on `localhost:5433`
  - Database: `packinglist_dev`
  - Username: `packinglist_user` 
  - Password: `supersecretpassword`

## Development Commands

### Container Management
```bash
# View running containers
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f web-dev

# Restart services
docker-compose --profile dev restart

# Stop services
docker-compose --profile dev down

# Clean rebuild
docker-compose --profile dev down
docker-compose --profile dev up -d --build
```

### Django Management Commands
```bash
# Django shell
docker-compose exec web-dev python manage.py shell

# Create migrations
docker-compose exec web-dev python manage.py makemigrations

# Run migrations
docker-compose exec web-dev python manage.py migrate

# Collect static files
docker-compose exec web-dev python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web-dev python manage.py createsuperuser
```

### Database Access
```bash
# PostgreSQL shell
docker-compose exec db psql -U packinglist_user -d packinglist_dev

# Database backup
docker-compose exec db pg_dump -U packinglist_user packinglist_dev > backup.sql

# Database restore
docker-compose exec -T db psql -U packinglist_user -d packinglist_dev < backup.sql
```

## Environment Configuration

The local environment uses these default settings in `.env`:

```env
# Database
DB_NAME=packinglist_dev
DB_USER=packinglist_user
DB_PASS=supersecretpassword
DB_HOST=db
DB_PORT=5432

# Django
DEBUG=True
SECRET_KEY=local-dev-secret-key-not-for-production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
WEB_PORT=8000
```

## Troubleshooting

### Container Won't Start
```bash
# Check container status
docker-compose ps

# Check logs for errors
docker-compose logs web-dev
docker-compose logs db

# Restart with clean build
docker-compose --profile dev down --volumes
docker-compose --profile dev up -d --build
```

### Database Issues
```bash
# Reset database (WARNING: loses all data)
docker-compose down --volumes
docker-compose --profile dev up -d

# Recreate migrations
docker-compose exec web-dev find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
docker-compose exec web-dev python manage.py makemigrations
docker-compose exec web-dev python manage.py migrate
```

### Port Already in Use
If port 8000 or 5433 is already in use, modify the `.env` file:

```env
WEB_PORT=8001
DB_PORT_HOST=5434
```

Then restart:
```bash
docker-compose --profile dev down
docker-compose --profile dev up -d
```

## Development Workflow

1. **Make code changes** - Files are mounted as volumes, so changes appear immediately
2. **Database changes** - Run migrations when models change
3. **Static files** - Run `collectstatic` when CSS/JS changes
4. **Dependencies** - Rebuild containers when requirements change

## VS Code Integration

For VS Code development:

1. Install the "Dev Containers" extension
2. Open the project folder
3. Use "Dev Containers: Reopen in Container" for full IDE integration

## Performance

The development setup includes:
- **Hot reloading** for Python code changes
- **Database persistence** across container restarts  
- **Static file mounting** for immediate CSS/JS updates
- **Optimized Docker layers** for faster rebuilds

## Security Notes

⚠️ **Local Development Only**: The default credentials and settings are for local development only. Never use these in production.

- Default admin: `admin` / `admin123`
- Database password: `supersecretpassword` 
- Secret key: Development placeholder only