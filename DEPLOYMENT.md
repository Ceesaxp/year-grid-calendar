# Deployment Guide

This guide explains how to deploy the Year Grid Calendar Generator as a web service behind Caddy reverse proxy.

## Architecture

```
Internet → Caddy (year-grid.your-domain.com) → Docker Container (year-grid-calendar:8000)
                                          ↓
                                    shared_net network
```

## Prerequisites

- Docker and Docker Compose installed
- Caddy web server running with access to `shared_net` network
- Domain `year-grid.your-domain.com` DNS pointing to your server

## Directory Structure

```
year-grid-calendar/
├── src/
│   └── calendar_core.py          # Core calendar generation logic
├── web/
│   ├── app.py                     # FastAPI web application
│   └── Dockerfile                 # Container definition
├── main.py                        # CLI tool (optional, for local use)
├── docker-compose.yml             # Service orchestration
├── Caddyfile                      # Caddy configuration snippet
└── DEPLOYMENT.md                  # This file
```

## Step 1: Create Shared Network

If you don't already have a `shared_net` network for Caddy, create it:

```bash
docker network create shared_net
```

## Step 2: Configure Caddy

Add the configuration from `Caddyfile` to your existing Caddy setup.

### Option A: Include the file

In your main Caddyfile:

```
import /path/to/year-grid-calendar/Caddyfile
```

### Option B: Merge manually

Copy the contents of `Caddyfile` into your main Caddy configuration file.

### Reload Caddy

```bash
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
# or if running as a service:
systemctl reload caddy
```

## Step 3: Build and Deploy

Navigate to the project directory and start the service:

```bash
cd year-grid-calendar

# Build and start the container
docker-compose up -d --build

# Check logs
docker-compose logs -f calendar-web
```

## Step 4: Verify Deployment

### Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Test via Caddy

```bash
curl https://year-grid.ceesaxp.org/
# Should return the HTML form
```

### Generate a Test Calendar

Visit `https://year-grid.ceesaxp.org/` in your browser and:
1. Select a year
2. Click "Generate Calendar PDF"
3. Download should start automatically

## Maintenance

### View Logs

```bash
docker-compose logs -f calendar-web
```

### Restart Service

```bash
docker-compose restart calendar-web
```

### Update Deployment

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Stop Service

```bash
docker-compose down
```

## Monitoring

### Check Container Status

```bash
docker ps | grep year-grid-calendar
```

### Check Resource Usage

```bash
docker stats year-grid-calendar
```

### Health Check Endpoint

The service provides a health check at `/health` which is used by Docker's healthcheck:

```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs calendar-web

# Check if port 8000 is already in use
netstat -tulpn | grep 8000
```

### Cannot Connect via Caddy

```bash
# Verify container is on shared_net
docker network inspect shared_net

# Check Caddy logs
docker logs caddy

# Test direct connection to container
docker exec -it year-grid-calendar curl localhost:8000/health
```

### Font Issues

If custom fonts aren't working, verify font mounts in `docker-compose.yml`:

```yaml
volumes:
  - /Library/Fonts:/fonts:ro
  - /System/Library/Fonts:/system-fonts:ro
```

### PDF Generation Fails

Check container logs for ReportLab errors:

```bash
docker-compose logs calendar-web | grep -i error
```

## Security Considerations

### Rate Limiting

The provided Caddyfile includes commented rate limiting configuration. To enable:

1. Install Caddy rate limit plugin
2. Uncomment the rate_limit section in Caddyfile
3. Reload Caddy

### File Upload Limits

By default, FastAPI limits file uploads to a reasonable size. To adjust:

Edit `web/app.py` and add:

```python
from fastapi import FastAPI
app = FastAPI(max_request_size=10_000_000)  # 10MB limit
```

### HTTPS

Caddy automatically handles HTTPS with Let's Encrypt. Ensure:
- Port 443 is open
- DNS is correctly configured
- Caddy has permissions to bind to privileged ports

## Performance Tuning

### Increase Workers

For high traffic, increase Uvicorn workers in `web/Dockerfile`:

```dockerfile
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  calendar-web:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
```

## Backup and Recovery

### Backup Configuration

Important files to backup:
- `docker-compose.yml`
- `Caddyfile`
- Any custom events files

```bash
tar -czf year-grid-calendar-backup.tar.gz \
  docker-compose.yml \
  Caddyfile \
  events.txt
```

### Recovery

```bash
# Restore files
tar -xzf year-grid-calendar-backup.tar.gz

# Rebuild and start
docker-compose up -d --build
```

## Updates

### Update Dependencies

To update Python packages:

1. Edit `web/Dockerfile` to specify newer versions
2. Rebuild: `docker-compose up -d --build`

### Update Application Code

```bash
git pull
docker-compose up -d --build
```

## CLI Tool (Local Use)

The CLI tool remains available for local/offline use:

```bash
# From project root
./main.py -y 2026 -e events.txt -o calendar_2026.pdf
```

The CLI and web service share the same core logic from `src/calendar_core.py`.

## Environment Variables

Optional environment variables can be set in `docker-compose.yml`:

```yaml
environment:
  - TZ=America/New_York          # Set timezone
  - LOG_LEVEL=INFO               # Logging level
  - MAX_UPLOAD_SIZE=10485760     # Max upload size in bytes
```

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify network connectivity
3. Test health endpoint
4. Review Caddy configuration
5. Check DNS resolution

## License

MIT License - See main README.md for details.
