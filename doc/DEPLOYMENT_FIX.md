# Deployment Fix: BASE_URL Not Substituting in Docker

## Problem

When running the Docker image from Docker Hub, the `/robots.txt` endpoint shows:
```
Sitemap: {BASE_URL}/sitemap.xml
```

Instead of:
```
Sitemap: https://year-grid.ceesaxp.org/sitemap.xml
```

## Root Cause

The Docker image on Docker Hub was built with the old code before the bug fix was applied. Simply removing local images doesn't help because you're pulling the old image from Docker Hub.

## Solution

You need to **rebuild and push a new Docker image** to Docker Hub with the fixed code.

## Step-by-Step Fix

### Option 1: Using the Automated Script

1. **Configure your Docker Hub username:**
   ```bash
   export DOCKER_USERNAME=your-dockerhub-username
   ```

2. **Run the rebuild script:**
   ```bash
   ./rebuild-and-push.sh
   ```

   This script will:
   - Remove old local images
   - Build a new image with the fixed code
   - Test BASE_URL substitution
   - Push to Docker Hub
   - Provide deployment instructions

### Option 2: Manual Rebuild

1. **Remove old local images:**
   ```bash
   docker rmi your-username/year-grid-calendar:latest
   ```

2. **Build new image with fixed code:**
   ```bash
   docker build -t your-username/year-grid-calendar:latest -f web/Dockerfile .
   ```

3. **Test locally first:**
   ```bash
   docker run -d --name test-calendar \
     -p 8888:8000 \
     -e BASE_URL=https://year-grid.ceesaxp.org \
     your-username/year-grid-calendar:latest
   
   # Test it works
   curl http://localhost:8888/robots.txt
   
   # Should show: Sitemap: https://year-grid.ceesaxp.org/sitemap.xml
   
   # Cleanup
   docker stop test-calendar
   docker rm test-calendar
   ```

4. **Push to Docker Hub:**
   ```bash
   docker login
   docker push your-username/year-grid-calendar:latest
   ```

## Deployment Server Steps

Once you've pushed the new image to Docker Hub:

### 1. Pull the New Image

```bash
# Force pull to ensure you get the latest
docker pull your-username/year-grid-calendar:latest --no-cache
```

### 2. Stop and Remove Old Container

```bash
docker stop year-grid-calendar
docker rm year-grid-calendar
```

### 3. Run with BASE_URL Environment Variable

**Using docker run:**
```bash
docker run -d \
  --name year-grid-calendar \
  --restart unless-stopped \
  -p 8000:8000 \
  -e BASE_URL=https://year-grid.ceesaxp.org \
  your-username/year-grid-calendar:latest
```

**Using docker-compose:**

Update your `docker-compose.yml` to include BASE_URL:
```yaml
services:
  calendar-web:
    image: your-username/year-grid-calendar:latest
    container_name: year-grid-calendar
    restart: unless-stopped
    environment:
      - TZ=UTC
      - BASE_URL=https://year-grid.ceesaxp.org  # Add this line
    ports:
      - "8000:8000"
```

Then:
```bash
docker-compose pull
docker-compose up -d
```

### 4. Verify It Works

```bash
curl https://year-grid.ceesaxp.org/robots.txt
```

Expected output:
```
User-agent: *
Allow: /
Disallow: /generate

Sitemap: https://year-grid.ceesaxp.org/sitemap.xml
```

Also test sitemap:
```bash
curl https://year-grid.ceesaxp.org/sitemap.xml
```

Should contain `<loc>https://year-grid.ceesaxp.org/</loc>`

## Important Notes

### Cache Issues

If you still see `{BASE_URL}` after pulling:

1. **Check you're pulling the right image:**
   ```bash
   docker images | grep year-grid-calendar
   ```

2. **Force remove all related images:**
   ```bash
   docker rmi $(docker images | grep year-grid-calendar | awk '{print $3}')
   ```

3. **Pull with --no-cache:**
   ```bash
   docker pull your-username/year-grid-calendar:latest --no-cache
   ```

### Environment Variable

The `BASE_URL` environment variable is **critical**. Make sure it's set when running the container:

- ✅ Correct: `-e BASE_URL=https://year-grid.ceesaxp.org`
- ❌ Wrong: Not setting BASE_URL at all (will use default)
- ❌ Wrong: Setting after container is running (won't take effect)

### Docker Hub Repository

Make sure you're pushing to and pulling from the correct repository:
- Repository: `your-username/year-grid-calendar`
- Tag: `latest` (or use version tags like `v1.0`)

## Verification Checklist

- [ ] New Docker image built with fixed code
- [ ] Image tested locally with BASE_URL
- [ ] robots.txt shows correct URL locally
- [ ] sitemap.xml shows correct URL locally
- [ ] Image pushed to Docker Hub
- [ ] Old container stopped on server
- [ ] New image pulled on server (with --no-cache)
- [ ] Container started with BASE_URL env variable
- [ ] robots.txt shows correct URL on production
- [ ] sitemap.xml shows correct URL on production

## Quick Test Command

Run this on your deployment server to verify everything:

```bash
echo "Testing robots.txt:"
curl https://year-grid.ceesaxp.org/robots.txt | grep "year-grid.ceesaxp.org" && echo "✅ robots.txt OK" || echo "❌ robots.txt FAILED"

echo "Testing sitemap.xml:"
curl https://year-grid.ceesaxp.org/sitemap.xml | grep "year-grid.ceesaxp.org" && echo "✅ sitemap.xml OK" || echo "❌ sitemap.xml FAILED"
```

## Troubleshooting

### Still seeing {BASE_URL}?

1. Check the container is using the new image:
   ```bash
   docker inspect year-grid-calendar | grep Image
   ```

2. Check BASE_URL is set in the container:
   ```bash
   docker exec year-grid-calendar env | grep BASE_URL
   ```

3. Check the app.py file in the container:
   ```bash
   docker exec year-grid-calendar cat /app/web/app.py | grep -A 5 "async def robots"
   ```

   Should show:
   ```python
   return f"""User-agent: *
   ```

   NOT:
   ```python
   content = f"""User-agent: *
   ...
   return Response(content=content, media_type="text/plain")
   ```

### Container won't start?

Check logs:
```bash
docker logs year-grid-calendar
```

Common issues:
- Port 8000 already in use
- Missing dependencies (shouldn't happen with our Dockerfile)
- Python syntax error (run `python -m py_compile web/app.py` locally first)

## Summary

The fix requires:
1. ✅ Code is fixed in `web/app.py` (already done)
2. 🔨 **Rebuild Docker image** (you need to do this)
3. 📤 **Push to Docker Hub** (you need to do this)
4. 🚀 **Pull and deploy on server with BASE_URL** (you need to do this)

Use the `rebuild-and-push.sh` script to automate steps 2-3!

---

**Last Updated:** 2026-01-08
**Status:** Ready to rebuild and deploy
