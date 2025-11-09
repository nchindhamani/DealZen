#!/bin/bash

# DealZen Complete Setup Script
echo "╔══════════════════════════════════════════╗"
echo "║      DealZen Complete Setup Script       ║"
echo "║   AI Shopping Assistant - Black Friday   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check for required tools
echo "🔍 Checking prerequisites..."

MISSING_TOOLS=()

if ! command -v python3 &> /dev/null; then
    MISSING_TOOLS+=("Python 3.9+")
fi

if ! command -v node &> /dev/null; then
    MISSING_TOOLS+=("Node.js 18+")
fi

if ! command -v docker &> /dev/null; then
    MISSING_TOOLS+=("Docker")
fi

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo "❌ Missing required tools:"
    for tool in "${MISSING_TOOLS[@]}"; do
        echo "   - $tool"
    done
    echo ""
    echo "Please install the missing tools and run this script again."
    exit 1
fi

echo "✅ All prerequisites found!"
echo ""

# Step 1: Start Weaviate
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/4: Starting Weaviate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./start_weaviate.sh
echo ""

# Step 2: Setup Backend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/4: Setting up Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./setup_backend.sh
echo ""

# Step 3: Setup Frontend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/4: Setting up Frontend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./setup_frontend.sh
echo ""

# Step 4: Instructions for .env
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/4: Final Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANT: Before running the application, you need to:"
echo ""
echo "1. Add your OpenAI API key to backend/.env"
echo "   Open the file and replace 'your_openai_api_key_here'"
echo ""
echo "2. Ingest sample data:"
echo "   cd scripts && python ingest_data.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:5173"
echo ""
echo "📖 For more information, see README.md or QUICKSTART.md"

