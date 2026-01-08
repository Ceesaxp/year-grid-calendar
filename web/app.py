"""FastAPI web application for year grid calendar generator."""

import logging
import os
import re
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calendar_core import create_calendar_pdf, parse_events_file, setup_fonts

app = FastAPI(title="Year Grid Calendar Generator")

# Validation constants
MAX_TITLE_LENGTH = 200
MAX_FILE_SIZE = 1024 * 1024  # 1MB
ALLOWED_FONTS = set(STANDARD_FONTS)  # Will be updated after font discovery
MIN_YEAR = 1900
MAX_YEAR = 2200

# Rate limiting
RATE_LIMIT_REQUESTS = 10  # Max requests
RATE_LIMIT_WINDOW = 60  # Per 60 seconds
request_counts = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""

    async def dispatch(self, request: Request, call_next):
        # Only rate limit /generate endpoint
        if request.url.path != "/generate":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host

        # Clean old requests
        current_time = time.time()
        request_counts[client_ip] = [
            req_time
            for req_time in request_counts[client_ip]
            if current_time - req_time < RATE_LIMIT_WINDOW
        ]

        # Check rate limit
        if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return HTMLResponse(
                content="<h1>429 Too Many Requests</h1><p>Please wait a minute before generating another calendar.</p>",
                status_code=429,
            )

        # Add current request
        request_counts[client_ip].append(current_time)

        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


# Add middleware
app.add_middleware(RateLimitMiddleware)


def sanitize_title(title: str) -> str:
    """Sanitize title input to prevent injection and ensure safe display.

    Args:
        title: Raw title input from user

    Returns:
        Sanitized title string

    Raises:
        HTTPException: If title is invalid
    """
    if not title:
        return ""

    # Remove leading/trailing whitespace
    title = title.strip()

    # Check length
    if len(title) > MAX_TITLE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Title too long (max {MAX_TITLE_LENGTH} characters)",
        )

    # Remove control characters except newlines and tabs
    title = "".join(char for char in title if char.isprintable() or char in "\n\t")

    # Remove any null bytes
    title = title.replace("\x00", "")

    # Limit to single line (remove newlines/tabs for title)
    title = " ".join(title.split())

    # Check for potential script injection patterns
    dangerous_patterns = ["<script", "javascript:", "onerror=", "onclick="]
    title_lower = title.lower()
    for pattern in dangerous_patterns:
        if pattern in title_lower:
            raise HTTPException(
                status_code=400, detail="Title contains potentially unsafe content"
            )

    return title


def validate_year(year: int) -> int:
    """Validate year input.

    Args:
        year: Year value from user

    Returns:
        Validated year

    Raises:
        HTTPException: If year is invalid
    """
    if not isinstance(year, int):
        raise HTTPException(status_code=400, detail="Year must be an integer")

    if year < MIN_YEAR or year > MAX_YEAR:
        raise HTTPException(
            status_code=400, detail=f"Year must be between {MIN_YEAR} and {MAX_YEAR}"
        )

    return year


def validate_font(font_name: str, font_type: str = "font") -> str:
    """Validate font name input.

    Args:
        font_name: Font name from user
        font_type: Type of font (for error messages)

    Returns:
        Validated font name

    Raises:
        HTTPException: If font is invalid
    """
    if not font_name or not isinstance(font_name, str):
        raise HTTPException(status_code=400, detail=f"Invalid {font_type} name")

    # Remove any path traversal attempts
    font_name = os.path.basename(font_name)

    # Check against allowed fonts
    if font_name not in ALL_FONTS:
        raise HTTPException(
            status_code=400,
            detail=f"Font '{font_name}' not available. Choose from allowed fonts.",
        )

    return font_name


def validate_events_file(file: UploadFile) -> None:
    """Validate uploaded events file.

    Args:
        file: Uploaded file object

    Raises:
        HTTPException: If file is invalid
    """
    if not file.filename:
        return

    # Check file extension
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Events file must be a .txt file")

    # Check filename for path traversal
    safe_filename = os.path.basename(file.filename)
    if safe_filename != file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Check for suspicious filenames
    if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # File size will be checked during read


@app.on_event("startup")
async def startup_event():
    """Log when the application starts."""
    global ALLOWED_FONTS
    ALLOWED_FONTS = set(ALL_FONTS)

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

    try:
        # Validate inputs
        year = validate_year(year)
        title = sanitize_title(title)
        font = validate_font(font, "regular font")
        bold_font = validate_font(bold_font, "bold font")
        title_font = validate_font(title_font, "title font")

        if events_file and events_file.filename:
            validate_events_file(events_file)

        # Set title to year if not provided
        calendar_title = title if title else str(year)

        # Log the request
        logger.info(
            f"Calendar generation request: year={year}, title='{calendar_title}', fonts=({font}, {bold_font}, {title_font})"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid input parameters")

    # Setup fonts
    setup_fonts(font=font, bold_font=bold_font, title_font=title_font)

    # Handle events file if provided
    events = {}
    events_tmp_path = None

    if events_file and events_file.filename:
        try:
            # Read file content with size limit
            content = await events_file.read(MAX_FILE_SIZE + 1)

            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Events file too large (max {MAX_FILE_SIZE // 1024}KB)",
                )

            # Validate UTF-8 encoding
            try:
                content.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400, detail="Events file must be UTF-8 encoded"
                )

            # Save uploaded file temporarily with UTF-8 encoding
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".txt", mode="wb"
            ) as tmp:
                tmp.write(content)
                events_tmp_path = tmp.name

            # Parse events
            events = parse_events_file(events_tmp_path, year)
            logger.info(f"Parsed {len(events)} events from uploaded file")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing events file: {e}")
            raise HTTPException(status_code=400, detail="Failed to process events file")

    # Generate PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        output_path = tmp.name

    try:
        create_calendar_pdf(output_path, year, calendar_title, events)
        logger.info(f"Successfully generated calendar PDF: {calendar_title}")

        # Sanitize filename for download
        safe_filename = f"calendar_{year}.pdf"
        safe_filename = re.sub(r"[^\w\-_\.]", "_", safe_filename)

        # Return PDF as download
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=safe_filename,
            headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
        )
    except Exception as e:
        logger.error(f"Error generating calendar: {e}")
        # Cleanup temp files on error
        try:
            if os.path.exists(output_path):
                os.unlink(output_path)
        except:
            pass
        raise HTTPException(status_code=500, detail="Failed to generate calendar PDF")
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
