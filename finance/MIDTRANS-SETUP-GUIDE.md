# 💳 Midtrans Integration Guide

## Setup Instructions for MAHA LAKSHMI HOLDINGS

---

## 📋 Midtrans Credentials

| Field | Value | Status |
|-------|-------|--------|
| **Merchant ID** | M525420288 | ✅ Sandbox |
| **Client Key** | Mid-client-GAcV0ppiopCTdd-o | ✅ In use |
| **Server Key** | [Stored in .env] | 🔒 ENV only |
| **Environment** | Sandbox (Testing) | 🟡 |

⚠️ **IMPORTANT**: Server Key HARUS disimpan di environment variables, TIDAK di-commit ke repository!

---

## 🔧 Setup Steps

### 1. Environment Variables

Create `.env.midtrans` file (DO NOT commit this file!):

```bash
MIDTRANS_MERCHANT_ID=M525420288
MIDTRANS_CLIENT_KEY=Mid-client-GAcV0ppiopCTdd-o
MIDTRANS_SERVER_KEY=YOUR_ACTUAL_SERVER_KEY
MIDTRANS_ENV=sandbox
```

Add to `.gitignore`:
```
.env.midtrans
```

---

### 2. Server-Side Integration (Required)

Midtrans requires server-side code to generate payment tokens. Here's a Node.js example:

```javascript
// server/midtrans.js
const midtransClient = require('midtrans-client');

const snap = new midtransClient.Snap({
    isProduction: false,
    serverKey: process.env.MIDTRANS_SERVER_KEY,
    clientKey: process.env.MIDTRANS_CLIENT_KEY
});

app.post('/api/create-payment', async (req, res) => {
    const { amount, orderId, customerDetails } = req.body;
    
    const parameter = {
        transaction_details: {
            order_id: orderId,
            gross_amount: amount
        },
        customer_details: customerDetails
    };
    
    const transaction = await snap.createTransaction(parameter);
    res.json({ token: transaction.token });
});
```

---

### 3. Frontend Integration

The Finance Dashboard already includes Midtrans Snap.js integration:

```html
<script src="https://app.sandbox.midtrans.com/snap/snap.js"
    data-client-key="Mid-client-GAcV0ppiopCTdd-o">
</script>
```

---

### 4. Payment Methods Available

With Midtrans, you can accept:

| Method | Description |
|--------|-------------|
| 🏦 Bank Transfer | BCA, Mandiri, BNI, BRI, Permata |
| 💳 Credit Card | Visa, Mastercard, JCB |
| 📱 E-Wallet | GoPay, OVO, DANA, LinkAja |
| 🏪 Retail | Alfamart, Indomaret |
| 🔄 Installment | Cicilan 0% |

---

## 📊 How It Works

```
1. Customer clicks "Bayar dengan Midtrans"
2. Frontend calls server for payment token
3. Server calls Midtrans API
4. Midtrans returns token to frontend
5. Snap.js displays payment popup
6. Customer completes payment
7. Midtrans notifies server (webhook)
8. Server updates your database
9. Settlement goes to your bank account
```

---

## 💰 Settlement

### Automatic Settlement
- Midtrans automatically settles to your registered bank account
- Default: Daily settlement at 11:00 WIB
- Settlement goes directly to: BCA Account registered with Midtrans

### CEO Transfer Flow
```
Revenue Masuk (via Midtrans)
         ↓
    BCA Account (Settlement)
         ↓
    Pak Pur Terima Langsung
         ↓
    GAURANGA Catat & Report
```

---

## 🔒 Security Notes

### DO:
- ✅ Store Server Key in environment variables
- ✅ Use HTTPS for all API calls
- ✅ Implement webhook verification
- ✅ Verify transaction status before fulfilling

### DON'T:
- ❌ Commit credentials to git
- ❌ Expose Server Key in frontend
- ❌ Skip webhook verification
- ❌ Trust client-side transaction results only

---

## 📞 Midtrans Support

- Dashboard: https://dashboard.midtrans.com
- Documentation: https://docs.midtrans.com
- Support: https://midtrans.com/contact

---

## 🚀 Production Checklist

Before going live:

- [ ] Change `MIDTRANS_ENV` to `production`
- [ ] Update Client Key to production key
- [ ] Update Server Key to production key
- [ ] Enable required payment methods
- [ ] Configure settlement account
- [ ] Test all payment methods
- [ ] Setup webhook endpoint

---

**Last Updated:** 13 Juli 2026
**Version:** 1.0
