#!/bin/bash
# ================================================
# GAURANGA - Restart Script
# ================================================

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"

echo "🔄 Restarting GAURANGA..."

# Stop
bash $APP_DIR/deploy/stop.sh

# Wait
sleep 2

# Start
bash $APP_DIR/deploy/start.sh
