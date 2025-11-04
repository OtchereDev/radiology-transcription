#!/bin/bash

echo "Medical Dictation Streaming - System Monitor"
echo "============================================="
echo ""

# Container status
echo "Container Status:"
docker-compose ps
echo ""

# GPU usage
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Usage:"
    nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total --format=csv,noheader,nounits
    echo ""
fi

# Memory usage
echo "Memory Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

# Service health
echo "Health Check:"
curl -s http://localhost/health | python3 -m json.tool
echo ""

# Active sessions
echo "Active Sessions:"
curl -s http://localhost/stats | python3 -m json.tool | grep -A 5 "current_active_sessions"
echo ""

# Recent logs
echo "Recent Logs (last 20 lines):"
docker compose logs --tail=20