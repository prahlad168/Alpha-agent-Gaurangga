#!/bin/bash
# ================================================
# GAURANGA - PRODUCTION DEPLOYMENT SCRIPT
# ================================================
# This script deploys GAURANGA to production
# Run as: bash deploy/production-deploy.sh
# ================================================

set -e

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
SERVER_DIR="$APP_DIR/server"
DEPLOY_DIR="$APP_DIR/deploy"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$DEPLOY_DIR/gauranga.pid"
PORT=5000

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}  🚀 GAURANGA PRODUCTION DEPLOYMENT${NC}"
echo -e "${GREEN}==============================================${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python3 not found${NC}"; exit 1; }
echo "✅ Python3 found"

# Step 2: Create directories
echo ""
echo -e "${YELLOW}[2/6] Creating directories...${NC}"
mkdir -p $LOG_DIR
mkdir -p $DEPLOY_DIR
echo "✅ Directories created"

# Step 3: Setup Python environment
echo ""
echo -e "${YELLOW}[3/6] Setting up Python environment...${NC}"
cd $SERVER_DIR

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

# Step 4: Setup environment
echo ""
echo -e "${YELLOW}[4/6] Setting up environment...${NC}"

# Use production env
if [ -f "$SERVER_DIR/.env.production" ]; then
    cp $SERVER_DIR/.env.production $SERVER_DIR/.env
    echo "✅ Production environment configured"
else
    echo "⚠️  Using default environment"
fi

# Step 5: Stop existing server
echo ""
echo -e "${YELLOW}[5/6] Stopping existing server...${NC}"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat $PID_FILE)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        kill $OLD_PID
        echo "✅ Old server stopped (PID: $OLD_PID)"
    fi
    rm $PID_FILE
fi

# Also kill any process on port 5000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    lsof -Pi :$PORT -sTCP:LISTEN -t | xargs kill 2>/dev/null || true
    echo "✅ Process on port $PORT stopped"
fi

# Step 6: Start server
echo ""
echo -e "${YELLOW}[6/6] Starting GAURANGA server...${NC}"
cd $SERVER_DIR
source venv/bin/activate

# Start in background with logging
nohup python3 gauranga_server.py > $LOG_DIR/gauranga.log 2>&1 &
SERVER_PID=$!

# Save PID
echo $SERVER_PID > $PID_FILE

# Wait for server to start
sleep 3

# Check if server is running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ GAURANGA server started successfully!${NC}"
    echo ""
    echo -e "${GREEN}==============================================${NC}"
    echo -e "${GREEN}  🎉 DEPLOYMENT COMPLETE!${NC}"
    echo -e "${GREEN}==============================================${NC}"
    echo ""
    echo "📊 Server Status:"
    echo "   PID:        $SERVER_PID"
    echo "   Port:       $PORT"
    echo "   Log:        $LOG_DIR/gauranga.log"
    echo ""
    echo "🌐 Endpoints:"
    echo "   Health:     http://localhost:$PORT/api/health"
    echo "   Status:     http://localhost:$PORT/api/status"
    echo "   Chat:       POST http://localhost:$PORT/api/chat"
    echo ""
    
    # Test endpoints
    echo "🏥 Testing endpoints..."
    HEALTH=$(curl -s http://localhost:$PORT/api/health 2>/dev/null || echo '{"status":"error"}')
    echo "   Health: $HEALTH"
    echo ""
    echo -e "${GREEN}🚀 GAURANGA is LIVE on port $PORT!${NC}"
else
    echo -e "${RED}❌ Server failed to start. Check logs:${NC}"
    echo "   tail -f $LOG_DIR/gauranga.log"
    exit 1
fi
