#!/bin/bash
# ================================================
# TOKOCRYPTO PAYOUT EXECUTION SCRIPT
# MAHA LAKSHMI HOLDINGS
# ================================================
#
# Usage:
#   ./execute-payout.sh [amount_in_IDR]
#   
# Example:
#   ./execute-payout.sh 20000     # Test Rp 20,000
#   ./execute-payout.sh 334920116 # Full CEO payout
#
# IMPORTANT:
#   - Run from IP address in Indonesia, OR
#   - Set up VPN to Indonesia first, OR
#   - Deploy to Indonesian VPS
#
# ================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.payout"
LOG_FILE="$SCRIPT_DIR/execution-log-$(date +%Y%m%d-%H%M%S).json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "🏦 MAHA LAKSHMI - CEO PAYOUT EXECUTION"
echo "============================================"
echo ""

# Check for .env file
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: .env.payout not found!${NC}"
    echo "Please create $ENV_FILE with your Tokocrypto API credentials"
    echo ""
    echo "Required variables:"
    echo "  TOKOCRYPTO_API_KEY=your_api_key"
    echo "  TOKOCRYPTO_API_SECRET=your_api_secret"
    echo "  BTC_WALLET_ADDRESS=1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2"
    exit 1
fi

# Load environment variables
source "$ENV_FILE"

# Validate configuration
if [ -z "$TOKOCRYPTO_API_KEY" ] || [ "$TOKOCRYPTO_API_KEY" == "YOUR_API_KEY_HERE" ]; then
    echo -e "${RED}❌ Error: TOKOCRYPTO_API_KEY not configured!${NC}"
    exit 1
fi

if [ -z "$TOKOCRYPTO_API_SECRET" ] || [ "$TOKOCRYPTO_API_SECRET" == "YOUR_API_SECRET_HERE" ]; then
    echo -e "${RED}❌ Error: TOKOCRYPTO_API_SECRET not configured!${NC}"
    exit 1
fi

# Get amount from argument or use default
AMOUNT=${1:-20000}
if ! [[ "$AMOUNT" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}❌ Error: Amount must be a number${NC}"
    exit 1
fi

# Check IP location
echo "📡 Checking IP location..."
IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
echo "   Your IP: $IP"

# Detect country (basic check)
COUNTRY=$(curl -s "https://ipapi.co/$IP/country_name/" 2>/dev/null || echo "unknown")
echo "   Country: $COUNTRY"

if [ "$COUNTRY" != "Indonesia" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  WARNING: You are not in Indonesia!${NC}"
    echo "   Tokocrypto may block requests from outside Indonesia."
    echo ""
    echo "   Options:"
    echo "   1. Use VPN with Indonesian server"
    echo "   2. Deploy to Indonesian VPS"
    echo "   3. Execute from Indonesian IP"
    echo ""
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo ""
echo -e "${GREEN}✅ Configuration validated${NC}"
echo ""
echo "============================================"
echo "EXECUTION DETAILS"
echo "============================================"
echo "   Amount:        Rp $AMOUNT"
echo "   BTC Wallet:    $BTC_WALLET_ADDRESS"
echo "   API Key:       ${TOKOCRYPTO_API_KEY:0:10}..."
echo ""
echo "============================================"
echo ""

# Execute the Node.js script
echo "🚀 Executing payout..."

cd "$SCRIPT_DIR"

# Run with simulation mode disabled
SIMULATION_MODE=false node tokocrypto.js $AMOUNT > "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo ""
echo "============================================"
echo "RESULT"
echo "============================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ EXECUTION SUCCESSFUL${NC}"
else
    echo -e "${RED}❌ EXECUTION FAILED${NC}"
fi

echo ""
echo "Log file: $LOG_FILE"
echo ""

# Display log content
echo "--- LOG OUTPUT ---"
cat "$LOG_FILE"
echo "--- END LOG ---"

exit $EXIT_CODE
