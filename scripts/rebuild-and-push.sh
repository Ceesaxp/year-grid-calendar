#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Year Grid Calendar - Docker Rebuild & Push Script         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-your-dockerhub-username}"
IMAGE_NAME="year-grid-calendar"
VERSION="${VERSION:-latest}"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo -e "   Docker Hub Username: ${DOCKER_USERNAME}"
echo -e "   Image Name: ${IMAGE_NAME}"
echo -e "   Version: ${VERSION}"
echo -e "   Full Image: ${FULL_IMAGE_NAME}"
echo ""

# Confirm before proceeding
read -p "Continue with rebuild and push? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Aborted by user${NC}"
    exit 0
fi

# Step 1: Remove old local images
echo -e "${YELLOW}🗑️  Removing old local images...${NC}"
docker rmi ${FULL_IMAGE_NAME} 2>/dev/null || echo "   No local image to remove"
docker rmi ${DOCKER_USERNAME}/${IMAGE_NAME} 2>/dev/null || echo "   No untagged image to remove"

# Step 2: Build new image
echo ""
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t ${FULL_IMAGE_NAME} -f web/Dockerfile .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"

# Step 3: Tag latest
echo ""
echo -e "${YELLOW}🏷️  Tagging image as latest...${NC}"
docker tag ${FULL_IMAGE_NAME} ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

# Step 4: Test the image locally
echo ""
echo -e "${YELLOW}🧪 Testing image locally...${NC}"
TEST_CONTAINER="test-${IMAGE_NAME}-$$"
docker run -d --name ${TEST_CONTAINER} -p 8888:8000 -e BASE_URL=https://test.example.com ${FULL_IMAGE_NAME}

echo "   Waiting for container to start..."
sleep 3

# Test robots.txt
ROBOTS_RESPONSE=$(docker exec ${TEST_CONTAINER} curl -s http://localhost:8000/robots.txt)
if echo "$ROBOTS_RESPONSE" | grep -q "https://test.example.com/sitemap.xml"; then
    echo -e "${GREEN}   ✅ robots.txt BASE_URL substitution working${NC}"
else
    echo -e "${RED}   ❌ robots.txt BASE_URL substitution NOT working${NC}"
    echo "   Response: $ROBOTS_RESPONSE"
    docker stop ${TEST_CONTAINER} > /dev/null
    docker rm ${TEST_CONTAINER} > /dev/null
    exit 1
fi

# Test sitemap.xml
SITEMAP_RESPONSE=$(docker exec ${TEST_CONTAINER} curl -s http://localhost:8000/sitemap.xml)
if echo "$SITEMAP_RESPONSE" | grep -q "https://test.example.com"; then
    echo -e "${GREEN}   ✅ sitemap.xml BASE_URL substitution working${NC}"
else
    echo -e "${RED}   ❌ sitemap.xml BASE_URL substitution NOT working${NC}"
    echo "   Response: $SITEMAP_RESPONSE"
    docker stop ${TEST_CONTAINER} > /dev/null
    docker rm ${TEST_CONTAINER} > /dev/null
    exit 1
fi

# Cleanup test container
docker stop ${TEST_CONTAINER} > /dev/null
docker rm ${TEST_CONTAINER} > /dev/null

echo -e "${GREEN}✅ All tests passed${NC}"

# Step 5: Login to Docker Hub
echo ""
echo -e "${YELLOW}🔐 Logging in to Docker Hub...${NC}"
if [ -z "${DOCKER_PASSWORD}" ]; then
    docker login
else
    echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker login failed!${NC}"
    exit 1
fi

# Step 6: Push to Docker Hub
echo ""
echo -e "${YELLOW}📤 Pushing image to Docker Hub...${NC}"
docker push ${FULL_IMAGE_NAME}
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Push failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ SUCCESS!                                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Image built successfully${NC}"
echo -e "${GREEN}✅ Tests passed${NC}"
echo -e "${GREEN}✅ Image pushed to Docker Hub${NC}"
echo ""
echo -e "${BLUE}📦 Image available at: ${FULL_IMAGE_NAME}${NC}"
echo ""
echo -e "${YELLOW}🚀 Next steps on your deployment server:${NC}"
echo ""
echo -e "   1. Pull the new image:"
echo -e "      ${BLUE}docker pull ${FULL_IMAGE_NAME}${NC}"
echo ""
echo -e "   2. Stop and remove old container:"
echo -e "      ${BLUE}docker stop year-grid-calendar${NC}"
echo -e "      ${BLUE}docker rm year-grid-calendar${NC}"
echo ""
echo -e "   3. Run with your BASE_URL:"
echo -e "      ${BLUE}docker run -d --name year-grid-calendar \\${NC}"
echo -e "      ${BLUE}  -p 8000:8000 \\${NC}"
echo -e "      ${BLUE}  -e BASE_URL=https://year-grid.ceesaxp.org \\${NC}"
echo -e "      ${BLUE}  ${FULL_IMAGE_NAME}${NC}"
echo ""
echo -e "   Or use docker-compose:"
echo -e "      ${BLUE}docker-compose pull${NC}"
echo -e "      ${BLUE}docker-compose up -d${NC}"
echo ""
echo -e "   4. Verify it works:"
echo -e "      ${BLUE}curl https://year-grid.ceesaxp.org/robots.txt${NC}"
echo ""
