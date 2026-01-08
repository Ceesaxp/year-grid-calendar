#!/bin/bash
# Automated deployment script for Year Grid Calendar
# Builds, pushes to DO Container Registry, and optionally deploys to droplet

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="registry.digitalocean.com/year-grid-calendar/app"
VERSION=${1:-$(date +%Y%m%d-%H%M%S)}

echo "🚀 Year Grid Calendar - DOCR Deployment"
echo "=========================================="
echo ""
echo "Registry: $REGISTRY"
echo "Version: $VERSION"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi

# Check doctl
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}❌ doctl not found${NC}"
    echo "Install with: brew install doctl"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# Authenticate to registry
echo "🔐 Authenticating to DO Container Registry..."
if ! doctl registry login; then
    echo -e "${RED}❌ Registry authentication failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Authenticated${NC}"
echo ""

# Download fonts
echo "📦 Preparing fonts..."
if [ ! -d "fonts" ]; then
    echo -e "${RED}❌ fonts/ directory not found${NC}"
    exit 1
fi

cd fonts
if [ ! -f "NotoSans-Regular.ttf" ]; then
    echo "📥 Downloading fonts..."
    ./download_fonts.sh
fi
cd ..
echo -e "${GREEN}✅ Fonts ready${NC}"
echo ""

# Build image
echo "🏗️  Building Docker image..."
echo "This may take a few minutes..."
docker build -f Dockerfile.do \
    -t $REGISTRY:latest \
    -t $REGISTRY:$VERSION \
    .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Image built${NC}"
echo ""

# Push to registry
echo "⬆️  Pushing to Container Registry..."
echo "Pushing: $REGISTRY:latest"
docker push $REGISTRY:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Push failed${NC}"
    exit 1
fi

echo "Pushing: $REGISTRY:$VERSION"
docker push $REGISTRY:$VERSION

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Push failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Images pushed to registry${NC}"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Build and push complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Images pushed:"
echo "  - $REGISTRY:latest"
echo "  - $REGISTRY:$VERSION"
echo ""

# Ask about deployment to droplet
echo "Deploy to droplet now?"
echo "  1) Deploy to droplet via SSH"
echo "  2) Show manual deployment instructions"
echo "  3) Skip deployment"
echo ""
read -p "Choose (1-3): " deploy_choice

case $deploy_choice in
    1)
        echo ""
        read -p "Enter droplet IP or hostname: " DROPLET_HOST

        if [ -z "$DROPLET_HOST" ]; then
            echo -e "${RED}❌ Droplet host required${NC}"
            exit 1
        fi

        echo ""
        echo "🚀 Deploying to $DROPLET_HOST..."

        # SSH and deploy
        ssh root@$DROPLET_HOST << 'ENDSSH'
cd /opt/year-grid-calendar || exit 1

echo "📥 Authenticating to registry..."
doctl registry login

echo "📥 Pulling latest image..."
docker-compose pull

echo "🔄 Restarting service..."
docker-compose up -d

echo "⏳ Waiting for health check..."
sleep 5

if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed!"
    exit 1
fi
ENDSSH

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Deployed successfully to $DROPLET_HOST${NC}"
        else
            echo -e "${RED}❌ Deployment failed${NC}"
            exit 1
        fi
        ;;

    2)
        echo ""
        echo "📋 Manual Deployment Instructions:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "On your droplet, run:"
        echo ""
        echo "  cd /opt/year-grid-calendar"
        echo "  doctl registry login"
        echo "  docker-compose pull"
        echo "  docker-compose up -d"
        echo ""
        echo "Or use the update script:"
        echo "  /opt/year-grid-calendar/update.sh"
        echo ""
        echo "Or deploy specific version:"
        echo "  deploy-calendar $VERSION"
        echo ""
        ;;

    3)
        echo ""
        echo "Skipping deployment."
        echo ""
        echo "To deploy later on your droplet:"
        echo "  cd /opt/year-grid-calendar"
        echo "  doctl registry login"
        echo "  docker-compose pull"
        echo "  docker-compose up -d"
        echo ""
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ All done!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Version tags:"
echo "  latest - Always points to newest build"
echo "  $VERSION - This specific build"
echo ""
echo "View in registry:"
echo "  doctl registry repository list-tags year-grid-calendar/app"
echo ""
echo "View images:"
echo "  https://cloud.digitalocean.com/registry/year-grid-calendar"
echo ""
