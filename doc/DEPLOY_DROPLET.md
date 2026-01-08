# Deploy to Digital Ocean Droplet from Container Registry

Complete guide for building, pushing to DO Container Registry, and deploying to your droplet.

## Overview

This method gives you full control while using DO's managed container registry:

```
Local → Build Image → Push to DOCR → Pull on Droplet → Run Container
```

**Benefits:**
- ✅ Private container registry
- ✅ Full control over deployment
- ✅ Use existing droplet infrastructure
- ✅ No vendor lock-in
- ✅ Lower cost than App Platform for multiple services

**Cost:**
- Container Registry: $5/month (20GB storage)
- Droplet: $6-10/month (your existing cost)
- **Total: $11-15/month** (vs $12+ for App Platform)

## Prerequisites

- Digital Ocean account with Container Registry enabled
- Droplet with Docker installed
- `doctl` CLI installed locally

## Part 1: Setup Container Registry (One-Time)

### Step 1: Create Container Registry

**Via Dashboard:**
1. Go to https://cloud.digitalocean.com/registry
2. Click **"Create Registry"**
3. Choose plan: **Basic ($5/month)**
4. Name: `year-grid-calendar`
5. Region: Choose closest to your droplet
6. Click **"Create"**

**Via CLI:**
```bash
doctl registry create year-grid-calendar --subscription-tier basic
```

### Step 2: Authenticate Docker Locally

```bash
# Login to DOCR
doctl registry login

# Verify
doctl registry get
```

Expected output:
```
Name                  Endpoint                                    Created At
year-grid-calendar    registry.digitalocean.com/year-grid-calendar    2024-01-08
```

### Step 3: Get Registry Credentials for Droplet

Your registry URL will be:
```
registry.digitalocean.com/year-grid-calendar
```

## Part 2: Build and Push Image

### Build Image Locally

```bash
cd year-grid-calendar

# Download fonts first
cd fonts && ./download_fonts.sh && cd ..

# Build image with DOCR tag
docker build -f Dockerfile.do \
  -t registry.digitalocean.com/year-grid-calendar/app:latest \
  -t registry.digitalocean.com/year-grid-calendar/app:v1.0 \
  .

# Check image was created
docker images | grep year-grid-calendar
```

**Output:**
```
registry.digitalocean.com/year-grid-calendar/app   latest   abc123   2 minutes ago   450MB
registry.digitalocean.com/year-grid-calendar/app   v1.0     abc123   2 minutes ago   450MB
```

### Push to Container Registry

```bash
# Push latest tag
docker push registry.digitalocean.com/year-grid-calendar/app:latest

# Push version tag (recommended for rollbacks)
docker push registry.digitalocean.com/year-grid-calendar/app:v1.0
```

**Time:** 2-5 minutes depending on upload speed

### Verify Upload

```bash
# List repositories
doctl registry repository list

# List tags
doctl registry repository list-tags year-grid-calendar/app
```

Expected:
```
TAG       COMPRESSED SIZE    UPDATED AT
latest    150 MB             2024-01-08 12:00:00
v1.0      150 MB             2024-01-08 12:00:00
```

## Part 3: Setup Droplet

### Step 1: SSH to Droplet

```bash
ssh root@your-droplet-ip
```

### Step 2: Install Docker (if not installed)

```bash
# Update packages
apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify
docker --version
```

### Step 3: Install doctl on Droplet

```bash
# Download doctl
cd /tmp
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz

# Extract
tar xf doctl-*.tar.gz

# Move to PATH
mv doctl /usr/local/bin/

# Verify
doctl version
```

### Step 4: Authenticate Droplet to DOCR

**Method A: Using API Token (Recommended)**

```bash
# Get API token from: https://cloud.digitalocean.com/account/api/tokens
doctl auth init

# Login Docker to DOCR
doctl registry login

# Verify access
docker pull registry.digitalocean.com/year-grid-calendar/app:latest
```

**Method B: Using Registry Token (More Secure)**

Create a read-only registry token:

```bash
# On local machine
doctl registry kubernetes-manifest | grep dockerconfigjson | awk '{print $2}' | base64 -d

# Copy the output, then on droplet:
docker login registry.digitalocean.com -u <username> -p <password>
```

