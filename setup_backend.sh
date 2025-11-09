#!/bin/bash

# DealZen Backend Setup Script
echo "🚀 Setting up DealZen Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python version: $PYTHON_VERSION"

# Navigate to backend directory
cd backend || exit

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit backend/.env and add your OpenAI API key!"
    echo "   Open backend/.env and replace 'your_openai_api_key_here' with your actual key."
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Start Weaviate: docker run -d -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true weaviate/weaviate:latest"
echo "3. Ingest data: cd scripts && python ingest_data.py"
echo "4. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"

