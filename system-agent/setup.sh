#!/bin/bash
#===============================================
# GAURANGA SYSTEM AGENT - SETUP SCRIPT
#===============================================
# For Termux / Android
# Author: GAURANGA Team
#===============================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   🤖 GAURANGA SYSTEM AGENT SETUP          ║"
echo "║   For Termux / Android                    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running in Termux
if [[ -d "/data/data/com.termux/files/home" ]]; then
    echo -e "${GREEN}[✓] Running in Termux${NC}"
    TERMUX_HOME="/data/data/com.termux/files/home"
else
    echo -e "${YELLOW}[!] Not in Termux - Some features may not work${NC}"
    TERMUX_HOME="$HOME"
fi

# Step 1: Update packages
echo ""
echo -e "${YELLOW}[1/6] Updating packages...${NC}"
pkg update -y && pkg upgrade -y

# Step 2: Install dependencies
echo ""
echo -e "${YELLOW}[2/6] Installing dependencies...${NC}"
pkg install -y python git curl unzip wget

# Step 3: Install Ollama
echo ""
echo -e "${YELLOW}[3/6] Checking Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}[✓] Ollama already installed${NC}"
else
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Step 4: Pull LLM model
echo ""
echo -e "${YELLOW}[4/6] Setting up AI models...${NC}"
echo "This may take a while for first-time download..."
echo ""
read -p "Download Llama 3.2 model? (3GB) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ollama pull llama3.2:1b
    echo -e "${GREEN}[✓] Model downloaded${NC}"
else
    echo -e "${YELLOW}[!] Skipped - You'll need to run 'ollama pull llama3.2:1b' later${NC}"
fi

# Step 5: Create directories
echo ""
echo -e "${YELLOW}[5/6] Creating directories...${NC}"
mkdir -p ~/gauranga/data
mkdir -p ~/gauranga/models
mkdir -p ~/gauranga/logs

# Step 6: Setup Python environment
echo ""
echo -e "${YELLOW}[6/6] Setting up Python environment...${NC}"
pip install pyyaml requests numpy

# Create startup script
echo ""
echo -e "${YELLOW}Creating startup script...${NC}"
cat > ~/gauranga/gauranga.sh << 'SCRIPT'
#!/bin/bash
cd ~/gauranga/system-agent
python gauranga_agent.py "$@"
SCRIPT
chmod +x ~/gauranga/gauranga.sh

# Create alias
echo ""
echo -e "${YELLOW}Adding alias to bashrc...${NC}"
echo "alias gauranga='~/gauranga/gauranga.sh'" >> ~/.bashrc

# Final message
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   ✅ SETUP COMPLETE!                        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}To start GAURANGA, run:${NC}"
echo "  gauranga"
echo ""
echo -e "${GREEN}Or directly:${NC}"
echo "  cd ~/gauranga/system-agent && python gauranga_agent.py"
echo ""
echo -e "${GREEN}To start Ollama (in background):${NC}"
echo "  ollama serve &"
echo ""
echo -e "${YELLOW}First time setup complete!${NC}"
echo -e "Run ${GREEN}gauranga --test${NC} to verify installation."
echo ""