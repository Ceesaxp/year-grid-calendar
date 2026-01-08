# Fonts for Year Grid Calendar

This directory contains open-source fonts bundled with the calendar generator.

## Quick Setup

Download all fonts with one command:

```bash
./download_fonts.sh
```

This will download 5 carefully selected font families optimized for calendar design.

## Included Fonts

### 1. **Noto Sans** (Google)
- **License**: SIL Open Font License
- **Best for**: Universal content, excellent Unicode support
- **Special**: Full Cyrillic support for Russian/Ukrainian text
- **Files**: NotoSans-Regular.ttf, NotoSans-Bold.ttf, NotoSans-Italic.ttf

### 2. **Inter** (Rasmus Andersson)
- **License**: SIL Open Font License
- **Best for**: Digital displays, excellent number clarity
- **Special**: Optimized for screens, great at small sizes
- **Files**: Inter-Regular.ttf, Inter-Bold.ttf

### 3. **Roboto** (Google)
- **License**: Apache 2.0
- **Best for**: Modern, clean designs
- **Special**: Geometric yet friendly, includes Cyrillic
- **Files**: Roboto-Regular.ttf, Roboto-Bold.ttf, Roboto-Italic.ttf

### 4. **Montserrat** (Julieta Ulanovsky)
- **License**: SIL Open Font License
- **Best for**: Titles and headers
- **Special**: Beautiful geometric sans-serif, inspired by Buenos Aires signage
- **Files**: Montserrat-Regular.ttf, Montserrat-Bold.ttf, Montserrat-Italic.ttf

### 5. **Source Sans Pro** (Adobe)
- **License**: SIL Open Font License
- **Best for**: Professional documents, body text
- **Special**: Adobe's first open-source typeface, highly legible
- **Files**: SourceSansPro-Regular.ttf, SourceSansPro-Bold.ttf, SourceSansPro-Italic.ttf

## Why These Fonts?

**Calendar-Specific Requirements:**
- ✅ Excellent number legibility (dates!)
- ✅ Clear at multiple sizes
- ✅ Professional appearance
- ✅ Unicode support (international characters)
- ✅ Cyrillic support (Russian names/events)
- ✅ Open-source and free

**Recommended Combinations:**

| Use Case | Title Font | Body Font | Why |
|----------|-----------|-----------|-----|
| Modern & Clean | Montserrat Bold | Inter Regular | Geometric contrast |
| Professional | Source Sans Pro Bold | Source Sans Pro Regular | Consistent family |
| Universal | Noto Sans Bold | Noto Sans Regular | Best Unicode support |
| Tech-forward | Roboto Bold | Inter Regular | Digital-optimized |
| Classic | Source Sans Pro Bold | Noto Sans Regular | Reliable legibility |

## Unicode Support

**Full Cyrillic Support:**
- Noto Sans ⭐ (Best)
- Roboto ⭐
- Montserrat (Basic)

**For Russian/Ukrainian events**, use **Noto Sans** or **Roboto**.

## Font Weights Included

All fonts include:
- **Regular**: For body text, dates, events
- **Bold**: For weekends, month labels, titles
- **Italic**: For event descriptions (where available)

## Manual Installation (Alternative)

If the script doesn't work, download manually:

1. **Noto Sans**: https://fonts.google.com/noto/specimen/Noto+Sans
2. **Inter**: https://github.com/rsms/inter/releases
3. **Roboto**: https://github.com/googlefonts/roboto/releases
4. **Montserrat**: https://github.com/JulietaUla/Montserrat/releases
5. **Source Sans Pro**: https://github.com/adobe-fonts/source-sans/releases

Place `.ttf` files in this directory.

## Usage in Calendar Generator

### CLI
```bash
./main.py -y 2026 \
  -r NotoSans-Regular \
  -b NotoSans-Bold \
  -T Montserrat-Bold \
  -e events_cyrillic.txt
```

### Web Interface
Fonts will automatically appear in the dropdown menus once downloaded.

## License Information

All fonts are **free for personal and commercial use**:
- **OFL (Open Font License)**: Noto Sans, Inter, Montserrat, Source Sans Pro
- **Apache 2.0**: Roboto

No attribution required (though appreciated).

## File Structure

```
fonts/
├── README.md                    # This file
├── download_fonts.sh            # Auto-download script
├── NotoSans-Regular.ttf
├── NotoSans-Bold.ttf
├── NotoSans-Italic.ttf
├── Inter-Regular.ttf
├── Inter-Bold.ttf
├── Roboto-Regular.ttf
├── Roboto-Bold.ttf
├── Roboto-Italic.ttf
├── Montserrat-Regular.ttf
├── Montserrat-Bold.ttf
├── Montserrat-Italic.ttf
├── SourceSansPro-Regular.ttf
├── SourceSansPro-Bold.ttf
└── SourceSansPro-Italic.ttf
```

## Troubleshooting

**Script fails to download:**
- Check internet connection
- Try manual download from links above
- Ensure `curl` and `unzip` are installed

**Fonts not appearing in web app:**
- Restart the web service after downloading fonts
- Check that `.ttf` files are in this directory
- Verify file permissions: `chmod 644 *.ttf`

**Cyrillic text not displaying:**
- Use **Noto Sans** or **Roboto** (best Cyrillic support)
- Ensure font files are properly downloaded
- Check that events file is saved as UTF-8

## Credits

- **Noto Sans**: Google Fonts, Design by Monotype
- **Inter**: Rasmus Andersson
- **Roboto**: Christian Robertson (Google)
- **Montserrat**: Julieta Ulanovsky
- **Source Sans Pro**: Paul D. Hunt (Adobe)

Thank you to all the designers and foundries for making these excellent fonts freely available!
