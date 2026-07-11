/**
 * ================================================
 * SALES AGENT - GAURANGA
 * ================================================
 * Agent ID: sales-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const SalesAgent = {
    // Revenue targets
    TARGETS: {
        saas: 30000000,
        freelance: 25000000,
        digital: 20000000,
        total: 75000000
    },
    
    // Current revenue (simulated)
    CURRENT: {
        saas: 0,
        freelance: 0,
        digital: 0
    },
    
    // Pipeline stages
    PIPELINE_STAGES: [
        { name: 'Lead', count: 50, conversion: 100 },
        { name: 'Qualified', count: 25, conversion: 50 },
        { name: 'Proposal', count: 15, conversion: 30 },
        { name: 'Negotiation', count: 10, conversion: 20 },
        { name: 'Closed Won', count: 5, conversion: 10 }
    ],
    
    // Products
    PRODUCTS: {
        saas: [
            { name: 'Starter', price: 500000, period: 'bulan', features: ['Basic features', 'Email support'] },
            { name: 'Professional', price: 1500000, period: 'bulan', features: ['All features', 'Priority support', 'Analytics'] },
            { name: 'Enterprise', price: 5000000, period: 'bulan', features: ['Custom solution', '24/7 support', 'Dedicated manager'] }
        ],
        freelance: [
            { name: 'Landing Page', price: 3000000, duration: '1-2 minggu' },
            { name: 'Corporate Website', price: 10000000, duration: '2-4 minggu' },
            { name: 'E-commerce', price: 25000000, duration: '4-8 minggu' },
            { name: 'Simple App', price: 15000000, duration: '2-4 minggu' },
            { name: 'Medium App', price: 35000000, duration: '4-8 minggu' }
        ],
        digital: [
            { name: 'E-Course', priceRange: '500rb - 2jt' },
            { name: 'Template', priceRange: '99rb - 500rb' },
            { name: 'Preset', priceRange: '99rb - 299rb' }
        ]
    },
    
    // Sales tips
    SALES_TIPS: [
        "Always qualify leads before pitching",
        "Listen more, talk less - understand the pain points",
        "Follow up within 24 hours of any interaction",
        "Use social proof - case studies and testimonials",
        "Create urgency without being pushy",
        "Bundle products for higher deal value",
        "Always ask for referral at the end of successful sale"
    ],
    
    /**
     * Format currency
     */
    formatRupiah(num) {
        return 'Rp ' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    },
    
    /**
     * Get progress percentage
     */
    getProgress(current, target) {
        return Math.round((current / target) * 100);
    },
    
    /**
     * Get sales dashboard
     */
    getDashboard() {
        const totalCurrent = this.CURRENT.saas + this.CURRENT.freelance + this.CURRENT.digital;
        const totalTarget = this.TARGETS.total;
        const totalProgress = this.getProgress(totalCurrent, totalTarget);
        
        let dashboard = `
💰 <b>Sales Dashboard - Maha Lakshmi Holdings</b>

<b>📊 Overall Progress:</b>
├── Target: ${this.formatRupiah(totalTarget)}
├── Current: ${this.formatRupiah(totalCurrent)}
└── Progress: ${totalProgress}% ${totalProgress >= 50 ? '🟢' : totalProgress >= 25 ? '🟡' : '🔴'}

<b>📈 Revenue by Channel:</b>

<b>☁️ SaaS Products:</b>
├── Target: ${this.formatRupiah(this.TARGETS.saas)}
├── Current: ${this.formatRupiah(this.CURRENT.saas)}
└── Progress: ${this.getProgress(this.CURRENT.saas, this.TARGETS.saas)}%

<b>🛠️ Freelance Services:</b>
├── Target: ${this.formatRupiah(this.TARGETS.freelance)}
├── Current: ${this.formatRupiah(this.CURRENT.freelance)}
└── Progress: ${this.getProgress(this.CURRENT.freelance, this.TARGETS.freelance)}%

<b>📚 Digital Products:</b>
├── Target: ${this.formatRupiah(this.TARGETS.digital)}
├── Current: ${this.formatRupiah(this.CURRENT.digital)}
└── Progress: ${this.getProgress(this.CURRENT.digital, this.TARGETS.digital)}%

<b>💡 Mau update progress sales, Pak Pur?</b>
Ketik: "update sales [jumlah]"
`;
        return dashboard;
    },
    
    /**
     * Get pipeline status
     */
    getPipeline() {
        let pipeline = `
📊 <b>Sales Pipeline</b>

<b>Funnel Conversion:</b>
`;
        this.PIPELINE_STAGES.forEach((stage, i) => {
            const arrow = i < this.PIPELINE_STAGES.length - 1 ? '→' : '';
            pipeline += `\n${i + 1}. ${stage.name}: ${stage.count} leads (${stage.conversion}%) ${arrow}`;
        });
        
        pipeline += `

<b>📋 Pipeline Actions:</b>
• Follow up dengan Qualified leads
• Kirim proposal ke Negotiation stage
• Tutup deal di Closed Won
• Catat reason jika Lost

<b>Mau update pipeline, Pak Pur?</b>
Ketik: "update pipeline [stage] [jumlah]"
`;
        return pipeline;
    },
    
    /**
     * Get pricing info
     */
    getPricing() {
        let pricing = `
💰 <b>Price List - Maha Lakshmi Holdings</b>

<b>☁️ SaaS Products (per bulan):</b>
`;
        this.PRODUCTS.saas.forEach(product => {
            pricing += `\n• ${product.name}: ${this.formatRupiah(product.price)}/${product.period}
   Features: ${product.features.join(', ')}`;
        });
        
        pricing += `

<b>🛠️ Freelance Services:</b>
`;
        this.PRODUCTS.freelance.forEach(product => {
            pricing += `\n• ${product.name}: ${this.formatRupiah(product.price)}
   Durasi: ${product.duration}`;
        });
        
        pricing += `

<b>📚 Digital Products:</b>
`;
        this.PRODUCTS.digital.forEach(product => {
            pricing += `\n• ${product.name}: ${product.priceRange}`;
        });
        
        pricing += `

<b>💡 Tips:</b> Bundle products untuk discount!
`;
        return pricing;
    },
    
    /**
     * Get sales tips
     */
    getSalesTips() {
        let tips = `
🎯 <b>Sales Tips & Best Practices</b>

<b>📋 Daily Routine:</b>
• 08:00 - Check inbox & respond leads
• 09:00 - Cold outreach to new prospects
• 10:00 - Product demos
• 14:00 - Follow-up & negotiation
• 17:00 - Update CRM & daily report

<b>💡 Top Tips:</b>
${this.SALES_TIPS.map((tip, i) => `${i + 1}. ${tip}`).join('\n')}

<b>⚠️ Common Mistakes to Avoid:</b>
• Not following up promptly
• Pitching before understanding needs
• Giving discounts too easily
• Not asking for the sale

<b>🎯 Lead Qualification (BANT):</b>
• Budget - Can they afford it?
• Authority - Can they decide?
• Need - Do they have the problem?
• Timeline - When do they need it?
`;
        return tips;
    },
    
    /**
     * Get revenue targets
     */
    getRevenueTargets() {
        return `
💰 <b>Revenue Targets</b>

| Channel | Monthly Target |
|---------|---------------|
| SaaS | ${this.formatRupiah(this.TARGETS.saas)} |
| Freelance | ${this.formatRupiah(this.TARGETS.freelance)} |
| Digital | ${this.formatRupiah(this.TARGETS.digital)} |
| <b>TOTAL</b> | <b>${this.formatRupiah(this.TARGETS.total)}</b> |

<b>📊 Required Deals:</b>
• SaaS (avg Rp 1.5jt): ~20 deals/bulan
• Freelance (avg Rp 10jt): ~3 deals/bulan
• Digital (avg Rp 500rb): ~40 sales/bulan

<b>🎯 Goal: Close 1-2 deals per hari!</b>
`;
    },
    
    /**
     * Main query handler
     */
    query(query) {
        const q = query.toLowerCase();
        
        if (q.includes('sales') || q.includes('revenue') || q.includes('uang')) {
            return this.getDashboard();
        }
        
        if (q.includes('pipeline') || q.includes('leads') || q.includes('funnel')) {
            return this.getPipeline();
        }
        
        if (q.includes('harga') || q.includes('price') || q.includes('pricing')) {
            return this.getPricing();
        }
        
        if (q.includes('tips') || q.includes('best practice')) {
            return this.getSalesTips();
        }
        
        if (q.includes('target')) {
            return this.getRevenueTargets();
        }
        
        return this.getDashboard();
    }
};

// Export for Node.js / ES modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SalesAgent;
}

// Make available globally
if (typeof window !== 'undefined') {
    window.SalesAgent = SalesAgent;
}
