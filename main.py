#!/usr/bin/env python3
"""Generate a year calendar PDF for A1 paper (landscape)."""

import argparse
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from reportlab.lib.colors import Color, black, red
from reportlab.lib.pagesizes import A1
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Font search paths
FONT_PATHS = [
    Path.home() / "Library" / "Fonts",
    Path("/Library/Fonts"),
    Path("/System/Library/Fonts"),
]

# PDF standard fonts that don't require file lookup
STANDARD_FONTS = {
    "Helvetica",
    "Helvetica-Bold",
    "Helvetica-Oblique",
    "Helvetica-BoldOblique",
    "Courier",
    "Courier-Bold",
    "Courier-Oblique",
    "Courier-BoldOblique",
    "Times-Roman",
    "Times-Bold",
    "Times-Italic",
    "Times-BoldItalic",
}


def find_font(font_name: str) -> str | None:
    """Search for a font file in system font directories.

    Args:
        font_name: Font name with or without .ttf/.ttc extension

    Returns:
        Full path to font file if found, None otherwise
    """
    # If no extension provided, try both .ttf and .ttc
    if not (font_name.endswith(".ttf") or font_name.endswith(".ttc")):
        extensions = [".ttf", ".ttc"]
    else:
        extensions = [""]

    for font_dir in FONT_PATHS:
        if font_dir.exists():
            for ext in extensions:
                font_path = font_dir / (font_name + ext)
                if font_path.exists():
                    return str(font_path)
    return None


def register_font(font_name: str, font_file: str, fallback: str) -> str:
    """Register a font or return fallback.

    Args:
        font_name: Internal name for the font
        font_file: Font filename to search for (or standard font name)
        fallback: Fallback font name if not found

    Returns:
        Registered font name or fallback
    """
    # Check if it's a standard PDF font
    if font_file in STANDARD_FONTS:
        print(f"Using standard font: {font_file}")
        return font_file

    font_path = find_font(font_file)
    if font_path:
        try:
            # For .ttc files, try with subfontIndex
            if font_path.endswith(".ttc"):
                # Try to register with subfontIndex=0 (first font in collection)
                pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            print(f"Registered font: {font_file} from {font_path}")
            return font_name
        except Exception as e:
            print(f"Failed to register {font_file}: {e}")
            return fallback
    else:
        print(f"Font not found: {font_file}")
        return fallback


# Default fonts - will be overridden by command-line args
MONO_FONT = "Courier"
MONO_BOLD = "Courier-Bold"
TITLE_FONT = "Courier-Bold"


# Page setup - A1 Landscape
PAGE_WIDTH, PAGE_HEIGHT = A1[1], A1[0]  # Landscape: swap dimensions
MARGIN = 15.5 * mm

# Grid setup
COLS: int = 30
ROWS: int = 13
CELL_WIDTH = 27 * mm
CELL_HEIGHT = 40 * mm
BORDER = 1 * mm

# Title
TITLE_HEIGHT = 32 * mm

# Calculate grid origin (bottom-left of grid)
GRID_WIDTH = COLS * CELL_WIDTH + 2 * BORDER
GRID_HEIGHT = ROWS * CELL_HEIGHT + 2 * BORDER
GRID_X = MARGIN
GRID_Y = MARGIN

# Colors
DIMMED_RED = Color(0.7, 0.3, 0.3)  # Dimmed bold red for next year's weekends
GRAY_50 = Color(0.5, 0.5, 0.5)  # 50% gray for next year's weekdays

# Month labels
MONTH_LABELS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


def get_weekday_name(d: date) -> str:
    """Return 3-letter weekday name."""
    return d.strftime("%a")


def is_weekend(d: date) -> bool:
    """Check if date is Saturday or Sunday."""
    return d.weekday() >= 5


def generate_calendar_cells(year: int) -> list[Any]:
    """Generate all cells for the specified year calendar + partial next year.

    Args:
        year: The year to generate calendar for

    Returns:
        List of cell tuples (type, value, date_obj, is_gray)
    """
    cells: list[Any] = []

    # Main year calendar
    current_date = date(year, 1, 1)
    current_month = 1

    # Add January label
    cells.append(("month", "J", None, False))

    while current_date.year == year:
        if current_date.month != current_month:
            # New month - add label
            current_month = current_date.month
            cells.append(("month", MONTH_LABELS[current_month - 1], None, False))

        cells.append(("day", current_date.day, current_date, False))
        current_date += timedelta(days=1)

    # After Dec 31: Add next year cell
    next_year = year + 1
    cells.append(("year", str(next_year), None, True))

    # Add January next year label (gray)
    cells.append(("month", "J", None, True))

    # Add partial days of January next year (gray)
    for day in range(1, 12):
        d = date(next_year, 1, day)
        cells.append(("day", day, d, True))

    return cells


