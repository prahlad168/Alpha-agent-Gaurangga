/**
 * ================================================
 * PROJECT MANAGER AGENT - GAURANGA
 * ================================================
 * Agent ID: pm-agent-v1
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const PMAgent = {
    // On-time delivery target
    TARGET_ON_TIME: 95,
    
    // Projects
    PROJECTS: [
        { 
            name: 'Website Redesign Client A', 
            status: 'active', 
            progress: 60, 
            deadline: '2026-07-20',
            team: ['Developer', 'Designer']
        },
        { 
            name: 'Mobile App Development', 
            status: 'planning', 
            progress: 10, 
            deadline: '2026-08-15',
            team: ['Developer']
        }
    ],
    
    // Priorities
    PRIORITIES: [
        { level: 'P1', name: 'Critical', color: '🔴', desc: 'Must complete today' },
        { level: 'P2', name: 'High', color: '🟠', desc: 'Complete within 2 days' },
        { level: 'P3', name: 'Medium', color: '🟡', desc: 'Complete within 1 week' },
        { level: 'P4', name: 'Low', color: '🟢', desc: 'Complete within 2 weeks' }
    ],
    
    /**
     * Get dashboard
     */
    getDashboard() {
        let dashboard = `
📋 <b>Project Manager Dashboard</b>

<b>🎯 KPIs:</b>
├── On-time Delivery: ${this.TARGET_ON_TIME}% target
├── Active Projects: ${this.PROJECTS.filter(p => p.status === 'active').length}
├── Planning: ${this.PROJECTS.filter(p => p.status === 'planning').length}
└── Completed: ${this.PROJECTS.filter(p => p.status === 'completed').length}

<b>📊 Active Projects:</b>
`;
        this.PROJECTS.filter(p => p.status === 'active').forEach((p, i) => {
            dashboard += `\n${i + 1}. ${p.name}
   Progress: ${p.progress}%
   Deadline: ${p.deadline}
   Team: ${p.team.join(', ')}`;
        });
        
        dashboard += `

<b>Mau lihat detail project?</b>
Ketik: "project [nama]"
`;
        return dashboard;
    },
    
    /**
     * Get all projects
     */
    getProjects() {
        let projects = `
📁 <b>All Projects</b>

`;
        this.PROJECTS.forEach((p, i) => {
            const statusEmoji = p.status === 'active' ? '🟢' : p.status === 'planning' ? '🔵' : '✅';
            projects += `
${i + 1}. ${statusEmoji} ${p.name}
   Status: ${p.status}
   Progress: ${p.progress}%
   Deadline: ${p.deadline}
   Team: ${p.team.join(', ')}`;
        });
        
        projects += `

<b>Mau buat project baru?</b>
Ketik: "new project [nama]"
`;
        return projects;
    },
    
    /**
     * Get task management
     */
    getTaskManagement() {
        return `
✅ <b>Task Management System</b>

<b>⚡ Priority Levels:</b>
${this.PRIORITIES.map(p => `${p.color} ${p.level} - ${p.name}: ${p.desc}`).join('\n')}

<b>📋 Workflow:</b>
1. Task Created → Assigned to team
2. In Progress → Working on it
3. Review → QA checking
4. Done → Completed

<b>🎯 Daily Standup Questions:</b>
• What did you do yesterday?
• What will you do today?
• Any blockers?

<b>💡 Weekly: Review progress & adjust!</b>
`;
    },
    
    /**
     * Get quality gates
     */
    getQualityGates() {
        return `
🚪 <b>Quality Gates</b>

<b>📋 Milestone Reviews:</b>
1. Design Approval ✅
2. Development Complete
3. Testing Passed
4. Client UAT
5. Go-live Sign-off

<b>✅ Checklist per Milestone:</b>
• Code review passed
• Unit tests passing
• No critical bugs
• Documentation updated
• Client approved

<b>🎯 Goal: 95% on-time delivery!</b>
`;
    },
    
    /**
     * Main query handler
     */
    query(q) {
        if (q.includes('project')) {
            return this.getProjects();
        }
        if (q.includes('task') || q.includes('todo')) {
            return this.getTaskManagement();
        }
        if (q.includes('quality') || q.includes('qa')) {
            return this.getQualityGates();
        }
        if (q.includes('pm') || q.includes('project manager')) {
            return this.getDashboard();
        }
        return this.getDashboard();
    }
};

if (typeof window !== 'undefined') window.PMAgent = PMAgent;
