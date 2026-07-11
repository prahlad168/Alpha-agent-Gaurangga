/**
 * ================================================
 * CONTENT AGENT - GAURANGA
 * ================================================
 * Agent ID: content-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const ContentAgent = {
    // Monthly targets
    TARGETS: {
        blogPosts: 15,
        youtubeVideos: 8,
        podcastEpisodes: 4,
        infographics: 3,
        total: 30
    },
    
    // Content calendar
    CALENDAR: {
        monday: ['Blog post', 'Social media batch'],
        tuesday: ['Email newsletter', 'Instagram post'],
        wednesday: ['Blog post', 'YouTube video upload'],
        thursday: ['LinkedIn post', 'Twitter thread'],
        friday: ['Newsletter', 'TikTok video'],
        saturday: ['Instagram Stories', 'Behind scenes'],
        sunday: ['Newsletter feature', 'Planning']
    },
    
    // Content types
    CONTENT_TYPES: [
        { name: 'Blog Posts', target: 15, wordCount: '1500-2500 words', done: 0 },
        { name: 'YouTube Videos', target: 8, duration: '10-20 min', done: 0 },
        { name: 'Podcast Episodes', target: 4, duration: '20-30 min', done: 0 },
        { name: 'Infographics', target: 3, type: 'Visual', done: 0 }
    ],
    
    /**
     * Get content dashboard
     */
    getDashboard() {
        let dashboard = `
✍️ <b>Content Dashboard - Maha Lakshmi Holdings</b>

<b>📊 Monthly Targets:</b>
├── Total: ${this.TARGETS.total} pieces/month
├── Done: ${this.CONTENT_TYPES.reduce((sum, c) => sum + c.done, 0)}
└── Remaining: ${this.TARGETS.total - this.CONTENT_TYPES.reduce((sum, c) => sum + c.done, 0)}

<b>📝 Content Breakdown:</b>
`;
        this.CONTENT_TYPES.forEach(c => {
            const pct = Math.round((c.done / c.target) * 100);
            dashboard += `\n• ${c.name}: ${c.done}/${c.target} (${pct}%)`;
        });
        
        dashboard += `

<b>💡 Mau generate content idea?</b>
Ketik: "content idea [topic]"
`;
        return dashboard;
    },
    
    /**
     * Get content calendar
     */
    getCalendar() {
        let calendar = `
📅 <b>Weekly Content Calendar</b>

<b>📆 Content Schedule:</b>

<b>🟢 Monday:</b>
• Blog post
• Social media batch

<b>🔵 Tuesday:</b>
• Email newsletter
• Instagram post

<b>🟡 Wednesday:</b>
• Blog post
• YouTube video upload

<b>🟠 Thursday:</b>
• LinkedIn post
• Twitter thread

<b>🔴 Friday:</b>
• Newsletter
• TikTok video

<b>🟣 Saturday:</b>
• Instagram Stories
• Behind scenes

<b>⚪ Sunday:</b>
• Newsletter feature
• Planning

<b>💡 Stay consistent, Pak Pur!</b>
`;
        return calendar;
    },
    
    /**
     * Get SEO tips
     */
    getSEOTips() {
        return `
🔍 <b>SEO Best Practices</b>

<b>📝 Per Article:</b>
✅ Primary keyword in title
✅ Meta description (150-160 chars)
✅ Internal links (2-3)
✅ Word count: 1500-2500 words
✅ Images with alt text
✅ Headers (H1, H2, H3)
✅ External links

<b>🔑 Keyword Research:</b>
• Use Google Keyword Planner
• Long-tail keywords first
• Competitor analysis
• Search intent match

<b>📊 Monthly SEO Tasks:</b>
• Technical audit: 1x/month
• Content optimization: 20 pages
• Backlink building: 30 links
• Keyword research: 50 keywords
`;
    },
    
    /**
     * Generate content idea
     */
    generateIdea(topic) {
        const ideas = [
            `📝 <b>Blog Post Idea:</b> "5 Cara ${topic} untuk Meningkatkan Revenue Bisnis Anda"`,
            `🎥 <b>YouTube Idea:</b> "Tutorial Lengkap ${topic} - Step by Step"`,
            `📱 <b>Social Post:</b> "3 Tips ${topic} yang Wajib Kamu Tahu! 🔥"`,
            `📧 <b>Newsletter:</b> "Weekly Update: Semua Tentang ${topic}"`,
            `🎧 <b>Podcast:</b> "Deep Dive: ${topic} dengan Expert Insights"`
        ];
        return ideas[Math.floor(Math.random() * ideas.length)];
    },
    
    /**
     * Main query handler
     */
    query(q) {
        if (q.includes('content') && (q.includes('idea') || q.includes('ideas'))) {
            const topic = q.replace(/.*idea[s]?\s*/, '').trim() || 'bisnis';
            return this.generateIdea(topic);
        }
        if (q.includes('content') && q.includes('calendar')) {
            return this.getCalendar();
        }
        if (q.includes('seo')) {
            return this.getSEOTips();
        }
        if (q.includes('content')) {
            return this.getDashboard();
        }
        return this.getDashboard();
    }
};

if (typeof window !== 'undefined') window.ContentAgent = ContentAgent;
