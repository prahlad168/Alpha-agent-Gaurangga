/**
 * ================================================
 * MARKETING AGENT - GAURANGA
 * ================================================
 * Agent ID: marketing-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const MarketingAgent = {
    // Targets
    TARGETS: {
        traffic: 100000,
        emailSubscribers: 50000,
        socialFollowers: 100000,
        contentPerMonth: 30
    },
    
    // Current stats
    CURRENT: {
        traffic: 0,
        emailSubscribers: 0,
        socialFollowers: 0,
        contentPublished: 0
    },
    
    // Campaigns
    CAMPAIGNS: [
        { name: 'Brand Awareness', status: 'planning', budget: 2000000, roi: 0 },
        { name: 'Product Launch', status: 'planning', budget: 5000000, roi: 0 },
        { name: 'Lead Generation', status: 'planning', budget: 3000000, roi: 0 }
    ],
    
    // Channels
    CHANNELS: [
        { name: 'Google Ads', budget: 5000000, status: 'not_started' },
        { name: 'Facebook/IG Ads', budget: 3000000, status: 'not_started' },
        { name: 'SEO', budget: 2000000, status: 'not_started' },
        { name: 'Content Marketing', budget: 1000000, status: 'not_started' }
    ],
    
    /**
     * Format currency
     */
    formatRupiah(num) {
        return 'Rp ' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    },
    
    /**
     * Get progress
     */
    getProgress(current, target) {
        return Math.round((current / target) * 100);
    },
    
    /**
     * Get dashboard
     */
    getDashboard() {
        let dashboard = `
📢 <b>Marketing Dashboard - Maha Lakshmi Holdings</b>

<b>📊 Overall Progress:</b>
├── Target Traffic: ${this.TARGETS.traffic.toLocaleString()} visitors
├── Current Traffic: ${this.CURRENT.traffic.toLocaleString()}
└── Progress: ${this.getProgress(this.CURRENT.traffic, this.TARGETS.traffic)}%

<b>📧 Email:</b>
├── Target: ${this.TARGETS.emailSubscribers.toLocaleString()} subscribers
├── Current: ${this.CURRENT.emailSubscribers.toLocaleString()}
└── Progress: ${this.getProgress(this.CURRENT.emailSubscribers, this.TARGETS.emailSubscribers)}%

<b>📱 Social Media:</b>
├── Target: ${this.TARGETS.socialFollowers.toLocaleString()} followers
├── Current: ${this.CURRENT.socialFollowers.toLocaleString()}
└── Progress: ${this.getProgress(this.CURRENT.socialFollowers, this.TARGETS.socialFollowers)}%

<b>✍️ Content:</b>
├── Target: ${this.TARGETS.contentPerMonth} pieces/month
├── Published: ${this.CURRENT.contentPublished}
└── Progress: ${this.getProgress(this.CURRENT.contentPublished, this.TARGETS.contentPerMonth)}%

<b>Mau mulai kampanyenya, Pak Pur?</b>
Ketik: "mulai campaign [nama]"
`;
        return dashboard;
    },
    
    /**
     * Get campaigns
     */
    getCampaigns() {
        let campaigns = `
📢 <b>Marketing Campaigns</b>

<b>🗓️ Planned Campaigns:</b>
`;
        this.CAMPAIGNS.forEach((c, i) => {
            const statusEmoji = c.status === 'active' ? '🟢' : c.status === 'paused' ? '🟡' : '⚪';
            campaigns += `\n${i + 1}. ${statusEmoji} ${c.name}
   Budget: ${this.formatRupiah(c.budget)}
   Status: ${c.status}
   ROI: ${c.roi}x`;
        });
        
        campaigns += `

<b>💡 Mau launch campaign baru?</b>
Ketik: "launch campaign [nama]"
`;
        return campaigns;
    },
    
    /**
     * Get channels
     */
    getChannels() {
        let channels = `
📱 <b>Marketing Channels</b>

<b>💰 Budget Allocation:</b>
`;
        const totalBudget = this.CHANNELS.reduce((sum, c) => sum + c.budget, 0);
        this.CHANNELS.forEach((c, i) => {
            const pct = Math.round((c.budget / totalBudget) * 100);
            const statusEmoji = c.status === 'active' ? '🟢' : c.status === 'paused' ? '🟡' : '⬜';
            channels += `\n${i + 1}. ${statusEmoji} ${c.name}
   Budget: ${this.formatRupiah(c.budget)} (${pct}%)
   Status: ${c.status}`;
        });
        
        channels += `

<b>📊 Total Budget: ${this.formatRupiah(totalBudget)}/bulan</b>
`;
        return channels;
    },
    
    /**
     * Get social media strategy
     */
    getSocialStrategy() {
        return `
📱 <b>Social Media Strategy</b>

<b>📸 Instagram (20 posts/bulan):</b>
• Educational: 30%
• Entertainment: 25%
• Promotional: 20%
• Behind scenes: 15%
• User generated: 10%

<b>🎵 TikTok (30 videos/bulan):</b>
• Quick tips: 40%
• Trends: 25%
• Product demos: 20%
• Behind scenes: 15%

<b>💼 LinkedIn (15 posts/bulan):</b>
• Industry insights: 40%
• Company updates: 20%
• Professional tips: 25%

<b>🎯 Target Reach: 500K/month</b>
`;
    },
    
    /**
     * Main query handler
     */
    query(q) {
        if (q.includes('marketing') || q.includes('promosi')) {
            return this.getDashboard();
        }
        if (q.includes('campaign')) {
            return this.getCampaigns();
        }
        if (q.includes('channel') || q.includes('social media')) {
            return this.getChannels();
        }
        if (q.includes('social strategy') || q.includes('instagram') || q.includes('tiktok')) {
            return this.getSocialStrategy();
        }
        return this.getDashboard();
    }
};

if (typeof window !== 'undefined') window.MarketingAgent = MarketingAgent;
