# Local Development Setup

Run the Community Packing List application locally using Docker Compose.

## Quick Start

### Option 1: Simple Docker Compose
```bash
# 1. Start development environment
docker-compose --profile dev up -d --build

# 2. Run setup commands
docker-compose exec web-dev python manage.py migrate
docker-compose exec web-dev python manage.py collectstatic --noinput
docker-compose exec web-dev python manage.py createsuperuser --noinput || echo "Admin exists"
```

### Option 2: Direct Command  
```bash
# One-line setup (after first time)
docker-compose --profile dev up -d --build && sleep 10 && docker-compose exec web-dev python manage.py migrate && docker-compose exec web-dev python manage.py collectstatic --noinput
```

## Access Points

- **Web App**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/ (admin/admin123)
- **Database**: localhost:5433 (packinglist_user/supersecretpassword)

## Management Commands

```bash
# View logs
docker-compose logs -f web-dev

# Django shell  
docker-compose exec web-dev python manage.py shell

# Stop services
docker-compose --profile dev down

# Clean rebuild
docker-compose --profile dev down && docker-compose --profile dev up -d --build
```

## Environment Variables

Create `.env` file with these local development settings:

```env
DB_NAME=packinglist_dev
DB_USER=packinglist_user
DB_PASS=supersecretpassword
DB_HOST=db
DB_PORT=5432
DB_PORT_HOST=5433
DEBUG=True
SECRET_KEY=local-dev-key-change-in-production
DJANGO_SETTINGS_MODULE=community_packing_list.settings
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
WEB_PORT=8000
NODE_ENV=development
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

## Modal Testing

After starting locally:
1. Navigate to http://localhost:8000
2. Go to any packing list 
3. Click "Add Price" buttons
4. Check browser console for debug messages:
   - `🟢 JAVASCRIPT LOADED` 
   - `🟢 Add Price link clicked - SUCCESS!`
5. Verify modals open with price forms

## Troubleshooting

- **Port conflicts**: Change WEB_PORT in .env
- **Database issues**: `docker-compose down --volumes` then restart
- **Container issues**: Check logs with `docker-compose logs web-dev`
