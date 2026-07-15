#!/bin/bash

# ============================================================================
# MAHALAKSMI AIOS v2.1.1 - Linux/Mac One-Click Launcher
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Clear screen
clear

# ASCII Art Banner
echo -e "${CYAN}"
cat << "BANNER"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ███╗   ███╗██╗███████╗██╗ ██████╗ ███████╗                       ║
║   ████╗ ████║██║██╔════╝██║██╔════╝ ██╔════╝                       ║
║   ██╔████╔██║██║███████╗██║██║  ███╗█████╗                         ║
║   ██║╚██╔╝██║██║╚════██║██║██║   ██║██╔══╝                         ║
║   ██║ ╚═╝ ██║██║███████║██║╚██████╔╝███████╗                       ║
║   ╚═╝     ╚═╝╚═╝╚══════╝╚═╝ ╚═════╝ ╚══════╝                       ║
║                                                                      ║
║   ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗███████╗║
║  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝║
║  ██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗  ║
║  ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝ ║
║  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ███████╗║
║   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝║
║                                                                      ║
║                    Enterprise AI Operating System                     ║
║                         Version 2.1.1                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

echo -e "${YELLOW}[*] Detected OS: ${BOLD}$OSTYPE${NC}"
echo -e "${YELLOW}[*] Starting MAHALAKSMI AIOS...${NC}"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}[ERROR] Python is not installed!${NC}"
    echo "        Please install Python 3.8+ from https://python.org"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
echo -e "${GREEN}[*] Using Python: ${PYTHON_CMD}$(${PYTHON_CMD} --version 2>&1)${NC}"

# Check for virtual environment
VENV_PATH=".venv"

if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}[*] Activating virtual environment...${NC}"
    source "${VENV_PATH}/bin/activate"
elif [ -f "${VENV_PATH}/bin/activate" ]; then
    echo -e "${GREEN}[*] Activating virtual environment...${NC}"
    source "${VENV_PATH}/bin/activate"
fi

# Check for required packages
echo -e "${YELLOW}[*] Checking dependencies...${NC}"

if ! ${PYTHON_CMD} -c "import fastapi" &> /dev/null; then
    echo -e "${YELLOW}[!] Installing required packages...${NC}"
    ${PYTHON_CMD} -m pip install fastapi uvicorn httpx --quiet 2>/dev/null
fi

# Kill any existing server on port 5000
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}[!] Port 5000 is already in use. Stopping existing server...${NC}"
    lsof -Pi :5000 -sTCP:LISTEN -t | xargs kill 2>/dev/null || true
    sleep 1
fi

# Change to script directory
cd "$(dirname "$0")" 2>/dev/null || cd /workspace/project/Alpha-agent-Gaurangga

echo ""
echo -e "${GREEN}[+] Starting MAHALAKSMI AIOS Server...${NC}"
echo -e "${GREEN}[+] Dashboard will open at: ${BOLD}http://localhost:5000/dashboard${NC}"
echo ""
echo -e "${CYAN}    Press Ctrl+C to stop the server${NC}"
echo ""

# Start server in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload > server.log 2>&1 &
SERVER_PID=$!

echo -e "${YELLOW}[*] Server PID: ${SERVER_PID}${NC}"

# Wait for server to start
echo -e "${YELLOW}[*] Waiting for server startup...${NC}"
sleep 3

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}[ERROR] Server failed to start!${NC}"
    echo "Check server.log for details:"
    tail -20 server.log
    exit 1
fi

# Open browser based on OS
echo -e "${GREEN}[+] Opening dashboard in browser...${NC}"

if [ "$OS" == "macos" ]; then
    open http://localhost:5000/dashboard
elif [ "$OS" == "linux" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5000/dashboard
    elif command -v gnome-open &> /dev/null; then
        gnome-open http://localhost:5000/dashboard
    else
        echo -e "${YELLOW}[!] Could not auto-open browser. Please visit:${NC}"
        echo -e "${BOLD}    http://localhost:5000/dashboard${NC}"
    fi
else
    echo -e "${YELLOW}[!] Unknown OS. Please visit:${NC}"
    echo -e "${BOLD}    http://localhost:5000/dashboard${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}${BOLD}   🎉 MAHALAKSMI AIOS is running!${NC}${GREEN}                            ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║${NC}   ${CYAN}Dashboard:${NC}  ${BOLD}http://localhost:5000/dashboard${NC}                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   ${CYAN}API Docs:${NC}   ${BOLD}http://localhost:5000/docs${NC}                     ${GREEN}║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║${NC}   ${YELLOW}Logs:${NC}      ${BOLD}tail -f server.log${NC}                             ${GREEN}║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Wait for interrupt
trap "echo ''; echo -e '${YELLOW}[*] Stopping server...${NC}'; kill $SERVER_PID 2>/dev/null; exit" INT TERM

wait $SERVER_PID
