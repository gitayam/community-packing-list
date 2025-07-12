# Google Cloud Serverless Deployment Guide

This guide provides step-by-step instructions for deploying the Community Packing List application to Google Cloud using serverless technologies.

## Architecture Overview

The serverless deployment uses:
- **Cloud Run**: Containerized application hosting
- **Cloud SQL (PostgreSQL)**: Managed database
- **Cloud Storage**: Static file hosting and media uploads
- **Cloud Build**: CI/CD pipeline
- **GitHub Actions**: Automated deployment workflow

## Prerequisites

1. **Google Cloud Project**
   - Create a new project or use existing one
   - Enable billing for the project

2. **Required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable sql-component.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable storage.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   ```

3. **Local Tools**
   - [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
   - Docker
   - Git

## Step 1: Initial Google Cloud Setup

### 1.1 Set Project Variables
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export SERVICE_NAME="community-packing-list"
export DB_INSTANCE_NAME="packing-list-db"
```

### 1.2 Configure gcloud
```bash
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud auth configure-docker $REGION-docker.pkg.dev
```

### 1.3 Create Artifact Registry
```bash
gcloud artifacts repositories create $SERVICE_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Community Packing List container images"
```

## Step 2: Database Setup

### 2.1 Create Cloud SQL Instance
```bash
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --deletion-protection
```

### 2.2 Create Database
```bash
gcloud sql databases create packinglist_db --instance=$DB_INSTANCE_NAME
```

### 2.3 Create Database User
```bash
# Generate a secure password
DB_PASSWORD=$(openssl rand -base64 32)
echo "Database password: $DB_PASSWORD"

gcloud sql users create app_user \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD
```

## Step 3: Cloud Storage Setup

### 3.1 Create Storage Buckets
```bash
# Static files bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-static

# Media files bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-media

# Set public access for static files
gsutil iam ch allUsers:objectViewer gs://$PROJECT_ID-static
```

### 3.2 Configure CORS for Media Bucket
```bash
cat > cors.json << 'EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type", "Authorization"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://$PROJECT_ID-media
rm cors.json
```

## Step 4: Secrets Management

### 4.1 Create Secrets
```bash
# Django Secret Key
openssl rand -base64 50 | gcloud secrets create django-secret-key --data-file=-

# Database URL
echo "postgresql://app_user:$DB_PASSWORD@//cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME/packinglist_db" | \
    gcloud secrets create database-url --data-file=-

# Cloud Storage settings
echo "$PROJECT_ID-static" | gcloud secrets create static-bucket-name --data-file=-
echo "$PROJECT_ID-media" | gcloud secrets create media-bucket-name --data-file=-
```

### 4.2 Create Service Account
```bash
gcloud iam service-accounts create $SERVICE_NAME-sa \
    --display-name="Community Packing List Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Grant secret access
for secret in django-secret-key database-url static-bucket-name media-bucket-name; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
done
```

## Step 5: GitHub Actions Setup

### 5.1 Create GitHub Repository Secrets

In your GitHub repository, go to Settings > Secrets and Variables > Actions, and add:

```
GCP_PROJECT_ID: your-project-id
GCP_REGION: us-central1
GCP_SERVICE_NAME: community-packing-list
GCP_SA_KEY: [Service Account JSON key - see below]
```

### 5.2 Generate Service Account Key for GitHub
```bash
gcloud iam service-accounts keys create key.json \
    --iam-account=$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com

# Add this JSON content to GCP_SA_KEY secret in GitHub
cat key.json

# Clean up the local key file
rm key.json
```

## Step 6: Environment Configuration

### 6.1 Cloud Run Environment Variables
The application will automatically read these from Cloud Run environment:
- `GOOGLE_CLOUD_PROJECT`: Set automatically by Cloud Run
- `DATABASE_URL`: From Secret Manager
- `DJANGO_SECRET_KEY`: From Secret Manager
- `GS_BUCKET_NAME`: From Secret Manager (static files)
- `GS_MEDIA_BUCKET_NAME`: From Secret Manager (media files)

## Step 7: Initial Deployment

