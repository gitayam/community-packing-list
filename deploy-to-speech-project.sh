#!/bin/bash
set -e

# Deploy Community Packing List to Google Cloud
echo "🚀 Deploying Community Packing List to Google Cloud"

# Load environment variables from .env file if it exists (only if not already set)
if [ -f .env ]; then
    echo "📁 Loading configuration from .env file..."
    set -o allexport
    source .env
    set +o allexport
fi

# Configuration from environment variables (terminal takes precedence)
PROJECT_ID="${PROJECT_ID}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-community-packing-list}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Try to get PROJECT_ID from gcloud config if not set
if [ -z "$PROJECT_ID" ]; then
    if command -v gcloud &> /dev/null; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "(unset)" ]; then
            echo "📋 Using PROJECT_ID from gcloud config: $PROJECT_ID"
        fi
    fi
fi

# Validate required environment variables
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    echo "❌ PROJECT_ID environment variable is required"
    echo "   Options to set it:"
    echo "   1. Export: export PROJECT_ID=your-project-id"
    echo "   2. Set in .env file: echo 'PROJECT_ID=your-project-id' >> .env"
    echo "   3. Set gcloud default: gcloud config set project your-project-id"
    exit 1
fi

echo "📋 Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION" 
echo "  Service: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Please install it first:"
    echo "   brew install google-cloud-sdk"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated. Please run:"
    echo "   gcloud auth login"
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.cloud -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG .

# Push to Google Container Registry
echo "📤 Pushing to Container Registry..."
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
    --min-instances 0 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=community_packing_list.settings_cloud,DEBUG=False"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "1. Test the service: curl $SERVICE_URL"
echo "2. Set up environment variables if needed"
echo "3. Configure custom domain (optional)"
echo ""
echo "🔧 Useful commands:"
echo "  View logs: gcloud logs read --service=$SERVICE_NAME --limit=20"
echo "  Update env vars: gcloud run services update $SERVICE_NAME --set-env-vars KEY=value --region=$REGION"
echo "  Scale service: gcloud run services update $SERVICE_NAME --max-instances=20 --region=$REGION"