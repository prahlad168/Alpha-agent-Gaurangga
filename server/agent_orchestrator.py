#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          🎯 GAURANGA AGENT ORCHESTRATOR                   ║
║          All Agents Working - Target Achieved!             ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python3 agent_orchestrator.py --start-all
    python3 agent_orchestrator.py --status
    python3 agent_orchestrator.py --daily-briefing
"""

import json
import sys
import os
from datetime import datetime
from database import RevenueDatabase, db

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

class AgentOrchestrator:
    def __init__(self):
        self.db = RevenueDatabase()
        self.targets = {
            'hospital': 50000000,
            'ecommerce': 30000000,
            'education': 25000000,
            'travel': 20000000,
            'property': 25000000,
            'food': 20000000
        }
        self.total_target = sum(self.targets.values())
    
    def print_header(self):
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║              👑 GAURANGA AGENT COMMAND CENTER             ║
║          All Agents Active - Target Rp 170jt/bulan         ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    def get_revenue_status(self):
        """Get current revenue status"""
        summary = self.db.get_revenue_summary()
        sbus = self.db.get_all_sbus()
        
        status = {}
        for sbu in sbus:
            name = sbu['name']
            if name in self.targets:
                target = self.targets[name]
                current = sbu['total_income']
                pct = (current / target * 100) if target > 0 else 0
                status[name] = {
                    'target': target,
                    'current': current,
                    'percentage': pct,
                    'remaining': max(0, target - current)
                }
        return status
    
    def start_all_agents(self):
        """Start all agents"""
        self.print_header()
        
        print(f"{CYAN}🚀 STARTING ALL AGENTS...{RESET}\n")
        
        agents = [
            ("👑", "CEO Agent", "Strategic planning, decision making"),
            ("💰", "Sales Agent", "Lead generation, closing deals"),
            ("📢", "Marketing Agent", "Content, social media, ads"),
            ("🎧", "CS Agent", "Customer support, retention"),
            ("📋", "PM Agent", "Project management, delivery"),
            ("👥", "HR Agent", "Recruitment, team building"),
            ("🏥", "Hospital Agent", "SIMRS sales, healthcare clients"),
            ("🛒", "E-Commerce Agent", "Online store solutions"),
            ("📚", "Education Agent", "LMS, e-learning platforms"),
            ("✈️", "Travel Agent", "Booking systems, tourism"),
            ("🏠", "Property Agent", "Real estate platforms"),
            ("🍔", "Food Agent", "Restaurant, delivery apps"),
        ]
        
        for icon, name, desc in agents:
            print(f"   {GREEN}✓{RESET} {icon} {BOLD}{name}{RESET} - {desc}")
        
        print(f"\n{CYAN}📊 AGENT STATUS:{RESET}\n")
        self.show_targets()
        
        print(f"\n{GREEN}✅ ALL AGENTS ACTIVATED!{RESET}")
        print(f"{YELLOW}🎯 Mission: Achieve Rp {self.total_target:,} monthly revenue{RESET}\n")
    
    def show_targets(self):
        """Show all targets and progress"""
        status = self.get_revenue_status()
        
        print(f"   {'SBU':<15} {'TARGET':>15} {'CURRENT':>15} {'PROGRESS':>15} {'STATUS'}")
        print(f"   {'-'*15} {'-'*15} {'-'*15} {'-'*15} {'-'*10}")
        
        total_current = 0
        for name, data in status.items():
            target = data['target']
            current = data['current']
            pct = data['percentage']
            total_current += current
            
            # Progress bar
            filled = int(pct / 10)
            bar = '█' * filled + '░' * (10 - filled)
            
            if pct >= 100:
                status_icon = f"{GREEN}✅ ACHIEVED{RESET}"
            elif pct >= 50:
                status_icon = f"{YELLOW}🔥 ON TRACK{RESET}"
            else:
                status_icon = f"{RED}⏳ WORKING{RESET}"
            
            print(f"   {name:<15} Rp {target:>12,} Rp {current:>12,} [{bar}] {status_icon}")
        
        print(f"   {'-'*15} {'-'*15} {'-'*15} {'-'*15} {'-'*10}")
        overall_pct = (total_current / self.total_target * 100) if self.total_target > 0 else 0
        print(f"   {BOLD}TOTAL:{RESET:<9} Rp {self.total_target:>12,} Rp {total_current:>12,} [{'█' * int(overall_pct/10)}{'░' * (10 - int(overall_pct/10))}] {overall_pct:.1f}%")
    
    def daily_briefing(self):
        """Generate daily briefing report"""
        self.print_header()
        
        print(f"{CYAN}📅 DAILY BRIEFING - {datetime.now().strftime('%d %B %Y')}{RESET}\n")
        
        summary = self.db.get_revenue_summary()
        status = self.get_revenue_status()
        
        # Summary
        print(f"   {BOLD}📊 REVENUE SUMMARY:{RESET}")
        print(f"   ├─ Total Revenue:  Rp {summary['total_income']:,}")
        print(f"   ├─ Total Expense:  Rp {summary['total_expense']:,}")
        print(f"   └─ Total Profit:   Rp {summary['total_profit']:,}\n")
        
        # SBU Performance
        print(f"   {BOLD}🏢 SBU PERFORMANCE:{RESET}")
        for name, data in status.items():
            icon = {'hospital': '🏥', 'ecommerce': '🛒', 'education': '📚', 
                   'travel': '✈️', 'property': '🏠', 'food': '🍔'}.get(name, '📦')
            pct = data['percentage']
            if pct >= 100:
                status_icon = f"{GREEN}✅{RESET}"
            elif pct >= 50:
                status_icon = f"{YELLOW}🔥{RESET}"
            else:
                status_icon = f"{RED}⏳{RESET}"
            print(f"   {status_icon} {icon} {name.title():<12} {pct:>5.1f}% ({Rp_format(data['current'])})")
        
        print()
        
        # Agent Tasks
        print(f"   {BOLD}🤖 AGENT TASKS:{RESET}")
        tasks = [
            ("Sales Agent", "Contact 10 prospects today", "High"),
            ("Marketing Agent", "Post 3 social media updates", "High"),
            ("Hospital Agent", "Follow up with 5 RS leads", "High"),
            ("CS Agent", "Respond to all tickets < 1hr", "Medium"),
            ("PM Agent", "Update project progress", "Medium"),
        ]
        
        for agent, task, priority in tasks:
            icon = "🔴" if priority == "High" else "🟡"
            print(f"   {icon} {agent}: {task}")
        
        print()
        
        # Action Items
        print(f"   {BOLD}📋 TODAY'S ACTION ITEMS:{RESET}")
        print(f"   1. 💰 Add any new income to system")
        print(f"   2. 📞 Follow up with pending clients")
        print(f"   3. 📧 Send proposals to hot leads")
        print(f"   4. 🎯 Focus on: Hospital SIMRS (highest ROI)")
        print()
        
        # Motivation
        remaining = self.total_target - summary['total_income']
        if remaining > 0:
            print(f"   {BOLD}{YELLOW}🎯 TARGET REMAINING: Rp {remaining:,}{RESET}")
            print(f"   {BOLD}{GREEN}💪 YOU CAN DO IT! Let's achieve our goals!{RESET}\n")
        else:
            print(f"   {BOLD}{GREEN}🎉 TARGET ACHIEVED! Congratulations!{RESET}\n")
    
    def assign_tasks(self):
        """Assign tasks to each agent"""
        self.print_header()
        
        print(f"{CYAN}📋 TASK ASSIGNMENT - ALL AGENTS{RESET}\n")
        
        tasks = {
            "💰 Sales Agent": [
                "Generate 20 new leads this week",
                "Contact all qualified prospects",
                "Schedule 5 demos",
                "Send 10 proposals",
                "Close 2 deals"
            ],
            "📢 Marketing Agent": [
                "Post daily content (IG, LinkedIn, TikTok)",
                "Run Facebook/Google Ads campaign",
                "Send weekly newsletter",
                "Create 3 case studies",
                "Update website with new portfolio"
            ],
            "🏥 Hospital Agent": [
                "Outreach to 10 RS/Klinik in Bali",
                "Send SIMRS proposal to hot leads",
                "Demo to 3 interested prospects",
                "Create case study from recent project",
                "Partner with medical association"
            ],
            "🛒 E-Commerce Agent": [
                "Outreach to 10 retail businesses",
                "Create e-commerce portfolio",
                "Offer free consultation",
                "Partner with marketplace",
                "Target: 3 new clients this month"
            ],
            "📚 Education Agent": [
                "Identify 10 schools/universities",
                "Create LMS demo video",
                "Partner with EdTech community",
                "Target: Online course platforms",
                "Focus: Language schools, training centers"
            ],
            "✈️ Travel Agent": [
                "Identify travel agencies",
                "Create booking system demo",
                "Partner with tourism board",
                "Target: Tour operators",
                "Focus: Bali tourism market"
            ],
            "🏠 Property Agent": [
                "Identify property developers",
                "Create property portal demo",
                "Partner with real estate associations",
                "Target: Property agents, developers",
                "Focus: Bali property market"
            ],
            "🍔 Food Agent": [
                "Identify restaurants, cafes",
                "Create food delivery demo",
                "Partner with food blogger",
                "Target: Cloud kitchens",
                "Focus: Quick service restaurants"
            ],
            "🎧 CS Agent": [
                "Response time < 1 hour",
                "Customer satisfaction > 90%",
                "Follow up on renewal",
                "Collect testimonials",
                "Upsell to existing clients"
            ],
            "📋 PM Agent": [
                "Update all project statuses",
                "Deliver on time, every time",
                "Quality check all deliverables",
                "Client acceptance sign-off",
                "Document lessons learned"
            ],
            "👥 HR Agent": [
                "Hire 1 developer",
                "Hire 1 sales person",
                "Create onboarding process",
                "Training program",
                "Team building activities"
            ]
        }
        
        for agent, task_list in tasks.items():
            print(f"   {BOLD}{agent}{RESET}")
            for i, task in enumerate(task_list, 1):
                print(f"   {i}. {task}")
            print()
        
        print(f"{GREEN}✅ ALL TASKS ASSIGNED! Execute now!{RESET}\n")

def Rp_format(num):
    """Format number as Indonesian Rupiah"""
    return f"Rp {num:,}".replace(",", ".")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 agent_orchestrator.py [--start-all|--status|--daily-briefing|--tasks]")
        sys.exit(1)
    
    orchestrator = AgentOrchestrator()
    command = sys.argv[1]
    
    if command == '--start-all':
        orchestrator.start_all_agents()
    elif command == '--status':
        orchestrator.print_header()
        orchestrator.show_targets()
    elif command == '--daily-briefing':
        orchestrator.daily_briefing()
    elif command == '--tasks':
        orchestrator.assign_tasks()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
