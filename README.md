# Year Grid Calendar Generator

A Python tool to generate beautiful A1-sized yearly calendar PDFs with customizable fonts, titles, and events. Great for putting up on the wall and then scribbling in your important and not-so-much life events for a retrospective at the end of the year!

Available as both a **CLI tool** for local use and a **web service** for online access.

## Features

- **A1 Landscape Layout**: Perfect for wall calendars
- **31-Column Grid**: Consistent layout with February 29 always included (empty for non-leap years)
- **Customizable Fonts**: Use system fonts or specify custom TrueType fonts
- **Event Support**: Load events from a simple text file, displayed in italics
- **Weekend Highlighting**: Weekends shown in red/bold
- **Next Year Preview**: Includes first 10 days of the following year
- **Print-Ready**: 2-point borders, optimized spacing for annotations
- **Web Interface**: Beautiful web UI for easy calendar generation
- **Docker Ready**: Containerized deployment with Caddy integration

## Installation

### CLI Tool (Local Use)

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies
uv sync

# Or use pip
pip install reportlab fastapi uvicorn python-multipart
```

### Web Service (Local Development)

Run the web service locally without Docker:

```bash
# Install dependencies
uv sync

# Run web server
uvicorn web.app:app --reload

# Access at http://localhost:8000
```

See [LOCAL_DEV.md](LOCAL_DEV.md) for detailed local development guide.

### Web Service (Docker Deployment)

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

```bash
# Quick start
docker-compose up -d --build
```

Then access at `https://year-grid.ceesaxp.org`

## Usage

### CLI Tool

Generate a calendar for the current default year (2026):

```bash
./main.py
```

### Command-Line Options

```bash
./main.py [OPTIONS]

Options:
  -y, --year YEAR              Year to generate (default: 2026)
  -r, --font FONTNAME          Regular font name or filename (default: Helvetica)
  -b, --bold-font FONTNAME     Bold font name or filename (default: Helvetica-Bold)
  -T, --title-font FONTNAME    Title font name or filename (default: same as bold-font)
  -t, --title TITLE            Title text (default: YEAR)
  -e, --events FILE            Events file path
  -o, --output FILE            Output PDF filename (default: calendar_YEAR.pdf)
```

### Examples

**Generate a 2027 calendar:**
```bash
./main.py -y 2027
```

**Use custom fonts:**
```bash
./main.py -y 2026 -r Montserrat-Regular -b Montserrat-Bold
```

**Add a custom title:**
```bash
./main.py -y 2026 -t "2026 • Family Calendar"
```

**Include events:**
```bash
./main.py -y 2026 -e events.txt
```

**Complete example:**
```bash
./main.py -y 2026 \
  -r Helvetica \
  -b Helvetica-Bold \
  -t "2026 Calendar" \
  -e events.txt \
  -o my_calendar.pdf
```

## Events File Format

Create a plain text file with one event per line:

```
# This is a comment
# Format: DDMMM  Event description (flexible whitespace)

01jan  New Year
14feb  Valentine's Day
31oct  Halloween
25dec  Christmas
```

### Format Rules:

- **Date Format**: `DDMMM` where DD is day (01-31) and MMM is month (Jan, feb, MAR, etc.)
- **Case Insensitive**: Month names can be uppercase, lowercase, or mixed
- **Separator**: One or more spaces/tabs between date and event description
- **Comments**: Lines starting with `#` are ignored
- **Blank Lines**: Ignored
- **Event Display**: Events appear in italics on the dedicated event line in each day cell

### Example Events File:

```
# Birthdays
25Jan  John
13Aug  Maria
01Apr  Ho - IIRC!

# Holidays
01JAN  New Year
14FEB  Valentine's Day
```

## Font Discovery

The tool automatically searches for fonts in these directories:

1. `~/Library/Fonts` (user fonts)
2. `/Library/Fonts` (system fonts)
3. `/System/Library/Fonts` (macOS system fonts)

### Standard Fonts

These built-in PDF fonts work without file lookup:

- `Helvetica`, `Helvetica-Bold`, `Helvetica-Oblique`
- `Courier`, `Courier-Bold`, `Courier-Oblique`
- `Times-Roman`, `Times-Bold`, `Times-Italic`

### Custom Fonts

Specify font filenames with or without `.ttf` or `.ttc` extensions:

```bash
./main.py -r Montserrat-Regular.ttf -b Montserrat-Bold.ttf
# or
./main.py -r Montserrat-Regular -b Montserrat-Bold
```

The tool automatically finds italic variants for events (e.g., `Montserrat-Italic`).

## Web Service

The calendar generator is also available as a web service with a beautiful UI.

### Features

- **Interactive Form**: Easy-to-use web interface
- **Real-time Generation**: Generate calendars on-demand
- **File Upload**: Upload events files directly
- **Instant Download**: PDF downloads immediately after generation
- **Mobile Friendly**: Responsive design works on all devices

### Deployment

Full deployment instructions available in [DEPLOYMENT.md](DEPLOYMENT.md).

**Quick deployment:**

1. Create shared network: `docker network create shared_net`
2. Start service: `docker-compose up -d --build`
3. Configure Caddy with provided `Caddyfile`
4. Access at `https://year-grid.ceesaxp.org`

### API Endpoints

- `GET /` - Web interface
- `POST /generate` - Generate calendar (form data)
- `GET /health` - Health check endpoint

## Calendar Layout

### Grid Structure
- **Size**: 31 columns × 13 rows
- **Cell Dimensions**: 26mm × 40mm
- **Border Width**: 2 points
- **Paper**: A1 landscape (594mm × 841mm)

### Day Cell Layout
Each day cell contains:
1. **Date Line**: Day number (left) and weekday abbreviation (right)
2. **Event Line**: Reserved space for event names (in italics if event exists)
3. **Bullet Points**: Three grey bullet points for notes

### Special Cells
- **Month Labels**: Large centered letter (J, F, M, A, M, J, J, A, S, O, N, D)
- **Year Cell**: Next year displayed as two lines (e.g., "20" / "27")
- **Empty Cell**: February 29 on non-leap years

## Output

The generated PDF includes:
- **Title**: Large title at the top (customizable)
- **Grid**: Full year calendar with consistent layout
- **Preview**: First 10 days of next January (in grey)
- **Print Info**: Console output with page size and cell count

## Requirements

- Python 3.10+
- ReportLab

## License

MIT License - Feel free to use and modify for personal or commercial projects.

## Tips

- **Printing**: Use high-quality paper for best results on A1 prints
- **Annotations**: The 2-point borders and bullet points are sized for handwritten notes
- **Events**: Keep event descriptions short (they auto-truncate with "…" if too long)
- **Customization**: Edit `main.py` to adjust colors, spacing, or cell dimensions

## Troubleshooting

**Font not found errors:**
- Verify font files exist in one of the search directories
- Use standard fonts (Helvetica, Courier) as fallback
- Check font filename spelling and capitalization

**Events not showing:**
- Verify events file format (DDMMM  Description)
- Check for correct month abbreviations (jan, feb, mar, etc.)
- Ensure dates are valid (01-31)

**PDF layout issues:**
- Ensure you're using A1 paper size for printing
- Check margins if modifying cell dimensions
