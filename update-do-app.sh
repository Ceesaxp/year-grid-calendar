#!/bin/bash
# Update existing Digital Ocean App Platform deployment
# Fixes branch name and removes conflicting run_command

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔧 Updating Digital Ocean App Configuration"
echo "============================================"
echo ""

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}❌ doctl not found${NC}"
    echo "Install with: brew install doctl"
    exit 1
fi

# Get APP_ID
if [ -f ".app_id" ]; then
    source .app_id
fi

if [ -z "$APP_ID" ]; then
    echo "Enter your App ID (find it in DO dashboard or run: doctl apps list)"
    read -p "App ID: " APP_ID

    if [ -z "$APP_ID" ]; then
        echo -e "${RED}❌ App ID required${NC}"
        exit 1
    fi

    # Save for future use
    echo "export APP_ID=$APP_ID" > .app_id
fi

echo "App ID: $APP_ID"
echo ""

# Detect git branch
BRANCH=$(git branch --show-current)
if [ -z "$BRANCH" ]; then
    BRANCH="master"
fi

echo "Detected git branch: $BRANCH"
echo ""

# Create updated app spec
echo "📝 Creating updated app spec..."
cat > /tmp/app-update.yaml << EOF
name: year-grid-calendar

services:
  - name: web
    dockerfile_path: Dockerfile.do

    github:
      repo: ceesaxp/year-grid-calendar
      branch: $BRANCH
      deploy_on_push: true

    envs:
      - key: PORT
        value: "8080"
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: TZ
        value: "UTC"

    http_port: 8080

    health_check:
      http_path: /health
      initial_delay_seconds: 20
      period_seconds: 30
      timeout_seconds: 10
      success_threshold: 1
      failure_threshold: 3

    instance_size_slug: basic-xs
    instance_count: 1

    routes:
      - path: /

domains:
  - domain: year-grid.ceesaxp.org
    type: PRIMARY
    zone: ceesaxp.org

region: nyc

alerts:
  - rule: DEPLOYMENT_FAILED
  - rule: DOMAIN_FAILED

features:
  - buildpack-stack=ubuntu-22
EOF

echo "✅ App spec created"
echo ""

# Update app
echo "🔄 Updating app configuration..."
doctl apps update $APP_ID --spec /tmp/app-update.yaml

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Update failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ App configuration updated${NC}"
echo ""

# Trigger new deployment
echo "🚀 Triggering new deployment..."
doctl apps create-deployment $APP_ID

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed to trigger${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deployment triggered${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Update complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "The app will now:"
echo "  1. Use branch: $BRANCH"
echo "  2. Use Dockerfile CMD (not run_command)"
echo "  3. Start deployment"
echo ""
echo "Watch deployment:"
echo "  doctl apps logs $APP_ID --follow"
echo ""
echo "Check status:"
echo "  doctl apps get $APP_ID"
echo ""
echo "View in dashboard:"
echo "  https://cloud.digitalocean.com/apps/$APP_ID"
echo ""

# Ask if user wants to watch logs
read -p "Watch deployment logs now? (y/N): " watch
if [[ $watch =~ ^[Yy]$ ]]; then
    echo ""
    echo "📋 Watching logs (Ctrl+C to stop)..."
    echo ""
    doctl apps logs $APP_ID --follow
fi
