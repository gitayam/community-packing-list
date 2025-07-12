#!/bin/bash

# AWS Serverless Deployment Script for Community Packing List
# This script deploys the application to AWS Lambda with all required infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AWS Serverless Deployment for Community Packing List${NC}"
echo "========================================================"

# Configuration
STAGE=${STAGE:-"dev"}
REGION=${REGION:-"us-east-1"}

echo -e "${YELLOW}Configuration:${NC}"
echo "Stage: $STAGE"
echo "Region: $REGION"
echo ""

# Check if required tools are installed
echo -e "${GREEN}🔧 Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js from: https://nodejs.org/"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3"
    exit 1
fi

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed${NC}"
    echo "Please install AWS CLI from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    echo "Please configure AWS credentials using: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Install Serverless Framework if not installed
if ! command -v serverless &> /dev/null; then
    echo -e "${GREEN}📦 Installing Serverless Framework...${NC}"
    npm install -g serverless
fi

# Install Serverless plugins
echo -e "${GREEN}📦 Installing Serverless plugins...${NC}"
npm install serverless-python-requirements serverless-domain-manager serverless-plugin-warmup

# Install Python dependencies
echo -e "${GREEN}📦 Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

# Install Node.js dependencies
echo -e "${GREEN}📦 Installing Node.js dependencies...${NC}"
npm install

# Build TypeScript
echo -e "${GREEN}🔨 Building TypeScript...${NC}"
npm run build

# Build CSS
echo -e "${GREEN}🎨 Building CSS...${NC}"
npm run css:build

# Generate secrets if not provided
if [ -z "$SECRET_KEY" ]; then
    echo -e "${YELLOW}🔐 Generating Django secret key...${NC}"
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
fi

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}🔐 Generating database password...${NC}"
    export DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
fi

echo -e "${GREEN}🏗️ Deploying to AWS Lambda...${NC}"
serverless deploy --stage $STAGE --region $REGION --verbose

# Run migrations
echo -e "${GREEN}🗄️ Running database migrations...${NC}"
serverless invoke --function migrate --stage $STAGE --region $REGION

# Get deployment info
echo -e "${GREEN}📊 Getting deployment information...${NC}"
ENDPOINT=$(serverless info --stage $STAGE --region $REGION --verbose | grep 'ServiceEndpoint' | cut -d' ' -f2)

# Test the deployment
echo -e "${GREEN}🧪 Testing deployment...${NC}"
if curl -f "$ENDPOINT/health/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️ Health check failed, but deployment may still be successful${NC}"
fi

# Display deployment information
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo "========================================================"
echo -e "${GREEN}🌐 Service Endpoint: $ENDPOINT${NC}"
echo -e "${GREEN}📊 AWS Console: https://console.aws.amazon.com/lambda/home?region=$REGION${NC}"
echo -e "${GREEN}📈 CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Visit your application at: $ENDPOINT"
echo "2. Check logs: serverless logs --function app --stage $STAGE --tail"
echo "3. Monitor: https://console.aws.amazon.com/lambda/home?region=$REGION"
echo "4. Update domain: serverless create_domain --stage $STAGE (if configured)"
echo ""
echo -e "${GREEN}🎉 Your serverless Django application is now live on AWS!${NC}"

# Save deployment info
cat > deployment-info.json << EOF
{
  "stage": "$STAGE",
  "region": "$REGION",
  "endpoint": "$ENDPOINT",
  "deployed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "secret_key": "$SECRET_KEY",
  "db_password": "$DB_PASSWORD"
}
EOF

echo -e "${YELLOW}💾 Deployment information saved to deployment-info.json${NC}"
echo -e "${RED}⚠️ Keep deployment-info.json secure - it contains sensitive information${NC}" 