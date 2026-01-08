# Project Structure

This document describes the organization of the Year Grid Calendar Generator project, which supports both CLI and web deployment modes.

## Directory Layout

```
year-grid-calendar/
│
├── src/                          # Core library (shared by CLI and web)
│   └── calendar_core.py          # Calendar generation logic
│
├── web/                          # Web service components
│   ├── app.py                    # FastAPI web application
│   └── Dockerfile                # Container definition for web service
│
├── main.py                       # CLI entry point
├── events.txt                    # Example events file
│
├── docker-compose.yml            # Docker orchestration
├── Caddyfile                     # Caddy reverse proxy config
├── deploy.sh                     # Deployment automation script
├── .dockerignore                 # Docker build exclusions
│
├── README.md                     # Main documentation
├── DEPLOYMENT.md                 # Deployment guide
└── STRUCTURE.md                  # This file
```

## Component Architecture

### 1. Core Library (`src/calendar_core.py`)

**Purpose**: Shared calendar generation logic

**Key Functions**:
- `find_font()` - Search for fonts in system directories
- `register_font()` - Register fonts with ReportLab
- `setup_fonts()` - Configure font set for generation
- `parse_events_file()` - Parse events from text file
- `generate_calendar_cells()` - Create calendar cell data
- `draw_cell()` - Render individual cell
- `create_calendar_pdf()` - Generate final PDF

**Dependencies**:
- `reportlab` - PDF generation
- Python standard library (datetime, pathlib, re)

**Design**: Pure functions that can be imported by both CLI and web interfaces.

### 2. CLI Tool (`main.py`)

**Purpose**: Command-line interface for local calendar generation

**Features**:
- Argument parsing with `argparse`
- Direct file system access
- Local font discovery
- Immediate PDF generation

**Usage**:
```bash
./main.py -y 2026 -e events.txt -t "My Calendar" -o output.pdf
```

**Design**: Thin wrapper around `calendar_core` that handles CLI-specific concerns.

### 3. Web Service (`web/app.py`)

**Purpose**: HTTP API and web interface for calendar generation

**Framework**: FastAPI

**Endpoints**:
- `GET /` - Serves HTML form interface
- `POST /generate` - Accepts form data, returns PDF
- `GET /health` - Health check for monitoring

**Features**:
- File upload handling
- Temporary file management
- Responsive HTML/CSS interface
- Automatic cleanup

**Design**: Imports `calendar_core` and wraps it with HTTP request/response handling.

### 4. Container (`web/Dockerfile`)

**Base Image**: `python:3.12-slim`

**Layers**:
1. System dependencies (fonts)
2. Application code (src/ and web/)
3. Python dependencies (reportlab, fastapi, uvicorn)
4. Service configuration

**Entry Point**: `uvicorn web.app:app`

**Port**: 8000

### 5. Orchestration (`docker-compose.yml`)

**Services**:
- `calendar-web` - The web application container

**Networks**:
- `shared_net` (external) - Connects to existing Caddy instance

**Volumes**:
- `/Library/Fonts` - macOS user fonts (read-only)
- `/System/Library/Fonts` - macOS system fonts (read-only)

**Health Check**: Polls `/health` endpoint

### 6. Reverse Proxy (`Caddyfile`)

**Domain**: `year-grid.ceesaxp.org`

**Features**:
- Automatic HTTPS with Let's Encrypt
- Compression (gzip, zstd)
- Security headers
- Access logging
- Optional rate limiting

**Target**: `year-grid-calendar:8000` via `shared_net`

## Data Flow

### CLI Mode

```
User → main.py → calendar_core → PDF file → Disk
           ↓
     Parse args
     Setup fonts
     Load events
```

### Web Mode

```
User → Browser → Caddy → FastAPI → calendar_core → PDF
                   ↓        ↓           ↓
              HTTPS    Upload file   Generate
                       Parse form    Return PDF
```

## Deployment Models

### Local Development (CLI)

```bash
# Install dependencies
uv sync

# Run directly
./main.py -y 2026
```

### Docker Deployment (Web)

```bash
# Create network
docker network create shared_net

# Deploy service
docker-compose up -d --build

# Configure Caddy
# (add Caddyfile contents to Caddy config)

# Access
curl https://year-grid.ceesaxp.org
```

## Key Design Decisions

### 1. Separation of Concerns