def draw_cell(
    c: canvas.Canvas,
    x: float,
    y: float,
    cell_type: str,
    value: str,
    date_obj: date,
    is_gray: bool,
):
    """Draw a single cell."""
    # Draw cell border
    border_color = black  # GRAY_50 if is_gray else black
    c.setStrokeColor(border_color)
    c.setLineWidth(BORDER)
    c.rect(x, y, CELL_WIDTH, CELL_HEIGHT)

    if cell_type == "month":
        # Month label - large centered letter
        c.setFont(MONO_BOLD, 48)
        c.setFillColor(GRAY_50 if is_gray else black)
        text_width = c.stringWidth(value, MONO_BOLD, 48)
        text_x = x + (CELL_WIDTH - text_width) / 2
        text_y = y + CELL_HEIGHT / 2 - 16
        c.drawString(text_x, text_y, value)

    elif cell_type == "year":
        # Year label - split into two lines: regular "20", bold "27"
        c.setFillColor(GRAY_50)

        # Split year into two parts (e.g., "2027" -> "20" and "27")
        line1 = value[:2]  # First two digits (regular font)
        line2 = value[2:]  # Last two digits (bold font)

        font_size = 42

        # Calculate centered positions for each line
        text_width1 = c.stringWidth(line1, MONO_FONT, font_size)
        text_width2 = c.stringWidth(line2, MONO_BOLD, font_size)

        text_x1 = x + (CELL_WIDTH - text_width1) / 2
        text_x2 = x + (CELL_WIDTH - text_width2) / 2

        # Calculate vertical centering
        # Total height of both lines plus spacing
        line_spacing = 4  # Small gap between lines
        total_text_height = font_size * 2 + line_spacing

        # Start from center and position both lines
        start_y = y + (CELL_HEIGHT + total_text_height) / 2
        text_y1 = start_y - font_size  # Top line
        text_y2 = start_y - font_size * 2 - line_spacing  # Bottom line

        # Draw first line (regular)
        c.setFont(MONO_FONT, font_size)
        c.drawString(text_x1, text_y1, line1)

        # Draw second line (bold)
        c.setFont(MONO_BOLD, font_size)
        c.drawString(text_x2, text_y2, line2)

    elif cell_type == "day":
        # Day cell
        day_str: str = f"{value:02d}"
        weekday_str: str = get_weekday_name(date_obj)
        weekend: bool = is_weekend(date_obj)

        # Determine colors
        if is_gray:
            if weekend:
                text_color = DIMMED_RED
                font = MONO_BOLD
            else:
                text_color = GRAY_50
                font = MONO_FONT
        else:
            if weekend:
                text_color = red
                font = MONO_BOLD
            else:
                text_color = black
                font = MONO_FONT

        c.setFillColor(text_color)

        # First line: DD on left, Www on right
        c.setFont(font, 10)
        padding = 2 * mm
        line_y = y + CELL_HEIGHT - 4 * mm

        c.drawString(x + padding, line_y, day_str)
        weekday_width = c.stringWidth(weekday_str, font, 10)
        c.drawString(x + CELL_WIDTH - padding - weekday_width, line_y, weekday_str)

        # Bullet points (3 lines)
        bullet_color = GRAY_50 if is_gray else black
        c.setFillColor(bullet_color)
        c.setFont(MONO_FONT, 8)

        bullet_y_start = line_y - 6 * mm
        bullet_spacing = 5 * mm

        for i in range(3):
            bullet_y = bullet_y_start - i * bullet_spacing
            c.drawString(x + padding, bullet_y, "•")


def create_calendar_pdf(filename: str, year: int, title: str):
    """Create the calendar PDF.

    Args:
        filename: Output PDF filename
        year: Year to generate calendar for
        title: Title text to display
    """
    c: canvas.Canvas = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # Draw title area
    title_y = GRID_Y + GRID_HEIGHT + 10 * mm
    c.setFont(TITLE_FONT, 72)
    c.setFillColor(black)
    c.drawString(MARGIN, title_y, title)

    # Generate cells
    cells = generate_calendar_cells(year)

    # Draw grid from top-left
    row = 0
    col = 0

    for cell in cells:
        cell_type, value, date_obj, is_gray = cell

        # Calculate position (top-left origin, going right then down)
        x = GRID_X + col * CELL_WIDTH + BORDER
        y = GRID_Y + GRID_HEIGHT - (row + 1) * CELL_HEIGHT - BORDER

        draw_cell(c, x, y, cell_type, value, date_obj, is_gray)

        col += 1
        if col >= COLS:
            col = 0
            row += 1

    c.save()
    print(f"Created {filename}")
    print(f"Page size: {PAGE_WIDTH/mm:.0f} x {PAGE_HEIGHT/mm:.0f} mm (A1 landscape)")
    print(f"Grid size: {GRID_WIDTH/mm:.0f} x {GRID_HEIGHT/mm:.0f} mm")
    print(f"Cells: {len(cells)}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a year calendar PDF for A1 paper (landscape)"
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=2026,
        help="Year to generate calendar for (default: 2026)",
    )
    parser.add_argument(
        "-r",
        "--font",
        type=str,
        default="Helvetica",
        help="Regular font name or filename (default: Helvetica)",
    )
    parser.add_argument(
        "-b",
        "--bold-font",
        type=str,
        default="Helvetica-Bold",
        help="Bold font name or filename (default: Helvetica-Bold)",
    )
    parser.add_argument(
        "-T",
        "--title-font",
        type=str,
        default=None,
        help="Title font filename (default: same as bold-font)",
    )
    parser.add_argument(
        "-t", "--title", type=str, default=None, help="Title text (default: YEAR)"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output PDF filename (default: calendar_YEAR.pdf)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Register fonts
    MONO_FONT = register_font("RegularFont", args.font, "Courier")
    MONO_BOLD = register_font("BoldFont", args.bold_font, "Courier-Bold")

    # Use bold font for title if title-font not specified
    title_font_file = args.title_font if args.title_font else args.bold_font
    TITLE_FONT = register_font("TitleFont", title_font_file, "Courier-Bold")

    # Set default title and output filename
    title = args.title if args.title else str(args.year)
    output = args.output if args.output else f"calendar_{args.year}.pdf"

    create_calendar_pdf(output, args.year, title)
