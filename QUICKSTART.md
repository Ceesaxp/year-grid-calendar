# Quick Start Guide

Fast reference for common tasks with Year Grid Calendar Generator.

## 🚀 First Time Setup

### CLI Only
```bash
uv sync
./main.py -y 2026
```

### Font Setup (Recommended)
```bash
# Download bundled open-source fonts with Unicode support
cd fonts
./download_fonts.sh
cd ..
```

This downloads 5 high-quality fonts including Noto Sans (best Cyrillic support).

### Web Service (Docker)
```bash
# Create network (first time only)
docker network create shared_net

# Download fonts first (recommended for Unicode support)
cd fonts && ./download_fonts.sh && cd ..

# Deploy
./deploy.sh

# Or manually
docker-compose up -d --build
```

### Web Service (Local - No Docker)
```bash
# Install dependencies
uv sync
# OR: pip install reportlab fastapi uvicorn python-multipart

# Download fonts (recommended)
cd fonts && ./download_fonts.sh && cd ..

# Run web server
uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload

# Access at http://localhost:8000
```

## 📋 Common CLI Commands

### Basic Generation
```bash
./main.py -y 2026                          # Generate 2026 calendar
./main.py -y 2027 -o my_calendar.pdf       # Custom output name
```

### With Events
```bash
./main.py -y 2026 -e events.txt            # Include events
```

### Custom Fonts
```bash
./main.py -r Helvetica -b Helvetica-Bold   # Standard fonts
./main.py -r Montserrat-Regular -b Montserrat-Bold  # Custom fonts
```

### Custom Title
```bash
./main.py -y 2026 -t "2026 • Family Calendar"
```

### All Options
```bash
./main.py -y 2026 \
  -r Helvetica \
  -b Helvetica-Bold \
  -T Helvetica-Bold \
  -t "My Calendar 2026" \
  -e events.txt \
  -o calendar_2026.pdf
```

## 🌐 Web Service Commands

### Deploy/Update
```bash
docker-compose up -d --build              # Deploy or update
docker-compose restart calendar-web       # Restart service
docker-compose down                       # Stop service
```

### Monitoring
```bash
docker-compose logs -f calendar-web       # Follow logs
docker-compose ps                         # Check status
docker stats year-grid-calendar           # Resource usage
curl http://localhost:8000/health         # Health check
```

### Caddy Integration
```bash
# Add Caddyfile to your Caddy config, then:
docker exec caddy caddy reload --config /etc/caddy/Caddyfile

# Or if Caddy is a system service:
systemctl reload caddy
./main.py -y 2026 -t "My Calendar 2026" -e events.txt -o output.pdf
```

## 🎨 Font Setup

### Download Bundled Fonts
```bash
cd fonts
./download_fonts.sh
```

**Fonts included:**
- Noto Sans (best Unicode/Cyrillic support)
- Inter (excellent for numbers)
- Roboto (modern and clean)
- Montserrat (beautiful titles)
- Source Sans Pro (professional)

**For Cyrillic/Russian text**, use Noto Sans or Roboto.

## 📝 Events File Format

Create `events.txt` (UTF-8 encoding):
```
# Comments start with #
01jan  New Year
14feb  Valentine's Day
21jan  Андрей
25dec  Christmas
```

Format: `DDMMM<space><space>Event description`
Supports Unicode characters (Cyrillic, emoji, etc.)

## 🔍 Troubleshooting

### Service Won't Start
```bash
docker-compose logs calendar-web          # Check logs
docker ps -a                              # Check all containers
docker network ls                         # Verify shared_net exists
```

### Can't Access via Domain
```bash
# Test local access first
curl http://localhost:8000/health

# Check Caddy logs
docker logs caddy

# Verify DNS
nslookup year-grid.ceesaxp.org
```

### Font Not Found
```bash
# Download bundled fonts
cd fonts && ./download_fonts.sh

# List available fonts
ls ~/Library/Fonts
ls /Library/Fonts
ls /System/Library/Fonts
ls fonts/

# Use standard fonts as fallback
./main.py -r Helvetica -b Helvetica-Bold

# Or use bundled fonts
./main.py -r NotoSans-Regular -b NotoSans-Bold
```

### Unicode/Cyrillic Not Displaying
```bash
# Use Noto Sans (best Unicode support)
./main.py -r NotoSans-Regular -b NotoSans-Bold -e events_cyrillic.txt

# Ensure events file is UTF-8 encoded
file events.txt
```

### PDF Generation Fails
```bash
# Check permissions
ls -la output_directory/

# Check disk space
df -h

# Try with minimal options
./main.py -y 2026 -o test.pdf
```

## 🔧 Quick Fixes

### Reset Everything (Web Service)
```bash
docker-compose down
docker network create shared_net
docker-compose up -d --build
```

### Clear Docker Cache
```bash
docker system prune -a
docker-compose up -d --build
```

### Reinstall CLI Dependencies
```bash
uv sync --reinstall
```

## 📍 URLs

- **Web Interface**: https://year-grid.ceesaxp.org
- **Health Check**: https://year-grid.ceesaxp.org/health
- **Local Dev**: http://localhost:8000

## 🎯 Quick Test

### Test CLI
```bash
./main.py -y 2026 -t "Test" -o test.pdf && open test.pdf
```

### Test Web Service
```bash
# Health check
curl http://localhost:8000/health

# Generate via API
curl -X POST http://localhost:8000/generate \
  -F "year=2026" \
  -F "title=Test Calendar" \
  -o test.pdf
```

## 📚 Documentation

- Full docs: [README.md](README.md)
- Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)
- Architecture: [STRUCTURE.md](STRUCTURE.md)

## ⚡ Pro Tips

1. **Download Fonts First**: Always run before first use
   ```bash
   cd fonts && ./download_fonts.sh && cd ..
   ```

2. **Batch Generate**: Loop for multiple years
   ```bash
   for year in 2026 2027 2028; do
     ./main.py -y $year -e events.txt
   done
   ```

3. **Watch Logs**: Auto-reload log view
   ```bash
   watch -n 2 'docker-compose logs --tail=20 calendar-web'
   ```

4. **Quick Deploy**: One-liner deploy
   ```bash
   cd fonts && ./download_fonts.sh && cd .. && docker network create shared_net 2>/dev/null; docker-compose up -d --build
   ```

5. **Check Container**: Enter running container
   ```bash
   docker exec -it year-grid-calendar /bin/bash
   ```

6. **Backup**: Quick backup of config
   ```bash
   tar -czf backup-$(date +%F).tar.gz docker-compose.yml Caddyfile events.txt
   ```

7. **Best Font Combo**: For Unicode support
   ```bash
   ./main.py -r NotoSans-Regular -b NotoSans-Bold -T Montserrat-Bold
   ```

## 🆘 Support

Issue? Check in order:
1. Logs: `docker-compose logs -f`
2. Health: `curl localhost:8000/health`
3. Network: `docker network inspect shared_net`
4. Caddy: `docker logs caddy`
5. DNS: `dig year-grid.ceesaxp.org`

Still stuck? Review [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.
