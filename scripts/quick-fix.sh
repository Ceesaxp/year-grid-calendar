#!/bin/bash
# Quick fix script - rebuilds and tests locally

set -e

echo "🔧 Quick Fix: Testing Docker image locally"
echo "============================================"

# Get Docker username
read -p "Enter your Docker Hub username: " DOCKER_USERNAME

# Build
echo "📦 Building image..."
docker build -t ${DOCKER_USERNAME}/year-grid-calendar:latest -f web/Dockerfile . > /dev/null 2>&1

# Test
echo "🧪 Testing with BASE_URL=https://year-grid.ceesaxp.org"
docker run -d --name test-fix -p 9999:8000 -e BASE_URL=https://year-grid.ceesaxp.org ${DOCKER_USERNAME}/year-grid-calendar:latest > /dev/null 2>&1
sleep 3

RESULT=$(docker exec test-fix curl -s http://localhost:8000/robots.txt)

docker stop test-fix > /dev/null 2>&1
docker rm test-fix > /dev/null 2>&1

echo ""
echo "📄 robots.txt output:"
echo "--------------------"
echo "$RESULT"
echo ""

if echo "$RESULT" | grep -q "https://year-grid.ceesaxp.org/sitemap.xml"; then
    echo "✅ SUCCESS! BASE_URL is working correctly"
    echo ""
    echo "Next steps:"
    echo "  1. Push to Docker Hub:"
    echo "     docker push ${DOCKER_USERNAME}/year-grid-calendar:latest"
    echo ""
    echo "  2. On your server, run:"
    echo "     docker pull ${DOCKER_USERNAME}/year-grid-calendar:latest --no-cache"
    echo "     docker stop year-grid-calendar && docker rm year-grid-calendar"
    echo "     docker run -d --name year-grid-calendar -p 8000:8000 \\"
    echo "       -e BASE_URL=https://year-grid.ceesaxp.org \\"
    echo "       ${DOCKER_USERNAME}/year-grid-calendar:latest"
else
    echo "❌ FAILED! BASE_URL is not being substituted"
    echo "Please check the web/app.py file"
fi
