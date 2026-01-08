# TODO

## Completed

### 2026-01-08: Documentation and Script Cleanup

Cleaned up transient documentation and scripts accumulated during development:

**Scripts removed:**
- `scripts/deploy-droplet.sh` - Redundant (used DOCR)
- `scripts/docker-debug.sh` - Debug script for BASE_URL fix
- `scripts/inspect-image.sh` - One-time troubleshooting
- `scripts/quick-fix.sh` - Debug script for BASE_URL fix
- `scripts/rebuild-and-push.sh` - Superseded
- `scripts/update-do-app.sh` - For DO App Platform (not used)
- `scripts/deploy-dockerhub.sh` - Merged into deploy-do.sh
- `scripts/rebuild-push-do.sh` - Merged into deploy-do.sh

**Scripts kept:**
- `scripts/deploy-do.sh` - Primary deployment (build + push to Docker Hub)
- `scripts/deploy.sh` - Local docker-compose deployment
- `scripts/test_local.sh` - Local development testing

**Documentation removed:**
- `doc/DEPLOY_DIGITALOCEAN.md` - For DO App Platform (not used)
- `doc/DEPLOYMENT_FIX.md` - BASE_URL bug fix (resolved)
- `doc/DEPLOYMENT_STEPS.txt` - BASE_URL bug checklist (resolved)
- `doc/DEPLOYMENT_OPTIONS.md` - Outdated comparison
- `doc/BUGFIX.md` - robots.txt fix (historical)
- `doc/FIXES.md` - UI fixes (historical)
- `doc/CHANGES.txt` - SEO changes (redundant)
- `doc/SEO_QUICK_REFERENCE.md` - Redundant
- `doc/SUMMARY.md` - SEO summary (redundant)
- `doc/README_WEB.md` - Redundant with main README
- `doc/DEPLOYMENT_CHECKLIST.md` - Merged into DEPLOYMENT.md
- `doc/DEPLOY_DROPLET.md` - Merged into DEPLOYMENT.md
- `doc/SEO_IMPROVEMENTS.md` - Removed

**Documentation kept:**
- `doc/DEPLOYMENT.md` - Consolidated deployment guide
- `doc/LOCAL_DEV.md` - Local development instructions
- `doc/QUICKSTART.md` - Quick reference
- `doc/STRUCTURE.md` - Project architecture
- `doc/SECURITY.md` - Security documentation

### 2026-01-08: Docker Image Optimization

- Changed base image from `python:3.12-slim` to `python:3.12-alpine`
- Reduced image size from ~280MB to ~113MB
- Fixed `#!/bin/bash` to `#!/bin/sh` in `fonts/download_fonts.sh` for Alpine compatibility
- Changed CMD from `uvicorn` to `python -m uvicorn` to fix exec format issues
- Added `--platform linux/amd64` for cross-platform builds from ARM Mac
- Fixed healthcheck to use Python instead of curl (not in Alpine)

## Pending

- None currently