### 7.1 Build and Deploy Manually (First Time)
```bash
# Build the image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:latest .

# Push to Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:latest

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:latest \
    --platform=managed \
    --region=$REGION \
    --service-account=$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:$DB_INSTANCE_NAME \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-secrets="DATABASE_URL=database-url:latest,DJANGO_SECRET_KEY=django-secret-key:latest,GS_BUCKET_NAME=static-bucket-name:latest,GS_MEDIA_BUCKET_NAME=media-bucket-name:latest" \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --max-instances=10 \
    --min-instances=0 \
    --concurrency=80 \
    --timeout=300 \
    --port=8080
```

### 7.2 Run Database Migrations
```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

# Run migrations using Cloud Run Jobs
gcloud run jobs create $SERVICE_NAME-migrate \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:latest \
    --region=$REGION \
    --service-account=$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:$DB_INSTANCE_NAME \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-secrets="DATABASE_URL=database-url:latest,DJANGO_SECRET_KEY=django-secret-key:latest,GS_BUCKET_NAME=static-bucket-name:latest,GS_MEDIA_BUCKET_NAME=media-bucket-name:latest" \
    --command="python" \
    --args="manage.py,migrate" \
    --memory=1Gi \
    --cpu=1 \
    --max-retries=3

# Execute the migration job
gcloud run jobs execute $SERVICE_NAME-migrate --region=$REGION
```

### 7.3 Collect Static Files
```bash
# Create collect static job
gcloud run jobs create $SERVICE_NAME-collectstatic \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:latest \
    --region=$REGION \
    --service-account=$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-secrets="DATABASE_URL=database-url:latest,DJANGO_SECRET_KEY=django-secret-key:latest,GS_BUCKET_NAME=static-bucket-name:latest,GS_MEDIA_BUCKET_NAME=media-bucket-name:latest" \
    --command="python" \
    --args="manage.py,collectstatic,--noinput" \
    --memory=1Gi \
    --cpu=1 \
    --max-retries=3

# Execute the collect static job
gcloud run jobs execute $SERVICE_NAME-collectstatic --region=$REGION
```

## Step 8: Custom Domain (Optional)

### 8.1 Map Custom Domain
```bash
# Map domain to Cloud Run service
gcloud run domain-mappings create \
    --service=$SERVICE_NAME \
    --domain=your-domain.com \
    --region=$REGION
```

### 8.2 SSL Certificate
Cloud Run automatically provisions and manages SSL certificates for custom domains.

## Step 9: Monitoring and Logging

### 9.1 Enable Cloud Monitoring
```bash
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

### 9.2 Set up Alerts (Optional)
Create alerts for:
- High error rates
- Response latency
- Memory usage
- Database connections

## Ongoing Maintenance

### Database Backups
Cloud SQL automatically creates backups. To create manual backup:
```bash
gcloud sql backups create --instance=$DB_INSTANCE_NAME
```

### Scaling Configuration
Adjust Cloud Run settings based on traffic:
```bash
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --min-instances=1 \
    --max-instances=20 \
    --concurrency=100
```

### Cost Optimization
- Use Cloud SQL's automatic scaling
- Set appropriate Cloud Run min/max instances
- Monitor storage usage and clean up old files
- Use Cloud CDN for static assets if needed

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify Cloud SQL instance is running
   - Check service account permissions
   - Ensure Cloud SQL connections are properly configured

2. **Static Files Not Loading**
   - Verify bucket permissions
   - Check CORS configuration
   - Ensure collectstatic was run successfully

3. **Memory Issues**
   - Increase Cloud Run memory allocation
   - Optimize Django settings for production
   - Use database connection pooling

### Useful Commands

```bash
# View logs
gcloud logs read --service=$SERVICE_NAME --limit=50

# Check service status
gcloud run services describe $SERVICE_NAME --region=$REGION

# Update service with new image
gcloud run services update $SERVICE_NAME \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME:latest \
    --region=$REGION
```

## Security Best Practices

1. **Secrets Management**: All sensitive data stored in Secret Manager
2. **Service Account**: Minimal required permissions
3. **Network**: Cloud Run with private networking options
4. **Database**: Cloud SQL with encryption at rest and in transit
5. **HTTPS**: Automatic SSL termination
6. **IAM**: Principle of least privilege

## Support

For issues with this deployment guide, please check:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Django on Google Cloud](https://cloud.google.com/python/django)