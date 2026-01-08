"""FastAPI web application for year grid calendar generator."""

import logging
import os
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calendar_core import create_calendar_pdf, parse_events_file, setup_fonts

app = FastAPI(title="Year Grid Calendar Generator")


@app.on_event("startup")
async def startup_event():
    """Log when the application starts."""
    logger.info("=" * 60)
    logger.info("Year Grid Calendar Generator - Web Service Starting")
    logger.info("=" * 60)
    logger.info(f"Bundled fonts available: {len(BUNDLED_FONTS)}")
    logger.info(f"Total fonts available: {len(ALL_FONTS)}")
    logger.info("Server is ready to accept requests")
    logger.info("=" * 60)


# Get available fonts
FONTS_DIR = Path(__file__).parent.parent / "fonts"
BUNDLED_FONTS = []

if FONTS_DIR.exists():
    for font_file in FONTS_DIR.glob("*.ttf"):
        font_name = font_file.stem
        BUNDLED_FONTS.append(font_name)

# Standard PDF fonts
STANDARD_FONTS = [
    "Helvetica",
    "Helvetica-Bold",
    "Courier",
    "Courier-Bold",
    "Times-Roman",
    "Times-Bold",
]

ALL_FONTS = sorted(set(STANDARD_FONTS + BUNDLED_FONTS))


def generate_font_options(selected=None):
    """Generate HTML options for font select."""
    options = []

    # Group fonts by family
    regular_fonts = [f for f in ALL_FONTS if "Bold" not in f and "Italic" not in f]

    for font in regular_fonts:
        sel = " selected" if font == selected else ""
        options.append(f'<option value="{font}"{sel}>{font}</option>')

    return "\n".join(options)


def generate_bold_font_options(selected=None):
    """Generate HTML options for bold font select."""
    options = []

    # Prefer bold variants
    bold_fonts = [f for f in ALL_FONTS if "Bold" in f]
    if not bold_fonts:
        bold_fonts = [f for f in ALL_FONTS if "Bold" not in f and "Italic" not in f]

    for font in bold_fonts:
        sel = " selected" if font == selected else ""
        options.append(f'<option value="{font}"{sel}>{font}</option>')

    return "\n".join(options)


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main page with calendar generation form."""

    regular_options = generate_font_options(
        "NotoSans-Regular" if "NotoSans-Regular" in ALL_FONTS else "Helvetica"
    )
    bold_options = generate_bold_font_options(
        "NotoSans-Bold" if "NotoSans-Bold" in ALL_FONTS else "Helvetica-Bold"
    )
    title_options = generate_bold_font_options(
        "Montserrat-Bold" if "Montserrat-Bold" in ALL_FONTS else "Helvetica-Bold"
    )

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Year Grid Calendar Generator</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 2em;
            }}
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
                font-size: 0.95em;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 8px;
                color: #444;
                font-weight: 500;
                font-size: 0.9em;
            }}
            input[type="number"],
            input[type="text"],
            input[type="file"],
            select {{
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s;
            }}
            input:focus, select:focus {{
                outline: none;
                border-color: #667eea;
            }}
            .file-input-wrapper {{
                position: relative;
                overflow: hidden;
            }}
            input[type="file"] {{
                cursor: pointer;
            }}
            button {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 14px 32px;
                font-size: 1.1em;
                border-radius: 8px;
                cursor: pointer;
                width: 100%;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }}
            button:active {{
                transform: translateY(0);
            }}
            button:disabled {{
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
            }}
            .info {{
                background: #f0f4ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-top: 20px;
                border-radius: 4px;
                font-size: 0.85em;
                color: #555;
            }}
            .info strong {{ color: #333; }}
            .spinner {{
                display: none;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                animation: spin 1s linear infinite;
                margin: 10px auto 0;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .loading button {{ opacity: 0.7; pointer-events: none; }}
            .loading .spinner {{ display: block; }}
            .font-notice {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px;
                margin-bottom: 20px;
                border-radius: 4px;
                font-size: 0.85em;
                color: #856404;
            }}
            .font-notice a {{
                color: #856404;
                font-weight: 600;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📅 Year Grid Calendar</h1>
            <p class="subtitle">Generate a beautiful A1-sized yearly calendar PDF</p>

            {f'<div class="font-notice">💡 For best results and Unicode support, download fonts: <code>./fonts/download_fonts.sh</code></div>' if len(BUNDLED_FONTS) == 0 else ''}

            <form id="calendarForm" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="year">Year</label>
                    <input type="number" id="year" name="year" value="2026" min="2000" max="2100" required>
                </div>

                <div class="form-group">
                    <label for="title">Title (optional)</label>
                    <input type="text" id="title" name="title" placeholder="Leave empty to use year as title">
                </div>

                <div class="form-group">
                    <label for="font">Regular Font</label>
                    <select id="font" name="font">
                        {regular_options}
                    </select>
                </div>

                <div class="form-group">
                    <label for="bold_font">Bold Font</label>
                    <select id="bold_font" name="bold_font">
                        {bold_options}
                    </select>
                </div>

                <div class="form-group">
                    <label for="title_font">Title Font</label>
                    <select id="title_font" name="title_font">
                        {title_options}
                    </select>
                </div>

                <div class="form-group">
                    <label for="events_file">Events File (optional)</label>
                    <input type="file" id="events_file" name="events_file" accept=".txt">
                </div>

                <button type="submit" id="submitBtn">Generate Calendar PDF</button>
                <div class="spinner"></div>

                <div class="info">
                    <strong>Events file format:</strong><br>
                    <code>01jan  New Year<br>14feb  Valentine's Day</code><br>
                    <small>Format: DDMMM followed by spaces and event description. Supports Unicode (Cyrillic, etc.)</small>
                </div>
            </form>
        </div>

        <script>
            const form = document.getElementById('calendarForm');
            const submitBtn = document.getElementById('submitBtn');
            const container = document.querySelector('.container');

            form.addEventListener('submit', async function(e) {{
                e.preventDefault();

                // Show loading state
                container.classList.add('loading');
                submitBtn.disabled = true;

                try {{
                    // Create FormData from form
                    const formData = new FormData(form);

                    // Send request
                    const response = await fetch('/generate', {{
                        method: 'POST',
                        body: formData
                    }});

                    if (!response.ok) {{
                        throw new Error('Failed to generate calendar');
                    }}

                    // Get the PDF as a blob
                    const blob = await response.blob();

                    // Create download link
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    const year = formData.get('year');
                    a.download = `calendar_${{year}}.pdf`;
                    document.body.appendChild(a);
                    a.click();

                    // Cleanup
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);

                }} catch (error) {{
                    alert('Error generating calendar: ' + error.message);
                }} finally {{
                    // Reset loading state
                    container.classList.remove('loading');
                    submitBtn.disabled = false;
                }}
            }});
        </script>
    </body>
    </html>
    """


