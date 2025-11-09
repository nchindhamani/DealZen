# DealZen - AI Shopping Assistant

A production-ready Black Friday AI Shopping Assistant powered by RAG (Retrieval-Augmented Generation), featuring hybrid search with Weaviate and GPT-4o.

## 🏗️ Architecture

- **Backend:** FastAPI with RAG pipeline
- **Vector Database:** Weaviate (Hybrid Search: Vector + Keyword)
- **AI Model:** GPT-4o for answer generation
- **Frontend:** React + Vite + Tailwind CSS (Premium Indigo/Violet theme)
- **Strategy:** Per-deal semantic chunking, Top 5 results retrieval

## 📁 Project Structure

```
DealZen/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app with /chat endpoint
│   │   ├── rag_pipeline.py      # RAG logic using GPT-4o
│   │   ├── weaviate_client.py   # Weaviate connection & hybrid search
│   │   └── schemas.py           # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatInterface.jsx
│   │   ├── hooks/
│   │   │   └── useUserLimits.js
│   │   ├── App.jsx
│   │   ├── index.jsx
│   │   ├── apiClient.js
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── scripts/
│   ├── process_flyers.py       # GPT-4o Vision flyer extraction (offline)
│   ├── ingest_data.py          # Weaviate data ingestion
│   ├── deals.json              # Generated from process_flyers.py
│   └── deals.example.json      # Sample deal data
└── flyer-images/               # Place flyer images here for processing
    └── README.md
```

## 🔄 Complete Workflow

DealZen has two main phases:

### Phase 1: Offline Flyer Processing (Before Launch)
1. **Collect flyer images** → Place in `flyer-images/`
2. **Run `process_flyers.py`** → GPT-4o Vision extracts deals
3. **Generate `deals.json`** → Structured deal data
4. **Run `ingest_data.py`** → Populate Weaviate vector database

### Phase 2: Live Application (During Event)
1. **Users ask questions** → Frontend sends to backend
2. **Hybrid search** → Weaviate finds top 5 relevant deals
3. **GPT-4o generates answer** → Contextual response
4. **Display results** → Deal cards with pricing

📖 **For detailed flyer processing instructions, see [`FLYER_PROCESSING_GUIDE.md`](FLYER_PROCESSING_GUIDE.md)**

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker (for Weaviate)
- OpenAI API Key

### 1. Start Weaviate

Run Weaviate locally using Docker:

```bash
docker run -d \
  -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  weaviate/weaviate:latest
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
WEAVIATE_URL=http://localhost:8080
OPENAI_API_KEY=your_openai_api_key_here
EOF
```

**Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 3. Ingest Sample Data

```bash
# From the project root directory
cd scripts
python ingest_data.py
```

This will populate Weaviate with the sample deals from `deals.example.json`.

### 4. Start Backend

```bash
cd ../backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### 5. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 🎯 Features

### User Limits
- **10 questions per user** (tracked via localStorage)
- **250 character limit** on queries
- Question counter displayed in header

### Search Strategy
- **Hybrid Search:** 50/50 blend of vector and keyword search
- **Top 5 Results:** Returns the 5 most relevant deals
- **Semantic Chunking:** Each deal is a complete semantic unit

### UI/UX
- Mobile-first responsive design
- Premium Indigo/Violet theme
- Beautiful deal cards with pricing
- Auto-scrolling chat interface
- Loading states and error handling

## 🔧 Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
WEAVIATE_URL=http://localhost:8080
OPENAI_API_KEY=sk-...your-key-here...
```

### Frontend API Configuration

The frontend is configured to connect to `http://localhost:8000`. If your backend runs on a different port, update `frontend/src/apiClient.js`:

```javascript
const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // Change this if needed
});
```

## 📊 Data Schema

Each deal follows this structure:

```json
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
```

## 🧪 Testing the Application

1. Open `http://localhost:5173` in your browser
2. Try example queries:
   - "Show me TV deals"
   - "What air fryers are on sale?"
   - "Best Buy deals under $500"
   - "Online-only kitchen appliances"

## 🔄 Adding More Deals

### Option 1: Automated (Recommended) - Process Flyer Images

Use GPT-4o Vision to automatically extract deals from retail flyer images:

```bash
# 1. Add flyer images to the folder
cp ~/Downloads/bestbuy_flyer.jpg flyer-images/

# 2. Run the flyer processing script
cd scripts
python process_flyers.py

# 3. Ingest the extracted deals
python ingest_data.py
```

**See the complete guide:** [`FLYER_PROCESSING_GUIDE.md`](FLYER_PROCESSING_GUIDE.md)

### Option 2: Manual - Edit JSON Directly

1. Edit `scripts/deals.json` directly
2. Follow the schema structure (see Data Schema section)
3. Run the ingestion script:

```bash
cd scripts
python ingest_data.py
```

## 🛠️ Production Deployment

### Backend
- Use production ASGI server: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
- Set up environment variables securely
- Use managed Weaviate instance (Weaviate Cloud Services)

### Frontend
```bash
cd frontend
npm run build
# Deploy the 'dist' folder to your hosting service
```

## 📝 API Endpoints

### POST `/chat`

**Request:**
```json
{
  "query": "What TV deals do you have?"
}
```

**Response:**
```json
{
  "answer": "I found some great TV deals for you...",
  "source_deals": [
    { /* deal object */ }
  ]
}
```

## 🎨 Customization

### Changing Theme Colors

Edit `frontend/tailwind.config.js` to customize the color scheme:

```javascript
colors: {
  indigo: {
    // Customize these values
  }
}
```

### Adjusting Question Limits

Change the limit in `frontend/src/components/ChatInterface.jsx`:

```javascript
const { hasReachedLimit, remainingQuestions, incrementCount } = useUserLimits(10); // Change 10 to desired limit
```

## 🐛 Troubleshooting

**Issue:** Backend fails to connect to Weaviate
- **Solution:** Ensure Weaviate Docker container is running: `docker ps`

**Issue:** Frontend can't reach backend
- **Solution:** Check CORS settings in `backend/app/main.py` and ensure backend is running on port 8000

**Issue:** No search results returned
- **Solution:** Verify data was ingested: Check Weaviate at `http://localhost:8080/v1/schema`

## 📄 License

MIT

## 👥 Support

For issues or questions, please check the documentation or contact support.

---

**Built with ❤️ for Black Friday 2025**

