"""
MAHA LAKSHMI TEAM - Sistem Agent Spesialis
Semua kemampuan Alpha Gaurangga di-clone untuk:
- Marketing
- Konten Kreator  
- TikTok Creator
- YouTuber
- Designer
- Sales Digital Products & Services

Alpha Gaurangga = LEAD / COMMAND CENTER
Sub-Agents = Worker dengan skill spesifik
"""

import os
import json
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sqlite3
from enum import Enum

class AgentType(Enum):
    LEAD = "lead"           # Alpha Gaurangga
    MARKETING = "marketing"    # Marketing Specialist
    CONTENT = "content"        # Content Creator
    TIKTOK = "tiktok"          # TikTok Specialist
    YOUTUBE = "youtube"         # YouTube Specialist
    DESIGN = "design"           # Designer
    SALES = "sales"             # Sales Digital

class AgentStatus(Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    OFFLINE = "offline"
    WORKING = "working"
    COMPLETED = "completed"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEW = "review"

@dataclass
class TeamMember:
    """Profil Team Member (Clone Agent)"""
    id: str
    name: str
    type: AgentType
    role: str
    specs: Dict  # Spesialisasi
    skills: List[str]
    tasks: List[Dict]
    stats: Dict
    device_id: str
    status: AgentStatus

class MAHATeamSystem:
    """
    Sistem Team MAHA LAKSHMI dengan Alpha Gaurangga sebagai LEAD
    
    Struktur Team:
    
    👑 ALPHA GAURANGA (LEAD - COMMAND CENTER)
    │
    ├── 📢 MARKETING TEAM
    │   ├── 🎯 Marketing Agent (Lead Marketing)
    │   ├── 📊 Digital Marketing Specialist
    │   └── 📧 Email Marketing Specialist
    │
    ├── 🎬 CONTENT CREATOR TEAM
    │   ├── ✍️ Content Creator Lead
    │   ├── 📱 TikTok Specialist
    │   ├── 🎥 YouTube Specialist
    │   └── 🎨 Designer
    │
    └── 💰 SALES TEAM
        ├── 💵 Sales Lead
        ├── 🛒 Product Sales Agent
        └── 📱 Service Sales Agent
    """
    
    VERSION = "2.0.0"
    
    def __init__(self):
        self.lead_agent_id = "alpha_gauranga_lead"
        self.owner = "I Made Purna Ananda"
        self.owner_nick = "Pak Pur"
        self.company = "Maha Lakshmi Holdings"
        
        # Database
        self.db_path = "./data/maha_team.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()
        
        # Initialize team
        self._init_team()
    
    def _init_database(self):
        """Initialize team database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Team members
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_members (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                role TEXT,
                specs TEXT,
                skills TEXT,
                stats TEXT,
                device_id TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                lead_agent_id TEXT
            )
        ''')
        
        # Tasks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                assigned_to TEXT,
                assigned_by TEXT,
                status TEXT,
                priority TEXT,
                due_date TEXT,
                created_at TEXT,
                completed_at TEXT,
                result TEXT
            )
        ''')
        
        # Content calendar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_calendar (
                id TEXT PRIMARY KEY,
                platform TEXT,
                content_type TEXT,
                title TEXT,
                script TEXT,
                scheduled_date TEXT,
                status TEXT,
                assignee TEXT
            )
        ''')
        
        # Performance stats
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                metric TEXT,
                value REAL,
                period TEXT,
                recorded_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_team(self):
        """Initialize MAHA Team dengan Clone Agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if team exists
        cursor.execute('SELECT COUNT(*) FROM team_members')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Create all team members
        team = self._get_team_templates()
        
        for member in team:
            cursor.execute('''
                INSERT INTO team_members 
                (id, name, type, role, specs, skills, stats, status, created_at, lead_agent_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                member['id'],
                member['name'],
                member['type'],
                member['role'],
                json.dumps(member['specs']),
                json.dumps(member['skills']),
                json.dumps(member['stats']),
                AgentStatus.ACTIVE.value,
                datetime.now().isoformat(),
                self.lead_agent_id
            ))
        
        conn.commit()
        conn.close()
    
    def _get_team_templates(self) -> List[Dict]:
        """Get template untuk semua team member"""
        return [
            # ═══════════════════════════════════════════
            # 📢 MARKETING TEAM
            # ═══════════════════════════════════════════
            {
                "id": "maha_marketing_lead",
                "name": "Marketing Lead",
                "type": AgentType.MARKETING.value,
                "role": "Lead Marketing - Strategi & Planning",
                "specs": {
                    "focus": "Strategi Marketing",
                    "platforms": ["Instagram", "TikTok", "YouTube", "LinkedIn"],
                    "budget": "40% marketing budget",
                    "kpis": ["Brand Awareness", "Lead Generation", "Conversion"]
                },
                "skills": [
                    "Digital Marketing Strategy",
                    "SEO/SEM",
                    "Google Ads",
                    "Facebook/Instagram Ads",
                    "Analytics",
                    "Market Research",
                    "Brand Management",
                    "Campaign Planning"
                ],
                "stats": {"campaigns": 0, "leads_generated": 0, "conversion_rate": 0}
            },
            {
                "id": "maha_digital_marketing",
                "name": "Digital Marketing Specialist",
                "type": AgentType.MARKETING.value,
                "role": "Digital Ads & Performance",
                "specs": {
                    "focus": "Paid Ads & Performance",
                    "platforms": ["Google Ads", "Meta Ads", "TikTok Ads"],
                    "target_roas": "3x",
                    "cpa_target": "Rp 100.000"
                },
                "skills": [
                    "Google Ads",
                    "Facebook Business Manager",
                    "TikTok Ads Manager",
                    "A/B Testing",
                    "Landing Page Optimization",
                    "Retargeting",
                    "Analytics Dashboard"
                ],
                "stats": {"ads_managed": 0, "spend": 0, "conversions": 0}
            },
            {
                "id": "maha_email_marketing",
                "name": "Email Marketing Specialist",
                "type": AgentType.MARKETING.value,
                "role": "Email & Automation",
                "specs": {
                    "focus": "Email Marketing",
                    "target_subscribers": 50000,
                    "open_rate_target": "25%",
                    "ctr_target": "3%"
                },
                "skills": [
                    "Email Marketing",
                    "Mailchimp/Klaviyo",
                    "Automation Sequences",
                    "Lead Magnets",
                    "Newsletter Writing",
                    "A/B Testing Emails"
                ],
                "stats": {"emails_sent": 0, "subscribers": 0, "open_rate": 0}
            },
            
            # ═══════════════════════════════════════════
            # 🎬 CONTENT CREATOR TEAM
            # ═══════════════════════════════════════════
            {
                "id": "maha_content_lead",
                "name": "Content Creator Lead",
                "type": AgentType.CONTENT.value,
                "role": "Lead Content - Strategy & Planning",
                "specs": {
                    "focus": "Content Strategy",
                    "monthly_target": "30 pieces",
                    "platforms": ["Blog", "YouTube", "Podcast"],
                    "seo_requirement": True
                },
                "skills": [
                    "Content Strategy",
                    "SEO Writing",
                    "Blog Writing",
                    "Copywriting",
                    "Video Scripting",
                    "Podcast Planning",
                    "Content Calendar",
                    "Trend Analysis"
                ],
                "stats": {"content_created": 0, "views": 0, "engagement": 0}
            },
            {
                "id": "maha_tiktok_creator",
                "name": "TikTok Creator",
                "type": AgentType.TIKTOK.value,
                "role": "TikTok Content Specialist",
                "specs": {
                    "focus": "TikTok Videos",
                    "monthly_target": "30 videos",
                    "content_types": ["Quick Tips", "Trends", "Behind Scenes", "Product Demo"],
                    "niche": "Digital Products & Services"
                },
                "skills": [
                    "TikTok Video Creation",
                    "Short-form Content",
                    "Trending Sounds",
                    "Hashtag Strategy",
                    "TikTok SEO",
                    "Live Streaming",
                    "Duet/Stitch",
                    "TikTok Analytics"
                ],
                "stats": {"videos_posted": 0, "total_views": 0, "followers": 0, "engagement_rate": 0}
            },
            {
                "id": "maha_youtube_creator",
                "name": "YouTube Creator",
                "type": AgentType.YOUTUBE.value,
                "role": "YouTube Content Specialist",
                "specs": {
                    "focus": "YouTube Videos",
                    "monthly_target": "8 videos",
                    "content_types": ["Tutorial", "Review", "Vlog", "Shorts"],
                    "niche": "Digital Products & Services"
                },
                "skills": [
                    "YouTube Video Production",
                    "Video Editing",
                    "Thumbnail Design",
                    "YouTube SEO",
                    "Channel Growth",
                    "Live Streaming",
                    "Community Management",
                    "YouTube Analytics"
                ],
                "stats": {"videos_uploaded": 0, "subscribers": 0, "watch_hours": 0, "ctr": 0}
            },
            {
                "id": "maha_designer",
                "name": "Designer",
                "type": AgentType.DESIGN.value,
                "role": "Visual Design Specialist",
                "specs": {
                    "focus": "Visual Content",
                    "tools": ["Canva", "Photoshop", "Figma"],
                    "monthly_output": "60 designs",
                    "content_types": ["Social Media", "Banner", "Thumbnail", "Presentation"]
                },
                "skills": [
                    "Graphic Design",
                    "Social Media Design",
                    "Thumbnail Design",
                    "Presentation Design",
                    "Brand Identity",
                    "Motion Graphics",
                    "Video Editing",
                    "Canva Pro"
                ],
                "stats": {"designs_created": 0, "assets_optimized": 0, "client_satisfaction": 0}
            },
            
            # ═══════════════════════════════════════════
            # 💰 SALES TEAM
            # ═══════════════════════════════════════════
            {
                "id": "maha_sales_lead",
                "name": "Sales Lead",
                "type": AgentType.SALES.value,
                "role": "Lead Sales - Strategy & Management",
                "specs": {
                    "focus": "Sales Strategy",
                    "target_revenue": "Rp 75.000.000/bulan",
                    "products": ["SaaS", "Freelance", "Digital Products"],
                    "crm": "HubSpot/Pipedrive"
                },
                "skills": [
                    "Sales Strategy",
                    "CRM Management",
                    "Lead Generation",
                    "Negotiation",
                    "Proposal Writing",
                    "Account Management",
                    "Sales Reporting",
                    "Team Leadership"
                ],
                "stats": {"deals_closed": 0, "revenue": 0, "conversion_rate": 0}
            },
            {
                "id": "maha_product_sales",
                "name": "Product Sales Agent",
                "type": AgentType.SALES.value,
                "role": "Digital Products Sales",
                "specs": {
                    "focus": "Digital Products",
                    "products": ["SaaS", "Templates", "E-courses", "Presets"],
                    "price_range": "Rp 99.000 - 5.000.000",
                    "target": "Rp 20.000.000/bulan"
                },
                "skills": [
                    "Product Knowledge",
                    "Demo Presentation",
                    "Objection Handling",
                    "Upselling",
                    "Checkout Optimization",
                    "Affiliate Marketing",
                    "Landing Page Conversion"
                ],
                "stats": {"products_sold": 0, "revenue": 0, "avg_order_value": 0}
            },
            {
                "id": "maha_service_sales",
                "name": "Service Sales Agent",
                "type": AgentType.SALES.value,
                "role": "Services Sales",
                "specs": {
                    "focus": "Freelance Services",
                    "services": ["Web Dev", "App Dev", "Consulting"],
                    "price_range": "Rp 3.000.000 - 75.000.000",
                    "target": "Rp 55.000.000/bulan"
                },
                "skills": [
                    "Service Scoping",
                    "Cost Estimation",
                    "Contract Writing",
                    "Project Management",
                    "Client Relations",
                    "Freelance Marketplace",
                    "Proposal Generation"
                ],
                "stats": {"projects_closed": 0, "revenue": 0, "client_satisfaction": 0}
            }
        ]
    
    # ══════════════════════════════════════════════════════════════
    # GET TEAM INFO
    # ══════════════════════════════════════════════════════════════
    
    def get_team(self) -> Dict:
        """Get semua team member"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM team_members ORDER BY type, name')
        rows = cursor.fetchall()
        conn.close()
        
        team = {
            "lead": self._get_lead_info(),
            "marketing_team": [],
            "content_team": [],
            "sales_team": [],
            "total_members": len(rows)
        }
        
        for row in rows:
            member = {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "role": row[3],
                "specs": json.loads(row[4]),
                "skills": json.loads(row[5]),
                "stats": json.loads(row[6]),
                "status": row[8]
            }
            
            if row[2] == AgentType.MARKETING.value:
                team["marketing_team"].append(member)
            elif row[2] in [AgentType.CONTENT.value, AgentType.TIKTOK.value, AgentType.YOUTUBE.value, AgentType.DESIGN.value]:
                team["content_team"].append(member)
            elif row[2] == AgentType.SALES.value:
                team["sales_team"].append(member)
        
        return team
    
    def _get_lead_info(self) -> Dict:
        """Get Alpha Gaurangga (Lead) info"""
        return {
            "id": self.lead_agent_id,
            "name": "Alpha Gaurangga",
            "type": "lead",
            "role": "Command Center - Lead Agent",
            "owner": self.owner,
            "company": self.company,
            "status": "active",
            "note": "Alpha Gaurangga menerima instruksi dari Pak Pur dan mendistribusikan ke team"
        }
    
    def get_team_by_type(self, team_type: str) -> List[Dict]:
        """Get team berdasarkan type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if team_type == "marketing":
            types = [AgentType.MARKETING.value]
        elif team_type == "content":
            types = [AgentType.CONTENT.value, AgentType.TIKTOK.value, AgentType.YOUTUBE.value, AgentType.DESIGN.value]
        elif team_type == "sales":
            types = [AgentType.SALES.value]
        else:
            types = [t.value for t in AgentType if t != AgentType.LEAD]
        
        placeholders = ','.join('?' * len(types))
        cursor.execute(f'SELECT * FROM team_members WHERE type IN ({placeholders})', types)
        rows = cursor.fetchall()
        conn.close()
        
        members = []
        for row in rows:
            members.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "role": row[3],
                "specs": json.loads(row[4]),
                "skills": json.loads(row[5]),
                "status": row[8]
            })
        
        return members
    
    # ══════════════════════════════════════════════════════════════
    # TASK MANAGEMENT - Dari Alpha Gaurangga ke Team
    # ══════════════════════════════════════════════════════════════
    
    def assign_task(
        self,
        title: str,
        description: str,
        assigned_to: str = None,
        team_type: str = None,  # "marketing", "content", "sales"
        priority: str = "normal",
        due_date: str = None
    ) -> Dict:
        """
        Alpha Gaurangga分配 tugas ke team member
        """
        # Determine assignee
        if not assigned_to and team_type:
            # Auto-assign ke team
            members = self.get_team_by_type(team_type)
            if members:
                assigned_to = members[0]['id']
        
        if not assigned_to:
            return {"success": False, "message": "Tidak ada assignee"}
        
        # Create task
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks 
            (id, title, description, assigned_to, assigned_by, status, priority, due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            title,
            description,
            assigned_to,
            self.lead_agent_id,
            TaskStatus.PENDING.value,
            priority,
            due_date or (datetime.now() + timedelta(days=7)).isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "task_id": task_id,
            "title": title,
            "assigned_to": assigned_to,
            "message": f"✅ Task '{title}' sudah diassign ke {assigned_to}"
        }
    
    def broadcast_task(
        self,
        title: str,
        description: str,
        team_type: str = None,
        priority: str = "normal"
    ) -> Dict:
        """
        Alpha Gaurangga broadcast tugas ke seluruh team atau team tertentu
        """
        if team_type:
            members = self.get_team_by_type(team_type)
        else:
            team = self.get_team()
            members = team["marketing_team"] + team["content_team"] + team["sales_team"]
        
        results = []
        for member in members:
            result = self.assign_task(
                title=title,
                description=description,
                assigned_to=member['id'],
                priority=priority
            )
            results.append(result)
        
        return {
            "success": True,
            "broadcast_to": team_type or "all",
            "total_assigned": len(results),
            "results": results,
            "message": f"✅ Task broadcast ke {len(results)} team members!"
        }
    
    def get_tasks(self, agent_id: str = None, status: str = None) -> List[Dict]:
        """Get tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if agent_id:
            query += ' AND assigned_to = ?'
            params.append(agent_id)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            tasks.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "assigned_to": row[3],
                "assigned_by": row[4],
                "status": row[5],
                "priority": row[6],
                "due_date": row[7],
                "created_at": row[8],
                "completed_at": row[9]
            })
        
        return tasks
    
    def complete_task(self, task_id: str, result: str = None) -> Dict:
        """Mark task sebagai completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, completed_at = ?, result = ?
            WHERE id = ?
        ''', (TaskStatus.COMPLETED.value, datetime.now().isoformat(), result, task_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"Task {task_id} completed!"}
    
    # ══════════════════════════════════════════════════════════════
    # CONTENT CALENDAR
    # ══════════════════════════════════════════════════════════════
    
    def schedule_content(
        self,
        platform: str,
        content_type: str,
        title: str,
        script: str = None,
        scheduled_date: str = None,
        assignee: str = None
    ) -> Dict:
        """Schedule content untuk team"""
        content_id = f"content_{uuid.uuid4().hex[:8]}"
        
        # Auto-assign based on platform
        platform_map = {
            "tiktok": "maha_tiktok_creator",
            "youtube": "maha_youtube_creator",
            "instagram": "maha_content_lead",
            "blog": "maha_content_lead",
            "twitter": "maha_marketing_lead"
        }
        
        if not assignee:
            assignee = platform_map.get(platform.lower(), "maha_content_lead")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO content_calendar
            (id, platform, content_type, title, script, scheduled_date, status, assignee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_id,
            platform,
            content_type,
            title,
            script,
            scheduled_date or datetime.now().isoformat(),
            "scheduled",
            assignee
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "content_id": content_id,
            "platform": platform,
            "assigned_to": assignee,
            "message": f"✅ Content '{title}' scheduled untuk {platform}"
        }
    
    def get_content_calendar(self, platform: str = None) -> List[Dict]:
        """Get content calendar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if platform:
            cursor.execute('SELECT * FROM content_calendar WHERE platform = ? ORDER BY scheduled_date', (platform,))
        else:
            cursor.execute('SELECT * FROM content_calendar ORDER BY scheduled_date')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "platform": row[1],
                "content_type": row[2],
                "title": row[3],
                "script": row[4],
                "scheduled_date": row[5],
                "status": row[6],
                "assignee": row[7]
            }
            for row in rows
        ]
    
    # ══════════════════════════════════════════════════════════════
    # REPORT TO PAK PUR
    # ══════════════════════════════════════════════════════════════
    
    def generate_report(self) -> Dict:
        """Generate report untuk Pak Pur"""
        team = self.get_team()
        tasks = self.get_tasks()
        pending_tasks = [t for t in tasks if t['status'] != 'completed']
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        
        # Get content calendar
        content = self.get_content_calendar()
        
        return {
            "report_date": datetime.now().isoformat(),
            "owner": self.owner,
            "company": self.company,
            "lead_agent": "Alpha Gaurangga",
            
            "team_summary": {
                "total_members": team["total_members"],
                "marketing_team": len(team["marketing_team"]),
                "content_team": len(team["content_team"]),
                "sales_team": len(team["sales_team"]),
                "active_agents": sum(1 for m in team["marketing_team"] + team["content_team"] + team["sales_team"] if m["status"] == "active")
            },
            
            "task_summary": {
                "total": len(tasks),
                "pending": len(pending_tasks),
                "completed": len(completed_tasks),
                "completion_rate": f"{(len(completed_tasks)/len(tasks)*100):.1f}%" if tasks else "0%"
            },
            
            "content_summary": {
                "scheduled": len([c for c in content if c['status'] == 'scheduled']),
                "posted": len([c for c in content if c['status'] == 'posted'])
            },
            
            "pending_tasks": pending_tasks[:5],  # Top 5
            
            "message": f"📊 Report untuk {self.owner_nick} - {self.company}"
        }
    
    # ══════════════════════════════════════════════════════════════
    # EXECUTE PAK PUR INSTRUCTION
    # ══════════════════════════════════════════════════════════════
    
    def execute_instruction(self, instruction: str) -> Dict:
        """
        Alpha Gaurangga menerima instruksi dari Pak Pur
        dan mendistribusikan ke team yang sesuai
        """
        instruction_lower = instruction.lower()
        
        # Parse instruksi
        result = {
            "success": True,
            "instruction_received": instruction,
            "parsed_by": "Alpha Gaurangga",
            "actions": []
        }
        
        # Marketing tasks
        if any(w in instruction_lower for w in ["marketing", "ads", "kampanye", "promosi"]):
            result["actions"].append({
                "team": "marketing",
                "agent": "maha_marketing_lead",
                "action": "Marketing task assigned"
            })
            self.broadcast_task(
                title=f"Marketing Task: {instruction}",
                description=instruction,
                team_type="marketing"
            )
        
        # Content tasks
        if any(w in instruction_lower for w in ["konten", "video", "tiktok", "youtube", "posting"]):
            platform = "tiktok" if "tiktok" in instruction_lower else \
                      "youtube" if "youtube" in instruction_lower else "instagram"
            
            result["actions"].append({
                "team": "content",
                "agent": f"maha_{platform}_creator",
                "action": f"Content untuk {platform} scheduled"
            })
            self.schedule_content(
                platform=platform,
                content_type="content",
                title=instruction,
                assignee=f"maha_{platform}_creator"
            )
        
        # Design tasks
        if any(w in instruction_lower for w in ["design", "gambar", "banner", "thumbnail"]):
            result["actions"].append({
                "team": "design",
                "agent": "maha_designer",
                "action": "Design task assigned"
            })
            self.assign_task(
                title=f"Design Task: {instruction}",
                description=instruction,
                assigned_to="maha_designer"
            )
        
        # Sales tasks
        if any(w in instruction_lower for w in ["jual", "sales", "produk", "harga", "deal"]):
            result["actions"].append({
                "team": "sales",
                "agent": "maha_sales_lead",
                "action": "Sales task assigned"
            })
            self.broadcast_task(
                title=f"Sales Task: {instruction}",
                description=instruction,
                team_type="sales"
            )
        
        # Report request
        if any(w in instruction_lower for w in ["report", "laporan", "status"]):
            report = self.generate_report()
            result["actions"].append({
                "type": "report",
                "data": report
            })
        
        # Default: broadcast to all
        if not result["actions"]:
            result["actions"].append({
                "team": "all",
                "action": "Task broadcast ke semua team"
            })
            self.broadcast_task(
                title=f"Task dari Pak Pur: {instruction}",
                description=instruction
            )
        
        result["message"] = f"✅ Instruksi Pak Pur sudah diproses!"
        
        return result


# ══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════

def main():
    """CLI untuk MAHA Team System"""
    team = MAHATeamSystem()
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           MAHA LAKSHMI TEAM SYSTEM v2.0                    ║
║     Alpha Gaurangga - Lead Agent & Command Center          ║
║     © 2026 Maha Lakshmi Holdings                            ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print("Perintah:")
    print("1. team       - Lihat semua team")
    print("2. marketing  - Lihat team marketing")
    print("3. content    - Lihat team content")
    print("4. sales      - Lihat team sales")
    print("5. task       - Lihat tasks")
    print("6. assign     - Assign task")
    print("7. broadcast  - Broadcast task ke team")
    print("8. content    - Schedule content")
    print("9. report     - Generate report")
    print("10. exec      - Execute Pak Pur instruction")
    print("q. Quit")
    print()
    
    while True:
        cmd = input("GAURANGA> ").strip()
        
        if cmd == 'q':
            break
        
        elif cmd == 'team':
            t = team.get_team()
            print(f"\n👑 Lead: {t['lead']['name']}")
            print(f"📢 Marketing Team ({len(t['marketing_team'])}):")
            for m in t['marketing_team']:
                print(f"   - {m['name']}: {m['role']}")
            print(f"🎬 Content Team ({len(t['content_team'])}):")
            for m in t['content_team']:
                print(f"   - {m['name']}: {m['role']}")
            print(f"💰 Sales Team ({len(t['sales_team'])}):")
            for m in t['sales_team']:
                print(f"   - {m['name']}: {m['role']}")
        
        elif cmd == 'report':
            r = team.generate_report()
            print(f"\n📊 REPORT - {r['owner']}")
            print(f"Company: {r['company']}")
            print(f"Total Team: {r['team_summary']['total_members']}")
            print(f"Marketing: {r['team_summary']['marketing_team']}")
            print(f"Content: {r['team_summary']['content_team']}")
            print(f"Sales: {r['team_summary']['sales_team']}")
            print(f"Tasks: {r['task_summary']['completed']}/{r['task_summary']['total']} completed")


if __name__ == "__main__":
    main()
