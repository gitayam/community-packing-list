# Deployment Guide

This directory contains deployment scripts and configurations for the Community Packing List application.

## 🚀 Quick Deployment

### Production (Google Cloud Run)
```bash
./deployment/deploy-cloud.sh
```

### Local Development
```bash
./deployment/deploy-local.sh
```

## 📋 Deployment Scripts

### `deploy-cloud.sh`
Deploys the application to Google Cloud Run with:
- PostgreSQL Cloud SQL integration
- Static file serving via Cloud Storage
- Auto-scaling and HTTPS
- Health checks and monitoring

**Prerequisites:**
- Google Cloud SDK installed and authenticated
- Project configured with billing enabled
- Cloud Run, Cloud SQL, and Cloud Storage APIs enabled

### `deploy-local.sh`
Sets up local development environment with:
- Docker Compose services (PostgreSQL, Redis)
- Django development server
- Database migrations and admin user creation
- Example data loading

**Prerequisites:**
- Docker and Docker Compose installed
- Python 3.11+ for local Django server

## 🔧 Configuration

### Environment Variables

Both deployment methods use environment variables for configuration:

**Production (.env.cloud):**
```bash
DATABASE_URL=postgresql://user:password@/db?host=/cloudsql/project:region:instance
GCS_BUCKET_NAME=your-storage-bucket
DJANGO_SECRET_KEY=production-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
```

**Local (.env.local):**
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/packing_list_db
DJANGO_SECRET_KEY=local-development-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration

**Production:** Uses Google Cloud SQL PostgreSQL instance
**Local:** Uses PostgreSQL container via Docker Compose

## 🏗️ Infrastructure

### Google Cloud Resources

The cloud deployment creates/uses:
- **Cloud Run Service**: Main application container
- **Cloud SQL Instance**: PostgreSQL database
- **Cloud Storage Bucket**: Static file storage
- **VPC Connector**: Secure database connection
- **Load Balancer**: HTTPS termination and routing

### Local Development Stack

- **Django**: Web application (port 8000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Caching (port 6379)

## 🔍 Monitoring & Health Checks

### Production Monitoring
- Cloud Run built-in monitoring
- Health check endpoint: `/health/`
- Error reporting via Cloud Logging
- Performance metrics in Cloud Monitoring

### Local Development
- Django debug toolbar (when DEBUG=True)
- Console logging
- Basic health check endpoint

## 🚨 Troubleshooting

### Common Issues

**Cloud Deployment:**
- Ensure Cloud SQL instance is running
- Check VPC connector configuration
- Verify storage bucket permissions
- Review Cloud Run service logs

**Local Development:**
- Ensure Docker daemon is running
- Check port conflicts (8000, 5432, 6379)
- Verify environment variables in .env.local
- Check database connection in Django settings

### Logs and Debugging

**Production:**
```bash
# View Cloud Run logs
gcloud run services logs read community-packing-list --project=YOUR_PROJECT

# Check Cloud SQL status
gcloud sql instances describe YOUR_INSTANCE --project=YOUR_PROJECT
```

**Local:**
```bash
# View application logs
docker-compose logs web

# View database logs
docker-compose logs db

# Django debug mode provides detailed error pages
```

## 📈 Scaling Considerations

### Production Scaling
- Cloud Run automatically scales based on traffic
- Cloud SQL can be scaled vertically
- Static files served from globally distributed CDN
- Consider read replicas for high traffic

### Development Scaling
- Local environment suitable for single developer
- Use production-like data volumes for testing
- Consider staging environment for team development

## 🔒 Security

### Production Security
- HTTPS enforced by Cloud Run
- Private VPC for database access
- IAM-based access control
- Secrets stored in environment variables

### Development Security
- Local development only accessible on localhost
- Development secret keys (not for production)
- Database isolated in Docker network

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Docker Compose Reference](https://docs.docker.com/compose/)