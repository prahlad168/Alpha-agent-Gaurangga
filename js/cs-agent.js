/**
 * ================================================
 * CUSTOMER SERVICE AGENT - GAURANGA
 * ================================================
 * Agent ID: cs-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const CSAgent = {
    // SLA targets
    SLA: {
        email: '4 hours',
        liveChat: '1 minute',
        socialMedia: '2 hours',
        firstResponse: '< 1 hour'
    },
    
    // Ticket categories
    CATEGORIES: [
        { name: 'Billing Issues', count: 0, priority: 'high' },
        { name: 'Technical Problems', count: 0, priority: 'high' },
        { name: 'Feature Requests', count: 0, priority: 'medium' },
        { name: 'Account Management', count: 0, priority: 'medium' },
        { name: 'General Inquiries', count: 0, priority: 'low' }
    ],
    
    // Stats
    STATS: {
        totalTickets: 0,
        resolved: 0,
        avgResponseTime: 0,
        csat: 0
    },
    
    /**
     * Get dashboard
     */
    getDashboard() {
        let dashboard = `
🎧 <b>Customer Service Dashboard</b>

<b>📊 Today's Stats:</b>
├── Total Tickets: ${this.STATS.totalTickets}
├── Resolved: ${this.STATS.resolved}
├── CSAT Score: ${this.STATS.csat}%
└── Avg Response: ${this.STATS.avgResponseTime} min

<b>⚡ SLA Targets:</b>
├── Email: < ${this.SLA.email}
├── Live Chat: < ${this.SLA.liveChat}
├── Social Media: < ${this.SLA.socialMedia}
└── First Response: ${this.SLA.firstResponse}

<b>📋 Open Tickets by Category:</b>
`;
        this.CATEGORIES.forEach(c => {
            const emoji = c.priority === 'high' ? '🔴' : c.priority === 'medium' ? '🟡' : '🟢';
            dashboard += `\n• ${emoji} ${c.name}: ${c.count} open`;
        });
        
        dashboard += `

<b>Mau lihat detail tickets?</b>
Ketik: "tickets" atau "open tickets"
`;
        return dashboard;
    },
    
    /**
     * Get tickets
     */
    getTickets(status = 'open') {
        let tickets = `
🎫 <b>Support Tickets</b>

<b>Status: ${status.toUpperCase()}</b>

<b>🔴 High Priority:</b>
`;
        const highTickets = this.CATEGORIES.filter(c => c.priority === 'high' && c.count > 0);
        if (highTickets.length === 0) {
            tickets += '\n   No high priority tickets';
        } else {
            highTickets.forEach(t => {
                tickets += `\n   • ${t.name}: ${t.count} tickets`;
            });
        }
        
        tickets += `

<b>🟡 Medium Priority:</b>
`;
        const medTickets = this.CATEGORIES.filter(c => c.priority === 'medium' && c.count > 0);
        if (medTickets.length === 0) {
            tickets += '\n   No medium priority tickets';
        } else {
            medTickets.forEach(t => {
                tickets += `\n   • ${t.name}: ${t.count} tickets`;
            });
        }
        
        tickets += `

<b>🟢 Low Priority:</b>
`;
        const lowTickets = this.CATEGORIES.filter(c => c.priority === 'low' && c.count > 0);
        if (lowTickets.length === 0) {
            tickets += '\n   No low priority tickets';
        } else {
            lowTickets.forEach(t => {
                tickets += `\n   • ${t.name}: ${t.count} tickets`;
            });
        }
        
        tickets += `

<b>💡 All tickets akan direspon dalam SLA!</b>
`;
        return tickets;
    },
    
    /**
     * Get response templates
     */
    getTemplates() {
        return `
📝 <b>Response Templates</b>

<b>1️⃣ Greeting:</b>
"Hi! Terima kasih udah hubungi kami. Saya akan bantu解决 masalah kamu 😊"

<b>2️⃣ Billing Issue:</b>
"Hi, terkait billing kamu... Saya sudah cek dan akan kami proses dalam 1x24 jam."

<b>3️⃣ Technical Support:</b>
"Hi, untuk issue teknis yang kamu alami... Coba langkah berikut:
1. Clear cache browser
2. Login ulang
3. Jika masih error, silakan screenshot"

<b>4️⃣ Feature Request:</b>
"Hi! Terima kasih atas masukannya. Kami sudah catat dan akan dipertimbangkan untuk update selanjutnya."

<b>5️⃣ Closing:</b>
"Ada yang lain yang bisa kami bantu? 😊"

<b>💡 Pakai template sesuai konteks, ya!</b>
`;
    },
    
    /**
     * Main query handler
     */
    query(q) {
        if (q.includes('ticket') || q.includes('support')) {
            return this.getTickets();
        }
        if (q.includes('template') || q.includes('response')) {
            return this.getTemplates();
        }
        if (q.includes('cs') || q.includes('customer service')) {
            return this.getDashboard();
        }
        return this.getDashboard();
    }
};

if (typeof window !== 'undefined') window.CSAgent = CSAgent;
