/**
 * ================================================
 * KNOWLEDGE AGENT - GAURANGA
 * ================================================
 * Agent ID: knowledge-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const KnowledgeAgent = {
    // Knowledge Base
    KB: {
        // Company Info
        company: {
            name: "Maha Lakshmi Holdings",
            type: "Multi-SBU Corporation",
            founder: "I Made Purna Ananda (Pak Pur)",
            wife: "Ni Wayan Lestiani (Bunda Lila)",
            children: ["Putu Gaurangga Vishnu Bhakta", "Kadek Srutakirti"],
            bank: { name: "BCA", account: "6485086645" },
            whatsapp: "081337558787",
            github: "https://github.com/prahlad168"
        },
        
        // Products & Services
        products: {
            saas: {
                name: "SaaS Products",
                tiers: [
                    { name: "Starter", price: 500000, period: "bulan" },
                    { name: "Professional", price: 1500000, period: "bulan" },
                    { name: "Enterprise", price: 5000000, period: "bulan" }
                ],
                target: "Rp 30.000.000/bulan"
            },
            freelance: {
                name: "Freelance Services",
                services: [
                    { name: "Landing Page", price: 3000000 },
                    { name: "Corporate Website", price: 10000000 },
                    { name: "E-commerce", price: 25000000 },
                    { name: "Simple App", price: 15000000 },
                    { name: "Medium App", price: 35000000 }
                ],
                target: "Rp 25.000.000/bulan"
            },
            digital: {
                name: "Digital Products",
                items: [
                    { name: "E-Course", priceRange: "500rb - 2jt" },
                    { name: "Template", priceRange: "99rb - 500rb" },
                    { name: "Preset", priceRange: "99rb - 299rb" }
                ],
                target: "Rp 20.000.000/bulan"
            }
        },
        
        // Revenue Targets
        targets: {
            month1: 5000000,
            month3: 25000000,
            month6: 100000000
        },
        
        // SBUs
        sbus: [
            { name: "Hospital Management", emoji: "🏥" },
            { name: "E-Commerce", emoji: "🛒" },
            { name: "Education Tech", emoji: "🎓" },
            { name: "Travel Tech", emoji: "✈️" },
            { name: "Property Tech", emoji: "🏠" },
            { name: "Food Tech", emoji: "🍔" }
        ],
        
        // Team Structure
        agents: {
            sales: {
                name: "Sales Team",
                members: [
                    { name: "SaaS Sales Agent", target: "Rp 30jt/bulan" },
                    { name: "Freelance Agent", target: "Rp 25jt/bulan" },
                    { name: "Digital Products Agent", target: "Rp 20jt/bulan" }
                ]
            },
            marketing: {
                name: "Marketing Team",
                members: [
                    { name: "Content Agent", target: "30 pieces/bulan" },
                    { name: "Social Media Agent", target: "500K reach/bulan" },
                    { name: "SEO & Ads Agent", target: "3x ROAS" },
                    { name: "Email Marketing Agent", target: "50K subscribers" }
                ]
            },
            operations: {
                name: "Operations Team",
                members: [
                    { name: "HR Agent", target: "10 orang dalam 6 bulan" },
                    { name: "Finance Agent", target: "99.9% accuracy" },
                    { name: "Project Manager Agent", target: "95% on-time" }
                ]
            },
            support: {
                name: "Support Team",
                members: [
                    { name: "Customer Service Agent", target: "< 1 jam response" },
                    { name: "Success Manager Agent", target: "> 85% retention" }
                ]
            }
        },
        
        // Skills
        skills: {
            programming: ["PHP", "Laravel", "React", "Vue", "Python", "WordPress", "Firebase", "HTML/CSS"],
            ai: ["LLM Integration", "RAG Systems", "Agent Development", "Automation Scripts"],
            marketing: ["SEO", "Content Writing", "Social Media", "Email Marketing", "Paid Ads", "Copywriting"],
            sales: ["Lead Generation", "Cold Outreach", "Negotiation", "CRM Management"],
            finance: ["Accounting", "Invoicing", "Tax Calculation", "Financial Analysis"]
        }
    },
    
    /**
     * Format currency Indonesia
     */
    formatRupiah(num) {
        return 'Rp ' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    },
    
    /**
     * Get company info
     */
    getCompanyInfo() {
        const c = this.KB.company;
        return `
🏢 <b>${c.name}</b>

<b>📋 Info Dasar:</b>
• Tipe: ${c.type}
• Founder: ${c.founder}
• WhatsApp: ${c.whatsapp}
• GitHub: ${c.github}

<b>👨‍👩‍👧‍👦 Keluarga:</b>
• Istri: ${c.wife}
• Anak 1: ${c.children[0]}
• Anak 2: ${c.children[1]}

<b>🏦 Bank:</b>
• ${c.bank.name}: ${c.bank.account}
`;
    },
    
    /**
     * Get revenue targets
     */
    getRevenueTargets() {
        const t = this.KB.targets;
        return `
💰 <b>Target Revenue Maha Lakshmi Holdings</b>

| Timeline | Target |
|----------|--------|
| Bulan 1 | ${this.formatRupiah(t.month1)} |
| Bulan 3 | ${this.formatRupiah(t.month3)} |
| Bulan 6 | ${this.formatRupiah(t.month6)} |

<b>📊 Total Target:</b> ${this.formatRupiah(t.month6)}
`;
    },
    
    /**
     * Get pricing info
     */
    getPricing() {
        const p = this.KB.products;
        let pricing = `
💰 <b>Harga Produk & Jasa</b>

<b>☁️ SaaS (per bulan):</b>
`;
        p.saas.tiers.forEach(tier => {
            pricing += `• ${tier.name}: ${this.formatRupiah(tier.price)}/${tier.period}\n`;
        });
        
        pricing += `\n<b>🛠️ Freelance Services:</b>\n`;
        p.freelance.services.forEach(svc => {
            pricing += `• ${svc.name}: ${this.formatRupiah(svc.price)}\n`;
        });
        
        pricing += `\n<b>📚 Digital Products:</b>\n`;
        p.digital.items.forEach(item => {
            pricing += `• ${item.name}: ${item.priceRange}\n`;
        });
        
        return pricing;
    },
    
    /**
     * Get SBUs list
     */
    getSBUs() {
        let sbus = `
🏢 <b>Strategic Business Units (SBUs)</b>

`;
        this.KB.sbus.forEach((sbu, i) => {
            sbus += `${i + 1}. ${sbu.emoji} ${sbu.name}\n`;
        });
        return sbus;
    },
    
    /**
     * Get team/agents info
     */
    getTeam() {
        let team = `
👥 <b>Genesis Council - 75+ AI Agents</b>

`;
        Object.entries(this.KB.agents).forEach(([key, division]) => {
            team += `\n<b>${division.name}:</b>\n`;
            division.members.forEach(member => {
                team += `• ${member.name} (${member.target})\n`;
            });
        });
        return team;
    },
    
    /**
     * Get skills list
     */
    getSkills() {
        let skills = `
🛠️ <b>Skills Library</b>

`;
        Object.entries(this.KB.skills).forEach(([category, items]) => {
            skills += `\n<b>${category.toUpperCase()}:</b>\n`;
            skills += items.map(s => `• ${s}`).join('\n') + '\n';
        });
        return skills;
    },
    
    /**
     * Query knowledge
     */
    query(query) {
        const q = query.toLowerCase();
        
        // Company queries
        if (q.includes('company') || q.includes('perusahaan') || q.includes('maha') || q.includes('lakshmi')) {
            return this.getCompanyInfo();
        }
        
        // Founder queries
        if (q.includes('founder') || q.includes('pemilik') || q.includes(' founder')) {
            return this.getCompanyInfo();
        }
        
        // Target queries
        if (q.includes('target') || q.includes('revenue') || q.includes('uang') || q.includes('pendapatan')) {
            return this.getRevenueTargets();
        }
        
        // Pricing queries
        if (q.includes('harga') || q.includes('price') || q.includes('biaya') || q.includes('berapa')) {
            return this.getPricing();
        }
        
        // SBU queries
        if (q.includes('sbu') || q.includes('bisnis') || q.includes('unit')) {
            return this.getSBUs();
        }
        
        // Team queries
        if (q.includes('tim') || q.includes('team') || q.includes('agen') || q.includes('agent')) {
            return this.getTeam();
        }
        
        // Skills queries
        if (q.includes('skill') || q.includes('kemampuan') || q.includes('programming') || q.includes('ai')) {
            return this.getSkills();
        }
        
        // Default - show all categories
        return this.getSummary();
    },
    
    /**
     * Get summary of all knowledge
     */
    getSummary() {
        return `
🧠 <b>Knowledge Base Summary</b>

Halo Pak Pur! Saya Knowledge Agent. Saya bisa bantu dengan:

🏢 <b>Company Info:</b> "info company" / "siapa founder"
💰 <b>Revenue Targets:</b> "target revenue"
💵 <b>Pricing:</b> "harga" / "price list"
🏢 <b>SBUs:</b> "list sbu" / "bisnis apa aja"
👥 <b>Team:</b> "team" / "agents"
🛠️ <b>Skills:</b> "skills" / "kemampuan"

Mau tanya apa, Pak Pur? 😊
`;
    },
    
    /**
     * Get all categories
     */
    getCategories() {
        return Object.keys(this.KB);
    },
    
    /**
     * Get full knowledge base
     */
    getFullKB() {
        return this.KB;
    }
};

// Export for Node.js / ES modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KnowledgeAgent;
}

// Make available globally
if (typeof window !== 'undefined') {
    window.KnowledgeAgent = KnowledgeAgent;
}
