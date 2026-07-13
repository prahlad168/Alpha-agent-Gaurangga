#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          🎯 GAURANGA - EXECUTE ALL AGENTS                 ║
║          Making Things Happen - Target Achieved!           ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import sys
import os
import time
from datetime import datetime
from database import db

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

class AgentExecutor:
    def __init__(self):
        self.db = db
        self.ceo_wallet = 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
        self.bca_account = '6485086645'
    
    def log(self, icon, message):
        print(f"   {icon} {message}")
    
    def execute_all_agents(self):
        """Execute all agents activities"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║          🚀 GAURANGA AGENT EXECUTION                        ║
║          All Agents Working - Making Things Happen!         ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        self.execute_sales_agent()
        self.execute_marketing_agent()
        self.execute_hospital_agent()
        self.execute_ecommerce_agent()
        self.execute_support_agent()
        self.execute_finance_agent()
        
        self.show_final_status()
    
    def execute_sales_agent(self):
        """Sales Agent Activities"""
        print(f"\n{BOLD}{CYAN}💰 SALES AGENT - ACTIVATED{RESET}\n")
        
        # Get pipeline status
        projects = self.db.get_all_projects()
        clients = self.db.get_all_clients()
        
        # Pipeline breakdown
        pipeline = {'prospect': 0, 'qualified': 0, 'proposal': 0, 'negotiation': 0, 'won': 0}
        for p in projects:
            if p.get('status') in pipeline:
                pipeline[p.get('status')] += 1
        
        self.log("📊", f"Pipeline: {pipeline}")
        self.log("👥", f"Total Clients: {len(clients)}")
        self.log("💼", f"Total Projects: {len(projects)}")
        
        # Target for today
        daily_target = 5000000  # 5jt per day to hit 150jt/month
        self.log("🎯", f"Daily Target: Rp {daily_target:,}")
        self.log("📞", "Action: Contact 10 new prospects")
        self.log("📧", "Action: Send 5 proposals")
        self.log("🤝", "Action: Close 1 deal")
        
        # Show prospect list
        print(f"\n   {BOLD}📋 PROSPECT LIST:{RESET}")
        prospects = [
            ("RS Umum Bali", "Hospital", "Hot Lead", "Rp 75jt"),
            ("Toko Elektronik Jaya", "E-Commerce", "Qualified", "Rp 25jt"),
            ("SMA Negeri 1 Denpasar", "Education", "Prospect", "Rp 30jt"),
            ("PT Travel Nusantara", "Travel", "Prospect", "Rp 20jt"),
            ("PT Properti Indonesia", "Property", "Cold", "Rp 50jt"),
        ]
        
        for i, (name, sbu, status, value) in enumerate(prospects, 1):
            status_color = GREEN if status == "Hot Lead" else YELLOW if status == "Qualified" else RESET
            print(f"   {i}. {name:<25} | {sbu:<12} | {status_color}{status:<10}{RESET} | {value}")
    
    def execute_marketing_agent(self):
        """Marketing Agent Activities"""
        print(f"\n{BOLD}{CYAN}📢 MARKETING AGENT - ACTIVATED{RESET}\n")
        
        self.log("📱", "Social Media Plan for Today:")
        self.log("   ", "1. Instagram: Post SIMRS case study")
        self.log("   ", "2. LinkedIn: Industry insight article")
        self.log("   ", "3. TikTok: Quick demo video (15 sec)")
        self.log("   ", "4. WhatsApp Status: Testimonial")
        
        self.log("📧", "\nEmail Campaign:")
        self.log("   ", "1. Send newsletter to 500 subscribers")
        self.log("   ", "2. Follow up with 20 warm leads")
        self.log("   ", "3. New leads: 50 target")
        
        self.log("🎯", "\nAds Budget Allocation:")
        print(f"   {'Channel':<15} {'Budget':>12} {'Target'}")
        print(f"   {'-'*15} {'-'*12} {'-'*20}")
        print(f"   {'Google Ads':<15} {'Rp 2jt':>12} {'50 leads'}")
        print(f"   {'Facebook Ads':<15} {'Rp 1jt':>12} {'100 leads'}")
        print(f"   {'Instagram':<15} {'Rp 500rb':>12} {'30 leads'}")
    
    def execute_hospital_agent(self):
        """Hospital SBU Agent - Focus Area"""
        print(f"\n{BOLD}{CYAN}🏥 HOSPITAL AGENT - FOCUS AREA{RESET}\n")
        
        self.log("🎯", "PRIORITY: SIMRS Sales - Highest ROI!")
        
        # Hospital prospects
        prospects = [
            ("RS Umum Negara", "SIMRS Premium", "Rp 100jt", "Hot"),
            ("Klinik Pratama Sesetan", "SIMRS Basic", "Rp 25jt", "Hot"),
            ("RSUD Tabanan", "SIMRS Enterprise", "Rp 200jt", "Warm"),
            ("Klinik Agung", "SIMRS Basic", "Rp 25jt", "Warm"),
            ("RS Puri Raharja", "SIMRS Standard", "Rp 50jt", "Cold"),
        ]
        
        print(f"   {'Hospital Prospect':<25} {'Package':<18} {'Value':>12} {'Status'}")
        print(f"   {'-'*25} {'-'*18} {'-'*12} {'-'*10}")
        for name, package, value, status in prospects:
            status_color = GREEN if status == "Hot" else YELLOW if status == "Warm" else RESET
            print(f"   {name:<25} {package:<18} {value:>12} {status_color}{status:<10}{RESET}")
        
        self.log("\n📞", "Today's Outreach:")
        self.log("   ", "1. Call RS Umum Negara - Schedule demo")
        self.log("   ", "2. WhatsApp Klinik Pratama Sesetan")
        self.log("   ", "3. Visit RSUD Tabanan")
        self.log("   ", "4. Follow up Klinik Agung")
        
        self.log("\n💰", "Target: Close 1 deal this week = Rp 25jt+")
    
    def execute_ecommerce_agent(self):
        """E-Commerce SBU Agent"""
        print(f"\n{BOLD}{CYAN}🛒 E-COMMERCE AGENT - ACTIVATED{RESET}\n")
        
        prospects = [
            ("Toko Elektronik Jaya", "Online Store Pro", "Rp 25jt", "Hot"),
            ("Butik Fashion Bali", "Online Store Basic", "Rp 10jt", "Warm"),
            ("Warung Kopi Kintamani", "Food Delivery", "Rp 15jt", "Cold"),
            ("Distro Skateboard", "Online Store Pro", "Rp 20jt", "Cold"),
        ]
        
        print(f"   {'E-Commerce Prospect':<25} {'Package':<18} {'Value':>12}")
        print(f"   {'-'*25} {'-'*18} {'-'*12}")
        for name, package, value, _ in prospects:
            print(f"   {name:<25} {package:<18} {value:>12}")
        
        self.log("\n📞", "Today's Outreach:")
        self.log("   ", "1. Demo to Toko Elektronik Jaya")
        self.log("   ", "2. Send proposal to Butik Fashion")
        
        self.log("\n💰", "Target: Close 1 deal = Rp 10jt+")
    
    def execute_support_agent(self):
        """Customer Support Agent"""
        print(f"\n{BOLD}{CYAN}🎧 CS AGENT - ACTIVATED{RESET}\n")
        
        self.log("⏱️", "SLA: Response time < 1 hour")
        self.log("😊", "Target: CSAT > 90%")
        self.log("🔄", "Follow up on renewals")
        self.log("⭐", "Collect testimonials")
        
        self.log("\n📋", "Active Tickets:")
        self.log("   ", "1. RS Sehat Bali - Server issue (Urgent)")
        self.log("   ", "2. Klinik Mawar - Training request (Medium)")
        self.log("   ", "3. Toko Grosir - Payment confirmation (Low)")
    
    def execute_finance_agent(self):
        """Finance Agent"""
        print(f"\n{BOLD}{CYAN}💵 FINANCE AGENT - ACTIVATED{RESET}\n")
        
        summary = self.db.get_revenue_summary()
        
        self.log("📊", "Financial Status:")
        self.log("   ", f"Total Revenue: Rp {summary['total_income']:,}")
        self.log("   ", f"Total Expense: Rp {summary['total_expense']:,}")
        self.log("   ", f"Net Profit: Rp {summary['total_profit']:,}")
        
        # Profit margin
        margin = (summary['total_profit'] / summary['total_income'] * 100) if summary['total_income'] > 0 else 0
        self.log("📈", f"Profit Margin: {margin:.1f}%")
        
        self.log("\n💰", "Payment Info:")
        self.log("   ", f"🏦 BCA: {self.bca_account}")
        self.log("   ", f"₿ BTC: {self.ceo_wallet[:20]}...")
        
        # CEO transfer recommendation
        profit = summary['total_profit']
        if profit > 0:
            recommended_transfer = int(profit * 0.25)  # 25% to CEO
            self.log("\n👑", f"Recommended CEO Transfer: Rp {recommended_transfer:,} (25% of profit)")
            self.log("   ", "Execute: POST /api/ceo/transfer")
    
    def show_final_status(self):
        """Show final status"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║          📊 EXECUTION SUMMARY                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        summary = self.db.get_revenue_summary()
        
        print(f"   💰 Total Revenue:  Rp {summary['total_income']:,}")
        print(f"   💸 Total Expense: Rp {summary['total_expense']:,}")
        print(f"   📈 Net Profit:    Rp {summary['total_profit']:,}")
        
        # Target progress
        total_target = 170000000
        progress = (summary['total_income'] / total_target * 100)
        
        bar_length = 30
        filled = int(progress / 100 * bar_length)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\n   🎯 TARGET PROGRESS: [{bar}] {progress:.1f}%")
        print(f"   📍 Remaining: Rp {max(0, total_target - summary['total_income']):,}")
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║          ✅ ALL AGENTS EXECUTED - TARGET WITHIN REACH!      ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Next actions
        print(f"   {BOLD}📋 NEXT ACTIONS:{RESET}")
        print(f"   1. 💰 Add new income as deals close")
        print(f"   2. 📞 Contact hot leads immediately")
        print(f"   3. 📧 Send proposals today")
        print(f"   4. 🤝 Close at least 1 deal this week")
        print(f"   5. 👑 Transfer profit to CEO wallet")

def main():
    executor = AgentExecutor()
    executor.execute_all_agents()

if __name__ == '__main__':
    main()
