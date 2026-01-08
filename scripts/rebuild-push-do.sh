#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Year Grid Calendar - Digital Ocean Rebuild & Push           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
IMAGE_NAME="ceesaxp/year-grid-calendar:latest"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo -e "   Image: ${IMAGE_NAME}"
echo -e "   Platform: linux/amd64"
echo -e "   Dockerfile: Dockerfile.do"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    exit 1
fi

# Check if buildx is available
if ! docker buildx version > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: docker buildx is not available${NC}"
    echo -e "   Run: docker buildx create --use"
    exit 1
fi

# Confirm before proceeding
echo -e "${YELLOW}⚠️  This will rebuild and push ${IMAGE_NAME}${NC}"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted by user${NC}"
    exit 0
fi

# Step 1: Verify the code is fixed
echo ""
echo -e "${YELLOW}🔍 Verifying local code is fixed...${NC}"
if grep -A 5 "async def robots" web/app.py | grep -q "return f"; then
    echo -e "${GREEN}✅ Code verified: Using correct 'return f' pattern${NC}"
else
    echo -e "${RED}❌ WARNING: Code may still have the old pattern${NC}"
    echo -e "${RED}   Expected: return f\"\"\"User-agent: *...${NC}"
    echo -e "${RED}   Check web/app.py around line 756${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Clean old images locally
echo ""
echo -e "${YELLOW}🗑️  Cleaning old local images...${NC}"
docker rmi ${IMAGE_NAME} 2>/dev/null || echo "   No local image to remove"

# Step 3: Build and push with buildx
echo ""
echo -e "${YELLOW}🔨 Building and pushing Docker image...${NC}"
echo -e "   This may take several minutes..."
docker buildx build \
    --platform linux/amd64 \
    --no-cache \
    -f Dockerfile.do \
    -t ${IMAGE_NAME} \
    --push \
    .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build and push failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build and push successful${NC}"

# Step 4: Provide deployment instructions
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ SUCCESS!                                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Image built with fixed code${NC}"
echo -e "${GREEN}✅ Image pushed to Docker Hub${NC}"
echo ""
echo -e "${BLUE}📦 Image: ${IMAGE_NAME}${NC}"
echo ""
echo -e "${YELLOW}🚀 Next steps on your deployment server:${NC}"
echo ""
echo -e "${BLUE}cd /path/to/your/project${NC}"
echo -e "${BLUE}docker compose pull${NC}"
echo -e "${BLUE}docker compose down${NC}"
echo -e "${BLUE}docker compose up -d${NC}"
echo ""
echo -e "Or manually:"
echo ""
echo -e "${BLUE}docker pull ${IMAGE_NAME}${NC}"
echo -e "${BLUE}docker stop year-grid-calendar${NC}"
echo -e "${BLUE}docker rm year-grid-calendar${NC}"
echo -e "${BLUE}docker run -d --name year-grid-calendar \\${NC}"
echo -e "${BLUE}  -p 8080:8080 \\${NC}"
echo -e "${BLUE}  -e BASE_URL=https://year-grid.ceesaxp.org \\${NC}"
echo -e "${BLUE}  ${IMAGE_NAME}${NC}"
echo ""
echo -e "${YELLOW}✓ Verify deployment:${NC}"
echo -e "${BLUE}curl https://year-grid.ceesaxp.org/robots.txt${NC}"
echo ""
echo -e "Expected output should contain:"
echo -e "${GREEN}Sitemap: https://year-grid.ceesaxp.org/sitemap.xml${NC}"
echo ""
echo -e "NOT:"
echo -e "${RED}Sitemap: {BASE_URL}/sitemap.xml${NC}"
echo ""
