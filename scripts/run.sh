#!/bin/bash
set -e

echo "Starting Medical Dictation Streaming..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start services
docker compose up -d

echo ""
echo "✓ Services started!"
echo ""
echo "Access the application at: http://localhost"
echo "Health check: http://localhost/health"
echo "Stats: http://localhost/stats"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop services: docker-compose down"