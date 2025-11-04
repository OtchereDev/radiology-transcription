#!/bin/bash
set -e

echo "Deploying to production..."

# Check if running on GPU instance
if ! command -v nvidia-smi &> /dev/null; then
    echo "⚠️  Warning: GPU not detected!"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Pull latest code
git pull origin main

# Build images
docker compose build

# Stop old containers
docker compose down

# Start new containers
docker compose up -d

# Wait for health check
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check health
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✓ Deployment successful!"
    echo ""
    docker compose ps
else
    echo "✗ Health check failed!"
    echo "Check logs: docker-compose logs"
    exit 1
fi