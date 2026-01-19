#!/bin/bash
#===============================================================================
# YAVA Intent Classifier - Cloud Deployment Script
# 
# Supports: Google Cloud Run, AWS Lambda, IBM Code Engine
#===============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="yava-intent-classifier"
REGION="us-central1"

show_help() {
    echo "Usage: ./deploy_cloud.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --gcp          Deploy to Google Cloud Run"
    echo "  --ibm          Deploy to IBM Code Engine"
    echo "  --aws          Deploy to AWS Lambda (via container)"
    echo "  --local        Run locally with Docker"
    echo "  --help         Show this help"
    echo ""
}

deploy_gcp() {
    log_info "Deploying to Google Cloud Run..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_warn "gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Get project ID
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        echo "Enter your GCP Project ID:"
        read PROJECT_ID
        gcloud config set project $PROJECT_ID
    fi
    
    log_info "Building and pushing Docker image..."
    
    # Enable services
    gcloud services enable run.googleapis.com containerregistry.googleapis.com
    
    # Build and push
    IMAGE_URL="gcr.io/${PROJECT_ID}/${PROJECT_NAME}"
    
    cd "$SCRIPT_DIR"
    gcloud builds submit --tag $IMAGE_URL
    
    log_info "Deploying to Cloud Run..."
    
    gcloud run deploy $PROJECT_NAME \
        --image $IMAGE_URL \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 512Mi \
        --timeout 30
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $PROJECT_NAME --region $REGION --format 'value(status.url)')
    
    log_success "Deployed to: $SERVICE_URL"
    
    # Update OpenAPI spec
    log_info "Updating OpenAPI spec with service URL..."
    sed "s|http://localhost:8000|$SERVICE_URL|g" skills/openapi_local.json > skills/openapi_remote.json
    
    log_success "OpenAPI spec updated: skills/openapi_remote.json"
    echo ""
    echo "Next steps:"
    echo "  1. Import skill: orchestrate skills import -f skills/openapi_remote.json"
    echo "  2. Update agent with skill reference"
    echo "  3. Re-import agent: orchestrate agents import -f agent.yaml"
}

deploy_ibm() {
    log_info "Deploying to IBM Code Engine..."
    
    # Check if ibmcloud is installed
    if ! command -v ibmcloud &> /dev/null; then
        log_warn "ibmcloud CLI not found. Install from: https://cloud.ibm.com/docs/cli"
        exit 1
    fi
    
    # Login check
    ibmcloud target || ibmcloud login
    
    # Create Code Engine project
    ibmcloud ce project create --name $PROJECT_NAME 2>/dev/null || \
    ibmcloud ce project select --name $PROJECT_NAME
    
    log_info "Building and deploying application..."
    
    cd "$SCRIPT_DIR"
    
    # Deploy from source
    ibmcloud ce app create --name $PROJECT_NAME \
        --build-source . \
        --strategy dockerfile \
        --port 8080 \
        --memory 512M \
        --cpu 0.5 \
        --min-scale 0 \
        --max-scale 3 \
        2>/dev/null || \
    ibmcloud ce app update --name $PROJECT_NAME --build-source .
    
    # Get application URL
    SERVICE_URL=$(ibmcloud ce app get --name $PROJECT_NAME -o url)
    
    log_success "Deployed to: $SERVICE_URL"
    
    # Update OpenAPI spec
    sed "s|http://localhost:8000|$SERVICE_URL|g" skills/openapi_local.json > skills/openapi_remote.json
    
    log_success "OpenAPI spec updated: skills/openapi_remote.json"
}

deploy_aws() {
    log_info "Deploying to AWS Lambda (via ECR + Lambda Container)..."
    
    if ! command -v aws &> /dev/null; then
        log_warn "aws CLI not found. Install from: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=${AWS_REGION:-us-east-1}
    ECR_REPO="${PROJECT_NAME}"
    IMAGE_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest"
    
    log_info "Creating ECR repository..."
    aws ecr create-repository --repository-name $ECR_REPO 2>/dev/null || true
    
    log_info "Building and pushing Docker image..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    
    cd "$SCRIPT_DIR"
    docker build -t $ECR_REPO .
    docker tag $ECR_REPO:latest $IMAGE_URI
    docker push $IMAGE_URI
    
    log_info "Creating Lambda function..."
    
    # Create Lambda execution role if not exists
    aws iam create-role --role-name lambda-${PROJECT_NAME}-role \
        --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
        2>/dev/null || true
    
    aws iam attach-role-policy --role-name lambda-${PROJECT_NAME}-role \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null || true
    
    sleep 10  # Wait for role propagation
    
    aws lambda create-function \
        --function-name $PROJECT_NAME \
        --package-type Image \
        --code ImageUri=$IMAGE_URI \
        --role arn:aws:iam::${ACCOUNT_ID}:role/lambda-${PROJECT_NAME}-role \
        --timeout 30 \
        --memory-size 512 \
        2>/dev/null || \
    aws lambda update-function-code \
        --function-name $PROJECT_NAME \
        --image-uri $IMAGE_URI
    
    # Create Function URL
    aws lambda create-function-url-config \
        --function-name $PROJECT_NAME \
        --auth-type NONE \
        2>/dev/null || true
    
    SERVICE_URL=$(aws lambda get-function-url-config --function-name $PROJECT_NAME --query 'FunctionUrl' --output text)
    
    log_success "Deployed to: $SERVICE_URL"
    
    # Update OpenAPI spec
    sed "s|http://localhost:8000|${SERVICE_URL%/}|g" skills/openapi_local.json > skills/openapi_remote.json
    
    log_success "OpenAPI spec updated: skills/openapi_remote.json"
}

run_local() {
    log_info "Running locally with Docker..."
    
    cd "$SCRIPT_DIR"
    
    docker build -t $PROJECT_NAME .
    
    log_info "Starting container on port 8000..."
    docker run -d --name $PROJECT_NAME -p 8000:8080 $PROJECT_NAME
    
    sleep 3
    
    # Test
    log_info "Testing API..."
    curl -s -X POST http://localhost:8000/classify \
        -H "Content-Type: application/json" \
        -d '{"user_input": "I need to refill my prescription"}' | python3 -m json.tool
    
    log_success "API running at http://localhost:8000"
    log_info "To stop: docker stop $PROJECT_NAME && docker rm $PROJECT_NAME"
}

# Parse arguments
case "$1" in
    --gcp)
        deploy_gcp
        ;;
    --ibm)
        deploy_ibm
        ;;
    --aws)
        deploy_aws
        ;;
    --local)
        run_local
        ;;
    --help)
        show_help
        ;;
    *)
        show_help
        ;;
esac
