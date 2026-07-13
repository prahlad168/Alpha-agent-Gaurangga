/**
 * ================================================
 * FINANCE AGENT - GAURANGA
 * ================================================
 * Agent ID: finance-agent-v1
 * Version: 2.0.0 (CEO Bitcoin Transfer)
 * Created: 2026-07-11
 * Updated: 2026-07-13
 * ================================================
 */

const FinanceAgent = {
    // Accuracy target
    ACCURACY_TARGET: 99.9,
    
    // Monthly summary
    MONTHLY: {
        revenue: 0,
        expenses: 0,
        profit: 0
    },
    
    // CEO Bitcoin Wallet Info
    CEO_WALLET: {
        btcAddress: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
        btcRate: 1500000000, // 1 BTC = Rp 1.5 Miliar
        totalBtc: 0
    },
    
    // Expense categories
    EXPENSES: [
        { category: 'Gaji', amount: 0 },
        { category: 'Marketing', amount: 0 },
        { category: 'Tools/Subscriptions', amount: 0 },
        { category: 'Operasional', amount: 0 },
        { category: 'Lainnya', amount: 0 }
    ],
    
    /**
     * Format currency
     */
    formatRupiah(num) {
        return 'Rp ' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    },
    
    /**
     * Format BTC
     */
    formatBtc(satoshi) {
        const btc = satoshi / 100000000;
        return '₿ ' + btc.toFixed(8);
    },
    
    /**
     * Convert IDR to Satoshi
     */
    idrToSatoshi(idr) {
        return Math.floor((idr / this.CEO_WALLET.btcRate) * 100000000);
    },
    
    /**
     * Get dashboard
     */
    getDashboard() {
        const revenue = this.MONTHLY.revenue;
        const expenses = this.MONTHLY.expenses;
        const profit = revenue - expenses;
        const margin = revenue > 0 ? Math.round((profit / revenue) * 100) : 0;
        const totalBtc = this.CEO_WALLET.totalBtc;
        const totalIdr = (totalBtc / 100000000) * this.CEO_WALLET.btcRate;
        
        let dashboard = `
💵 <b>Finance Dashboard</b>

<b>📊 This Month:</b>
├── Revenue: ${this.formatRupiah(revenue)}
├── Expenses: ${this.formatRupiah(expenses)}
├── Profit: ${this.formatRupiah(profit)}
└── Margin: ${margin}%

<b>👑 CEO Bitcoin Wallet:</b>
├── Balance: ${this.formatBtc(totalBtc)}
├── Est. Value: ${this.formatRupiah(Math.floor(totalIdr))}
└── Address: ${this.CEO_WALLET.btcAddress.substring(0, 20)}...

<b>📈 Revenue Targets:</b>
├── Month 1: ${this.formatRupiah(5000000)}
├── Month 3: ${this.formatRupiah(25000000)}
└── Month 6: ${this.formatRupiah(100000000)}

<b>🎯 Accuracy Target: ${this.ACCURACY_TARGET}%</b>

<b>Commands:</b>
• "transfer" - Transfer ke CEO wallet
• "expenses" - Expense breakdown
• "invoice" - Invoice template
• "profit" - P&L report
`;
        return dashboard;
    },
    
    /**
     * Get CEO Transfer info
     */
    getCeoTransfer() {
        const totalBtc = this.CEO_WALLET.totalBtc;
        const totalIdr = (totalBtc / 100000000) * this.CEO_WALLET.btcRate;
        
        return `
👑 <b>CEO Bitcoin Transfer</b>

<b>💰 Wallet Balance:</b>
├── BTC: ${this.formatBtc(totalBtc)}
└── IDR: ${this.formatRupiah(Math.floor(totalIdr))}

<b>📋 Transfer Info:</b>
├── BTC Rate: 1 BTC = ${this.formatRupiah(this.CEO_WALLET.btcRate)}
└── Wallet: ${this.CEO_WALLET.btcAddress}

<b>🔄 Cara Transfer:</b>
1. Buka Finance Dashboard
2. Pilih tab "CEO Transfer"
3. Pilih SBU sumber
4. Masukkan jumlah (IDR)
5. Klik "Konfirmasi Transfer ke CEO"

<b>⚡ Quick Actions:</b>
• "transfer 10%" - 10% profit ke CEO
• "transfer 25%" - 25% profit ke CEO
• "transfer 50%" - 50% profit ke CEO
`;
    },
    
    /**
     * Get expenses
     */
    getExpenses() {
        let expenses = `
💸 <b>Monthly Expenses Breakdown</b>

<b>📋 Categories:</b>
`;
        let total = 0;
        this.EXPENSES.forEach((e, i) => {
            const pct = this.MONTHLY.expenses > 0 ? Math.round((e.amount / this.MONTHLY.expenses) * 100) : 0;
            expenses += `\n${i + 1}. ${e.category}: ${this.formatRupiah(e.amount)} (${pct}%)`;
            total += e.amount;
        });
        
        expenses += `

<b>💰 Total: ${this.formatRupiah(total)}</b>

<b>⚠️ Note:</b>
• Gaji = Salary expenses
• Marketing = Ads, campaigns
• Tools = SaaS subscriptions
• Operasional = Office, utilities
`;
        return expenses;
    },
    
    /**
     * Get invoice template with Bitcoin option
     */
    getInvoiceTemplate() {
        return `
📄 <b>Invoice Template</b>

```
INVOICE

From:
Maha Lakshmi Holdings
Jl. Bali, Indonesia

To:
[Client Name]
[Client Address]

Invoice #: INV-XXXX
Date: [Date]
Due: [Date + 14 days]

Description          Amount
---------------------------------
[Service]         Rp X,XXX,XXX
                   ----------
Subtotal:         Rp X,XXX,XXX
PPN (11%):        Rp XXX,XXX
                   ----------
TOTAL:            Rp X,XXX,XXX

Payment to:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏦 BCA: 6485086645
   a/n: Owner/Shareholder

₿ BITCOIN (Optional):
   ${this.CEO_WALLET.btcAddress}

Thank you!
```
`;
    },
    
    /**
     * Get P&L report
     */
    getProfitLoss() {
        const profit = this.MONTHLY.revenue - this.MONTHLY.expenses;
        
        return `
📊 <b>Profit & Loss Statement</b>

<b>REVENUE:</b>
├── SaaS: ${this.formatRupiah(0)}
├── Freelance: ${this.formatRupiah(0)}
├── Digital Products: ${this.formatRupiah(0)}
└── Total Revenue: ${this.formatRupiah(this.MONTHLY.revenue)}

<b>EXPENSES:</b>
`;
        this.EXPENSES.forEach(e => {
            if (e.amount > 0) {
                return `\n├── ${e.category}: ${this.formatRupiah(e.amount)}`;
            }
        });
        
        const profitBtc = this.idrToSatoshi(profit);
        
        return `
└── Total Expenses: ${this.formatRupiah(this.MONTHLY.expenses)}

<b>📈 NET PROFIT: ${this.formatRupiah(profit)}</b>
<b>📊 MARGIN: ${this.MONTHLY.revenue > 0 ? Math.round((profit / this.MONTHLY.revenue) * 100) : 0}%</b>

<b>💡 Jika ditransfer ke CEO:</b>
└── ~${this.formatBtc(profitBtc)} (BTC)
`;
    },
    
    /**
     * Main query handler
     */
    query(q) {
        const query = q.toLowerCase();
        
        if (query.includes('transfer') || query.includes('ceo') || query.includes('bitcoin') || query.includes('btc')) {
            return this.getCeoTransfer();
        }
        if (query.includes('expense') || query.includes('biaya')) {
            return this.getExpenses();
        }
        if (query.includes('invoice') || query.includes('tagihan')) {
            return this.getInvoiceTemplate();
        }
        if (query.includes('profit') || query.includes('pnl')) {
            return this.getProfitLoss();
        }
        if (query.includes('finance') || query.includes('uang') || query.includes('keuangan')) {
            return this.getDashboard();
        }
        return this.getDashboard();
    }
};

if (typeof window !== 'undefined') window.FinanceAgent = FinanceAgent;