## Part 4: Deploy with Docker Compose

### Create Deployment Directory

```bash
mkdir -p /opt/year-grid-calendar
cd /opt/year-grid-calendar
```

### Create docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  calendar:
    image: registry.digitalocean.com/year-grid-calendar/app:latest
    container_name: year-grid-calendar
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - PYTHONUNBUFFERED=1
      - TZ=UTC
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - shared_net
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  shared_net:
    external: true
EOF
```

### Create Network (if not exists)

```bash
docker network create shared_net || true
```

### Deploy Application

```bash
# Pull latest image
docker-compose pull

# Start service
docker-compose up -d

# View logs
docker-compose logs -f
```

## Part 5: Setup Caddy Reverse Proxy

### Install Caddy (if not installed)

```bash
# Install Caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install caddy
```

### Configure Caddy

```bash
# Edit Caddyfile
nano /etc/caddy/Caddyfile
```

Add:
```
year-grid.ceesaxp.org {
    reverse_proxy year-grid-calendar:8080
    
    encode gzip zstd
    
    header {
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
    }
    
    log {
        output file /var/log/caddy/year-grid-calendar.log
    }
}
```

### Reload Caddy

```bash
systemctl reload caddy
```

## Part 6: Updates and Maintenance

### Update Application

**On your local machine:**

```bash
# 1. Make changes to code
git pull  # or make local changes

# 2. Build new version
docker build -f Dockerfile.do \
  -t registry.digitalocean.com/year-grid-calendar/app:latest \
  -t registry.digitalocean.com/year-grid-calendar/app:v1.1 \
  .

# 3. Push to registry
docker push registry.digitalocean.com/year-grid-calendar/app:latest
docker push registry.digitalocean.com/year-grid-calendar/app:v1.1
```

**On your droplet:**

```bash
cd /opt/year-grid-calendar

# Pull latest image
docker-compose pull

# Restart with new image
docker-compose up -d

# Check logs
docker-compose logs -f
```

**Total update time:** 2-3 minutes

### Automated Update Script

Create `/opt/year-grid-calendar/update.sh`:

```bash
cat > /opt/year-grid-calendar/update.sh << 'EOF'
#!/bin/bash
set -e

echo "🔄 Updating Year Grid Calendar..."

cd /opt/year-grid-calendar

# Authenticate to registry
doctl registry login

# Pull latest image
echo "📥 Pulling latest image..."
docker-compose pull

# Restart service
echo "🔄 Restarting service..."
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for health check..."
sleep 5

# Check health
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Update successful!"
    echo "📊 Service status:"
    docker-compose ps
else
    echo "❌ Health check failed!"
    echo "Rolling back..."
    docker-compose down
    exit 1
fi

echo "🎉 Done!"
EOF

chmod +x /opt/year-grid-calendar/update.sh
```

Usage:
```bash
/opt/year-grid-calendar/update.sh
```

### Rollback to Previous Version

```bash
cd /opt/year-grid-calendar

# Stop current version
docker-compose down

# Update docker-compose.yml to use specific version
sed -i 's/:latest/:v1.0/' docker-compose.yml

# Start old version
docker-compose up -d

# Verify
curl http://localhost:8080/health
```

## Part 7: Monitoring

### View Logs

```bash
# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f calendar
```

### Check Status

```bash
# Container status
docker-compose ps

# Health check
curl http://localhost:8080/health

# Resource usage
docker stats year-grid-calendar
```

### Log Rotation

Configured in docker-compose.yml:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

Logs automatically rotate at 10MB, keeping 3 files.

## Part 8: Backup and Recovery

### Backup Configuration

```bash
# Backup deployment files
tar -czf year-grid-calendar-backup-$(date +%Y%m%d).tar.gz \
  /opt/year-grid-calendar/docker-compose.yml \
  /etc/caddy/Caddyfile

# Store securely
mv year-grid-calendar-backup-*.tar.gz ~/backups/
```

### Recovery

```bash
# Extract backup
tar -xzf year-grid-calendar-backup-20240108.tar.gz

# Pull image from registry
cd /opt/year-grid-calendar
docker-compose pull

# Start service
docker-compose up -d
```

## Part 9: Security Best Practices

### Firewall Setup

```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Block direct access to app port
ufw deny 8080/tcp

