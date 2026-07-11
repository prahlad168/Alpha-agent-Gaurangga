/**
 * ================================================
 * DAILY BRIEFING AGENT - GAURANGA
 * ================================================
 * Agent ID: daily-briefing-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const DailyBriefingAgent = {
    // Configuration
    GENESIS_START_DATE: new Date('2026-07-05'),
    
    // Monthly revenue targets
    REVENUE_TARGETS: {
        month1: 5000000,
        month3: 25000000,
        month6: 100000000
    },
    
    // Nama bulan Indonesia
    BULAN_ID: [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ],
    
    // Nama hari Indonesia
    HARI_ID: ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'],
    
    // Cuaca options
    CUACA: ['☀️ Cerah', '🌤️ Mendung', '🌧️ Hujan', '⛅ Berawan', '🌩️ Badai'],
    
    // Motivational quotes
    QUOTES: [
        '"Dari nol menjadi satu, dari satu menjadi banyak." - Pak Pur',
        '"Success is not final, failure is not fatal." - Winston Churchill',
        '"The best time to plant a tree was 20 years ago. The second best time is now."',
        '"行动胜于空谈。" - Confucius (Chinese Proverb)',
        '"Quality is not an act, it is a habit." - Aristotle'
    ],
    
    /**
     * Calculate Genesis Day
     */
    getGenesisDay() {
        const today = new Date();
        const diffTime = today - this.GENESIS_START_DATE;
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        return diffDays + 1; // Day 1 starts at Genesis
    },
    
    /**
     * Format tanggal Indonesia
     */
    formatTanggal(date) {
        const hari = this.HARI_ID[date.getDay()];
        const tanggal = date.getDate();
        const bulan = this.BULAN_ID[date.getMonth()];
        const tahun = date.getYear() + 1900;
        return `${hari}, ${tanggal} ${bulan} ${tahun}`;
    },
    
    /**
     * Get waktu greeting
     */
    getGreeting() {
        const hour = new Date().getHours();
        if (hour < 12) return 'Selamat Pagi';
        if (hour < 15) return 'Selamat Siang';
        if (hour < 18) return 'Selamat Sore';
        return 'Selamat Malam';
    },
    
    /**
     * Get random cuaca
     */
    getCuaca() {
        return this.CUACA[Math.floor(Math.random() * this.CUACA.length)];
    },
    
    /**
     * Get random quote
     */
    getQuote() {
        return this.QUOTES[Math.floor(Math.random() * this.QUOTES.length)];
    },
    
    /**
     * Format currency Indonesia
     */
    formatRupiah(num) {
        return 'Rp ' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    },
    
    /**
     * Get current month
     */
    getCurrentMonth() {
        return new Date().getMonth() + 1;
    },
    
    /**
     * Get target revenue bulan ini
     */
    getTargetBulanIni() {
        return this.REVENUE_TARGETS.month1;
    },
    
    /**
     * Generate todo list untuk demo
     */
    getTodoList() {
        return [
            { task: 'Check inbox & respond email', done: true },
            { task: 'Review sales pipeline', done: false },
            { task: 'Update project status', done: true },
            { task: 'Prepare tomorrow briefing', done: false },
            { task: 'Follow up with leads', done: false }
        ];
    },
    
    /**
     * Generate full morning report
     */
    generateReport() {
        const today = new Date();
        const genesisDay = this.getGenesisDay();
        const greeting = this.getGreeting();
        const tanggal = this.formatTanggal(today);
        const cuaca = this.getCuaca();
        const quote = this.getQuote();
        
        const todoList = this.getTodoList();
        const completed = todoList.filter(t => t.done).length;
        const total = todoList.length;
        const progressPercent = Math.round((completed / total) * 100);
        
        // Simulasi revenue (nanti bisa dari database/API)
        const targetRevenue = this.getTargetBulanIni();
        const currentRevenue = Math.floor(targetRevenue * (genesisDay / 30) * 0.7);
        
        // Generate ASCII art report
        let report = `
╔══════════════════════════════════════════════════════════════╗
║           🌅 ${greeting.toUpperCase()}, PAK PUR! 🌅                       ║
║                    Genesis Day #${genesisDay.toString().padStart(3, '0')}                        ║
║                   ${tanggal}                              ║
║                      ${cuaca}                              ║
╚══════════════════════════════════════════════════════════════╝

📅 Jadwal Hari Ini:
├── 08:00 - Briefing pagi
├── 10:00 - Team standup meeting  
├── 13:00 - Client call
└── 15:00 - Project review

💰 Progress Target Bulan Ini:
├── Target: ${this.formatRupiah(targetRevenue)}
├── Current: ${this.formatRupiah(currentRevenue)}
├── Progress: ${progressPercent}% ${progressPercent >= 30 ? '📊' : '⚠️'}
└── Sisa: ${this.formatRupiah(targetRevenue - currentRevenue)}

🎯 Todo Hari Ini:
${todoList.map(t => `├── [${t.done ? '✓' : ' '}] ${t.task}`).join('\n')}

📊 Statistik:
├── Total Tasks: ${total}
├── Completed: ${completed}
└── Remaining: ${total - completed}

💬 Motivasi:
${quote}

🌟 Semangat Pak Pur! Kamu pasti bisa! 🌟
        `.trim();
        
        return report;
    },
    
    /**
     * Get report as object (for API response)
     */
    getReportData() {
        const today = new Date();
        return {
            genesisDay: this.getGenesisDay(),
            greeting: this.getGreeting(),
            tanggal: this.formatTanggal(today),
            cuaca: this.getCuaca(),
            quote: this.getQuote(),
            revenue: {
                target: this.getTargetBulanIni(),
                current: Math.floor(this.getTargetBulanIni() * (this.getGenesisDay() / 30) * 0.7)
            },
            todos: this.getTodoList(),
            stats: {
                total: 5,
                completed: 2,
                remaining: 3
            },
            generatedAt: new Date().toISOString()
        };
    }
};

// Export for Node.js / ES modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DailyBriefingAgent;
}

// Make available globally
if (typeof window !== 'undefined') {
    window.DailyBriefingAgent = DailyBriefingAgent;
}
