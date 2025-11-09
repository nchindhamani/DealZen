# DealZen Flyer Processing Guide

## Overview

DealZen uses **GPT-4o Vision API** to automatically extract deal information from retail flyer images. This is an **offline process** that happens before you start your application.

---

## 🔄 Complete Workflow

```
1. Collect Flyer Images
         ↓
2. Run process_flyers.py
         ↓
3. GPT-4o Vision extracts deals
         ↓
4. Generate deals.json
         ↓
5. Run ingest_data.py
         ↓
6. Populate Weaviate
         ↓
7. Start DealZen App
```

---

## 📋 Step-by-Step Instructions

### Step 1: Prepare Your Flyer Images

1. **Collect flyer images** (screenshots, PDFs converted to images, scanned flyers)
2. **Supported formats:** `.png`, `.jpg`, `.jpeg`
3. **Place them** in the `flyer-images/` folder

**Recommended naming convention:**
```
bestbuy_blackfriday_2025_page1.jpg
walmart_thanksgiving_deals.png
target_cyber_monday_electronics.jpg
```

### Step 2: Verify Your Environment

Ensure your OpenAI API key is configured:

```bash
# Check that backend/.env has your API key
cat backend/.env

# Should contain:
# OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Run the Flyer Processing Script

```bash
cd scripts
python process_flyers.py
```

**What happens:**
- Script reads all images from `flyer-images/`
- Each image is sent to GPT-4o Vision API
- AI extracts all deals from each flyer
- Results are compiled into `scripts/deals.json`

**Example output:**
```
--- Starting DealZen Flyer Processing Script ---
--- Processing: bestbuy_blackfriday.jpg ---
[API Call] Sending bestbuy_blackfriday.jpg to GPT-4o Vision...
[API Call] Received response for bestbuy_blackfriday.jpg.
   > Extracted 12 deals from bestbuy_blackfriday.jpg.
--------------------
--- Processing: walmart_deals.png ---
[API Call] Sending walmart_deals.png to GPT-4o Vision...
[API Call] Received response for walmart_deals.png.
   > Extracted 8 deals from walmart_deals.png.
--------------------

--- SUCCESS ---
Total deals extracted: 20
All deals saved to: ./scripts/deals.json
```

### Step 4: Review the Extracted Deals (Optional)

```bash
# View the generated deals.json
cat scripts/deals.json

# Or use jq for pretty formatting
cat scripts/deals.json | jq '.'
```

**Check for:**
- Correct pricing
- Accurate product names
- Valid store names
- Proper date formatting

**Edit if needed:** You can manually correct any errors in `deals.json` before ingestion.

### Step 5: Ingest Deals into Weaviate

```bash
cd scripts
python ingest_data.py
```

**Expected output:**
```
Successfully ingested 20 deals.
```

### Step 6: Start Your Application

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Now your DealZen app is ready with all the extracted deals!

---

## 🎯 How the Extraction Works

### GPT-4o Vision Prompt

The script uses a carefully crafted "mega-prompt" that instructs GPT-4o Vision to:

1. **Find all deals** on the flyer
2. **Extract structured data** for each deal:
   - Product name
   - SKU/model number
   - Price (sale and original)
   - Store name
   - Valid dates
   - Deal conditions
   - Product attributes
3. **Return JSON only** (no extra text)
4. **Be precise** with numbers and dates

### Model Configuration

```python
model="gpt-4o"           # Vision-capable model
max_tokens=4096          # Enough space for many deals
temperature=0.1          # Low for accuracy, not creativity
```

---

## 💰 Cost Considerations

### GPT-4o Vision Pricing (as of 2025)

- **Input:** ~$2.50 per 1M tokens
- **Output:** ~$10 per 1M tokens

**Typical flyer processing:**
- 1 flyer image ≈ 1,000-2,000 input tokens
- Response with 10 deals ≈ 500-1,000 output tokens
- **Cost per flyer:** ~$0.01 - $0.03

**100 flyer pages = ~$1-3 in API costs**

### Tips to Optimize Costs

1. **Batch process** all flyers at once
2. **Use high-quality images** (reduces retry needs)
3. **Review results** before re-processing
4. **Keep original flyers** to avoid re-processing

---

## 🔧 Script Configuration

### Configuration Variables

Located at the top of `scripts/process_flyers.py`:

```python
INPUT_FOLDER = './flyer-images'           # Where flyer images are stored
OUTPUT_FILE = './scripts/deals.json'      # Where results are saved
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # From backend/.env
```

### Customizing the Extraction Prompt

If you need different fields or stricter rules, edit the `EXTRACTION_SYSTEM_PROMPT` in `process_flyers.py`.

---

## 🐛 Troubleshooting

### Error: "OPENAI_API_KEY not found in backend/.env file"

**Solution:**
```bash
# Check your .env file
cat backend/.env

