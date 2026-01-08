#!/bin/bash
set -e

# Year Grid Calendar - Deployment Script
# This script helps deploy the calendar web service with Caddy integration

echo "🗓️  Year Grid Calendar Deployment"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to check if network exists
network_exists() {
    docker network inspect shared_net &> /dev/null
}

# Step 1: Create shared network if it doesn't exist
echo "📡 Checking for shared_net network..."
if network_exists; then
    echo "✅ Network 'shared_net' already exists"
else
    echo "📡 Creating 'shared_net' network..."
    docker network create shared_net
    echo "✅ Network created"
fi
echo ""

# Step 2: Build and start the service
echo "🐳 Building and starting the calendar service..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for service to be healthy..."
sleep 5

# Step 3: Check if service is running
if docker ps | grep -q year-grid-calendar; then
    echo "✅ Container is running"
else
    echo "❌ Container failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Step 4: Test health endpoint
echo ""
echo "🏥 Testing health endpoint..."
for i in {1..10}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Service is healthy"
        break
    else
        if [ $i -eq 10 ]; then
            echo "❌ Service health check failed after 10 attempts"
            echo "Check logs with: docker-compose logs calendar-web"
            exit 1
        fi
        echo "⏳ Waiting for service... (attempt $i/10)"
        sleep 3
    fi
done

# Step 5: Display status
echo ""
echo "✅ Deployment successful!"
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose ps
echo ""

# Step 6: Show next steps
echo "🎉 Next Steps:"
echo "=============="
echo ""
echo "1. Configure Caddy to proxy to the service:"
echo "   Add the contents of 'Caddyfile' to your Caddy configuration"
echo "   Then reload: docker exec caddy caddy reload --config /etc/caddy/Caddyfile"
echo ""
echo "2. Test the service locally:"
echo "   curl http://localhost:8000/health"
echo "   Or visit: http://localhost:8000"
echo ""
echo "3. Access via domain (after Caddy config):"
echo "   https://year-grid.ceesaxp.org"
echo ""
echo "4. View logs:"
echo "   docker-compose logs -f calendar-web"
echo ""
echo "5. Stop service:"
echo "   docker-compose down"
echo ""
echo "📚 For detailed information, see DEPLOYMENT.md"
echo ""
