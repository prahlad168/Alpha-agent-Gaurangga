#!/bin/bash
# ================================================
# GAURANGA - Auto-Start Script (rc.local style)
# ================================================
# For systems without systemd or development use
# Add to /etc/rc.local or crontab
# ================================================

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
SERVER_DIR="$APP_DIR/server"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$APP_DIR/deploy/gauranga.pid"
PORT=5000

# Wait for system to be ready
sleep 10

# Check if already running
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "GAURANGA already running on port $PORT"
    exit 0
fi

# Create directories
mkdir -p $LOG_DIR

# Start server
cd $SERVER_DIR
source venv/bin/activate
nohup python3 gauranga_server.py > $LOG_DIR/gauranga.log 2>&1 &
echo $! > $PID_FILE

echo "GAURANGA started on port $PORT (PID: $(cat $PID_FILE))"
