#!/bin/bash
# ================================================
# GAURANGA - Boot Startup Script
# ================================================
# Auto-start GAURANGA on system boot
# Add to crontab: @reboot bash /path/to/boot-startup.sh
# ================================================

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
DEPLOY_DIR="$APP_DIR/deploy"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$DEPLOY_DIR/gauranga.pid"
PORT=5000

# Log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_DIR/boot-startup.log
}

log "========================================="
log "GAURANGA Boot Startup - Initializing..."

# Wait for system services
sleep 5

# Check if already running
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    log "GAURANGA already running on port $PORT"
    exit 0
fi

# Create directories
mkdir -p $LOG_DIR

# Start server
log "Starting GAURANGA server..."
cd $APP_DIR
bash deploy/start.sh > /dev/null 2>&1 &

# Wait and verify
sleep 5

if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    log "✅ GAURANGA started successfully (PID: $PID)"
else
    log "❌ GAURANGA failed to start"
fi
