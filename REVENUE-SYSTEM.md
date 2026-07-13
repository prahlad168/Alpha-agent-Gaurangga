# 💰 GAURANGA Revenue System

## 🎉 Deployment Complete!

Sistem revenue tracking real-time sudah berhasil di-deploy!

---

## 📊 Dashboard

Buka file: `dashboard-revenue.html`

Dashboard menampilkan:
- **Total Revenue** - Semua pendapatan
- **Total Expense** - Semua pengeluaran
- **Total Profit** - Keuntungan bersih
- **CEO Bitcoin** - Total transfer ke wallet Pak Pur
- **SBU Breakdown** - Pendapatan per sektor
- **Recent Transactions** - Transaksi terbaru
- **Pending Invoices** - Invoice belum lunas

---

## 🚀 Running Server

```bash
# Start server
cd server
./start-revenue.sh

# Or direct
python3 server/revenue_api.py

# Stop
./stop-revenue.sh
```

Server running on: **http://localhost:5001**

---

## 📡 API Endpoints

### Revenue
- `GET /api/revenue/summary` - Ringkasan revenue
- `GET /api/revenue/dashboard` - Data lengkap dashboard

### SBU
- `GET /api/sbu` - List semua SBU
- `GET /api/sbu/<name>` - Detail SBU

### Transactions
- `GET /api/transactions` - List transaksi
- `POST /api/quick/income` - Tambah income
- `POST /api/quick/expense` - Tambah expense

### Clients & Projects
- `GET /api/clients` - List clients
- `POST /api/clients` - Tambah client
- `GET /api/projects` - List projects
- `POST /api/projects` - Tambah project

### Invoices
- `GET /api/invoices` - List invoices
- `POST /api/invoices` - Buat invoice
- `POST /api/invoices/<id>/pay` - Mark paid

### CEO Transfers
- `GET /api/ceo/transfers` - History transfer
- `POST /api/ceo/transfer` - Transfer ke Bitcoin wallet

---

## 💡 Quick Examples

### Add Income
```bash
curl -X POST http://localhost:5001/api/quick/income \
  -H "Content-Type: application/json" \
  -d '{
    "sbu": "hospital",
    "amount": 50000000,
    "description": "SIMRS Project - RS Sehat",
    "payment_method": "BCA"
  }'
```

### Add Expense
```bash
curl -X POST http://localhost:5001/api/quick/expense \
  -H "Content-Type: application/json" \
  -d '{
    "sbu": "general",
    "amount": 5000000,
    "description": "Server Hosting",
    "category": "operational"
  }'
```

### CEO Bitcoin Transfer
```bash
curl -X POST http://localhost:5001/api/ceo/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "amount_idr": 10000000,
    "sbu_source": "hospital",
    "note": "Monthly profit"
  }'
```

---

## 🗄️ Database

Database file: `server/data/gauranga_revenue.db`

Tables:
- `sbu` - Strategic Business Units
- `clients` - Client database
- `projects` - Projects tracking
- `transactions` - Income/Expense transactions
- `invoices` - Invoice management
- `ceo_transfers` - CEO Bitcoin transfers

---

## 👑 CEO Bitcoin Wallet

```
Address: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
Rate: 1 BTC = Rp 1.5 Billion
```

---

## 📈 Target Revenue

| SBU | Target/Bulan |
|-----|-------------|
| 🏥 Hospital | Rp 50,000,000 |
| 🛒 E-Commerce | Rp 30,000,000 |
| 📚 Education | Rp 25,000,000 |
| ✈️ Travel | Rp 20,000,000 |
| 🏠 Property | Rp 25,000,000 |
| 🍔 Food | Rp 20,000,000 |
| **TOTAL** | **Rp 170,000,000** |

---

## 🎯 Next Steps

1. **Add Real Clients** - Input data client dan project nyata
2. **Create Invoices** - Generate invoice untuk billing
3. **Track Payments** - Mark invoice sebagai paid saat diterima
4. **CEO Transfers** - Transfer profit ke Bitcoin wallet

---

## 📞 Support

WhatsApp: 081337558787 (Pak Pur)
GitHub: https://github.com/prahlad168/Alpha-agent-Gaurangga

---

**Version:** 1.0.0
**Status:** 🚀 PRODUCTION READY
**Updated:** 13 July 2026