**CLI and Web are separate but share core logic**
- `src/calendar_core.py` - Pure business logic
- `main.py` - CLI-specific concerns (arg parsing, file I/O)
- `web/app.py` - HTTP-specific concerns (routes, file uploads)

**Benefits**:
- Easy to test core logic independently
- Can add new interfaces (GUI, API) without duplicating logic
- Changes to PDF generation affect both interfaces consistently

### 2. External Network for Caddy

**Why `shared_net` is external**:
- Allows multiple services to share one Caddy instance
- Caddy runs independently from this service
- Services can be updated without affecting Caddy

**Alternative**: Could run Caddy in same compose file, but less flexible.

### 3. Font Mounting

**Volumes mount system fonts read-only**:
- Container can access host system fonts
- No need to bundle fonts in image
- Read-only for security
- Works on macOS (can adapt paths for Linux)

### 4. Temporary File Handling

**Web service uses temp files for uploads and outputs**:
- `tempfile.NamedTemporaryFile()` for events uploads
- Generated PDFs saved to temp location
- FastAPI's `FileResponse` with `background=None` for cleanup
- Explicit cleanup with `Path.unlink(missing_ok=True)`

### 5. Health Checks

**Container includes health monitoring**:
- Docker-native healthcheck in compose file
- `/health` endpoint for external monitoring
- 30-second intervals with 3 retries
- 40-second startup grace period

## Security Considerations

### 1. File Upload Safety

- Only `.txt` files accepted for events
- Temporary storage with automatic cleanup
- No arbitrary file execution
- Size limits implicitly enforced by FastAPI

### 2. Network Isolation

- Container not exposed directly to internet
- Only accessible via Caddy reverse proxy
- Caddy handles HTTPS/TLS
- Optional rate limiting available

### 3. Container Security

- Run as non-root (could be improved)
- Minimal base image (slim variant)
- No unnecessary packages
- Read-only font mounts

### 4. Input Validation

- Year range validation (2000-2100)
- Font name validation via allowlist
- Event file parsing with error handling
- No shell command execution

## Performance Characteristics

### PDF Generation Time

- ~2-5 seconds for typical calendar
- Single-threaded by default
- CPU-bound operation

### Scalability Options

1. **Horizontal**: Multiple container replicas
2. **Vertical**: Increase worker processes in Uvicorn
3. **Caching**: Could cache PDFs by parameters (not implemented)
4. **Queue**: Add job queue for async processing (not implemented)

### Resource Usage

- **Memory**: ~100-200MB per container
- **CPU**: Spikes during PDF generation, idle otherwise
- **Disk**: Temporary files cleaned up automatically
- **Network**: Minimal (just PDF downloads)

## Maintenance

### Updates

1. **Code changes**: Rebuild with `docker-compose up -d --build`
2. **Dependency updates**: Edit Dockerfile, rebuild
3. **Config changes**: Update compose/Caddy, restart services

### Monitoring

1. **Health endpoint**: `GET /health`
2. **Container logs**: `docker-compose logs -f`
3. **Resource usage**: `docker stats year-grid-calendar`
4. **Caddy logs**: `/var/log/caddy/year-grid-calendar.log`

### Backup

**Critical files**:
- `docker-compose.yml`
- `Caddyfile`
- `events.txt` (if customized)

**Not needed**:
- Generated PDFs (ephemeral)
- Container images (can rebuild)
- Temp files (auto-cleaned)

## Future Enhancements

### Potential Improvements

1. **Authentication**: Add user login for personalization
2. **Persistence**: Store generated calendars for re-download
3. **Templates**: Multiple calendar styles/layouts
4. **Customization**: Web UI for colors, fonts, spacing
5. **Preview**: Show preview before download
6. **API**: RESTful API for programmatic access
7. **Batch**: Generate multiple years at once
8. **Internationalization**: Multi-language support
9. **Time Zones**: Display events in user's timezone
10. **Collaboration**: Share events between users

### Code Quality

1. **Tests**: Add unit tests for `calendar_core`
2. **Type Hints**: Complete typing coverage
3. **Linting**: Add pre-commit hooks
4. **Documentation**: API documentation with Swagger
5. **CI/CD**: Automated builds and deployments

## Conclusion

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Flexible deployment (CLI or web)
- ✅ Production-ready containerization
- ✅ Integration with existing Caddy infrastructure
- ✅ Maintainable and extensible codebase

The design prioritizes simplicity while maintaining professional deployment standards.
