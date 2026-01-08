# Static Assets

This directory contains static files for the Year Grid Calendar web application.

## Contents

### Icons

All icons have been generated with a calendar theme (📅) on a purple/blue background (#667eea).

**Apple Touch Icons:**
- `apple-touch-icon.png` (180x180) - Main iOS home screen icon
- `apple-touch-icon-precomposed.png` (180x180) - Fallback for older iOS devices
- `apple-touch-icon-120x120.png` (120x120) - iPhone retina
- `apple-touch-icon-152x152.png` (152x152) - iPad retina
- `apple-touch-icon-167x167.png` (167x167) - iPad Pro
- `apple-touch-icon-180x180.png` (180x180) - iPhone X and newer

**Favicons:**
- `favicon.ico` - Multi-size ICO file (16x16, 32x32)
- `favicon-16x16.png` - Small favicon
- `favicon-32x32.png` - Standard favicon
- `favicon-96x96.png` - Large favicon

**Android Chrome Icons:**
- `android-chrome-192x192.png` (192x192) - Android home screen
- `android-chrome-512x512.png` (512x512) - Android splash screen

### PWA Support

**manifest.json**
- Web App Manifest for Progressive Web App functionality
- Enables "Add to Home Screen" feature
- Defines app name, colors, and icons
- Standalone display mode for app-like experience

## Regenerating Icons

If you want to customize the icons:

1. Install Pillow (optional dependency):
   ```bash
   uv pip install Pillow
   # or
   pip install Pillow
   ```

2. Edit `generate-icons.py` to customize:
   - `BACKGROUND_COLOR` - Change icon background color
   - `EMOJI` - Change emoji (or it falls back to simple calendar grid)
   - `SIZES` - Add/remove icon sizes

3. Run the generator:
   ```bash
   python3 generate-icons.py
   ```

## Browser Support

These icons provide optimal display across:
- ✅ iOS Safari (all versions)
- ✅ Android Chrome
- ✅ Desktop Chrome/Firefox/Safari/Edge
- ✅ PWA installations
- ✅ Bookmark icons
- ✅ Tab favicons

## File Sizes

Total: ~200KB (all icons combined)
- Favicons: ~5KB each
- Apple icons: ~10-40KB each
- Android icons: ~15-60KB each

## Usage

Icons are automatically served by FastAPI's StaticFiles middleware and referenced in the HTML head section of the web app. No manual configuration needed after generation.

## Notes

- Icons use PNG format (except favicon.ico)
- All icons optimized for file size
- Transparent backgrounds not used (solid color for better visibility)
- Calendar emoji requires system font support (falls back to grid design)
- Icons work both online and offline (PWA)

## Related Files

- `generate-icons.py` - Icon generation script
- `manifest.json` - PWA manifest
- `../app.py` - Web app that serves these files
