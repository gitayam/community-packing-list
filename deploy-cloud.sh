#!/bin/bash
set -e

# Community Packing List - Cloud Deployment Script
# Supports Google Cloud Run and App Engine deployment

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "📁 Loading configuration from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

PROJECT_ID="${PROJECT_ID}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-community-packing-list}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Validate required environment variables
if [ -z "$PROJECT_ID" ]; then
    echo "❌ PROJECT_ID environment variable is required"
    echo "   Set it in .env file or export PROJECT_ID=your-project-id"
    exit 1
fi

echo "🚀 Starting cloud deployment for Community Packing List"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Please install it first."
    exit 1
fi

# Check if logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud. Please run 'gcloud auth login'"
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "⚙️ Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push the container
echo "🔨 Building container image..."
docker build -f Dockerfile.cloud -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG .

echo "📤 Pushing container to registry..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=community_packing_list.settings_cloud"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "Next steps:"
echo "1. Set up your database (Cloud SQL or external)"
echo "2. Configure environment variables in Cloud Run"
echo "3. Set up custom domain (optional)"
echo "4. Configure monitoring and logging"