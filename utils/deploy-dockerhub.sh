#!/bin/bash
# Deploy Year Grid Calendar to Digital Ocean via Docker Hub
# No GitHub connection required

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🐳 Year Grid Calendar - Docker Hub Deployment"
echo "=============================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    echo "Install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Get Docker Hub username
if [ -z "$DOCKERHUB_USER" ]; then
    echo "Enter your Docker Hub username:"
    read -p "> " DOCKERHUB_USER

    if [ -z "$DOCKERHUB_USER" ]; then
        echo -e "${RED}❌ Username required${NC}"
        exit 1
    fi
fi

IMAGE_NAME="year-grid-calendar"
FULL_IMAGE="$DOCKERHUB_USER/$IMAGE_NAME:latest"

echo "Image: $FULL_IMAGE"
echo ""

# Check Docker login
echo "🔐 Checking Docker Hub login..."
if ! docker info | grep -q "Username:"; then
    echo "Please log in to Docker Hub:"
    docker login
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Docker login failed${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Logged in to Docker Hub${NC}"
echo ""

# Download fonts
echo "📦 Preparing fonts..."
if [ ! -d "fonts" ]; then
    echo -e "${RED}❌ fonts/ directory not found${NC}"
    exit 1
fi

cd fonts
if [ ! -f "download_fonts.sh" ]; then
    echo -e "${RED}❌ download_fonts.sh not found${NC}"
    exit 1
fi

if [ ! -f "NotoSans-Regular.ttf" ]; then
    echo "📥 Downloading fonts..."
    chmod +x download_fonts.sh
    ./download_fonts.sh
else
    echo "✅ Fonts already present"
fi
cd ..
echo ""

# Build image
echo "🏗️  Building Docker image..."
echo "This may take a few minutes on first build..."
docker build -f Dockerfile.do -t "$FULL_IMAGE" .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Image built successfully${NC}"
echo ""

# Push to Docker Hub
echo "⬆️  Pushing to Docker Hub..."
docker push "$FULL_IMAGE"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker push failed${NC}"
    echo ""
    echo "Common issues:"
    echo "  - Not logged in: run 'docker login'"
    echo "  - Wrong username: check DOCKERHUB_USER variable"
    echo "  - Private repo: make it public on Docker Hub"
    exit 1
fi

echo -e "${GREEN}✅ Image pushed to Docker Hub${NC}"
echo ""

# Check if app exists
if [ -f ".app_id" ]; then
    source .app_id
fi

if [ -z "$APP_ID" ]; then
    # Create new app
    echo "📋 Creating new Digital Ocean app..."
    echo ""

    # Create app spec
    cat > /tmp/app-dockerhub.yaml << EOF
name: year-grid-calendar
services:
  - name: web
    image:
      registry_type: DOCKER_HUB
      registry: $DOCKERHUB_USER
      repository: $IMAGE_NAME
      tag: latest
    run_command: uvicorn web.app:app --host 0.0.0.0 --port 8080
    envs:
      - key: PORT
        value: "8080"
      - key: PYTHONUNBUFFERED
        value: "1"
    http_port: 8080
    health_check:
      http_path: /health
      initial_delay_seconds: 20
      period_seconds: 30
      timeout_seconds: 10
    instance_size_slug: basic-xs
    instance_count: 1
    routes:
      - path: /
domains:
  - domain: year-grid.ceesaxp.org
    type: PRIMARY
region: nyc
EOF

    echo "Creating app on Digital Ocean..."
    APP_ID=$(doctl apps create --spec /tmp/app-dockerhub.yaml --format ID --no-header 2>&1)

    if [ -z "$APP_ID" ] || [[ "$APP_ID" == *"error"* ]] || [[ "$APP_ID" == *"Error"* ]]; then
        echo -e "${RED}❌ Failed to create app${NC}"
        echo "$APP_ID"
        echo ""
        echo "Make sure:"
        echo "  - doctl is authenticated: doctl auth init"
        echo "  - Image is public on Docker Hub"
        exit 1
    fi

    # Save APP_ID for future use
    echo "export APP_ID=$APP_ID" > .app_id

    echo -e "${GREEN}✅ App created: $APP_ID${NC}"
    echo ""
    echo "View in dashboard:"
    echo "  https://cloud.digitalocean.com/apps/$APP_ID"
    echo ""
else
    # Update existing app
    echo "🔄 Triggering redeployment of existing app..."
    doctl apps create-deployment $APP_ID

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Redeployment failed${NC}"
        echo ""
        echo "The app may have been deleted. Remove .app_id and try again."
        exit 1
    fi

    echo -e "${GREEN}✅ Redeployment triggered${NC}"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Deployment initiated successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "App ID: $APP_ID"
echo ""
echo "Next steps:"
echo "  1. Wait for deployment (5-10 minutes)"
echo "  2. Configure domain in DO dashboard (if not automatic)"
echo "  3. Access your app!"
echo ""
echo "Useful commands:"
echo "  Watch logs:    doctl apps logs $APP_ID --follow"
echo "  Check status:  doctl apps get $APP_ID"
echo "  List apps:     doctl apps list"
echo ""
echo "To update in the future:"
echo "  export APP_ID=$APP_ID"
echo "  ./deploy-dockerhub.sh"
echo ""
echo "Or just run this script again - APP_ID is saved in .app_id"
echo ""
