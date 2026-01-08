# Deployment Guide

Complete guide to deploying the Year Grid Calendar Generator.

## Overview

This application can be deployed via Docker Hub to a Digital Ocean Droplet (or any VPS) with Caddy as a reverse proxy.

```
Local Machine → Build Image → Push to Docker Hub → Pull on Droplet → Run Container → Caddy → Internet
```

## Prerequisites

- Docker and Docker Compose installed locally
- Docker Hub account
- VPS/Droplet with Docker installed
- Caddy web server running on the droplet
- Domain pointing to your server

## Quick Start

### 1. Build and Push to Docker Hub

```bash
# From project root
cd fonts && ./download_fonts.sh && cd ..
./scripts/deploy-do.sh
```

This will:
- Build an AMD64 image using `Dockerfile.do`
- Push to Docker Hub as `$DOCKERHUB_USER/year-grid-calendar:latest`

### 2. Deploy on Droplet

SSH to your droplet and run:

```bash
# Pull and start with docker-compose
cd /path/to/year-grid-calendar
docker compose pull
docker compose up -d
```

Or run directly:

```bash
docker pull $DOCKERHUB_USER/year-grid-calendar:latest
docker run -d \
  --name year-grid-calendar \
  --restart unless-stopped \
  --network proxy_net \
  -e TZ=UTC \
  $DOCKERHUB_USER/year-grid-calendar:latest
```

### 3. Configure Caddy

Add to your Caddyfile:

```
year-grid.yourdomain.com {
    reverse_proxy year-grid-calendar:8080
    encode gzip zstd
    
    header {
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
    }
}
```

Reload Caddy:

```bash
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
# Or: systemctl reload caddy
```

## Directory Structure

```
year-grid-calendar/
├── src/
│   └── calendar_core.py      # Core calendar generation logic
├── web/
│   ├── app.py                # FastAPI web application
│   ├── Dockerfile            # Local development container
│   └── static/               # Static assets (icons, manifest)
├── fonts/
│   └── download_fonts.sh     # Font download script
├── scripts/
│   ├── deploy-do.sh          # Build and push to Docker Hub
│   └── deploy.sh             # Local docker-compose deployment
├── Dockerfile.do             # Production Dockerfile (Alpine)
├── docker-compose.yml        # Docker orchestration
├── Caddyfile                 # Caddy configuration snippet
└── main.py                   # CLI tool
```

## Docker Compose Configuration

Example `docker-compose.yml` for the droplet:

```yaml
services:
  calendar-web:
    image: docker.io/yourusername/year-grid-calendar:latest
    container_name: year-grid-calendar
    restart: unless-stopped
    networks:
      - proxy_net
    environment:
      - TZ=UTC
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  proxy_net:
    external: true
```

## Updating the Application

### From Local Machine

```bash
# Make code changes, then:
./scripts/deploy-do.sh
```

### On Droplet

```bash
docker compose pull
docker compose up -d
```

## Monitoring

### Health Check

```bash
curl http://localhost:8080/health
# Or via domain:
curl https://year-grid.yourdomain.com/health
```

Expected response:
```json
{"status": "healthy", "bundled_fonts": 14, "total_fonts": 20}
```

### View Logs

```bash
docker compose logs -f calendar-web
# Or:
docker logs -f year-grid-calendar
```

### Resource Usage

```bash
docker stats year-grid-calendar
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs year-grid-calendar

# Check if port is in use
netstat -tlnp | grep 8080
```

### Cannot Connect via Caddy

```bash
# Verify container is on shared network
docker network inspect proxy_net

# Check Caddy logs
docker logs caddy

# Test direct connection
docker exec year-grid-calendar python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"
```

### exec format error

This means architecture mismatch. The image must be built for AMD64:

```bash
# Rebuild with correct platform
docker buildx build --platform linux/amd64 -f Dockerfile.do -t youruser/year-grid-calendar:latest --push .
```

### Font Issues

Fonts are bundled in the image. If issues occur:

```bash
# Check fonts in container
docker exec year-grid-calendar ls -la /app/fonts/
```

## Security Considerations

### Container Security
- Runs as non-root user (`appuser`)
- Alpine-based minimal image (~113MB)
- No unnecessary packages

### Network Security
- Container not exposed directly to internet
- Access only via Caddy reverse proxy
- Caddy handles HTTPS/TLS automatically

### Rate Limiting
Built into the application (10 requests per 60 seconds per IP).

## Performance

### Resource Usage
- Memory: ~50-100MB
- CPU: Spikes during PDF generation
- Disk: Temporary files cleaned automatically

### Scaling
For high traffic, increase container replicas behind a load balancer.

---

## Deployment Checklist

### Pre-Deployment

- [ ] Fonts downloaded (`cd fonts && ./download_fonts.sh`)
- [ ] Docker Hub credentials configured
- [ ] `Dockerfile.do` uses correct CMD (`python -m uvicorn`)
- [ ] Test build locally works

### Deployment

- [ ] Build and push: `./scripts/deploy-do.sh`
- [ ] Pull on droplet: `docker compose pull`
- [ ] Start container: `docker compose up -d`
- [ ] Configure Caddy reverse proxy
- [ ] Reload Caddy

### Post-Deployment Verification

- [ ] Health check passes: `curl https://yourdomain.com/health`
- [ ] Homepage loads correctly
- [ ] PDF generation works
- [ ] robots.txt accessible
- [ ] sitemap.xml accessible

### SEO Verification (if applicable)

- [ ] Submit sitemap to Google Search Console
- [ ] Test social media previews (Facebook Debugger)
- [ ] Validate structured data (Google Rich Results Test)

---

## Quick Reference

### Build and Deploy

```bash
# Local: build and push
./scripts/deploy-do.sh

# Droplet: pull and restart
docker compose pull && docker compose up -d
```

### Useful Commands

```bash
# View logs
docker logs -f year-grid-calendar

# Restart
docker compose restart

# Stop
docker compose down

# Check status
docker compose ps

# Shell access
docker exec -it year-grid-calendar /bin/sh
```

### URLs

- Health: `/health`
- Robots: `/robots.txt`
- Sitemap: `/sitemap.xml`

---

**Image Size**: ~113MB (Alpine-based)
**Port**: 8080 (internal)
**Architecture**: linux/amd64
