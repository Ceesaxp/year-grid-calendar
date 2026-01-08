# Local Development Guide

This guide explains how to run the Year Grid Calendar web service locally without Docker.

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager

## Setup

### 1. Install Dependencies

**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install reportlab fastapi uvicorn[standard] python-multipart
```

## Running the Web Service Locally

### Method 1: Direct Python Execution

```bash
cd web
python app.py
```

The service will start on `http://localhost:8000`

### Method 2: Using Uvicorn with Auto-reload

For development with automatic reloading on code changes:

```bash
# From project root
uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
```

### Method 3: Custom Port

```bash
uvicorn web.app:app --host 127.0.0.1 --port 3000 --reload
```

## Accessing the Service

Once running, open your browser to:

- **Web Interface**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs** (FastAPI auto-generated): http://localhost:8000/docs

## Testing Locally

### Via Web Browser

1. Open http://localhost:8000
2. Fill in the form:
   - Select year
   - Enter optional title
   - Choose fonts
   - Upload events file (optional)
3. Click "Generate Calendar PDF"
4. PDF downloads automatically

### Via curl

**Health check:**
```bash
curl http://localhost:8000/health
```

**Generate calendar:**
```bash
curl -X POST http://localhost:8000/generate \
  -F "year=2026" \
  -F "title=Test Calendar" \
  -F "font=Helvetica" \
  -F "bold_font=Helvetica-Bold" \
  -o test_calendar.pdf
```

**With events file:**
```bash
curl -X POST http://localhost:8000/generate \
  -F "year=2026" \
  -F "events_file=@events.txt" \
  -o test_calendar.pdf
```

## Development Workflow

### 1. Make Code Changes

Edit files in `src/` for core logic or `web/` for web interface.

### 2. Auto-reload (if using --reload flag)

Changes will be detected automatically and the server will restart.

### 3. Test Changes

Refresh browser or re-run curl commands.

## Project Structure

```
year-grid-calendar/
├── src/
│   └── calendar_core.py      # Core calendar logic (shared)
├── web/
│   └── app.py                 # Web application
└── main.py                    # CLI tool
```

Both `main.py` (CLI) and `web/app.py` (web) import from `src/calendar_core.py`.

## Common Development Tasks

### Run CLI Tool
```bash
./main.py -y 2026 -e events.txt
```

### Run Web Service
```bash
uvicorn web.app:app --reload
```

### Test Core Functions
```bash
python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

from calendar_core import setup_fonts, create_calendar_pdf

setup_fonts()
create_calendar_pdf("test.pdf", 2026, "Test", {})
print("✅ Generated test.pdf")
EOF
```

### Format Code (optional)
```bash
# Install formatter
pip install black

# Format code
black src/ web/ main.py
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'calendar_core'`

**Solution**: The code adds `src/` to Python path. Run from project root:
```bash
# Wrong (from web/ directory)
cd web && python app.py  # ❌

# Correct (from project root)
python web/app.py  # ✅
# or
uvicorn web.app:app  # ✅
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**: Use a different port:
```bash
uvicorn web.app:app --port 8001
```

Or find and kill the process using port 8000:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Or use a different port
```

### Font Not Found

**Problem**: Custom fonts not working

**Solution**: Use standard fonts for local development:
- Helvetica (default)
- Courier
- Times-Roman

Or ensure fonts are installed in:
- `~/Library/Fonts`
- `/Library/Fonts`
- `/System/Library/Fonts`

### File Upload Issues

**Problem**: Events file not parsed correctly

**Solution**: Check file format:
```
01jan  New Year
14feb  Valentine's Day
```
- Format: `DDMMM<spaces>Event description`
- Month names are case-insensitive
- Comments start with `#`

## Environment Variables

Optional environment variables:

```bash
# Set log level
export LOG_LEVEL=DEBUG
uvicorn web.app:app --log-level debug

# Set timezone
export TZ=America/New_York
uvicorn web.app:app
```

## Hot Reload Tips

When using `--reload` flag:

**Watched files:**
- `web/app.py`
- `src/calendar_core.py`

**Not watched:**
- Static files (HTML is inline)
- Config files
- Events files

**Trigger reload manually:**
- Save any `.py` file
- Or restart: `Ctrl+C` then re-run

## Production vs Development

### Development (Local)
```bash
uvicorn web.app:app --reload --log-level debug
```

### Production (Docker)
```bash
docker-compose up -d
```

**Differences:**
- Local: Single worker, auto-reload, verbose logging
- Docker: Multiple workers possible, no reload, production logging

## VS Code Setup (Optional)

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Web Service",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "web.app:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true
    }
  ]
}
```

Then press F5 to start debugging.

## Next Steps

- Make changes to `src/calendar_core.py` for calendar logic
- Make changes to `web/app.py` for web interface
- Test locally before deploying to Docker
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Quick Commands Reference

```bash
# Install
uv sync

# Run web (dev)
uvicorn web.app:app --reload

# Run CLI
./main.py -y 2026

# Test
curl http://localhost:8000/health

# Stop
Ctrl+C
```

Happy coding! 🚀
