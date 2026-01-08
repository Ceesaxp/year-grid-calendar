#!/bin/bash
# Quick deployment script for Digital Ocean App Platform
# Year Grid Calendar

set -e

echo "🚀 Digital Ocean App Platform Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}❌ doctl CLI not found${NC}"
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install doctl"
    echo "  Linux:   wget https://github.com/digitalocean/doctl/releases/latest/download/doctl-*-linux-amd64.tar.gz"
    echo "  Windows: choco install doctl"
    echo ""
    exit 1
fi

# Check authentication
echo "🔑 Checking authentication..."
if ! doctl auth list &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated with Digital Ocean${NC}"
    echo ""
    echo "Please authenticate:"
    echo "  1. Get API token from: https://cloud.digitalocean.com/account/api/tokens"
    echo "  2. Run: doctl auth init"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Authenticated${NC}"
echo ""

# Check GitHub connection
echo "🔗 Checking GitHub connection..."
if doctl apps list-regions &> /dev/null; then
    echo -e "${GREEN}✅ API access working${NC}"
else
    echo -e "${RED}❌ API access failed${NC}"
    exit 1
fi
echo ""

# Download fonts
echo "📦 Setting up fonts..."
if [ ! -f "fonts/download_fonts.sh" ]; then
    echo -e "${RED}❌ fonts/download_fonts.sh not found${NC}"
    exit 1
fi

cd fonts
if [ ! -f "NotoSans-Regular.ttf" ]; then
    echo "📥 Downloading fonts..."
    chmod +x download_fonts.sh
    ./download_fonts.sh
    echo -e "${GREEN}✅ Fonts downloaded${NC}"
else
    echo -e "${GREEN}✅ Fonts already present${NC}"
fi
cd ..
echo ""

# Check if app spec exists
if [ ! -f ".do/app.yaml" ]; then
    echo -e "${RED}❌ .do/app.yaml not found${NC}"
    exit 1
fi

# Ask user for deployment method
echo "Choose deployment method:"
echo "  1) Create new app (with GitHub integration)"
echo "  2) Create new app (without GitHub - manual updates)"
echo "  3) Update existing app"
echo "  4) Validate app spec only"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📋 Creating new app from spec..."
        echo ""

        # Check if GitHub is connected
        echo "⚠️  This requires GitHub to be connected to your Digital Ocean account."
        echo ""
        echo "If you haven't connected GitHub yet:"
        echo "  1. Go to: https://cloud.digitalocean.com/apps"
        echo "  2. Click 'Create App'"
        echo "  3. Select 'GitHub' and authorize"
        echo "  4. Then come back and run this script again"
        echo ""
        read -p "Have you connected GitHub? (y/N): " github_ready

        if [[ ! $github_ready =~ ^[Yy]$ ]]; then
            echo ""
            echo "Choose option 2 to deploy without GitHub integration."
            exit 0
        fi

        echo "Creating app with GitHub integration..."
        APP_ID=$(doctl apps create --spec .do/app.yaml --format ID --no-header 2>&1)

        if [ -z "$APP_ID" ] || [[ "$APP_ID" == *"error"* ]] || [[ "$APP_ID" == *"Error"* ]]; then
            echo -e "${RED}❌ Failed to create app${NC}"
            echo "$APP_ID"
            echo ""
            echo "Common issues:"
            echo "  - GitHub not connected: Use option 2 for non-GitHub deployment"
            echo "  - Invalid app spec: Use option 4 to validate"
            echo "  - Permissions: Check your DO API token permissions"
            exit 1
        fi

        echo -e "${GREEN}✅ App created successfully!${NC}"
        echo ""
        echo "App ID: $APP_ID"
        echo ""
        echo "View your app:"
        echo "  Dashboard: https://cloud.digitalocean.com/apps/$APP_ID"
        echo "  CLI: doctl apps get $APP_ID"
        echo ""
        echo "Watch deployment logs:"
        echo "  doctl apps logs $APP_ID --follow"
        echo ""

        read -p "Watch logs now? (y/N): " watch_logs
        if [[ $watch_logs =~ ^[Yy]$ ]]; then
            doctl apps logs $APP_ID --follow
        fi
        ;;

    2)
        echo ""
        echo "📦 Creating app WITHOUT GitHub integration..."
        echo ""
        echo "This will deploy from your local files."
        echo "Updates will need to be pushed manually or via image registry."
        echo ""

        if [ ! -f ".do/app-no-github.yaml" ]; then
            echo -e "${RED}❌ .do/app-no-github.yaml not found${NC}"
            exit 1
        fi

        echo "Creating app..."
        APP_ID=$(doctl apps create --spec .do/app-no-github.yaml --format ID --no-header 2>&1)

        if [ -z "$APP_ID" ] || [[ "$APP_ID" == *"error"* ]] || [[ "$APP_ID" == *"Error"* ]]; then
            echo -e "${RED}❌ Failed to create app${NC}"
            echo "$APP_ID"
            exit 1
        fi

        echo -e "${GREEN}✅ App created successfully!${NC}"
        echo ""
        echo "App ID: $APP_ID"
        echo ""
        echo "⚠️  Note: Without GitHub integration, you'll need to:"
        echo "  - Manually trigger deployments via CLI or dashboard"
        echo "  - Or set up an image registry workflow"
        echo ""
        echo "View your app:"
        echo "  Dashboard: https://cloud.digitalocean.com/apps/$APP_ID"
        echo "  CLI: doctl apps get $APP_ID"
        echo ""
        echo "Watch deployment logs:"
        echo "  doctl apps logs $APP_ID --follow"
        echo ""

        read -p "Watch logs now? (y/N): " watch_logs
        if [[ $watch_logs =~ ^[Yy]$ ]]; then
            doctl apps logs $APP_ID --follow
        fi
        ;;

    3)
        echo ""
        echo "📋 Listing your apps..."
        doctl apps list
        echo ""
        read -p "Enter App ID to update: " APP_ID

        if [ -z "$APP_ID" ]; then
            echo -e "${RED}❌ App ID required${NC}"
            exit 1
        fi

        echo ""
        echo "Updating app $APP_ID..."
        doctl apps update $APP_ID --spec .do/app.yaml

        echo -e "${GREEN}✅ App updated successfully!${NC}"
        echo ""
        echo "Watch deployment logs:"
        echo "  doctl apps logs $APP_ID --follow"
        echo ""

        read -p "Watch logs now? (y/N): " watch_logs
        if [[ $watch_logs =~ ^[Yy]$ ]]; then
            doctl apps logs $APP_ID --follow
        fi
        ;;

    4)
        echo ""
        echo "🔍 Validating app spec..."

        # Use apps spec validate if available
        if doctl apps spec validate --help &> /dev/null; then
            doctl apps spec validate .do/app.yaml
            echo -e "${GREEN}✅ App spec is valid${NC}"
        else
            echo -e "${YELLOW}⚠️  Validation command not available, skipping${NC}"
        fi
        ;;

    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Deployment process complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Wait for deployment to complete (5-10 minutes)"
echo "  2. Configure your domain in DO dashboard"
echo "  3. Test your app at the provided URL"
echo ""
echo "Useful commands:"
echo "  View app:    doctl apps get $APP_ID"
echo "  View logs:   doctl apps logs $APP_ID --follow"
echo "  Redeploy:    doctl apps create-deployment $APP_ID"
echo "  List apps:   doctl apps list"
echo ""
echo "Documentation:"
echo "  📖 DEPLOY_DIGITALOCEAN.md"
echo ""
