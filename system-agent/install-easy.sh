#!/bin/bash
# ===========================================
# GAURANGA SYSTEM AI v2.0 - Easy Install
# For Android via Termux
# ===========================================

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║     🤖 GAURANGA SYSTEM AI v2.0 - INSTALLER              ║"
echo "║        JARVIS Indonesia - From Zero to Hero             ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running in Termux
if [[ ! -d "$PREFIX" ]]; then
    echo -e "${RED}❌ ERROR: This script must be run in Termux!${NC}"
    echo ""
    echo "Please install Termux from F-Droid:"
    echo "https://f-droid.org/en/packages/com.termux/"
    exit 1
fi

echo -e "${GREEN}✅ Running in Termux${NC}"
echo ""

# Step 1: Update packages
echo -e "${YELLOW}📦 Step 1: Updating packages...${NC}"
pkg update && pkg upgrade -y
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}📦 Step 2: Installing dependencies...${NC}"
pkg install -y python git curl unzip
echo ""

# Step 3: Clone repository
echo -e "${YELLOW}📦 Step 3: Cloning GAURANGA...${NC}"
cd ~
if [ -d "Alpha-agent-Gaurangga" ]; then
    echo "Repository already exists. Updating..."
    cd Alpha-agent-Gaurangga
    git pull
else
    git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
    cd Alpha-agent-Gaurangga
fi
echo ""

# Step 4: Setup Python environment
echo -e "${YELLOW}📦 Step 4: Setting up Python...${NC}"
cd system-agent
pip install --upgrade pip
pip install pyyaml requests numpy
echo ""

# Step 5: Make scripts executable
echo -e "${YELLOW}📦 Step 5: Configuring permissions...${NC}"
chmod +x gauranga_main.py
chmod +x gauranga_agent.py
chmod +x setup.sh
chmod +x install-gauranga.sh
echo ""

# Step 6: Create shortcuts
echo -e "${YELLOW}📦 Step 6: Creating shortcuts...${NC}"
mkdir -p ~/../usr/bin
cat > ~/../usr/bin/gauranga << 'EOF'
#!/bin/bash
cd ~/Alpha-agent-Gaurangga/system-agent
python gauranga_main.py "$@"
EOF
chmod +x ~/../usr/bin/gauranga
echo ""

# Step 7: Test installation
echo -e "${YELLOW}📦 Step 7: Testing installation...${NC}"
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║     ✅ INSTALLATION COMPLETE! 🎉                        ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

echo -e "${GREEN}🚀 To start GAURANGA, run:${NC}"
echo ""
echo "    gauranga"
echo "    or"
echo "    cd ~/Alpha-agent-Gaurangga/system-agent"
echo "    python gauranga_main.py"
echo ""

echo -e "${GREEN}📱 To use with Android app:${NC}"
echo ""
echo "    1. Open the android-app folder"
echo "    2. Serve it with: python -m http.server 8080"
echo "    3. Open in browser: http://localhost:8080"
echo ""

echo -e "${YELLOW}⚠️ Note: For full voice features, install:${NC}"
echo "    - Termux:API package"
echo "    - Grant microphone permissions"
echo ""

echo -e "${GREEN}🎉 GAURANGA is ready to serve Pak Pur!${NC}"
echo ""

# Optional: Start interactive mode
read -p "Start GAURANGA now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    python gauranga_main.py --mode interactive
fi
