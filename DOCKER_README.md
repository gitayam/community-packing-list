# Docker Deployment Guide

## Quick Start

```bash
# 1. Copy environment files
cp .env.example .env.local

# 2. Start development environment
make dev

# 3. In another terminal, run migrations
make migrate

# 4. Create superuser
make createsuperuser
```

## Port Configuration

All ports have been configured to avoid conflicts with OmniCore services:

| Service | External Port | Internal Port | URL |
|---------|--------------|---------------|-----|
| **Django Web App** | 8001 | 8000 | http://localhost:8001 |
| **Django Admin** | 8001 | 8000 | http://localhost:8001/admin |
| **PostgreSQL** | 5434 | 5432 | postgresql://localhost:5434 |
| **Redis** | 6380 | 6379 | redis://localhost:6380 |
| **Mailhog SMTP** | 1026 | 1025 | smtp://localhost:1026 |
| **Mailhog Web UI** | 8026 | 8025 | http://localhost:8026 |
| **Frontend Dev** | 3001 | 3000 | http://localhost:3001 |

## Available Commands

### Development

```bash
make dev          # Start development environment
make dev-build    # Build and start development environment
make dev-down     # Stop development environment
make dev-logs     # Show development logs
make dev-shell    # Open Django shell
make dev-bash     # Open bash shell in container
```

### Database

```bash
make migrate          # Run Django migrations
make makemigrations   # Create new migrations
make createsuperuser  # Create admin user
make db-shell        # Open PostgreSQL shell
make db-backup       # Backup database
make db-restore FILE=backup.sql  # Restore database
```

### Testing

```bash
make test            # Run Django tests
make test-coverage   # Run tests with coverage
make test-js        # Run JavaScript tests
make lint           # Run linters
```

### Production

```bash
make prod           # Start production environment
make prod-build     # Build production environment
make prod-down      # Stop production environment
make prod-logs      # Show production logs
make prod-restart   # Restart production services
```

## Development Workflow

### 1. Starting Fresh

```bash
# Clean start with new database
make reset
make dev-build
make migrate
make createsuperuser
```

### 2. Daily Development

```bash
# Start services
make dev

# Watch logs in another terminal
make dev-logs

# Make code changes - they auto-reload!
```

### 3. Database Changes

```bash
# After changing models
make makemigrations
make migrate
```

### 4. Running Tests

```bash
# Django tests
make test

# JavaScript tests
make test-js

# All linting
make lint
```

## Troubleshooting

### Port Conflicts

If you still get port conflicts, you can customize ports in `docker-compose.local.yml` or set environment variables:

```bash
# Example: Use different web port
WEB_PORT=8002 docker-compose -f docker-compose.local.yml up
```

### Database Issues

```bash
# Reset database completely
make reset

# Or manually
docker-compose -f docker-compose.local.yml down -v
docker volume rm community-packing-list_postgres_data_local
```

### Permission Issues

If you get permission errors:

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or run with sudo (not recommended)
sudo make dev
```

### Container Issues

```bash
# Remove all containers and volumes
make docker-prune

# Check container status
docker ps

# Check logs for specific service
docker-compose -f docker-compose.local.yml logs web
docker-compose -f docker-compose.local.yml logs db
```

## Environment Variables

### Required for Production

- `SECRET_KEY` - Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG` - Set to `False` for production
- `DJANGO_ALLOWED_HOSTS` - Space-separated list of allowed hosts
- `DB_NAME`, `DB_USER`, `DB_PASS` - PostgreSQL credentials

### Optional

- `REDIS_URL` - Redis connection URL
- `EMAIL_*` - Email configuration
- `SENTRY_DSN` - Error tracking

## Docker Commands Reference

### Build Images

```bash
# Development
docker-compose -f docker-compose.local.yml build

# Production
docker-compose -f docker-compose.prod.yml build
```

### Container Management

```bash
# List running containers
docker ps

# Execute command in container
docker-compose -f docker-compose.local.yml exec web python manage.py shell

# View logs
docker-compose -f docker-compose.local.yml logs -f web

# Stop all containers
docker-compose -f docker-compose.local.yml down
```

### Volume Management

```bash
# List volumes
docker volume ls

# Remove specific volume
docker volume rm community-packing-list_postgres_data_local

# Remove all unused volumes
docker volume prune
```

## Production Deployment

### Using Docker Compose

```bash
# 1. Set production environment variables
cp .env.example .env
# Edit .env with production values

# 2. Build and start
make prod-build

# 3. Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 4. Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### SSL Configuration

1. Place SSL certificates in `./ssl/` directory:
   - `cert.pem` - SSL certificate
   - `key.pem` - SSL private key

2. Update `nginx-site.conf` with your domain

3. Restart nginx:
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

## Health Checks

All services include health checks. Monitor with:

```bash
# Check health status
docker-compose -f docker-compose.local.yml ps

# Custom health endpoint
curl http://localhost:8001/health/
```

## Backup Strategy

### Automated Backups

```bash
# Add to crontab for daily backups
0 2 * * * cd /path/to/project && make db-backup
```

### Manual Backup

```bash
# Backup database
make db-backup

# Backup media files
tar -czf media_backup.tar.gz media/

# Backup everything
tar -czf full_backup.tar.gz --exclude=node_modules --exclude=__pycache__ .
```

## Performance Tuning

### Docker Resources

Edit Docker Desktop preferences to allocate:
- Memory: 4GB minimum
- CPUs: 2 minimum
- Disk: 20GB minimum

### Database Optimization

```sql
-- Run in db-shell
VACUUM ANALYZE;
REINDEX DATABASE packinglist_dev;
```

### Redis Optimization

```bash
# Check Redis memory
docker-compose -f docker-compose.local.yml exec redis redis-cli INFO memory
```

## Security Notes

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Change default passwords** before production
3. **Use strong SECRET_KEY** in production
4. **Enable HTTPS** in production (configured in nginx)
5. **Set DEBUG=False** in production
6. **Restrict admin access** by IP if possible

## Support

For issues or questions:
1. Check logs: `make dev-logs`
2. Review this guide
3. Check GitHub issues
4. Contact development team