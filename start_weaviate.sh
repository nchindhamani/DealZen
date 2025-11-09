#!/bin/bash

# DealZen Weaviate Startup Script
echo "🚀 Starting Weaviate vector database..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Weaviate container is already running
EXISTING_CONTAINER=$(docker ps -q -f name=weaviate)

if [ ! -z "$EXISTING_CONTAINER" ]; then
    echo "✓ Weaviate is already running (Container ID: $EXISTING_CONTAINER)"
    exit 0
fi

# Check if Weaviate container exists but is stopped
STOPPED_CONTAINER=$(docker ps -aq -f name=weaviate)

if [ ! -z "$STOPPED_CONTAINER" ]; then
    echo "🔄 Starting existing Weaviate container..."
    docker start $STOPPED_CONTAINER
    echo "✅ Weaviate started successfully!"
else
    # Start new Weaviate container
    echo "📦 Creating and starting new Weaviate container..."
    docker run -d \
      --name weaviate \
      -p 8080:8080 \
      -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
      -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
      weaviate/weaviate:latest
    
    echo "✅ Weaviate started successfully!"
fi

# Wait for Weaviate to be ready
echo "⏳ Waiting for Weaviate to be ready..."
sleep 5

# Check if Weaviate is responding
if curl -s http://localhost:8080/v1/.well-known/ready | grep -q "ok"; then
    echo "✅ Weaviate is ready!"
    echo "🌐 Weaviate is running at: http://localhost:8080"
else
    echo "⚠️  Weaviate is starting but not ready yet. Please wait a moment and try again."
fi

