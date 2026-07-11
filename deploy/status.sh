#!/bin/bash
# ================================================
# GAURANGA - Status Script
# ================================================

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
PID_FILE="$APP_DIR/deploy/gauranga.pid"
LOG_DIR="$APP_DIR/logs"
SERVER_PORT=5000

echo "📊 GAURANGA Status"
echo "============================================"

# Check PID
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Status:     ✅ RUNNING"
        echo "PID:        $PID"
        echo "Port:       $SERVER_PORT"
        echo "Started:    $(ps -o lstart= -p $PID)"
        
        # Memory usage
        MEM=$(ps -o rss= -p $PID | awk '{printf "%.1f MB", $1/1024}')
        echo "Memory:     $MEM"
        
        # Uptime
        UPTIME=$(ps -o etime= -p $PID | xargs)
        echo "Uptime:     $UPTIME"
    else
        echo "Status:     ❌ NOT RUNNING (stale PID file)"
        echo "PID File:   $PID_FILE"
    fi
else
    echo "Status:     ❌ NOT RUNNING"
    echo "PID File:   Not found"
fi

echo ""
echo "📁 Directories:"
echo "   App:      $APP_DIR"
echo "   Logs:     $LOG_DIR"
echo "   Log File: $LOG_DIR/gauranga.log"

echo ""
echo "🌐 Endpoints:"
echo "   • http://localhost:$SERVER_PORT/api/health"
echo "   • http://localhost:$SERVER_PORT/api/status"

# Health check if curl available
if command -v curl &> /dev/null; then
    echo ""
    echo "🏥 Health Check:"
    RESPONSE=$(curl -s http://localhost:$SERVER_PORT/api/health 2>/dev/null || echo '{"status":"error"}')
    echo "   $RESPONSE"
fi

echo ""
