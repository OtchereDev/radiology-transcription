#!/bin/bash
set -e

echo "Building Medical Dictation Streaming..."

# Build the image
docker compose build --no-cache

echo ""
echo "✓ Build complete!"
echo ""
echo "To run: ./scripts/run.sh"