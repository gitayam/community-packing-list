# Community Packing List - Cloud Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Community Packing List Django application to various cloud platforms, with primary focus on Google Cloud Platform (Cloud Run and App Engine).

## Prerequisites

### 1. Google Cloud Account
- Active Google Cloud account with billing enabled
- Google Cloud CLI (`gcloud`) installed and configured
- Docker installed locally

### 2. Local Setup
```bash
# Install Google Cloud CLI (if not already installed)
# macOS: brew install google-cloud-sdk
# Linux: Follow https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login
gcloud auth configure-docker
```

### 3. Required APIs
Enable these Google Cloud APIs in your project:
- Cloud Run API
- Container Registry API
- Cloud Build API (for CI/CD)
- Cloud SQL API (if using managed database)

## Quick Deployment

### Option 1: Using the Deploy Script
```bash
# Set environment variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Run the deployment script
./deploy-cloud.sh
```

### Option 2: Manual Deployment
```bash
# Set your project ID
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="community-packing-list"

# Build and push container
docker build -f Dockerfile.cloud -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
```

## Deployment Options

### 1. Google Cloud Run (Recommended)
Best for: Automatic scaling, pay-per-use, serverless deployment

**Advantages:**
- Scales to zero when not in use
- Pay only for requests
- Automatic HTTPS
- Built-in load balancing

**Configuration:**
- Memory: 1GB
- CPU: 1 vCPU
- Max instances: 10
- Port: 8080

### 2. Google App Engine
Best for: Traditional web applications, integrated services

**Configuration:** Use `app.yaml` for deployment
```bash
gcloud app deploy app.yaml
```

### 3. Docker Compose (Local/VPS)
Best for: Local development, VPS deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.cloud.yml up -d
```

## Environment Configuration

### Required Environment Variables

For Cloud Run deployment, set these environment variables:

```bash
# Core Django settings
DJANGO_SETTINGS_MODULE=community_packing_list.settings_cloud
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database (if using Cloud SQL)
DATABASE_URL=postgres://user:password@host:port/database

# Security
DJANGO_ALLOWED_HOSTS=your-domain.com .run.app
CSRF_TRUSTED_ORIGINS=https://your-domain.com https://*.run.app
```

### Setting Environment Variables in Cloud Run

```bash
gcloud run services update community-packing-list \
  --set-env-vars="SECRET_KEY=your-secret-key,DATABASE_URL=your-db-url" \
  --region=us-central1
```

## Database Setup

### Option 1: SQLite (Default)
- Suitable for development and small deployments
- Data stored in container (not persistent across deployments)

### Option 2: Cloud SQL PostgreSQL
```bash
# Create Cloud SQL instance
gcloud sql instances create community-packing-list-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create community_packing_list \
  --instance=community-packing-list-db

# Create user
gcloud sql users create app_user \
  --instance=community-packing-list-db \
  --password=secure-password
```

### Option 3: External Database
Set `DATABASE_URL` environment variable to point to your external PostgreSQL database.

## Static Files

The application uses WhiteNoise for serving static files in production. Static files are automatically collected during the Docker build process.

For high-traffic applications, consider using Google Cloud Storage:

```python
# In settings_cloud.py
STATIC_URL = 'https://storage.googleapis.com/your-bucket/static/'
```

## CI/CD with GitHub Actions

The included GitHub Actions workflow (`.github/workflows/deploy.yml`) provides automatic deployment on pushes to the main branch.

### Setup GitHub Actions

1. Create a Google Cloud service account
2. Download the service account key (JSON)
3. Add these secrets to your GitHub repository:
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_SA_KEY`: Service account key (JSON content)

### Workflow Features
- Runs tests on PostgreSQL
- Builds and pushes Docker image
- Deploys to Cloud Run
- Only deploys on main branch

## Monitoring and Logging

### Cloud Logging
```bash
# View logs
gcloud logs read --service=community-packing-list --limit=50

# Follow logs in real-time
gcloud logs tail "resource.type=cloud_run_revision" --format="value(textPayload)"
```

### Health Checks
The Dockerfile includes a health check endpoint. Ensure your Django application has a `/health/` endpoint:

```python
# In urls.py
path('health/', views.health_check, name='health_check'),

# In views.py
def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

## Security Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **HTTPS**: Cloud Run provides automatic HTTPS
3. **IAM**: Use least-privilege service accounts
4. **Network**: Consider VPC for private communication
5. **Updates**: Regular dependency updates

## Cost Optimization

### Cloud Run Cost Optimization
- **Memory**: Start with 512MB, scale as needed
- **CPU**: Use 1 vCPU for most workloads
- **Min instances**: Set to 0 for development
- **Max instances**: Set reasonable limits (e.g., 10)

### Monitoring Costs
```bash
# Set up billing alerts
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Community Packing List Budget" \
  --budget-amount=50USD
```

## Troubleshooting

### Common Issues

1. **Port Binding Error**
   - Ensure Cloud Run port is set to 8080
   - Check Dockerfile.cloud CMD binding

2. **Static Files Not Loading**
   - Verify `collectstatic` runs in Dockerfile
   - Check STATIC_ROOT setting

3. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Check Cloud SQL proxy configuration

4. **Memory Issues**
   - Increase Cloud Run memory allocation
   - Optimize Django settings for production

### Debugging Commands
```bash
# Check service status
gcloud run services describe community-packing-list --region=us-central1

# View container logs
gcloud logs read --service=community-packing-list

# Test local Docker build
docker build -f Dockerfile.cloud -t test .
docker run -p 8080:8080 test
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Database set up and migrated
- [ ] Static files collecting properly
- [ ] Health check endpoint working
- [ ] HTTPS enforced
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Domain configured (if applicable)
- [ ] Load testing completed

## Support

For additional help:
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- GitHub Issues for project-specific questions

## Quick Reference

### Useful Commands
```bash
# Deploy
./deploy-cloud.sh

# Update service
gcloud run services update community-packing-list --region=us-central1

# View logs
gcloud logs read --service=community-packing-list

# Scale service
gcloud run services update community-packing-list \
  --max-instances=20 --region=us-central1

# Set environment variables
gcloud run services update community-packing-list \
  --set-env-vars="KEY=value" --region=us-central1
```