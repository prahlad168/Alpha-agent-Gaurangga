/**
 * ================================================
 * FINANCE AGENT - GAURANGA
 * ================================================
 * Agent ID: finance-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
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
     * Get dashboard
     */
    getDashboard() {
        const revenue = this.MONTHLY.revenue;
        const expenses = this.MONTHLY.expenses;
        const profit = revenue - expenses;
        const margin = revenue > 0 ? Math.round((profit / revenue) * 100) : 0;
        
        let dashboard = `
💵 <b>Finance Dashboard</b>

<b>📊 This Month:</b>
├── Revenue: ${this.formatRupiah(revenue)}
├── Expenses: ${this.formatRupiah(expenses)}
├── Profit: ${this.formatRupiah(profit)}
└── Margin: ${margin}%

<b>📈 Revenue Targets:</b>
├── Month 1: ${this.formatRupiah(5000000)}
├── Month 3: ${this.formatRupiah(25000000)}
└── Month 6: ${this.formatRupiah(100000000)}

<b>🎯 Accuracy Target: ${this.ACCURACY_TARGET}%</b>

<b>Mau lihat expense breakdown?</b>
Ketik: "expenses"
`;
        return dashboard;
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
     * Get invoice template
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
BCA: 6485086645
a/n: Owner

Thank you!
```
`;
    },
    
    /**
     * Get P&L report
     */
    getProfitLoss() {
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
        
        return `
└── Total Expenses: ${this.formatRupiah(this.MONTHLY.expenses)}

<b>📈 NET PROFIT: ${this.formatRupiah(this.MONTHLY.profit)}</b>
<b>📊 MARGIN: ${this.MONTHLY.revenue > 0 ? Math.round((this.MONTHLY.profit / this.MONTHLY.revenue) * 100) : 0}%</b>
`;
    },
    
    /**
     * Main query handler
     */
    query(q) {
        if (q.includes('expense') || q.includes('biaya')) {
            return this.getExpenses();
        }
        if (q.includes('invoice') || q.includes('tagihan')) {
            return this.getInvoiceTemplate();
        }
        if (q.includes('profit') || q.includes('pnl')) {
            return this.getProfitLoss();
        }
        if (q.includes('finance') || q.includes('uang') || q.includes('keuangan')) {
            return this.getDashboard();
        }
        return this.getDashboard();
    }
};

if (typeof window !== 'undefined') window.FinanceAgent = FinanceAgent;
