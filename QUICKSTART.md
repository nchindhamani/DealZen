# DealZen Quick Start Guide

Get DealZen up and running in 5 minutes!

## Prerequisites Check

```bash
# Verify Python version (need 3.9+)
python --version

# Verify Node.js version (need 18+)
node --version

# Verify Docker is installed
docker --version
```

## Step 1: Start Weaviate (30 seconds)

```bash
docker run -d \
  -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  weaviate/weaviate:latest
```

Verify Weaviate is running:
```bash
curl http://localhost:8080/v1/.well-known/ready
# Should return: {"status":"ok"}
```

## Step 2: Setup Backend (2 minutes)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI API key
cp .env.example .env
# Edit .env and add your OpenAI API key
```

**Important:** Edit `.env` and replace `your_openai_api_key_here` with your actual OpenAI API key.

## Step 3: Ingest Sample Data (30 seconds)

### Option A: Use Example Data (Quick Test)

```bash
# From the project root
cd scripts
python ingest_data.py
```

Expected output: `Successfully ingested 2 deals.`

### Option B: Process Your Own Flyers (Production)

```bash
# 1. Add flyer images
cp ~/Downloads/your_flyer.jpg flyer-images/

# 2. Extract deals using GPT-4o Vision
cd scripts
python process_flyers.py

# 3. Ingest extracted deals
python ingest_data.py
```

📖 **For detailed flyer processing, see:** [`FLYER_PROCESSING_GUIDE.md`](FLYER_PROCESSING_GUIDE.md)

## Step 4: Start Backend (10 seconds)

```bash
cd ../backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal running. Backend is ready when you see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Setup Frontend (1 minute)

Open a **new terminal**:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Expected output:
```
  VITE v5.0.11  ready in 500 ms

  ➜  Local:   http://localhost:5173/
```

## Step 6: Test the App!

1. Open your browser to: `http://localhost:5173`
2. You should see the DealZen chat interface
3. Try these example queries:
   - "Show me TV deals"
   - "What's on sale at Walmart?"
   - "Air fryer deals under $150"

## Troubleshooting

### Backend won't start
- **Error:** `ModuleNotFoundError: No module named 'weaviate'`
- **Fix:** Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

### Can't connect to Weaviate
- **Error:** Connection refused to localhost:8080
- **Fix:** Make sure Docker container is running: `docker ps | grep weaviate`

### Frontend shows "Network Error"
- **Fix:** Make sure backend is running on port 8000
- **Check:** Visit `http://localhost:8000/docs` to see FastAPI documentation

### No search results
- **Fix:** Run the ingestion script again: `cd scripts && python ingest_data.py`

## Next Steps

- Add more deals to `scripts/deals.example.json`
- Customize the theme in `frontend/tailwind.config.js`
- Read the full README.md for production deployment

## Quick Commands Reference

```bash
# Start Weaviate
docker start <container-id>

# Stop Weaviate
docker stop <container-id>

# Backend (from /backend)
uvicorn app.main:app --reload

# Frontend (from /frontend)
npm run dev

# Ingest data (from /scripts)
python ingest_data.py
```

---

**Need help?** Check the main README.md for detailed documentation.

