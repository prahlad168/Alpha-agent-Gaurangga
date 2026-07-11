#!/bin/bash
# ================================================
# GAURANGA - Start Script
# ================================================

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
SERVER_DIR="$APP_DIR/server"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$APP_DIR/deploy/gauranga.pid"
SERVER_PORT=5000

echo "🚀 Starting GAURANGA..."

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  GAURANGA is already running (PID: $PID)"
        echo "   Use 'restart.sh' to restart"
        exit 1
    fi
fi

# Check if port is in use
if lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $SERVER_PORT is in use"
    echo "   Stopping existing process..."
    lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t | xargs kill 2>/dev/null || true
    sleep 2
fi

# Check venv exists
if [ ! -d "$SERVER_DIR/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd $SERVER_DIR
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Create logs directory
mkdir -p $LOG_DIR

# Start server
cd $SERVER_DIR
source venv/bin/activate

nohup python3 gauranga_server.py > $LOG_DIR/gauranga.log 2>&1 &
echo $! > $PID_FILE

# Wait for startup
sleep 3

# Check if running
if ps -p $(cat $PID_FILE) > /dev/null 2>&1; then
    echo ""
    echo "============================================"
    echo "   🚀 GAURANGA STARTED SUCCESSFULLY! 🚀"
    echo "============================================"
    echo ""
    echo "   📡 Endpoints:"
    echo "      • Health:  http://localhost:$SERVER_PORT/api/health"
    echo "      • Status:  http://localhost:$SERVER_PORT/api/status"
    echo "      • Chat:    POST http://localhost:$SERVER_PORT/api/chat"
    echo ""
    echo "   📝 Logs: tail -f $LOG_DIR/gauranga.log"
    echo "   🛑 Stop:    bash $APP_DIR/deploy/stop.sh"
    echo "   🔄 Restart: bash $APP_DIR/deploy/restart.sh"
    echo ""
else
    echo "❌ Failed to start GAURANGA!"
    echo "   Check logs: $LOG_DIR/gauranga.log"
    exit 1
fi
