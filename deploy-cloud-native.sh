#!/bin/bash

# Cloud-Native Deployment Script for Community Packing List
# This script sets up a fully serverless, cloud-native deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Cloud-Native Deployment for Community Packing List${NC}"
echo "=================================================="

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"community-packing-list"}
DB_INSTANCE_NAME=${DB_INSTANCE_NAME:-"packing-list-db"}

echo -e "${YELLOW}Configuration:${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo "Database Instance: $DB_INSTANCE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo -e "${GREEN}📋 Setting up Google Cloud project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${GREEN}🔧 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    cloudrun.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    compute.googleapis.com

# Create Cloud SQL instance (PostgreSQL)
echo -e "${GREEN}🗄️ Creating Cloud SQL PostgreSQL instance...${NC}"
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --deletion-protection || echo "Database instance may already exist"

# Create database
echo -e "${GREEN}📊 Creating database...${NC}"
gcloud sql databases create packinglist_prod \
    --instance=$DB_INSTANCE_NAME || echo "Database may already exist"

# Create database user
echo -e "${GREEN}👤 Creating database user...${NC}"
DB_PASSWORD=$(openssl rand -base64 32)
gcloud sql users create packinglist_user \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD || echo "User may already exist"

# Create Cloud Storage buckets
echo -e "${GREEN}🪣 Creating Cloud Storage buckets...${NC}"
STATIC_BUCKET="${PROJECT_ID}-static"
MEDIA_BUCKET="${PROJECT_ID}-media"

gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$STATIC_BUCKET/ || echo "Static bucket may already exist"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$MEDIA_BUCKET/ || echo "Media bucket may already exist"

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://$STATIC_BUCKET/
gsutil iam ch allUsers:objectViewer gs://$MEDIA_BUCKET/

# Create secrets in Secret Manager
echo -e "${GREEN}🔐 Creating secrets...${NC}"
DJANGO_SECRET_KEY=$(openssl rand -base64 64)

# Create secrets
echo -n "$DJANGO_SECRET_KEY" | gcloud secrets create django-secret-key --data-file=- || echo "Secret may already exist"
echo -n "postgresql://packinglist_user:$DB_PASSWORD@//cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME/packinglist_prod" | gcloud secrets create database-url --data-file=- || echo "Secret may already exist"
echo -n "$STATIC_BUCKET" | gcloud secrets create static-bucket-name --data-file=- || echo "Secret may already exist"
echo -n "$MEDIA_BUCKET" | gcloud secrets create media-bucket-name --data-file=- || echo "Secret may already exist"

# Build and deploy to Cloud Run
echo -e "${GREEN}🏗️ Building and deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "ENVIRONMENT=production" \
    --set-env-vars "USE_GCS=true" \
    --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
echo -e "${GREEN}🗄️ Database: $DB_INSTANCE_NAME${NC}"
echo -e "${GREEN}🪣 Static Bucket: gs://$STATIC_BUCKET${NC}"
echo -e "${GREEN}🪣 Media Bucket: gs://$MEDIA_BUCKET${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Visit your application at: $SERVICE_URL"
echo "2. Check logs: gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo "3. Monitor: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
echo ""
echo -e "${GREEN}🎉 Your cloud-native Django application is now live!${NC}" 