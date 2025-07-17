#\!/bin/bash
echo "Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
echo "APIs enabled successfully\!"
EOF < /dev/null