# Make sure it contains:
OPENAI_API_KEY=sk-your-actual-key-here

# No quotes, no spaces around the =
```

### Error: "Input folder not found: ./flyer-images"

**Solution:**
```bash
# Create the folder
mkdir -p flyer-images

# Verify it exists
ls -la | grep flyer-images
```

### Error: "File X is not a valid image"

**Solution:**
- Ensure the file is actually an image (`.png`, `.jpg`, `.jpeg`)
- Try opening it with an image viewer to verify it's not corrupted
- Convert PDFs to images first using a tool like ImageMagick

### GPT-4o Returns Empty or Invalid JSON

**Possible causes:**
1. Flyer image is too blurry or low quality
2. Flyer doesn't contain standard retail deals
3. API timeout or error

**Solutions:**
- Use higher resolution images
- Check the error message in the console
- Try processing the flyer again
- Manually add deals to `deals.json` if needed

### Deals are Inaccurate

**If prices or names are wrong:**
1. **Check image quality** - use higher resolution
2. **Edit `deals.json` manually** - it's just a JSON file
3. **Adjust the prompt** - make instructions more specific
4. **Re-process** after edits

---

## 📁 File Structure

```
DealZen_CodeBase/
├── flyer-images/                    # Place your flyer images here
│   ├── README.md
│   ├── bestbuy_blackfriday.jpg
│   └── walmart_deals.png
├── scripts/
│   ├── process_flyers.py           # ⭐ The flyer processing script
│   ├── deals.json                  # Generated output
│   └── ingest_data.py              # Loads deals.json into Weaviate
└── backend/
    └── .env                        # Contains OPENAI_API_KEY
```

---

## 🎨 Example: Processing a Best Buy Flyer

**1. Add flyer:**
```bash
cp ~/Downloads/bestbuy_blackfriday.jpg flyer-images/
```

**2. Run script:**
```bash
cd scripts
python process_flyers.py
```

**3. Output in `deals.json`:**
```json
[
  {
    "product_name": "Samsung 55\" QLED TV (QN55Q80C)",
    "sku": "QN55Q80CBUXA",
    "product_category": "Electronics > Televisions > QLED TVs",
    "price": 499.99,
    "original_price": 799.99,
    "store": "Best Buy",
    "valid_from": "2025-11-27T08:00:00",
    "valid_to": "2025-11-28T23:59:59",
    "deal_type": "Black Friday Door Crasher",
    "in_store_only": true,
    "deal_conditions": ["Limit 1 per customer", "Valid from 8am"],
    "attributes": ["QLED", "55-inch", "4K", "Smart TV"]
  }
]
```

**4. Ingest:**
```bash
python ingest_data.py
```

**5. Start app and search:** "Show me TV deals under $500"

---

## 🚀 Production Tips

### For a 5-Day Black Friday Event

1. **Collect all flyers** in advance (Wednesday before)
2. **Process all at once** to batch API calls
3. **Review and correct** any extraction errors
4. **Ingest into Weaviate** Thursday evening
5. **Test queries** before event launch
6. **Keep flyers** for reference during event

### Quality Control Checklist

- [ ] All prices extracted correctly
- [ ] Store names are consistent
- [ ] Dates are in ISO 8601 format
- [ ] SKUs captured where available
- [ ] Deal conditions are clear
- [ ] Product categories make sense
- [ ] No duplicate deals

---

## 📚 Additional Resources

- **OpenAI Vision API Docs:** https://platform.openai.com/docs/guides/vision
- **Weaviate Documentation:** https://weaviate.io/developers/weaviate
- **DealZen Main README:** See `README.md` in project root

---

**Ready to process your flyers? Let's go! 🚀**

```bash
cd scripts
python process_flyers.py
```

