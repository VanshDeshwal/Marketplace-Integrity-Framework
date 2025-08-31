#!/bin/bash
# Deployment script for Marketplace Integrity Framework

set -e

echo "🚀 Starting deployment of Marketplace Integrity Framework"

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t marketplace-integrity-backend:latest ./backend

# Stop existing container if running
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Start the services
echo "🔄 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/health; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed"
    docker-compose logs backend
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "📊 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
