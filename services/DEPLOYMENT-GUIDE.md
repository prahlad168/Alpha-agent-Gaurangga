# 🚀 DEPLOYMENT GUIDE - TOKOCRYPTO INTEGRATION

## MAHA LAKSHMI HOLDINGS - CEO PAYOUT SYSTEM

---

## ⚠️ IMPORTANT: IP RESTRICTION

Tokocrypto API **blocks requests from outside Indonesia** (HTTP 451).

**Your current IP:** `34.10.175.217` (Iowa, US)

**Solution Options:**
1. **Deploy to Indonesian VPS** (Recommended)
2. **Use VPN to Indonesia**
3. **Execute locally from Indonesia**

---

## 📋 OPTION 1: DEPLOY TO INDONESIAN VPS (RECOMMENDED)

### Step 1: Choose Indonesian VPS Provider

| Provider | Location | Price |
|----------|----------|-------|
| DigitalOcean (Singapore) | Singapore 🇸🇬 | ~$6/mo |
| Vultr Indonesia | Jakarta 🇮🇩 | ~$6/mo |
| Linode (Tokyo/Singapore) | Asia | ~$5/mo |
| Niagahoster | Indonesia 🇮🇩 | ~Rp 50k/mo |
| CloudCone | Asia | ~$3/mo |

### Step 2: Deploy Script

```bash
# SSH to your VPS
ssh root@your_vps_ip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Clone repository
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
cd Alpha-agent-Gaurangga/services

# Copy and configure .env
cp .env.payout.example .env.payout
nano .env.payout
# Update TOKOCRYPTO_API_KEY and TOKOCRYPTO_API_SECRET

# Test with micro amount
./execute-payout.sh 20000

# Execute full payout (Rp 334,920,116)
./execute-payout.sh 334920116
```

### Step 3: Whitelist VPS IP

1. Login to Tokocrypto
2. Go to Settings → API Management
3. Add your VPS public IP to whitelist
4. Save

---

## 📋 OPTION 2: USE VPN TO INDONESIA

### Free Indonesian VPN Options:

| Service | Type | Link |
|---------|------|------|
| Psiphon | Free VPN | psiphon.ca |
| ProtonVPN | Free Tier | protonvpn.com |
| Cloudflare WARP | Free | 1.1.1.1 |

### Steps:

```bash
# After connecting to Indonesian VPN
# Get your new IP
curl ifconfig.me

# Update whitelist in Tokocrypto with new IP
# Then run
cd /workspace/project/Alpha-agent-Gaurangga/services
./execute-payout.sh 20000
```

---

## 📋 OPTION 3: LOCAL EXECUTION (WINDOWS/MAC/LINUX)

### Windows

```powershell
# 1. Install Node.js from https://nodejs.org

# 2. Open PowerShell
cd C:\path\to\Alpha-agent-Gaurangga\services

# 3. Copy .env.payout.example to .env.payout
# Edit with your API credentials

# 4. Run
node tokocrypto.js 20000
```

### Mac/Linux

```bash
# 1. Install Node.js
brew install node  # Mac
# OR
sudo apt install nodejs  # Ubuntu/Debian

# 2. Navigate to folder
cd ~/path/to/Alpha-agent-Gaurangga/services

# 3. Copy .env.payout.example to .env.payout
# Edit with your API credentials

# 4. Run
chmod +x execute-payout.sh
./execute-payout.sh 20000
```

---

## 🔧 CONFIGURATION

### Edit `.env.payout`:

```bash
# Tokocrypto API Credentials
TOKOCRYPTO_API_KEY=6D0c5B2a76063c5B83d4fD8781583637BvFfWOYJ8lML7D6lpxDUB2BiYvQnjtGp
TOKOCRYPTO_API_SECRET=8483a1Aa7402f5B796410C23370177DbpJWR16EfgacQbbZpC3ApBVJvjQpY4fK

# Mode Configuration  
SIMULATION_MODE=false

# BTC Wallet (CEO Native BTC)
BTC_WALLET_ADDRESS=1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2
```

---

## 🎯 EXECUTION COMMANDS

### Test Micro-Transaction (Rp 20,000)
```bash
node tokocrypto.js 20000
# OR
./execute-payout.sh 20000
```

### Full CEO Payout (Rp 334,920,116)
```bash
node tokocrypto.js 334920116
# OR
./execute-payout.sh 334920116
```

### Custom Amount
```bash
node tokocrypto.js 50000
```

---

## 📊 EXPECTED OUTPUT

### Success:
```json
{
  "success": true,
  "mode": "LIVE",
  "steps": {
    "step1_buy_btc": {
      "action": "Market Buy BTC",
      "order_id": "123456789",
      "btc_amount": "0.00022396",
      "status": "COMPLETED"
    },
    "step2_withdraw": {
      "action": "Withdraw BTC",
      "txid": "abc123...",
      "status": "PENDING_CONFIRMATION"
    }
  },
  "total_btc": "0.00022396",
  "destination_wallet": "1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2"
}
```

---

## ⚠️ TROUBLESHOOTING

### Error: HTTP 451
```
Problem: IP blocked by Tokocrypto
Solution: Use Indonesian IP (VPS/VPN/Local)
```

### Error: Invalid API Key
```
Problem: API credentials incorrect
Solution: Verify API_KEY and API_SECRET in .env.payout
```

### Error: Insufficient Balance
```
Problem: Not enough IDR in Tokocrypto account
Solution: Deposit IDR first via bank transfer
```

### Error: Withdrawal Disabled
```
Problem: API key doesn't have withdrawal permission
Solution: Enable withdrawal in Tokocrypto API settings
```

---

## 🔐 SECURITY CHECKLIST

- [ ] API credentials stored in `.env.payout`
- [ ] `.env.payout` added to `.gitignore`
- [ ] VPS IP whitelisted in Tokocrypto
- [ ] Withdrawal permission enabled on API key
- [ ] Test with small amount first (Rp 20,000)
- [ ] Verify TxID on blockchain after execution

---

## 📞 SUPPORT

For issues, check:
1. Tokocrypto API Status: https://www.tokocrypto.com
2. GAURANGA Audit Log: `ceo-revenue-share/03-audit-log.json`
3. Execution Logs: `services/execution-log-*.json`

---

## 🎯 QUICK START

```bash
# 1. Get Indonesian IP (VPS/VPN)
curl ifconfig.me  # Should show Indonesian IP

# 2. Whitelist IP in Tokocrypto

# 3. Configure credentials
nano services/.env.payout

# 4. Test with small amount
./execute-payout.sh 20000

# 5. Execute full payout
./execute-payout.sh 334920116
```

---

**Generated:** 2026-07-17
**Version:** 1.0.0
**MAHA LAKSHMI HOLDINGS**
