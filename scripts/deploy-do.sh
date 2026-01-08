#!/bin/sh
# Deploy Year Grid Calendar to Digital Ocean Droplet via Docker Hub
# Builds AMD64 image using buildx and pushes to Docker Hub

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "${BLUE}Year Grid Calendar - Docker Hub Deployment${NC}"
echo "=============================================="
echo ""

# Check Docker
if ! command -v docker > /dev/null 2>&1; then
    echo "${RED}Docker not found${NC}"
    echo "Install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "${RED}Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Check if buildx is available
if ! docker buildx version > /dev/null 2>&1; then
    echo "${RED}docker buildx is not available${NC}"
    echo "Run: docker buildx create --use"
    exit 1
fi

echo "${GREEN}Docker is running${NC}"
echo ""

# Get Docker Hub username
if [ -z "$DOCKERHUB_USER" ]; then
    printf "Enter your Docker Hub username: "
    read DOCKERHUB_USER

    if [ -z "$DOCKERHUB_USER" ]; then
        echo "${RED}Username required${NC}"
        exit 1
    fi
fi

IMAGE_NAME="year-grid-calendar"
FULL_IMAGE="$DOCKERHUB_USER/$IMAGE_NAME:latest"

echo "Image: $FULL_IMAGE"
echo "Platform: linux/amd64"
echo "Dockerfile: Dockerfile.do"
echo ""

# Check Docker login
echo "Checking Docker Hub login..."
if ! docker info 2>/dev/null | grep -q "Username:"; then
    echo "Please log in to Docker Hub:"
    docker login
    if [ $? -ne 0 ]; then
        echo "${RED}Docker login failed${NC}"
        exit 1
    fi
fi
echo "${GREEN}Logged in to Docker Hub${NC}"
echo ""

# Download fonts
echo "Preparing fonts..."
if [ ! -d "fonts" ]; then
    echo "${RED}fonts/ directory not found${NC}"
    exit 1
fi

cd fonts
if [ ! -f "download_fonts.sh" ]; then
    echo "${RED}download_fonts.sh not found${NC}"
    exit 1
fi

if [ ! -f "NotoSans-Regular.ttf" ]; then
    echo "Downloading fonts..."
    chmod +x download_fonts.sh
    ./download_fonts.sh
else
    echo "${GREEN}Fonts already present${NC}"
fi
cd ..
echo ""

# Create buildx builder if needed
echo "Setting up buildx builder..."
if ! docker buildx inspect mybuilder > /dev/null 2>&1; then
    docker buildx create --name mybuilder --use
else
    docker buildx use mybuilder
fi
echo ""

# Build and push image
echo "Building and pushing Docker image..."
echo "This may take several minutes..."
docker buildx build \
    --platform linux/amd64 \
    --no-cache \
    -f Dockerfile.do \
    -t "$FULL_IMAGE" \
    --push \
    .

if [ $? -ne 0 ]; then
    echo "${RED}Docker build/push failed${NC}"
    exit 1
fi

echo "${GREEN}Image built and pushed successfully${NC}"
echo ""

echo "=============================================="
echo "${GREEN}Deployment complete!${NC}"
echo "=============================================="
echo ""
echo "Image: $FULL_IMAGE"
echo ""
echo "Next steps on your droplet:"
echo ""
echo "  1. Pull the new image:"
echo "     docker pull $FULL_IMAGE"
echo ""
echo "  2. Update with docker-compose:"
echo "     docker compose pull"
echo "     docker compose up -d"
echo ""
echo "  3. Or run directly:"
echo "     docker stop year-grid-calendar"
echo "     docker rm year-grid-calendar"
echo "     docker run -d --name year-grid-calendar \\"
echo "       --restart unless-stopped \\"
echo "       --network proxy_net \\"
echo "       -e TZ=UTC \\"
echo "       $FULL_IMAGE"
echo ""
echo "  4. Verify:"
echo "     curl http://localhost:8080/health"
echo ""