@app.post("/generate")
async def generate_calendar(
    year: int = Form(2026),
    title: str = Form(""),
    font: str = Form("Helvetica"),
    bold_font: str = Form("Helvetica-Bold"),
    title_font: str = Form("Helvetica-Bold"),
    events_file: UploadFile = File(None),
):
    """Generate calendar PDF with the provided parameters."""

    # Set title to year if not provided
    calendar_title = title.strip() if title.strip() else str(year)

    # Log the request
    logger.info(
        f"Calendar generation request: year={year}, title='{calendar_title}', fonts=({font}, {bold_font}, {title_font})"
    )

    # Setup fonts
    setup_fonts(font=font, bold_font=bold_font, title_font=title_font)

    # Handle events file if provided
    events = {}
    events_tmp_path = None

    if events_file and events_file.filename:
        # Save uploaded file temporarily with UTF-8 encoding
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb") as tmp:
            content = await events_file.read()
            tmp.write(content)
            events_tmp_path = tmp.name

        # Parse events
        events = parse_events_file(events_tmp_path, year)
        logger.info(f"Parsed {len(events)} events from uploaded file")

    # Generate PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        output_path = tmp.name

    try:
        create_calendar_pdf(output_path, year, calendar_title, events)
        logger.info(f"Successfully generated calendar PDF: {calendar_title}")

        # Return PDF as download
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"calendar_{year}.pdf",
            headers={
                "Content-Disposition": f'attachment; filename="calendar_{year}.pdf"'
            },
        )
    finally:
        # Cleanup events temp file
        if events_tmp_path:
            try:
                os.unlink(events_tmp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp events file: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "bundled_fonts": len(BUNDLED_FONTS),
        "total_fonts": len(ALL_FONTS),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
