/**
 * ================================================
 * CALENDAR AGENT - GAURANGA
 * ================================================
 * Agent ID: calendar-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const CalendarAgent = {
    // Events today
    TODAY_EVENTS: [
        { time: '09:00', title: 'Daily Standup', type: 'meeting', status: 'upcoming' },
        { time: '14:00', title: 'Client Call', type: 'call', status: 'upcoming' }
    ],
    
    // Weekly schedule
    WEEKLY_SCHEDULE: {
        monday: ['09:00 Standup', '14:00 Team sync'],
        tuesday: ['10:00 Sales meeting', '15:00 Marketing review'],
        wednesday: ['09:00 Standup', '11:00 1-on-1'],
        thursday: ['10:00 Client calls', '14:00 Project review'],
        friday: ['09:00 Standup', '15:00 Week wrap-up'],
        saturday: [],
        sunday: []
    },
    
    /**
     * Get today's date
     */
    getToday() {
        const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
        const months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
        const now = new Date();
        return `${days[now.getDay()]}, ${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
    },
    
    /**
     * Get dashboard
     */
    getDashboard() {
        let dashboard = `
📅 <b>Calendar Dashboard</b>

<b>📆 Today:</b> ${this.getToday()}

<b>⏰ Upcoming Events:</b>
`;
        if (this.TODAY_EVENTS.length === 0) {
            dashboard += '\n   No events scheduled';
        } else {
            this.TODAY_EVENTS.forEach(e => {
                const emoji = e.type === 'meeting' ? '📌' : e.type === 'call' ? '📞' : '📋';
                dashboard += `\n${emoji} ${e.time} - ${e.title}`;
            });
        }
        
        dashboard += `

<b>📊 This Week:</b>
• Monday: ${this.WEEKLY_SCHEDULE.monday.length} events
• Tuesday: ${this.WEEKLY_SCHEDULE.tuesday.length} events
• Wednesday: ${this.WEEKLY_SCHEDULE.wednesday.length} events
• Thursday: ${this.WEEKLY_SCHEDULE.thursday.length} events
• Friday: ${this.WEEKLY_SCHEDULE.friday.length} events

<b>Mau lihat weekly schedule?</b>
Ketik: "weekly"
`;
        return dashboard;
    },
    
    /**
     * Get weekly schedule
     */
    getWeeklySchedule() {
        let schedule = `
📆 <b>Weekly Schedule</b>

<b>🟢 Monday:</b>
${this.WEEKLY_SCHEDULE.monday.length ? this.WEEKLY_SCHEDULE.monday.map(e => `   • ${e}`).join('\n') : '   • No events'}

<b>🔵 Tuesday:</b>
${this.WEEKLY_SCHEDULE.tuesday.length ? this.WEEKLY_SCHEDULE.tuesday.map(e => `   • ${e}`).join('\n') : '   • No events'}

<b>🟡 Wednesday:</b>
${this.WEEKLY_SCHEDULE.wednesday.length ? this.WEEKLY_SCHEDULE.wednesday.map(e => `   • ${e}`).join('\n') : '   • No events'}

<b>🟠 Thursday:</b>
${this.WEEKLY_SCHEDULE.thursday.length ? this.WEEKLY_SCHEDULE.thursday.map(e => `   • ${e}`).join('\n') : '   • No events'}

<b>🔴 Friday:</b>
${this.WEEKLY_SCHEDULE.friday.length ? this.WEEKLY_SCHEDULE.friday.map(e => `   • ${e}`).join('\n') : '   • No events'}

<b>⚪ Saturday:</b> Day off
<b>⚪ Sunday:</b> Day off
`;
        return schedule;
    },
    
    /**
     * Get time blocking
     */
    getTimeBlocking() {
        return `
🗓️ <b>Time Blocking Strategy</b>

<b>⏰ Daily Time Blocks:</b>

<b>06:00 - 08:00</b> 🟢 Morning Routine
   • Exercise
   • Breakfast
   • Review daily goals

<b>08:00 - 10:00</b> 🔵 Deep Work
   • Most important tasks
   • No meetings
   • Focus mode ON

<b>10:00 - 12:00</b> 🟡 Meetings
   • Team sync
   • Client calls
   • Collaborative work

<b>12:00 - 13:00</b> ⚪ Lunch Break
   • Rest
   • No work

<b>13:00 - 15:00</b> 🟠 Afternoon Work
   • Admin tasks
   • Emails
   • Follow-ups

<b>15:00 - 17:00</b> 🔴 Wrap Up
   • Review accomplishments
   • Plan tomorrow
   • No new tasks

<b>💡 Productivity tip: Protect your morning!</b>
`;
    },
    
    /**
     * Get reminders
     */
    getReminders() {
        return `
⏰ <b>Daily Reminders</b>

<b>🔔 Morning (08:00):</b>
• Check emails
• Review daily goals
• Team standup

<b>🔔 Midday (12:00):</b>
• Lunch break
• Quick progress check

<b>🔔 Afternoon (15:00):</b>
• Follow up leads
• Update CRM
• End-of-day review

<b>🔔 Evening (17:00):</b>
• Daily report
• Plan tomorrow
• Log time

<b>💡 Stay organized, Pak Pur!</b>
`;
    },
    
    /**
     * Main query handler
     */
    query(q) {
        if (q.includes('weekly')) {
            return this.getWeeklySchedule();
        }
        if (q.includes('time block') || q.includes('schedule')) {
            return this.getTimeBlocking();
        }
        if (q.includes('reminder')) {
            return this.getReminders();
        }
        if (q.includes('calendar') || q.includes('jadwal')) {
            return this.getDashboard();
        }
        return this.getDashboard();
    }
};

if (typeof window !== 'undefined') window.CalendarAgent = CalendarAgent;
