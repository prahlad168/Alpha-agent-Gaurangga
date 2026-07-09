#!/bin/bash
# GAURANGA Alpha - Start Server Script
# Usage: ./start-gauranga.sh [port]

PORT=${1:-5000}

echo "=========================================="
echo "  🚀 GAURANGA ALPHA - STARTUP"
echo "=========================================="

# Check for API keys
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set"
    echo "    AI will run in FALLBACK mode"
    echo ""
    echo "    To enable AI, run:"
    echo "    export GEMINI_API_KEY='your-key'"
    echo "    Get free key: https://aistudio.google.com/apikey"
    echo ""
fi

# Kill existing server
pkill -f "python.*deploy_server" 2>/dev/null || true
sleep 1

# Start server
cd "$(dirname "$0")/server"
echo "📍 Starting server on port $PORT..."
nohup python deploy_server.py > gauranga.log 2>&1 &
sleep 2

# Check if running
if curl -s http://localhost:$PORT/api/health > /dev/null 2>&1; then
    echo ""
    echo "✅ GAURANGA Alpha is ONLINE!"
    echo ""
    echo "=========================================="
    echo "  🌐 ACCESS URLs"
    echo "=========================================="
    echo "  Main App:    http://localhost:$PORT"
    echo "  Android:     http://localhost:$PORT/android"
    echo "  Finance:     http://localhost:$PORT/finance"
    echo "  API Status:  http://localhost:$PORT/api/status"
    echo "=========================================="
    echo ""
    echo "📝 Logs: server/gauranga.log"
else
    echo "❌ Failed to start server"
    echo "📝 Check: server/gauranga.log"
fi
