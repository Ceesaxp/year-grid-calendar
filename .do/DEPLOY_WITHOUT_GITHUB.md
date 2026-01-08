# Deploy to Digital Ocean Without GitHub

Complete guide to deploy Year Grid Calendar to DO App Platform without connecting GitHub.

## Why This Guide?

If you don't want to connect GitHub to Digital Ocean, you have two options:
1. **Push to Docker Hub** (recommended - covered here)
2. **Use DO Container Registry** (alternative)

## Option 1: Deploy via Docker Hub (Recommended)

### Prerequisites
- Docker installed locally
- Docker Hub account (free at https://hub.docker.com)

### Step 1: Build and Push Image

```bash
# 1. Download fonts first
cd fonts
./download_fonts.sh
cd ..

# 2. Log in to Docker Hub
docker login
# Enter your Docker Hub username and password

# 3. Build the image
docker build -f Dockerfile.do -t YOUR_DOCKERHUB_USERNAME/year-grid-calendar:latest .

# Example:
# docker build -f Dockerfile.do -t ceesaxp/year-grid-calendar:latest .

# 4. Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/year-grid-calendar:latest
```

### Step 2: Create App Spec for Docker Hub

Create `.do/app-dockerhub.yaml`:

```yaml
name: year-grid-calendar

services:
  - name: web
    # Use Docker Hub image
    image:
      registry_type: DOCKER_HUB
      registry: YOUR_DOCKERHUB_USERNAME
      repository: year-grid-calendar
      tag: latest

    # Run configuration
    run_command: uvicorn web.app:app --host 0.0.0.0 --port 8080

    # Environment variables
    envs:
      - key: PORT
        value: "8080"
      - key: PYTHONUNBUFFERED
        value: "1"

    # HTTP configuration
    http_port: 8080

    # Health check
    health_check:
      http_path: /health
      initial_delay_seconds: 20
      period_seconds: 30
      timeout_seconds: 10

    # Instance size
    instance_size_slug: basic-xs
    instance_count: 1

    routes:
      - path: /

# Domain (optional)
domains:
  - domain: year-grid.ceesaxp.org
    type: PRIMARY

region: nyc
```

### Step 3: Deploy to DO

```bash
# Replace YOUR_DOCKERHUB_USERNAME in the file first
sed -i '' 's/YOUR_DOCKERHUB_USERNAME/ceesaxp/g' .do/app-dockerhub.yaml

# Create app
doctl apps create --spec .do/app-dockerhub.yaml

# Get app ID from output
export APP_ID=your-app-id

# Watch deployment
doctl apps logs $APP_ID --follow
```

### Step 4: Updates

When you make changes:

```bash
# 1. Rebuild image
docker build -f Dockerfile.do -t ceesaxp/year-grid-calendar:latest .

# 2. Push to Docker Hub
docker push ceesaxp/year-grid-calendar:latest

# 3. Trigger redeployment on DO
doctl apps create-deployment $APP_ID
```

**Time for updates:** ~5 minutes

---

## Option 2: Digital Ocean Container Registry

### Step 1: Create Container Registry

```bash
# Create registry (one-time, $5/month)
doctl registry create year-grid-calendar

# Log in to DO registry
doctl registry login
```

### Step 2: Build and Push

```bash
# 1. Download fonts
cd fonts && ./download_fonts.sh && cd ..

# 2. Build image
docker build -f Dockerfile.do -t registry.digitalocean.com/year-grid-calendar/app:latest .

# 3. Push to DO registry
docker push registry.digitalocean.com/year-grid-calendar/app:latest
```

### Step 3: Create App Spec

Create `.do/app-registry.yaml`:

```yaml
name: year-grid-calendar

services:
  - name: web
    # Use DO Container Registry
    image:
      registry_type: DOCR
      registry: year-grid-calendar
      repository: app
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
```

### Step 4: Deploy

```bash
# Create app
doctl apps create --spec .do/app-registry.yaml

# Watch deployment
doctl apps logs $APP_ID --follow
```

### Step 5: Updates

```bash
# Rebuild and push
docker build -f Dockerfile.do -t registry.digitalocean.com/year-grid-calendar/app:latest .
docker push registry.digitalocean.com/year-grid-calendar/app:latest

# Redeploy
doctl apps create-deployment $APP_ID
```

**Cost:** +$5/month for Container Registry

---

## Comparison

| Method | Initial Cost | Update Time | Complexity |
|--------|-------------|-------------|------------|
| **Docker Hub** | Free | 5 min | Easy |
| **DO Registry** | +$5/month | 5 min | Easy |
| **GitHub** | Free | Auto | Easiest |

---

## Automated Deployment Script

Save as `deploy-dockerhub.sh`:

```bash
#!/bin/bash
set -e

DOCKERHUB_USER="ceesaxp"
IMAGE_NAME="year-grid-calendar"

echo "🐳 Building and deploying to Docker Hub..."

# Download fonts
cd fonts && ./download_fonts.sh && cd ..

# Build
echo "📦 Building Docker image..."
docker build -f Dockerfile.do -t $DOCKERHUB_USER/$IMAGE_NAME:latest .

# Push
echo "⬆️  Pushing to Docker Hub..."
docker push $DOCKERHUB_USER/$IMAGE_NAME:latest

# Check if app exists
if [ -z "$APP_ID" ]; then
    echo "Creating new app..."
    
    # Create app spec with your username
    cat > .do/app-dockerhub-temp.yaml << EOF
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
    instance_size_slug: basic-xs
    instance_count: 1
    routes:
      - path: /
domains:
  - domain: year-grid.ceesaxp.org
    type: PRIMARY
region: nyc
EOF

    APP_ID=$(doctl apps create --spec .do/app-dockerhub-temp.yaml --format ID --no-header)
    echo "✅ App created: $APP_ID"
    echo "export APP_ID=$APP_ID" > .app_id
else
    echo "🔄 Triggering redeployment..."
    doctl apps create-deployment $APP_ID
fi

echo "✅ Deployment initiated!"
echo "Watch logs: doctl apps logs $APP_ID --follow"
```

Make executable:
```bash
chmod +x deploy-dockerhub.sh
```

Use:
```bash
# First time
./deploy-dockerhub.sh

# Save the APP_ID
export APP_ID=your-app-id-from-output

# Future updates
./deploy-dockerhub.sh
```

---

## Recommended: Docker Hub Method

**Pros:**
- ✅ Free
- ✅ No GitHub needed
- ✅ Works everywhere
- ✅ Easy to automate
- ✅ Can deploy to multiple platforms

**Cons:**
- ⚠️ Manual updates (not automatic on push)
- ⚠️ Extra build/push step

**Best for:**
- Users who don't want GitHub integration
- Testing and development
- Controlled deployments

---

## Quick Start Summary

```bash
# 1. Install Docker (if needed)
# macOS: brew install docker
# Or download from docker.com

# 2. Create Docker Hub account
open https://hub.docker.com

# 3. Build and push
docker login
docker build -f Dockerfile.do -t YOUR_USERNAME/year-grid-calendar:latest .
docker push YOUR_USERNAME/year-grid-calendar:latest

# 4. Update app spec
# Edit .do/app-dockerhub.yaml with your Docker Hub username

# 5. Deploy
doctl apps create --spec .do/app-dockerhub.yaml

# Done! 🎉
```

---

## Troubleshooting

### Docker Build Fails

```bash
# Check Docker is running
docker ps

# Try building without cache
docker build --no-cache -f Dockerfile.do -t username/year-grid-calendar:latest .
```

### Push to Docker Hub Fails

```bash
# Re-login
docker logout
docker login

# Check image name format
docker images | grep year-grid-calendar
```

### DO Can't Pull Image

**Check:**
1. Image is public on Docker Hub
2. Image name matches app spec exactly
3. Tag exists (`latest`)

**Make image public:**
- Go to Docker Hub → Repository Settings
- Set visibility to "Public"

### Font Download Fails During Build

The Dockerfile handles this gracefully with fallback to system fonts. But to ensure fonts are included:

```bash
# Download fonts before building
cd fonts && ./download_fonts.sh && cd ..

# Verify fonts exist
ls fonts/*.ttf

# Then build
docker build -f Dockerfile.do -t username/year-grid-calendar:latest .
```

---

## Cost Comparison

| Method | App Cost | Registry | Total/Month |
|--------|----------|----------|-------------|
| Docker Hub | $12 | Free | **$12** |
| DO Registry | $12 | $5 | **$17** |
| GitHub (auto) | $12 | Free | **$12** |

**Recommendation:** Use Docker Hub for best value without GitHub.

---

## Next Steps

1. Choose Docker Hub or DO Registry
2. Follow the relevant section above
3. Deploy your app
4. Configure domain in DO dashboard
5. Test at https://year-grid.ceesaxp.org

For questions, see the main `DEPLOY_DIGITALOCEAN.md` guide.
