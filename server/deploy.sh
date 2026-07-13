#!/bin/bash

# ================================================
# GAURANGA - Full Deployment Script
# ================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║     🚀 GAURANGA FULL DEPLOYMENT             ║"
echo "║     Revenue System - Production Ready        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Configuration
SERVER_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SERVER_DIR")"
LOG_DIR="$PROJECT_DIR/logs"

# Create directories
echo "📁 Creating directories..."
mkdir -p "$LOG_DIR"
mkdir -p "$SERVER_DIR/data"

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install flask flask-cors --quiet --break-system-packages

# Create database
echo "🗄️  Initializing database..."
cd "$SERVER_DIR"
python3 -c "
import sys
sys.path.insert(0, '.')
from database import db
print('✅ Database initialized')
"

# Start Revenue API
echo "🚀 Starting Revenue API Server..."
cd "$SERVER_DIR"

# Kill existing
pkill -f "revenue_api.py" 2>/dev/null || true
sleep 1

# Start server
nohup python3 revenue_api.py > "$LOG_DIR/revenue-server.log" 2>&1 &
REVENUE_PID=$!

echo $REVENUE_PID > "$PROJECT_DIR/deploy/revenue.pid"

# Wait for server to start
sleep 2

# Check if server is running
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "✅ Revenue API running on port 5001"
else
    echo "❌ Revenue API failed to start"
    echo "Check logs: $LOG_DIR/revenue-server.log"
    exit 1
fi

# Create systemd service
echo "📝 Creating systemd service..."
cat > /tmp/gauranga-revenue.service << EOF
[Unit]
Description=GAURANGA Revenue API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SERVER_DIR
ExecStart=/usr/bin/python3 $SERVER_DIR/revenue_api.py
Restart=always
RestartSec=5
StandardOutput=append:$LOG_DIR/revenue-server.log
StandardError=append:$LOG_DIR/revenue-server.log

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║     ✅ DEPLOYMENT COMPLETE!                  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "📊 API Status:"
curl -s http://localhost:5001/api/status | python3 -m json.tool 2>/dev/null || echo "Checking..."
echo ""
echo "🌐 Endpoints:"
echo "   • Revenue API:  http://localhost:5001/api"
echo "   • Dashboard:   file://$PROJECT_DIR/dashboard-revenue.html"
echo ""
echo "📝 Commands:"
echo "   • View logs:   tail -f $LOG_DIR/revenue-server.log"
echo "   • Stop:        ./server/stop-revenue.sh"
echo "   • Restart:     ./server/start-revenue.sh"
echo ""
