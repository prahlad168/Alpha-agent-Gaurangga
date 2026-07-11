/**
 * ================================================
 * HR AGENT - GAURANGA
 * ================================================
 * Agent ID: hr-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const HRAgent = {
    // Target hiring
    HIRING_TARGET: 10,
    TIMELINE: {
        month1: 1,
        month3: 5,
        month6: 10
    },
    
    // Current team
    CURRENT_TEAM: 0,
    
    // Open positions
    POSITIONS: [
        {
            id: 1,
            title: "Sales Agent",
            priority: "HIGH",
            salary: "Rp 5-10 juta",
            skills: ["Lead Generation", "Cold Outreach", "CRM", "Negotiation"],
            description: "Fokus revenue generation untuk SaaS dan freelance services"
        },
        {
            id: 2,
            title: "Content Writer",
            priority: "HIGH",
            salary: "Rp 3-7 juta",
            skills: ["Content Writing", "SEO", "Social Media", "Copywriting"],
            description: "Buat konten untuk blog, YouTube, dan social media"
        },
        {
            id: 3,
            title: "Full-Stack Developer",
            priority: "MEDIUM",
            salary: "Rp 8-15 juta",
            skills: ["PHP/Laravel", "React/Vue", "Python", "WordPress"],
            description: "Develop aplikasi web dan mobile untuk clients"
        },
        {
            id: 4,
            title: "Marketing Specialist",
            priority: "MEDIUM",
            salary: "Rp 5-10 juta",
            skills: ["SEO/SEM", "Paid Ads", "Analytics", "Campaign"],
            description: "Kelola marketing campaigns dan optimize ROAS"
        },
        {
            id: 5,
            title: "Virtual Assistant",
            priority: "LOW",
            salary: "Rp 3-5 juta",
            skills: ["Admin", "Scheduling", "Email", "Research"],
            description: "Support operations dan admin tasks"
        }
    ],
    
    // Interview questions
    INTERVIEW_QUESTIONS: [
        "Ceritakan pengalaman Anda dalam [skill relevant]",
        "Bagaimana Anda handle deadline ketat?",
        "Apa yang Anda ketahui tentang Maha Lakshmi Holdings?",
        "Ke mana Anda melihat diri Anda dalam 2 tahun?",
        "Berapa ekspektasi salary Anda?",
        "Ceritakan project terbaik Anda",
        "Bagaimana Anda belajar hal baru dengan cepat?"
    ],
    
    // Onboarding checklist
    ONBOARDING_CHECKLIST: [
        { item: "Email company", done: false },
        { item: "Laptop & tools setup", done: false },
        { item: "Join Slack/WhatsApp group", done: false },
        { item: "Company orientation", done: false },
        { item: "Meet dengan team", done: false },
        { item: "Training produk/service", done: false },
        { item: "Assign mentor", done: false },
        { item: "First task assignment", done: false },
        { item: "30-day goals setting", done: false },
        { item: "Sign documents", done: false }
    ],
    
    /**
     * Get hiring status
     */
    getHiringStatus() {
        const current = this.CURRENT_TEAM;
        const target = this.HIRING_TARGET;
        const progress = Math.round((current / target) * 100);
        
        let status = `
👥 <b>Hiring Status - Maha Lakshmi Holdings</b>

<b>📊 Progress:</b>
├── Target: ${target} orang
├── Current: ${current} orang
└── Progress: ${progress}% ${progress >= 50 ? '🟢' : progress >= 25 ? '🟡' : '🔴'}

<b>📅 Timeline:</b>
├── Month 1 (Done): ${this.TIMELINE.month1} orang - ${current >= 1 ? '✅' : '⬜'}
├── Month 3: ${this.TIMELINE.month3} orang - ${current >= 5 ? '✅' : '⬜'}
└── Month 6: ${this.TIMELINE.month6} orang - ${current >= 10 ? '✅' : '⬜'}

<b>📋 Pipeline:</b>
├── Job Posting → Resume Screening
├── Initial Interview → Technical Interview
├── Final Interview → Offer & Onboarding
└── Time to Hire: ~30 days
`;
        return status;
    },
    
    /**
     * Get open positions
     */
    getOpenPositions() {
        let positions = `
💼 <b>Open Positions</b>

`;
        this.POSITIONS.forEach((pos, i) => {
            const priorityEmoji = pos.priority === 'HIGH' ? '🔴' : pos.priority === 'MEDIUM' ? '🟡' : '🟢';
            positions += `
${i + 1}. ${priorityEmoji} ${pos.title}
   💰 Salary: ${pos.salary}
   📝 ${pos.description}
   🛠️ Skills: ${pos.skills.join(', ')}
`;
        });
        
        positions += `
<b>Mau buka lowongan baru, Pak Pur?</b>
Ketik: "buka lowongan [posisi]"`;
        
        return positions;
    },
    
    /**
     * Get job requirements
     */
    getJobRequirements(position = null) {
        if (position) {
            const pos = this.POSITIONS.find(p => 
                p.title.toLowerCase().includes(position.toLowerCase())
            );
            if (pos) {
                return `
📋 <b>Job Description: ${pos.title}</b>

<b>Salary:</b> ${pos.salary}

<b>Description:</b>
${pos.description}

<b>Required Skills:</b>
${pos.skills.map(s => `• ${s}`).join('\n')}

<b>Priority:</b> ${pos.priority}

<b>Pipeline:</b>
1. Apply → Resume Screening (Day 3-5)
2. Initial Interview (Day 7-10)
3. Technical Interview (Day 14-17)
4. Final Interview (Day 21)
5. Offer & Onboarding (Day 25-30)
`;
            }
        }
        
        return this.getOpenPositions();
    },
    
    /**
     * Get interview tips
     */
    getInterviewTips() {
        return `
🎤 <b>Interview Guide</b>

<b>📋 Question Bank:</b>
${this.INTERVIEW_QUESTIONS.map((q, i) => `${i + 1}. ${q}`).join('\n')}

<b>💡 Tips untuk Kandidat:</b>
• Research tentang company
• Bawa portfolio/project samples
• Prepare pertanyaan untuk kami
• Tanyakan tentang growth path
• Jangan exaggerate kemampuan

<b>⚠️ Red Flags:</b>
• Tidak bisa explain project sebelumnya
• Ekspektasi salary tidak realistis
• Tidak ada enthusiasm
• Terlambat tanpa kabar
• Negative talk previous company

<b>✅ Good Signs:</b>
• Proaktif bertanya
• Enthusiastic tentang role
• Realistic expectations
• Team player mentality
• Continuous learner
`;
    },
    
    /**
     * Get onboarding checklist
     */
    getOnboardingChecklist() {
        let checklist = `
📝 <b>Onboarding Checklist</b>

<b>Week 1: Foundation</b>
${this.ONBOARDING_CHECKLIST.slice(0, 5).map((item, i) => `${i + 1}. [${item.done ? '✓' : ' '}] ${item.item}`).join('\n')}

<b>Week 2-4: Learning</b>
${this.ONBOARDING_CHECKLIST.slice(5, 9).map((item, i) => `${i + 6}. [${item.done ? '✓' : ' '}] ${item.item}`).join('\n')}

<b>Week 4+: Review</b>
${this.ONBOARDING_CHECKLIST.slice(9).map((item, i) => `${i + 10}. [${item.done ? '✓' : ' '}] ${item.item}`).join('\n')}

<b>📊 Status:</b> ${this.ONBOARDING_CHECKLIST.filter(i => i.done).length}/${this.ONBOARDING_CHECKLIST.length} completed
`;
        return checklist;
    },
    
    /**
     * Get team structure
     */
    getTeamStructure() {
        return `
👥 <b>Team Structure - Maha Lakshmi Holdings</b>

<b>🎯 Target:</b> 10 orang dalam 6 bulan

<b>📋 Needed Positions:</b>

<b>Sales & Revenue:</b>
• Sales Agent (1-2 orang)

<b>Marketing:</b>
• Content Writer (1-2 orang)
• Marketing Specialist (1 orang)

<b>Technical:</b>
• Full-Stack Developer (2-3 orang)
• WordPress Developer (1 orang)

<b>Operations:</b>
• Virtual Assistant (1-2 orang)
• Project Manager (1 orang)

<b>Current:</b> 0/${this.HIRING_TARGET} orang

<b>Mau mulai rekrut, Pak Pur?</b>
Ketik: "mulai rekrut [posisi]"
`;
    },
    
    /**
     * Main query handler
     */
    query(query) {
        const q = query.toLowerCase();
        
        if (q.includes('hire') || q.includes('rekrut') || q.includes('hiring') || q.includes('lowongan')) {
            return this.getHiringStatus();
        }
        
        if (q.includes('posisi') || q.includes('jobs') || q.includes('job')) {
            return this.getOpenPositions();
        }
        
        if (q.includes('interview') || q.includes('tips')) {
            return this.getInterviewTips();
        }
        
        if (q.includes('onboard') || q.includes('daftar') || q.includes('checklist')) {
            return this.getOnboardingChecklist();
        }
        
        if (q.includes('team') || q.includes('tim') || q.includes('struktur')) {
            return this.getTeamStructure();
        }
        
        return this.getHiringStatus();
    }
};

// Export for Node.js / ES modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HRAgent;
}

// Make available globally
if (typeof window !== 'undefined') {
    window.HRAgent = HRAgent;
}
