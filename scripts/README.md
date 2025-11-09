# DealZen Scripts Directory

This directory contains the data processing scripts for DealZen.

## Scripts Overview

### 1. `process_flyers.py` 🆕 (Offline Flyer Processing)

**Purpose:** Automatically extract deal information from retail flyer images using GPT-4o Vision API.

**Usage:**
```bash
cd scripts
python process_flyers.py
```

**What it does:**
- Reads all images (`.jpg`, `.jpeg`, `.png`) from `../flyer-images/`
- Sends each image to GPT-4o Vision API
- Extracts structured deal data (product name, price, store, etc.)
- Compiles results into `deals.json`

**Requirements:**
- OpenAI API key in `../backend/.env`
- Flyer images in `../flyer-images/`
- Internet connection (for API calls)

**Output:** `deals.json` (structured deal data)

📖 **Full guide:** See [`../FLYER_PROCESSING_GUIDE.md`](../FLYER_PROCESSING_GUIDE.md)

---

### 2. `ingest_data.py` (Weaviate Data Ingestion)

**Purpose:** Load deal data from JSON into Weaviate vector database.

**Usage:**
```bash
cd scripts
python ingest_data.py
```

**What it does:**
- Reads deals from `deals.json` (or falls back to `deals.example.json`)
- Creates/recreates the "Deal" collection in Weaviate
- Generates rich `vector_text` for semantic search
- Batch inserts all deals into Weaviate

**Requirements:**
- Weaviate running on localhost:8080
- OpenAI API key (for vectorization)
- Valid `deals.json` file

**Output:** Populated Weaviate database

---

## Complete Workflow

```
Step 1: Add Flyer Images
   Place retail flyer images in ../flyer-images/
        ↓
Step 2: Extract Deals
   python process_flyers.py
        ↓
Step 3: Ingest into Weaviate
   python ingest_data.py
        ↓
Step 4: Start Application
   Backend + Frontend
```

---

## Data Files

### `deals.json` (Generated)
- Created by `process_flyers.py`
- Contains extracted deals from flyer images
- Read by `ingest_data.py`
- **Note:** This file is generated, not version controlled

### `deals.example.json` (Sample Data)
- Contains 2 sample deals (Samsung TV, Ninja Airfryer)
- Used for testing and as a schema reference
- Fallback if `deals.json` doesn't exist

---

## Schema Reference

Each deal must have this structure:

```json
{
  "product_name": "string (required)",
  "sku": "string or null",
  "product_category": "string or null",
  "price": "float (required)",
  "original_price": "float or null",
  "store": "string (required)",
  "valid_from": "string (ISO 8601) or null",
  "valid_to": "string (ISO 8601) or null",
  "deal_type": "string (required)",
  "in_store_only": "boolean (required)",
  "deal_conditions": ["list", "of", "strings"],
  "attributes": ["list", "of", "features"]
}
```

---

## Troubleshooting

### `process_flyers.py` Issues

**Error: "OPENAI_API_KEY not found"**
```bash
# Check your .env file
cat ../backend/.env

# Should contain:
OPENAI_API_KEY=sk-your-actual-key-here
```

**Error: "Input folder not found"**
```bash
# Create the folder
mkdir -p ../flyer-images

# Add some images
cp ~/Downloads/flyer.jpg ../flyer-images/
```

### `ingest_data.py` Issues

**Error: Connection refused to Weaviate**
```bash
# Start Weaviate
docker run -d -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  weaviate/weaviate:latest

# Check it's running
curl http://localhost:8080/v1/.well-known/ready
```

**Error: "No such file: deals.json"**
```bash
# Either run process_flyers.py first, or use the example data
cp deals.example.json deals.json
```

---

## Dependencies

Both scripts require:
- `openai` (for GPT-4o/GPT-4o Vision)
- `weaviate-client` (for vector database)
- `python-dotenv` (for environment variables)

Install with:
```bash
cd ../backend
pip install -r requirements.txt
```

---

## Cost Estimation

### Flyer Processing (`process_flyers.py`)
- **GPT-4o Vision:** ~$0.01-0.03 per flyer page
- **100 pages:** ~$1-3 in API costs

### Vectorization (`ingest_data.py`)
- **OpenAI Embeddings:** ~$0.0001 per deal
- **1000 deals:** ~$0.10 in API costs

**Total for 100 flyers with 1000 deals: ~$1-4**

---

## Quick Reference

```bash
# Process flyers
cd scripts
python process_flyers.py

# Ingest data
python ingest_data.py

# Check results in Weaviate
curl http://localhost:8080/v1/schema
```

---

**Need help? Check the main project documentation:**
- [FLYER_PROCESSING_GUIDE.md](../FLYER_PROCESSING_GUIDE.md) - Detailed flyer processing
- [README.md](../README.md) - Complete project documentation
- [QUICKSTART.md](../QUICKSTART.md) - 5-minute setup guide

