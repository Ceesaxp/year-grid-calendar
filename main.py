#!/usr/bin/env python3
"""CLI wrapper for year grid calendar generator."""

import argparse
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from calendar_core import (
    create_calendar_pdf,
    parse_events_file,
    setup_fonts,
)


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
        "-e",
        "--events",
        type=str,
        default=None,
        help="Events file path (format: DDMMM  Event description)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output PDF filename (default: calendar_YEAR.pdf)",
    )
    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_args()

    # Setup fonts
    setup_fonts(
        font=args.font,
        bold_font=args.bold_font,
        title_font=args.title_font,
    )

    # Parse events file if provided
    events = parse_events_file(args.events, args.year)
    if events:
        print(f"Loaded {len(events)} events from {args.events}")

    # Set default title and output filename
    title = args.title if args.title else str(args.year)
    output = args.output if args.output else f"calendar_{args.year}.pdf"

    # Generate calendar
    create_calendar_pdf(output, args.year, title, events)


if __name__ == "__main__":
    main()
