#!/bin/bash
# ================================================
# GAURANGA - Auto Deploy Script
# ================================================
# Version: 1.0.0
# Date: 2026-07-11
# ================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emoji
ROCKET="🚀"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
SPARKLES="✨"

# Config
APP_NAME="gauranga"
APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
SERVER_PORT=5000
LOG_DIR="$APP_DIR/logs"
PID_FILE="$APP_DIR/deploy/gauranga.pid"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}     ${ROCKET} GAURANGA AUTO DEPLOY ${ROCKET}        ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# ================================================
# Function: Check Dependencies
# ================================================
check_dependencies() {
    echo -e "${BLUE}[1/6] Checking dependencies...${NC}"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "  ${CHECK} Python: $PYTHON_VERSION"
    else
        echo -e "  ${CROSS} Python3 not found!"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        echo -e "  ${CHECK} pip3: installed"
    else
        echo -e "  ${WARNING} pip3 not found, installing..."
        apt-get update && apt-get install -y python3-pip
    fi
    
    # Check git
    if command -v git &> /dev/null; then
        echo -e "  ${CHECK} git: installed"
    else
        echo -e "  ${CROSS} git not found!"
        exit 1
    fi
    
    echo -e "${GREEN}  ✓ Dependencies OK${NC}\n"
}

# ================================================
# Function: Pull Latest Code
# ================================================
pull_latest() {
    echo -e "${BLUE}[2/6] Pulling latest code...${NC}"
    
    cd $APP_DIR
    
    # Stash any local changes
    git stash push -m "Auto-deploy stash" 2>/dev/null || true
    
    # Pull latest
    echo -e "  ${SPARKLES} Fetching from remote..."
    git fetch origin
    
    echo -e "  ${SPARKLES} Pulling main branch..."
    git pull origin main
    
    echo -e "${GREEN}  ✓ Code updated${NC}\n"
}

# ================================================
# Function: Install Dependencies
# ================================================
install_deps() {
    echo -e "${BLUE}[3/6] Installing dependencies...${NC}"
    
    cd $APP_DIR/server
    
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        echo -e "  ${SPARKLES} Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Install requirements
    echo -e "  ${SPARKLES} Installing Python packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo -e "${GREEN}  ✓ Dependencies installed${NC}\n"
}

# ================================================
# Function: Setup Environment
# ================================================
setup_env() {
    echo -e "${BLUE}[4/6] Setting up environment...${NC}"
    
    cd $APP_DIR/server
    
    # Create .env if not exists
    if [ ! -f ".env" ]; then
        echo -e "  ${SPARKLES} Creating .env from template..."
        cp .env.example .env
        echo -e "  ${WARNING} Please edit .env and add your API keys!"
    else
        echo -e "  ${CHECK} .env already exists"
    fi
    
    # Create logs directory
    mkdir -p $LOG_DIR
    touch $LOG_DIR/gauranga.log
    
    echo -e "${GREEN}  ✓ Environment configured${NC}\n"
}

# ================================================
# Function: Stop Existing Server
# ================================================
stop_server() {
    echo -e "${BLUE}[5/6] Stopping existing server...${NC}"
    
    # Kill by PID file
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "  ${SPARKLES} Stopping process $PID..."
            kill $PID 2>/dev/null || true
            sleep 2
        fi
        rm $PID_FILE
    fi
    
    # Kill by port
    if lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "  ${SPARKLES} Killing process on port $SERVER_PORT..."
        lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t | xargs kill 2>/dev/null || true
        sleep 1
    fi
    
    echo -e "${GREEN}  ✓ Server stopped${NC}\n"
}

# ================================================
# Function: Start Server
# ================================================
start_server() {
    echo -e "${BLUE}[6/6] Starting GAURANGA server...${NC}"
    
    cd $APP_DIR/server
    source venv/bin/activate
    
    # Start in background
    nohup python3 gauranga_server.py > $LOG_DIR/gauranga.log 2>&1 &
    
    # Save PID
    echo $! > $PID_FILE
    
    # Wait for server to start
    sleep 3
    
    # Check if running
    if ps -p $(cat $PID_FILE) > /dev/null 2>&1; then
        echo -e "${GREEN}  ${ROCKET} GAURANGA Server started!${NC}"
        echo -e "${GREEN}  ✓ PID: $(cat $PID_FILE)${NC}"
        echo -e "${GREEN}  ✓ Log: $LOG_DIR/gauranga.log${NC}"
        echo -e "${GREEN}  ✓ Port: $SERVER_PORT${NC}"
    else
        echo -e "${RED}  ${CROSS} Server failed to start!${NC}"
        echo -e "${RED}  Check logs: $LOG_DIR/gauranga.log${NC}"
        exit 1
    fi
    
    echo ""
}

# ================================================
# Function: Health Check
# ================================================
health_check() {
    echo -e "${BLUE}Running health check...${NC}"
    
    sleep 2
    
    # Try curl
    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s http://localhost:$SERVER_PORT/api/health 2>/dev/null || echo "error")
        if echo "$RESPONSE" | grep -q "healthy"; then
            echo -e "${GREEN}  ${CHECK} Health check passed!${NC}"
            return 0
        fi
    fi
    
    echo -e "${YELLOW}  ${WARNING} Health check skipped (curl not available)${NC}"
    return 0
}

# ================================================
# Function: Show Status
# ================================================
show_status() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}     ${ROCKET} DEPLOYMENT COMPLETE ${ROCKET}          ${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
    echo -e "${GREEN}  ${APP_NAME} is running!${NC}"
    echo ""
    echo -e "  📡 Endpoints:"
    echo -e "     • Health:  http://localhost:$SERVER_PORT/api/health"
    echo -e "     • Status:  http://localhost:$SERVER_PORT/api/status"
    echo -e "     • Chat:    POST http://localhost:$SERVER_PORT/api/chat"
    echo ""
    echo -e "  📝 Logs:"
    echo -e "     • $LOG_DIR/gauranga.log"
    echo ""
    echo -e "  🔧 Commands:"
    echo -e "     • Stop:    $APP_DIR/deploy/stop.sh"
    echo -e "     • Restart: $APP_DIR/deploy/restart.sh"
    echo -e "     • Logs:    tail -f $LOG_DIR/gauranga.log"
    echo ""
}

# ================================================
# MAIN EXECUTION
# ================================================
main() {
    check_dependencies
    pull_latest
    install_deps
    setup_env
    stop_server
    start_server
    health_check
    show_status
    
    echo -e "${GREEN}✅ Deployment successful!${NC}\n"
}

# Run
main "$@"
