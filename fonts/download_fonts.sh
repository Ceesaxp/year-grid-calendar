#!/bin/sh
# Download open-source fonts for Year Grid Calendar
# All fonts are licensed under OFL (Open Font License) or Apache 2.0

set -e

FONTS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$FONTS_DIR"

echo "📥 Downloading open-source fonts for Year Grid Calendar"
echo "========================================================"
echo ""

# Create temporary directory
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Function to download and extract font
download_font() {
    local name=$1
    local url=$2
    local files=$3

    echo "📦 Downloading $name..."
    curl -L -o "$TMP_DIR/$name.zip" "$url"
    unzip -q "$TMP_DIR/$name.zip" -d "$TMP_DIR/$name"

    # Copy TTF files
    for file in $files; do
        find "$TMP_DIR/$name" -name "$file" -exec cp {} "$FONTS_DIR/" \;
    done

    echo "✅ $name installed"
}

# 1. Noto Sans (Google) - Excellent Unicode support, includes Cyrillic
# License: OFL
echo ""
echo "1/5 Noto Sans - Universal coverage with Cyrillic support"
download_font "NotoSans" \
    "https://github.com/notofonts/latin-greek-cyrillic/releases/download/NotoSans-v2.013/NotoSans-v2.013.zip" \
    "NotoSans-Regular.ttf NotoSans-Bold.ttf NotoSans-Italic.ttf"

# 2. Inter (Rasmus Andersson) - Designed for screens, excellent legibility
# License: OFL
echo ""
echo "2/5 Inter - Optimized for digital displays"
download_font "Inter" \
    "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip" \
    "Inter-Regular.ttf Inter-Bold.ttf"

# 3. Roboto (Google) - Clean and modern
# License: Apache 2.0
echo ""
echo "3/5 Roboto - Modern geometric sans-serif"
download_font "Roboto" \
    "https://github.com/googlefonts/roboto/releases/download/v2.138/roboto-unhinted.zip" \
    "Roboto-Regular.ttf Roboto-Bold.ttf Roboto-Italic.ttf"

# 4. Montserrat (Julieta Ulanovsky) - Beautiful geometric sans
# License: OFL
echo ""
echo "4/5 Montserrat - Elegant geometric design"
download_font "Montserrat" \
    "https://github.com/JulietaUla/Montserrat/archive/refs/heads/master.zip" \
    "Montserrat-Regular.ttf Montserrat-Bold.ttf Montserrat-Italic.ttf"

# 5. Source Sans Pro (Adobe) - Professional and versatile
# License: OFL
echo ""
echo "5/5 Source Sans Pro - Adobe's professional sans-serif"
download_font "SourceSansPro" \
    "https://github.com/adobe-fonts/source-sans/releases/download/3.052R/TTF-source-sans-3.052R.zip" \
    "SourceSans3-Regular.ttf SourceSans3-Bold.ttf SourceSans3-It.ttf"

# Rename Source Sans files to simpler names
if [ -f "SourceSans3-Regular.ttf" ]; then
    mv SourceSans3-Regular.ttf SourceSansPro-Regular.ttf
    mv SourceSans3-Bold.ttf SourceSansPro-Bold.ttf
    mv SourceSans3-It.ttf SourceSansPro-Italic.ttf
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All fonts downloaded successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Fonts installed in: $FONTS_DIR"
echo ""
echo "Fonts available:"
ls -1 *.ttf 2>/dev/null | sed 's/^/  - /'
echo ""
echo "These fonts support:"
echo "  ✓ Latin characters"
echo "  ✓ Cyrillic characters (Noto Sans, Roboto)"
echo "  ✓ Numbers and punctuation"
echo "  ✓ Common symbols"
echo ""
echo "All fonts are licensed under OFL or Apache 2.0"
echo "Free for personal and commercial use"
echo ""