# Enable firewall
ufw enable
```

### Registry Access Control

**Create Read-Only Token:**

1. Go to: https://cloud.digitalocean.com/registry/year-grid-calendar
2. Click **"Manage"** → **"Tokens"**
3. Create token with **"Read"** access only
4. Use this token on production droplets

### Auto-Updates (Optional)

Create cron job for automatic pulls:

```bash
# Edit crontab
crontab -e

# Add (checks for updates daily at 3 AM)
0 3 * * * cd /opt/year-grid-calendar && doctl registry login && docker-compose pull && docker-compose up -d
```

## Part 10: Multiple Environments

### Production vs Staging

**Use different tags:**

```bash
# Production uses stable versions
image: registry.digitalocean.com/year-grid-calendar/app:v1.0

# Staging uses latest
image: registry.digitalocean.com/year-grid-calendar/app:latest
```

**Separate droplets:**
- production.ceesaxp.org → droplet-prod
- staging.ceesaxp.org → droplet-staging

## Troubleshooting

### "unauthorized: authentication required"

**Problem:** Can't pull from registry

**Solution:**
```bash
# Re-authenticate
doctl auth init
doctl registry login

# Try pull again
docker-compose pull
```

### "connection refused" on health check

**Problem:** App not responding

**Solutions:**
```bash
# Check logs
docker-compose logs -f

# Check if container is running
docker ps -a

# Restart
docker-compose restart

# Check port binding
netstat -tlnp | grep 8080
```

### Image pull is slow

**Problem:** Large image download

**Solutions:**
1. Use same region for registry and droplet
2. Compress image layers better
3. Use image caching
4. Remove unnecessary files from image

## Cost Breakdown

**Monthly Costs:**
```
Container Registry (Basic):  $5
Droplet (2GB RAM):          $12
Domain (yearly):            $12/12 = $1
-----------------
Total:                      $18/month
```

**Compare to App Platform:**
```
Basic XS:                   $12
-----------------
Total:                      $12/month
```

**Droplet advantages for $6 extra:**
- Host multiple apps
- Full SSH access
- More flexibility
- Better for learning

## Automation Script

Create `/usr/local/bin/deploy-calendar`:

```bash
cat > /usr/local/bin/deploy-calendar << 'EOF'
#!/bin/bash
# Deploy Year Grid Calendar from DOCR
# Usage: deploy-calendar [version]

VERSION=${1:-latest}
REGISTRY="registry.digitalocean.com/year-grid-calendar/app"

echo "🚀 Deploying Year Grid Calendar version: $VERSION"

# Authenticate
doctl registry login

# Pull specific version
docker pull $REGISTRY:$VERSION

# Tag as latest
docker tag $REGISTRY:$VERSION $REGISTRY:latest

# Update deployment
cd /opt/year-grid-calendar
docker-compose up -d

# Health check
sleep 5
curl -f http://localhost:8080/health && echo "✅ Deployed!" || echo "❌ Failed!"
EOF

chmod +x /usr/local/bin/deploy-calendar
```

Usage:
```bash
# Deploy latest
deploy-calendar

# Deploy specific version
deploy-calendar v1.0
```

## Quick Reference

### Common Commands

```bash
# Build and push
docker build -f Dockerfile.do -t registry.digitalocean.com/year-grid-calendar/app:latest .
docker push registry.digitalocean.com/year-grid-calendar/app:latest

# On droplet - deploy
cd /opt/year-grid-calendar
doctl registry login
docker-compose pull
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
curl http://localhost:8080/health

# Update
docker-compose pull
docker-compose up -d

# Rollback
docker-compose down
sed -i 's/:latest/:v1.0/' docker-compose.yml
docker-compose up -d
```

## Summary

**Workflow:**
1. Local: Build image
2. Local: Push to DOCR
3. Droplet: Pull from DOCR
4. Droplet: Run with docker-compose
5. Caddy: Reverse proxy with SSL

**Benefits over App Platform:**
- More control
- Host multiple apps
- Lower cost per app
- Better for learning
- No vendor lock-in

**Benefits over direct Docker Hub:**
- Private registry
- Faster in same region
- Integrated with DO
- Better security

This setup gives you the best of both worlds: managed registry + full control! 🚀
