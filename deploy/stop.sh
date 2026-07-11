#!/bin/bash
# ================================================
# GAURANGA - Stop Script
# ================================================

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
PID_FILE="$APP_DIR/deploy/gauranga.pid"
SERVER_PORT=5000

echo "🛑 Stopping GAURANGA..."

# Kill by PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping process $PID..."
        kill $PID 2>/dev/null || true
        sleep 2
    fi
    rm $PID_FILE
    echo "✅ PID file removed"
fi

# Kill by port
if lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Killing process on port $SERVER_PORT..."
    lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t | xargs kill 2>/dev/null || true
fi

echo "✅ GAURANGA stopped!"
