#!/usr/bin/env python3
"""Generate a 2026 calendar PDF for A1 paper (landscape)."""

from datetime import date, timedelta
from typing import Any

from reportlab.lib.colors import Color, black, red
from reportlab.lib.pagesizes import A1
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Register JetBrains Mono if available, fallback to Courier
try:
    pdfmetrics.registerFont(  # type: ignore[no-untyped-call]
        TTFont(
            "JetBrainsMono",
            "/Users/andrei/Library/Fonts/Montserrat-Regular.ttf",  # JetBrainsMono-Regular.ttf",
        )
    )
    pdfmetrics.registerFont(
        TTFont(
            "JetBrainsMono-Bold",
            "/Users/andrei/Library/Fonts/Montserrat-Bold.ttf",  # JetBrainsMono-Bold.ttf",
        )
    )
    MONO_FONT = "JetBrainsMono"
    MONO_BOLD = "JetBrainsMono-Bold"
except OSError:
    print("Did not find JetBrainsMono!")
    MONO_FONT = "Courier"  # pyright: ignore[reportConstantRedefinition]
    MONO_BOLD = "Courier-Bold"  # pyright: ignore[reportConstantRedefinition]


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


def generate_calendar_cells() -> list[Any]:
    """Generate all cells for 2026 calendar + partial 2027."""
    cells: list[Any] = []

    # 2026 calendar
    current_date = date(2026, 1, 1)
    current_month = 1

    # Add January label
    cells.append(("month", "J", None, False))

    while current_date.year == 2026:
        if current_date.month != current_month:
            # New month - add label
            current_month = current_date.month
            cells.append(("month", MONTH_LABELS[current_month - 1], None, False))

        cells.append(("day", current_date.day, current_date, False))
        current_date += timedelta(days=1)

    # After Dec 31, 2026: Add 2027 cell
    cells.append(("year", "2027", None, True))

    # Add January 2027 label (gray)
    cells.append(("month", "J", None, True))

    # Add 24 days of January 2027 (gray)
    for day in range(1, 12):
        d = date(2027, 1, day)
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


def create_calendar_pdf(filename: str):
    """Create the calendar PDF."""
    c: canvas.Canvas = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # Draw title area
    title_y = GRID_Y + GRID_HEIGHT + 10 * mm
    c.setFont(MONO_BOLD, 72)
    c.setFillColor(black)
    title_text = "2026 • Andrei + Ksenia + Mila"
    # title_width = c.stringWidth(title_text, MONO_BOLD, 116)
    title_x = MARGIN  # + (GRID_WIDTH - title_width) / 2
    c.drawString(title_x, title_y, title_text)

    # Generate cells
    cells = generate_calendar_cells()

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


if __name__ == "__main__":
    create_calendar_pdf("calendar_2026.pdf")
