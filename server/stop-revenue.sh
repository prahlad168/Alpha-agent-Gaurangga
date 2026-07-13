#!/bin/bash

# ================================================
# GAURANGA - Stop Revenue Server
# ================================================

echo "🛑 Stopping GAURANGA Revenue System..."

# Kill by PID file
if [ -f "../deploy/revenue.pid" ]; then
    PID=$(cat ../deploy/revenue.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ Revenue API stopped (PID: $PID)"
    fi
    rm ../deploy/revenue.pid
fi

# Kill any remaining instances
pkill -f "revenue_api.py" 2>/dev/null || true

echo "✅ All services stopped"
