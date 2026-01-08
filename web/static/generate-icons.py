#!/usr/bin/env python3
"""Generate app icons for Year Grid Calendar web app."""

import os

from PIL import Image, ImageDraw, ImageFont

# Icon sizes for various platforms
SIZES = {
    "apple-touch-icon.png": 180,
    "apple-touch-icon-precomposed.png": 180,
    "apple-touch-icon-120x120.png": 120,
    "apple-touch-icon-152x152.png": 152,
    "apple-touch-icon-167x167.png": 167,
    "apple-touch-icon-180x180.png": 180,
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "favicon-96x96.png": 96,
    "favicon.ico": 32,  # Will be converted to ICO
    "android-chrome-192x192.png": 192,
    "android-chrome-512x512.png": 512,
}

# Calendar emoji or design
EMOJI = "📅"

# Colors
BACKGROUND_COLOR = (102, 126, 234)  # Purple/blue gradient color
TEXT_COLOR = (255, 255, 255)  # White


def create_icon(size, emoji=EMOJI):
    """Create an icon with emoji or simple calendar design."""

    # Create image with colored background
    img = Image.new("RGB", (size, size), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to use emoji first (if font supports it)
    try:
        # Try to load a font that supports emoji
        font_size = int(size * 0.6)

        # Try different fonts that might have emoji support
        font_paths = [
            "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux
            "seguiemj.ttf",  # Windows
        ]

        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue

        if font:
            # Draw emoji
            bbox = draw.textbbox((0, 0), emoji, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2 - bbox[0]
            y = (size - text_height) // 2 - bbox[1]
            draw.text((x, y), emoji, fill=TEXT_COLOR, font=font)
        else:
            raise Exception("No emoji font found")

    except Exception:
        # Fallback: Draw simple calendar grid icon
        padding = int(size * 0.15)

        # Draw calendar outline
        draw.rectangle(
            [padding, padding, size - padding, size - padding],
            outline=TEXT_COLOR,
            width=max(2, size // 40),
        )

        # Draw header bar
        header_height = padding + int(size * 0.15)
        draw.rectangle(
            [padding, padding, size - padding, header_height],
            fill=TEXT_COLOR,
        )

        # Draw grid (3x3 for simplicity)
        grid_start = header_height + int(size * 0.05)
        grid_size = size - padding - grid_start
        cell_size = grid_size // 3

        for i in range(1, 3):
            # Vertical lines
            x = padding + i * cell_size
            draw.line(
                [(x, grid_start), (x, size - padding)],
                fill=TEXT_COLOR,
                width=max(1, size // 60),
            )
            # Horizontal lines
            y = grid_start + i * cell_size
            draw.line(
                [(padding, y), (size - padding, y)],
                fill=TEXT_COLOR,
                width=max(1, size // 60),
            )

    return img


def create_favicon_ico(img_32):
    """Create multi-size ICO file."""
    sizes = [16, 32]
    icons = []

    for size in sizes:
        if size == 32:
            icons.append(img_32)
        else:
            icons.append(img_32.resize((size, size), Image.Resampling.LANCZOS))

    return icons


def main():
    """Generate all icon sizes."""
    print("📱 Generating app icons...")
    print("")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    ico_images = []
    img_32 = None

    for filename, size in SIZES.items():
        print(f"Creating {filename} ({size}x{size})...")

        img = create_icon(size)

        if filename == "favicon.ico":
            img_32 = img
            # ICO will be created at the end
            continue

        output_path = os.path.join(script_dir, filename)
        img.save(output_path, "PNG", optimize=True)
        print(f"  ✅ Saved to {filename}")

    # Create favicon.ico with multiple sizes
    if img_32:
        print("Creating favicon.ico (multi-size)...")
        ico_images = create_favicon_ico(img_32)
        ico_path = os.path.join(script_dir, "favicon.ico")
        ico_images[0].save(
            ico_path,
            format="ICO",
            sizes=[(16, 16), (32, 32)],
            append_images=ico_images[1:],
        )
        print(f"  ✅ Saved to favicon.ico")

    print("")
    print("✅ All icons generated successfully!")
    print("")
    print("Add these to your HTML <head>:")
    print("")
    print("<!-- Favicons -->")
    print(
        '<link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">'
    )
    print(
        '<link rel="icon" type="image/png" sizes="96x96" href="/static/favicon-96x96.png">'
    )
    print(
        '<link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">'
    )
    print('<link rel="shortcut icon" href="/static/favicon.ico">')
    print("")
    print("<!-- Apple Touch Icons -->")
    print(
        '<link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">'
    )
    print(
        '<link rel="apple-touch-icon-precomposed" href="/static/apple-touch-icon-precomposed.png">'
    )
    print("")
    print("<!-- Android Chrome Icons -->")
    print(
        '<link rel="icon" type="image/png" sizes="192x192" href="/static/android-chrome-192x192.png">'
    )
    print(
        '<link rel="icon" type="image/png" sizes="512x512" href="/static/android-chrome-512x512.png">'
    )
    print("")


if __name__ == "__main__":
    main()
