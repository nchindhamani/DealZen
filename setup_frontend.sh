#!/bin/bash

# DealZen Frontend Setup Script
echo "🚀 Setting up DealZen Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check Node version
NODE_VERSION=$(node --version)
echo "✓ Found Node.js version: $NODE_VERSION"

# Navigate to frontend directory
cd frontend || exit

# Install dependencies
echo "📥 Installing dependencies..."
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the development server: cd frontend && npm run dev"
echo "2. Open your browser to: http://localhost:5173"

