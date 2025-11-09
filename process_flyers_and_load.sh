#!/bin/bash

# DealZen Flyer Processing & Loading Script
# This script processes all flyers and loads them into Weaviate

echo "=================================================="
echo "   DealZen Flyer Processing & Loading Script"
echo "=================================================="
echo ""

# Check for flyer images
FLYER_COUNT=$(ls -1 flyer-images/*.{jpg,png,jpeg} 2>/dev/null | wc -l | tr -d ' ')

if [ "$FLYER_COUNT" -eq "0" ]; then
    echo "❌ No flyer images found in flyer-images/ folder"
    echo ""
    echo "Please add some flyer images first:"
    echo "  1. Download Black Friday flyers (JPG or PNG)"
    echo "  2. Copy them to: flyer-images/"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

echo "✅ Found $FLYER_COUNT flyer image(s) to process"
echo ""

# Step 1: Process flyers with GPT-4o Vision
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Processing flyers with GPT-4o Vision"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd scripts
source ../backend/.venv/bin/activate
export $(cat ../backend/.env | grep -v '^#' | xargs)

echo "Processing flyers... (this may take a minute)"
python process_flyers.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Flyer processing failed. Check error messages above."
    exit 1
fi

echo ""
echo "✅ Flyer processing complete!"
echo ""

# Step 2: Check how many deals were extracted
if [ -f "deals.json" ]; then
    DEAL_COUNT=$(python3 -c "import json; data=json.load(open('deals.json')); print(len(data))")
    echo "📊 Extracted $DEAL_COUNT deals from flyers"
    echo ""
else
    echo "❌ deals.json not found. Processing may have failed."
    exit 1
fi

# Step 3: Ingest into Weaviate
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Loading deals into Weaviate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /Users/chindhamani/development/DealZen/DealZen_CodeBase
PYTHONPATH=. python scripts/ingest_data.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Data ingestion failed. Check error messages above."
    exit 1
fi

echo ""
echo "=================================================="
echo "   ✅ SUCCESS! All Done!"
echo "=================================================="
echo ""
echo "📊 Summary:"
echo "  - Processed: $FLYER_COUNT flyer images"
echo "  - Extracted: $DEAL_COUNT deals"
echo "  - Loaded into: Weaviate database"
echo ""
echo "🎯 Next Steps:"
echo "  1. Open: http://localhost:5173"
echo "  2. Test queries with your real data!"
echo ""
echo "💡 Example queries to try:"
echo "  - 'Show me all TV deals'"
echo "  - 'What's under \$100?'"
echo "  - 'Best Buy electronics'"
echo ""

