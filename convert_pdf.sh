#!/bin/bash

# PDF to Images Converter for DealZen
# Usage: ./convert_pdf.sh your_flyer.pdf

set -e

PDF_FILE="$1"
OUTPUT_DIR="./flyer-images"

if [ -z "$PDF_FILE" ]; then
    echo "❌ Error: Please provide a PDF file"
    echo ""
    echo "Usage: ./convert_pdf.sh path/to/flyer.pdf"
    echo ""
    echo "Example: ./convert_pdf.sh ~/Downloads/walmart_flyer.pdf"
    exit 1
fi

if [ ! -f "$PDF_FILE" ]; then
    echo "❌ Error: File not found: $PDF_FILE"
    exit 1
fi

# Get filename without extension
BASENAME=$(basename "$PDF_FILE" .pdf)

echo "📄 Converting PDF to images..."
echo "   Input: $PDF_FILE"
echo "   Output: $OUTPUT_DIR/"
echo ""

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "⚠️  ImageMagick not found. Installing via Homebrew..."
    echo ""
    brew install imagemagick
fi

# Convert PDF to PNG images
convert -density 300 "$PDF_FILE" "$OUTPUT_DIR/${BASENAME}_page_%02d.png"

# Count generated images
IMAGE_COUNT=$(ls -1 "$OUTPUT_DIR/${BASENAME}_page_"*.png 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "✅ Success! Generated $IMAGE_COUNT images"
echo ""
echo "📁 Images saved to: $OUTPUT_DIR/"
echo ""
echo "🚀 Next step: Run the processing script"
echo "   ./process_flyers_and_load.sh"

