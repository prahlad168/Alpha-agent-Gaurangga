#!/bin/bash

# ================================================
# GAURANGA - Revenue System Startup Script
# ================================================

echo "🚀 GAURANGA Revenue System Starting..."

# Change to server directory
cd "$(dirname "$0")"

# Create data directory if not exists
mkdir -p data

# Install dependencies if needed
if ! pip show flask flask-cors > /dev/null 2>&1; then
    echo "📦 Installing dependencies..."
    pip install flask flask-cors --quiet
fi

# Kill any existing instances
pkill -f "revenue_api.py" 2>/dev/null || true
sleep 1

# Start the server
echo "🌐 Starting Revenue API Server on port 5001..."
echo ""
echo "📊 API Endpoints:"
echo "   • GET  http://localhost:5001/api/sbu"
echo "   • GET  http://localhost:5001/api/revenue/dashboard"
echo "   • POST http://localhost:5001/api/quick/income"
echo "   • POST http://localhost:5001/api/quick/expense"
echo ""
echo "📱 Dashboard: dashboard-revenue.html"
echo ""

# Run in background
nohup python3 revenue_api.py > ../logs/revenue-server.log 2>&1 &
REVENUE_PID=$!

echo "✅ Revenue API started (PID: $REVENUE_PID)"
echo "📝 Logs: ../logs/revenue-server.log"

# Save PID
echo $REVENUE_PID > ../deploy/revenue.pid

# Also start AI server if exists
if [ -f "gauranga_server.py" ]; then
    echo ""
    echo "🤖 Starting GAURANGA AI Server on port 5000..."
    nohup python3 gauranga_server.py > ../logs/ai-server.log 2>&1 &
    AI_PID=$!
    echo "✅ AI Server started (PID: $AI_PID)"
fi

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "📋 Quick Commands:"
echo "   • View logs:     tail -f ../logs/revenue-server.log"
echo "   • Stop server:  ./stop-revenue.sh"
echo "   • Dashboard:    open dashboard-revenue.html"
echo ""
