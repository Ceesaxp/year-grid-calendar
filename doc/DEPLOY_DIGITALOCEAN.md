# Digital Ocean App Platform Deployment Guide

Complete guide to deploying Year Grid Calendar on Digital Ocean's App Platform.

## Overview

Digital Ocean App Platform is a Platform-as-a-Service (PaaS) that:
- ✅ Automatically builds and deploys from Git
- ✅ Provides free SSL/HTTPS
- ✅ Handles load balancing and scaling
- ✅ No need for Caddy or manual reverse proxy setup
- ✅ Simple domain configuration
- ✅ Built-in monitoring and alerts

**Pricing**: Starts at $5/month for Basic plan

## Prerequisites

- Digital Ocean account
- Git repository (GitHub, GitLab, or Bitbucket)
- Domain name (optional, DO provides free subdomain)
- Credit card for DO billing

## Architecture

```
Internet → DO App Platform (SSL/LB) → Your App Container → PDF Generation
```

**Key Differences from Self-Hosted:**
- No Caddy needed (DO handles reverse proxy)
- No Docker Compose needed (DO manages containers)
- No manual SSL setup (automatic with Let's Encrypt)
- No server management needed

## Deployment Options

### Option 1: Deploy from GitHub/GitLab (Recommended)

**Pros:**
- Automatic deployments on git push
- Easy rollbacks
- Built-in CI/CD
- Version control

**Cons:**
- Requires public or connected private repo

### Option 2: Deploy via CLI

**Pros:**
- No GitHub account needed
- Quick one-off deployments

**Cons:**
- Manual updates required
- No automatic deployments

### Option 3: Deploy from Docker Hub

**Pros:**
- Pre-built images
- Fast deployments

**Cons:**
- Extra step to push images

## Step-by-Step Deployment

### Method A: Deploy from GitHub (Easiest)

#### 1. Prepare Your Repository

```bash
# Push your code to GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/year-grid-calendar.git
git push -u origin main
```

#### 2. Create App on Digital Ocean

**Via Web Console:**

1. Log in to [Digital Ocean](https://cloud.digitalocean.com)
2. Click **Apps** → **Create App**
3. Select **GitHub** as source
4. Authorize Digital Ocean to access your repos
5. Select `year-grid-calendar` repository
6. Select `main` branch
7. Click **Next**

#### 3. Configure Build Settings

**Dockerfile Path:**
```
Dockerfile.do
```

**Build Command:**
```bash
cd fonts && chmod +x download_fonts.sh && ./download_fonts.sh || true
```

**Run Command:**
```bash
uvicorn web.app:app --host 0.0.0.0 --port 8080
```

**HTTP Port:**
```
8080
```

#### 4. Configure Environment Variables

Add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `PORT` | `8080` | Port to bind to |
| `PYTHONUNBUFFERED` | `1` | Python logging |
| `TZ` | `UTC` | Timezone |

#### 5. Configure Resources

**Instance Size:**
- **Development**: Basic XXS ($5/month) - Good for testing
- **Production**: Basic XS ($12/month) - Recommended for real use
- **High Traffic**: Basic S ($24/month) or higher

**Instance Count:**
- Start with 1
- Enable auto-scaling if needed (Professional plans)

#### 6. Configure Domain

**Option A: Use DO Subdomain (Free)**
- DO provides: `your-app-name.ondigitalocean.app`
- SSL included automatically
- No DNS setup needed

**Option B: Use Custom Domain**

1. In App Platform settings, click **Add Domain**
2. Enter: `year-grid.ceesaxp.org`
3. DO will provide CNAME or A records
4. Add to your DNS provider:

```
Type: CNAME
Name: year-grid
Value: [provided by DO]
TTL: 3600
```

Or for root domain:
```
Type: A
Name: @
Value: [IP provided by DO]
TTL: 3600
```

5. Wait for DNS propagation (5-60 minutes)
6. SSL certificate auto-provisions

#### 7. Deploy!

Click **Create Resources** → App Platform will:
1. Clone your repository
2. Build Docker image using `Dockerfile.do`
3. Download fonts during build
4. Deploy container
5. Configure SSL/HTTPS
6. Provide URL

**First deployment takes 5-10 minutes.**

#### 8. Verify Deployment

**Check Health:**
```bash
curl https://year-grid.ceesaxp.org/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "bundled_fonts": 15,
  "total_fonts": 18
}
```

**Test in Browser:**
```
https://year-grid.ceesaxp.org
```

### Method B: Deploy via CLI

#### 1. Install doctl

**macOS:**
```bash
brew install doctl
```

**Linux:**
```bash
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
tar xf doctl-*.tar.gz
sudo mv doctl /usr/local/bin
```

**Windows:**
```powershell
choco install doctl
```

#### 2. Authenticate

```bash
# Get API token from: https://cloud.digitalocean.com/account/api/tokens
doctl auth init
```

#### 3. Create App Spec

The app spec is already in `.do/app.yaml`. Update it:

```bash
# Edit .do/app.yaml
# Update the GitHub repo or remove GitHub section for local deploy
```

#### 4. Deploy

```bash
# Deploy from app spec
doctl apps create --spec .do/app.yaml

# Get app ID from output
export APP_ID=your-app-id

# Watch deployment
doctl apps logs $APP_ID --follow
```

#### 5. Update App

```bash
# Update existing app
doctl apps update $APP_ID --spec .do/app.yaml
```

### Method C: Use App Platform UI Without Git

#### 1. Create App

1. Go to Digital Ocean → **Apps** → **Create App**
2. Select **Docker Hub** or **Container Registry**
3. Upload Dockerfile manually (not recommended for production)

## Configuration

### Resource Sizing

| Use Case | Instance Size | RAM | CPU | Cost/Month |
|----------|---------------|-----|-----|------------|
| Development/Testing | Basic XXS | 512MB | 0.5 vCPU | $5 |
| Light Production | Basic XS | 1GB | 1 vCPU | $12 |
| Production | Basic S | 2GB | 1 vCPU | $24 |
| High Traffic | Professional XS | 1GB | 1 vCPU | $12* |

*Professional plans include static outbound IP and advanced features

### Auto-Scaling (Professional Plans)

Add to `.do/app.yaml`:

```yaml
services:
  - name: web
    autoscaling:
      min_instance_count: 1
      max_instance_count: 5
      metrics:
        cpu:
          percent: 80
```

### Environment Variables

Additional optional variables:

```yaml
envs:
  - key: LOG_LEVEL
    value: "INFO"
  - key: MAX_UPLOAD_SIZE
    value: "10485760"  # 10MB
  - key: WORKERS
    value: "2"  # Number of Uvicorn workers
```

## Fonts Handling

### During Build (Automatic)

The build command downloads fonts:

```bash
cd fonts && ./download_fonts.sh
```

**If download fails:**
- Build continues with system fonts
- Standard fonts (Helvetica, Courier) still work
- Warning logged

### Manual Font Upload (Alternative)

If automatic download doesn't work:

1. Download fonts locally:
   ```bash
   cd fonts && ./download_fonts.sh
   ```

2. Commit to Git:
   ```bash
   git add fonts/*.ttf
   git commit -m "Add fonts"
   git push
   ```

3. Update `.gitignore` to allow font files:
   ```
   # Comment out these lines:
   # fonts/*.ttf
   ```

## Monitoring

### Built-in Metrics

DO App Platform provides:
- CPU usage
- Memory usage
- Request count
- Response times
- Error rates

**Access via:**
Dashboard → Apps → your-app → **Insights**

### Logs

**View logs:**
```bash
# Real-time
doctl apps logs $APP_ID --follow

# Type-specific
doctl apps logs $APP_ID --type build
doctl apps logs $APP_ID --type deploy
doctl apps logs $APP_ID --type run
```

**Via UI:**
Dashboard → Apps → your-app → **Runtime Logs**

### Alerts

Configure in `.do/app.yaml`:

```yaml
alerts:
  - rule: DEPLOYMENT_FAILED
  - rule: DOMAIN_FAILED
  - rule: DEPLOYMENT_LIVE
```

Or via UI: Dashboard → Apps → Settings → **Alerts**

## Updates and Maintenance

### Automatic Updates (Git-connected)

**Every git push triggers:**
1. New build
2. Automatic deployment
3. Zero-downtime rolling update

```bash
# Make changes
vim src/calendar_core.py

# Push to trigger deployment
git add .
git commit -m "Update feature"
git push
```

### Manual Redeployment

**Via CLI:**
```bash
doctl apps create-deployment $APP_ID
```

**Via UI:**
Settings → **Create Deployment**

### Rollback

**Via CLI:**
```bash
# List deployments
doctl apps list-deployments $APP_ID

# Rollback to specific deployment
doctl apps create-deployment $APP_ID --deployment-id previous-deployment-id
```

**Via UI:**
Deployments → Previous deployment → **Rollback**

## Custom Domain Setup

### DNS Configuration

**For subdomain (year-grid.ceesaxp.org):**

1. Get CNAME from DO App Platform
2. Add to DNS:
   ```
   year-grid  CNAME  your-app.ondigitalocean.app.
   ```

**For root domain (ceesaxp.org):**

1. Get A record IP from DO
2. Add to DNS:
   ```
   @  A  [IP from DO]
   ```

### SSL Certificate

**Automatic:**
- DO uses Let's Encrypt
- Certificate auto-renews
- No configuration needed

**Verify SSL:**
```bash
curl -I https://year-grid.ceesaxp.org
```

Look for:
```
HTTP/2 200
```

## Cost Optimization

### Tips to Reduce Costs

1. **Right-size instances:**
   - Start with Basic XXS ($5/month)
   - Monitor usage
   - Upgrade only if needed

2. **Use auto-scaling wisely:**
   - Set appropriate thresholds
   - Monitor scaling events
   - Adjust min/max instances

3. **Optimize builds:**
   - Use build cache
   - Multi-stage Docker builds
   - Pre-build fonts into image

4. **Dev/Prod separation:**
   - Use smaller instances for dev
   - Scale up production only

### Cost Estimation

**Minimal Setup:**
- 1x Basic XXS: $5/month
- Bandwidth: ~$0-2/month (1TB free)
- **Total: ~$5-7/month**

**Production Setup:**
- 1x Basic XS: $12/month
- Bandwidth: ~$2-5/month
- **Total: ~$14-17/month**

**High-Traffic Setup:**
- 2-5x Basic S (auto-scaled): $48-120/month
- Bandwidth: ~$5-20/month
- **Total: ~$53-140/month**

## Troubleshooting

### Build Fails

**Check build logs:**
```bash
doctl apps logs $APP_ID --type build
```

**Common issues:**
- Dockerfile.do not found → Check file exists in repo root
- Font download fails → Acceptable, uses system fonts
- Python dependency errors → Check requirements versions

**Solutions:**
```bash
# Test build locally
docker build -f Dockerfile.do -t test .

# Fix issues
git commit -am "Fix build"
git push
```

### App Won't Start

**Check runtime logs:**
```bash
doctl apps logs $APP_ID --type run --follow
```

**Common issues:**
- Port mismatch → Ensure app listens on port 8080
- Import errors → Check all files copied
- Font errors → Verify fonts/ directory included

### Health Check Failing

**Test locally:**
```bash
curl https://your-app.ondigitalocean.app/health
```

**Fix in `.do/app.yaml`:**
```yaml
health_check:
  http_path: /health
  initial_delay_seconds: 20  # Increase if slow start
  timeout_seconds: 15        # Increase if slow response
```

### Domain Not Working

**Check DNS:**
```bash
dig year-grid.ceesaxp.org
```

**Verify CNAME/A record:**
- Should point to DO-provided value
- TTL respected (wait for propagation)

**Check SSL:**
```bash
curl -I https://year-grid.ceesaxp.org
```

## Comparison: DO App Platform vs Self-Hosted

| Feature | DO App Platform | Self-Hosted (Docker) |
|---------|-----------------|---------------------|
| **Setup Time** | 15 minutes | 1-2 hours |
| **SSL/HTTPS** | Automatic | Manual (Caddy auto) |
| **Scaling** | Click or auto | Manual |
| **Monitoring** | Built-in | Setup required |
| **Maintenance** | Managed | Self-managed |
| **Cost** | $5-20/month | $5-10/month (VPS) |
| **Flexibility** | Medium | High |
| **Complexity** | Low | Medium-High |

**Choose DO App Platform if:**
- ✅ You want simplicity
- ✅ You prefer managed services
- ✅ You need auto-scaling
- ✅ You want zero-downtime deploys
- ✅ Time is more valuable than money

**Choose Self-Hosted if:**
- ✅ You want maximum control
- ✅ You're comfortable with Docker/Linux
- ✅ You have multiple services to host
- ✅ You want lowest possible cost
- ✅ You enjoy infrastructure work

## Advanced Configuration

### Multiple Environments

Create separate apps for dev/staging/prod:

```bash
# Production
doctl apps create --spec .do/app.yaml

# Staging
doctl apps create --spec .do/app.staging.yaml
```

### Static Outbound IP (Professional Plan)

Needed for:
- Whitelisting your app's IP
- External API access

```yaml
ingress:
  rules:
    - component:
        name: web
      match:
        path:
          prefix: /
```

### Custom Build Process

For advanced builds:

```yaml
services:
  - name: web
    dockerfile_path: Dockerfile.do
    build_command: |
      cd fonts && ./download_fonts.sh
      python -m pip install --upgrade pip
      pip install -r requirements.txt
```

### Database Integration

If you add user storage later:

```yaml
databases:
  - name: db
    engine: PG
    version: "14"
    size: db-s-1vcpu-1gb

services:
  - name: web
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}
```

## Migration from Self-Hosted

### From Docker on VPS

1. Push code to Git (if not already)
2. Create DO App from Git repo
3. Configure domain in DO (keep old one active)
4. Test DO deployment
5. Update DNS to point to DO
6. Wait for propagation
7. Decommission old server

### From Caddy + Docker Compose

1. Extract Dockerfile.do configuration
2. Remove Caddy dependency (DO handles it)
3. Update port from 8000 to 8080
4. Deploy to DO App Platform
5. Update DNS
6. Shutdown old infrastructure

## Security

### Best Practices

1. **Use secrets for sensitive data:**
   ```yaml
   envs:
     - key: API_KEY
       scope: RUN_TIME
       type: SECRET
       value: EV[secret_id]
   ```

2. **Run as non-root user:**
   Already configured in Dockerfile.do

3. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   ```

4. **Enable HTTPS only:**
   Automatically enforced by DO

5. **Monitor logs:**
   ```bash
   doctl apps logs $APP_ID --follow
   ```

## Support and Resources

- **DO Documentation:** https://docs.digitalocean.com/products/app-platform/
- **Community:** https://www.digitalocean.com/community
- **Support:** https://cloud.digitalocean.com/support
- **Status:** https://status.digitalocean.com/

## Quick Reference

### Essential Commands

```bash
# Authenticate
doctl auth init

# Create app
doctl apps create --spec .do/app.yaml

# List apps
doctl apps list

# Get app info
doctl apps get $APP_ID

# View logs
doctl apps logs $APP_ID --follow

# Redeploy
doctl apps create-deployment $APP_ID

# Delete app
doctl apps delete $APP_ID
```

### URLs

- **Dashboard:** https://cloud.digitalocean.com/apps
- **API Tokens:** https://cloud.digitalocean.com/account/api/tokens
- **Billing:** https://cloud.digitalocean.com/billing

## Conclusion

Digital Ocean App Platform offers a simple, managed way to deploy the Year Grid Calendar with:
- ✅ Minimal configuration
- ✅ Automatic SSL
- ✅ Easy scaling
- ✅ Built-in monitoring
- ✅ Git-based deployments

Perfect for users who want simplicity over infrastructure control.

**Total Setup Time:** 15-30 minutes
**Monthly Cost:** $5-20 depending on traffic
**Maintenance Required:** Minimal

For production use with moderate traffic, DO App Platform is an excellent choice!
