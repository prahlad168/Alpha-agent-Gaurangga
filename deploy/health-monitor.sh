#!/bin/bash
# ================================================
# GAURANGA - Health Monitor & Auto-Restart
# ================================================
# Monitors server health and auto-restarts if down
# Run in cron: */5 * * * * bash /path/to/health-monitor.sh
# ================================================

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
DEPLOY_DIR="$APP_DIR/deploy"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$DEPLOY_DIR/gauranga.pid"
PORT=5000
HEALTH_URL="http://localhost:$PORT/api/health"

# Log file
LOG_FILE="$LOG_DIR/health-monitor.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# Check if server is running
check_server() {
    # Check if PID file exists
    if [ ! -f "$PID_FILE" ]; then
        log "⚠️ PID file not found"
        return 1
    fi
    
    PID=$(cat $PID_FILE)
    
    # Check if process is running
    if ! ps -p $PID > /dev/null 2>&1; then
        log "⚠️ Process $PID not running"
        return 1
    fi
    
    # Check if port is listening
    if ! lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log "⚠️ Port $PORT not listening"
        return 1
    fi
    
    # Check health endpoint
    HEALTH=$(curl -s $HEALTH_URL 2>/dev/null)
    if echo "$HEALTH" | grep -q "healthy"; then
        log "✅ Server healthy"
        return 0
    else
        log "⚠️ Health check failed: $HEALTH"
        return 1
    fi
}

# Restart server
restart_server() {
    log "🔄 Restarting GAURANGA server..."
    
    # Stop existing
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        kill $PID 2>/dev/null || true
        sleep 2
    fi
    
    # Kill any process on port
    lsof -Pi :$PORT -sTCP:LISTEN -t | xargs kill 2>/dev/null || true
    sleep 1
    
    # Start new server
    cd $APP_DIR
    bash deploy/start.sh > /dev/null 2>&1
    
    sleep 3
    
    # Verify restart
    if check_server; then
        log "✅ Server restarted successfully"
    else
        log "❌ Server restart failed"
    fi
}

# Main
log "========================================="
log "Health check started"

if check_server; then
    echo -e "${GREEN}✅ Server healthy${NC}"
else
    echo -e "${YELLOW}⚠️ Server unhealthy, restarting...${NC}"
    restart_server
fi
