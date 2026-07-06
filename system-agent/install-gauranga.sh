#!/bin/bash
# ==============================================
# GAURANGA AGENT - AUTO INSTALLER
# One-click installation script
# ==============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Owner Info
OWNER_NAME="I Made Purna Ananda"
OWNER_NICK="Pak Pur"
COMPANY="Maha Lakshmi Holdings"

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                              ║${NC}"
echo -e "${BLUE}║    🤖 GAURANGA AGENT ALPHA - INSTALLER    ║${NC}"
echo -e "${BLUE}║                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Owner: ${OWNER_NAME}${NC}"
echo -e "${YELLOW}Company: ${COMPANY}${NC}"
echo ""

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}❌ ERROR: Please run this script in Termux!${NC}"
    echo -e "${YELLOW}1. Install Termux from F-Droid${NC}"
    echo -e "${YELLOW}2. Open Termux${NC}"
    echo -e "${YELLOW}3. Run: bash <(curl -sL https://github.com/prahlad168/Alpha-agent-Gaurangga/raw/main/system-agent/install-gauranga.sh)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Running in Termux${NC}"
echo ""

# Step 1: Update packages
echo -e "${YELLOW}📦 Step 1: Updating packages...${NC}"
pkg update && pkg upgrade -y
echo -e "${GREEN}✅ Packages updated${NC}"
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}📦 Step 2: Installing dependencies...${NC}"
pkg install git python -y
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 3: Clone repository
echo -e "${YELLOW}📥 Step 3: Cloning GAURANGA repository...${NC}"
if [ -d "$HOME/Alpha-agent-Gaurangga" ]; then
    echo -e "${YELLOW}Repository exists, pulling latest...${NC}"
    cd $HOME/Alpha-agent-Gaurangga
    git pull
else
    git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git $HOME/Alpha-agent-Gaurangga
fi
echo -e "${GREEN}✅ Repository cloned${NC}"
echo ""

# Step 4: Install Python dependencies
echo -e "${YELLOW}🐍 Step 4: Installing Python packages...${NC}"
cd $HOME/Alpha-agent-Gaurangga/system-agent
pip install pyyaml numpy requests --quiet
echo -e "${GREEN}✅ Python packages installed${NC}"
echo ""

# Step 5: Setup storage
echo -e "${YELLOW}💾 Step 5: Setting up storage...${NC}"
termux-setup-storage -y 2>/dev/null || true
echo -e "${GREEN}✅ Storage configured${NC}"
echo ""

# Step 6: Create shortcuts
echo -e "${YELLOW}🔗 Step 6: Creating shortcuts...${NC}"
cat > $PREFIX/bin/gauranga << 'EOF'
#!/bin/bash
cd $HOME/Alpha-agent-Gaurangga/system-agent
python gauranga_agent.py "$@"
EOF
chmod +x $PREFIX/bin/gauranga
echo -e "${GREEN}✅ Shortcut created: gauranga${NC}"
echo ""

# Step 7: Test
echo -e "${YELLOW}🧪 Step 7: Testing GAURANGA...${NC}"
echo ""

# Success message
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         🎉 INSTALLATION COMPLETE! 🎉        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📱 HOW TO USE GAURANGA:${NC}"
echo ""
echo -e "${BLUE}  Command:${NC}"
echo -e "    ${GREEN}gauranga${NC}           - Start GAURANGA"
echo -e "    ${GREEN}gauranga --test${NC}    - Test mode"
echo -e "    ${GREEN}gauranga --voice${NC}   - Voice mode"
echo -e "    ${GREEN}gauranga --daemon${NC}  - Background mode"
echo ""
echo -e "${BLUE}  Or run directly:${NC}"
echo -e "    cd ~/Alpha-agent-Gaurangga/system-agent"
echo -e "    python gauranga_agent.py --test"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}👑 Owner: ${OWNER_NAME}${NC}"
echo -e "${CYAN}🏢 Company: ${COMPANY}${NC}"
echo ""

# Ask to start now
echo -e "${YELLOW}Start GAURANGA now? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${GREEN}🚀 Starting GAURANGA Agent...${NC}"
    echo ""
    python gauranga_agent.py --test
fi