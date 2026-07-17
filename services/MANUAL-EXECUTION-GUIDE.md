# 📋 MANUAL EXECUTION GUIDE - CEO PAYOUT

## MAHA LAKSHMI HOLDINGS

---

## 🚨 PROBLEM: API BLOCKED FROM US IP

```
Your Current IP:  34.10.175.217 (Iowa, USA)
Tokocrypto:      Blocks requests from outside Indonesia
Solution:         Execute from Indonesian IP
```

---

## ✅ SOLUTION: 3 OPTIONS

### OPTION A: FREE - Use VPN Indonesia
### OPTION B: CHEAP - Deploy to Indonesian VPS (~$5/mo)
### OPTION C: EASIEST - Execute from your local computer in Indonesia

---

## 📋 OPTION C: LOCAL EXECUTION (RECOMMENDED)

### Step 1: Download Files

```bash
# Clone repository
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
cd Alpha-agent-Gaurangga/services
```

### Step 2: Install Node.js

**Windows:**
1. Download from https://nodejs.org
2. Run installer
3. Open Command Prompt

**Mac:**
```bash
brew install node
```

**Linux:**
```bash
sudo apt install nodejs npm
```

### Step 3: Configure API Credentials

Edit file `services/.env.payout`:

```
TOKOCRYPTO_API_KEY=6D0c5B2a76063c5B83d4fD8781583637BvFfWOYJ8lML7D6lpxDUB2BiYvQnjtGp
TOKOCRYPTO_API_SECRET=8483a1Aa7402f5B796410C23370177DbpJWR16EfgacQbbZpC3ApBVJvjQpY4fK
BTC_WALLET_ADDRESS=1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2
SIMULATION_MODE=false
```

### Step 4: Whitelist Your IP

1. Login ke https://www.tokocrypto.com
2. Settings → API Management
3. Add IP: `your_public_ip`
4. Get your IP: https://whatismyip.com

### Step 5: Execute Test (Rp 20,000)

```bash
cd services
node tokocrypto.js 20000
```

**Expected Output:**
```
🏦 MAHA LAKSHMI - CEO PAYOUT EXECUTION
📅 Timestamp: 2026-07-17T...
💰 Amount: Rp 20,000
👛 BTC Wallet: 1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2

📊 Step 1: Getting BTC price...
💵 Current BTC price: Rp 89,300,000

📊 Step 2: Placing market buy order...
✅ Buy order placed! Order ID: 123456789

📊 Step 3: Withdrawing BTC to CEO wallet...
✅ Withdrawal initiated! TxID: abc123...

✅ LIVE EXECUTION COMPLETE!
Total BTC: 0.00022396 BTC
Destination: 1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2
```

### Step 6: Verify Transaction

1. Check email: Tokocrypto akan kirim notification
2. Check wallet: https://blockstream.info/address/1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2
3. Wait ~60 menit untuk 1 confirmation

---

## 💰 FULL CEO PAYOUT EXECUTION

### Amount: Rp 334,920,116 (~3.75 BTC)

```bash
cd services
node tokocrypto.js 334920116
```

**WARNING: Execute this ONLY after verifying test transaction works!**

---

## 📊 TRANSACTION EXPECTED

| Field | Value |
|-------|-------|
| **Amount (IDR)** | Rp 334,920,116 |
| **BTC Price** | ~Rp 89,300,000 |
| **BTC Received** | ~3.75 BTC |
| **Destination** | `1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2` |
| **Network Fee** | ~0.0005 BTC |
| **Confirmations** | 1 (initial), 6 (final) |
| **Time** | ~60 minutes |

---

## 🔍 VERIFICATION CHECKLIST

- [ ] Test transaction (Rp 20,000) works
- [ ] TxID received from Tokocrypto
- [ ] BTC appears in wallet (blockstream.info)
- [ ] Full payout executed
- [ ] TxID recorded in audit log
- [ ] Email confirmation received

---

## 📁 FILES READY FOR EXECUTION

```
services/
├── tokocrypto.js          # Main execution script (Node.js)
├── tokocrypto.py          # Alternative (Python)
├── execute-payout.sh      # Shell script wrapper
├── .env.payout            # API credentials (NEVER COMMIT!)
├── DEPLOYMENT-GUIDE.md    # VPS deployment guide
└── MANUAL-EXECUTION-GUIDE.md  # This file
```

---

## 🆘 IF SOMETHING GOES WRONG

### Error: "IP not whitelisted"
```
Solution: Add your IP in Tokocrypto API Settings
```

### Error: "Insufficient balance"
```
Solution: Deposit IDR to Tokocrypto via bank transfer
```

### Error: "API key invalid"
```
Solution: Verify TOKOCRYPTO_API_KEY and API_SECRET are correct
```

### Error: "Withdrawal disabled"
```
Solution: Enable withdrawal permission in API settings
```

---

## 📞 QUICK REFERENCE

| Resource | Link |
|----------|------|
| Tokocrypto | https://www.tokocrypto.com |
| BTC Wallet | https://blockstream.info/address/1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2 |
| Check IP | https://whatismyip.com |
| Audit Log | `ceo-revenue-share/03-audit-log.json` |

---

## ✅ COMPLETE CHECKLIST BEFORE EXECUTION

```
□ 1. Running from Indonesian IP (or VPN)
□ 2. API credentials configured in .env.payout
□ 3. IP whitelisted in Tokocrypto
□ 4. Withdrawal permission enabled
□ 5. Test transaction successful (Rp 20,000)
□ 6. Balance sufficient for full payout
□ 7. BTC wallet address verified: 1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2
□ 8. All files synced from GitHub
```

---

## 🎯 READY TO EXECUTE

Once you have Indonesian IP access:

```bash
cd Alpha-agent-Gaurangga/services
node tokocrypto.js 20000  # Test first
node tokocrypto.js 334920116  # Full payout
```

---

**Generated:** 2026-07-17
**Version:** 1.0.0
**MAHA LAKSHMI HOLDINGS**
**CEO:** i Made Purna Ananda (Pak Pur)
