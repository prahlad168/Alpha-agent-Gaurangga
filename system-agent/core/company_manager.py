"""
GAURANGA Enterprise Company Management System
Sistem Manajemen Perusahaan untuk Maha Lakshmi Holdings
Mengelola 10 SBU dengan Maksimal
"""

import os
import json
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

class SBUType(Enum):
    """Jenis SBU"""
    AI_TECH = "ai_tech"
    DIGITAL_AGENCY = "digital_agency"
    ECOMMERCE = "ecommerce"
    EDUTECH = "edutech"
    FINTECH = "fintech"
    LOGISTICS = "logistics"
    FOODTECH = "foodtech"
    TRAVEL = "travel"
    PROPERTY = "property"
    HOLDING = "holding"

class Department(Enum):
    """Departemen"""
    EXECUTIVE = "executive"
    SALES = "sales"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    FINANCE = "finance"
    HR = "hr"
    IT = "it"
    LEGAL = "legal"

class KPICategory(Enum):
    """Kategori KPI"""
    REVENUE = "revenue"
    PROFIT = "profit"
    GROWTH = "growth"
    EFFICIENCY = "efficiency"
    CUSTOMER = "customer"
    EMPLOYEE = "employee"

class CompanyManager:
    """
    Sistem Manajemen Perusahaan Enterprise
    Mengelola semua aspek bisnis Maha Lakshmi Holdings
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.owner = self.config.get("agent.owner", "I Made Purna Ananda")
        self.company = "Maha Lakshmi Holdings"
        
        # Storage
        self.db_path = "./data/company.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load SBUs
        self.sbus = self._get_sbus()
    
    def _init_database(self):
        """Initialize company database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SBUs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sbus (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                target_revenue REAL DEFAULT 0,
                actual_revenue REAL DEFAULT 0,
                target_employees INTEGER DEFAULT 0,
                current_employees INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                department TEXT,
                sbu_id TEXT,
                email TEXT,
                phone TEXT,
                salary REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                hire_date TEXT,
                FOREIGN KEY (sbu_id) REFERENCES sbus(id)
            )
        ''')
        
        # KPIs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpis (
                id TEXT PRIMARY KEY,
                sbu_id TEXT,
                category TEXT NOT NULL,
                metric TEXT NOT NULL,
                target REAL DEFAULT 0,
                actual REAL DEFAULT 0,
                unit TEXT DEFAULT 'percent',
                period TEXT DEFAULT 'monthly',
                created_at TEXT,
                FOREIGN KEY (sbu_id) REFERENCES sbus(id)
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                sbu_id TEXT,
                assignee_id TEXT,
                priority INTEGER DEFAULT 2,
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Meetings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                sbu_id TEXT,
                participants TEXT,
                scheduled_at TEXT,
                duration_minutes INTEGER DEFAULT 60,
                status TEXT DEFAULT 'scheduled'
            )
        ''')
        
        # Financial records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS finances (
                id TEXT PRIMARY KEY,
                sbu_id TEXT,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date TEXT,
                created_at TEXT
            )
        ''')
        
        # Projects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                sbu_id TEXT,
                status TEXT DEFAULT 'planning',
                start_date TEXT,
                end_date TEXT,
                budget REAL DEFAULT 0,
                spent REAL DEFAULT 0,
                progress INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_sbus(self) -> List[Dict]:
        """Get all SBUs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sbus')
        rows = cursor.fetchall()
        conn.close()
        
        sbus = []
        for row in rows:
            sbus.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'description': row[3],
                'target_revenue': row[4],
                'actual_revenue': row[5],
                'status': row[8]
            })
        return sbus
    
    # ══════════════════════════════════════════════════════════════
    # SBU MANAGEMENT
    # ══════════════════════════════════════════════════════════════
    
    def initialize_sbus(self) -> Dict[str, Any]:
        """Initialize 10 SBU default"""
        default_sbus = [
            {
                "id": "sbu_01",
                "name": "Payangan AI Solutions",
                "type": SBUType.AI_TECH.value,
                "description": "AI & Machine Learning Solutions",
                "target_revenue": 100000000  # 100 juta
            },
            {
                "id": "sbu_02",
                "name": "Gianyar Tech Solutions",
                "type": SBUType.DIGITAL_AGENCY.value,
                "description": "Digital transformation & IT consulting",
                "target_revenue": 80000000
            },
            {
                "id": "sbu_03",
                "name": "Bali Digital Agency",
                "type": SBUType.DIGITAL_AGENCY.value,
                "description": "Creative digital agency services",
                "target_revenue": 60000000
            },
            {
                "id": "sbu_04",
                "name": "Gianyar E-Commerce Hub",
                "type": SBUType.ECOMMERCE.value,
                "description": "E-commerce platform & marketplace",
                "target_revenue": 150000000
            },
            {
                "id": "sbu_05",
                "name": "Bali EdTech Center",
                "type": SBUType.EDUTECH.value,
                "description": "Education technology & online learning",
                "target_revenue": 50000000
            },
            {
                "id": "sbu_06",
                "name": "Gianyar Finance Tech",
                "type": SBUType.FINTECH.value,
                "description": "Financial technology solutions",
                "target_revenue": 120000000
            },
            {
                "id": "sbu_07",
                "name": "Bali Logistics Network",
                "type": SBUType.LOGISTICS.value,
                "description": "Logistics & supply chain solutions",
                "target_revenue": 90000000
            },
            {
                "id": "sbu_08",
                "name": "Gianyar Food Tech",
                "type": SBUType.FOODTECH.value,
                "description": "Food technology & delivery",
                "target_revenue": 70000000
            },
            {
                "id": "sbu_09",
                "name": "Bali Travel Platform",
                "type": SBUType.TRAVEL.value,
                "description": "Travel & tourism platform",
                "target_revenue": 80000000
            },
            {
                "id": "sbu_10",
                "name": "Gianyar Property Tech",
                "type": SBUType.PROPERTY.value,
                "description": "Real estate technology",
                "target_revenue": 110000000
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for sbu in default_sbus:
            cursor.execute('''
                INSERT OR REPLACE INTO sbus 
                (id, name, type, description, target_revenue, actual_revenue, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, 'active', ?, ?)
            ''', (
                sbu['id'], sbu['name'], sbu['type'], sbu['description'],
                sbu['target_revenue'], datetime.now().isoformat(), datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"10 SBU berhasil diinisialisasi"}
    
    def get_all_sbus(self) -> List[Dict]:
        """Get all SBUs with stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, 
                   COUNT(DISTINCT e.id) as employees,
                   COUNT(DISTINCT t.id) as tasks,
                   SUM(CASE WHEN f.type='income' THEN f.amount ELSE 0 END) as total_income,
                   SUM(CASE WHEN f.type='expense' THEN f.amount ELSE 0 END) as total_expense
            FROM sbus s
            LEFT JOIN employees e ON e.sbu_id = s.id
            LEFT JOIN tasks t ON t.sbu_id = s.id
            LEFT JOIN finances f ON f.sbu_id = s.id
            GROUP BY s.id
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'description': row[3],
                'target_revenue': row[4],
                'actual_revenue': row[5],
                'status': row[8],
                'employees': row[9],
                'tasks': row[10],
                'total_income': row[11] or 0,
                'total_expense': row[12] or 0,
                'profit': (row[11] or 0) - (row[12] or 0),
                'achievement': round((row[5] / row[4] * 100), 2) if row[4] > 0 else 0
            })
        
        return results
    
    def update_sbu_revenue(self, sbu_id: str, amount: float, transaction_type: str) -> Dict:
        """Update SBU revenue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current revenue
        cursor.execute('SELECT actual_revenue FROM sbus WHERE id = ?', (sbu_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"success": False, "reason": "SBU tidak ditemukan"}
        
        current = row[0]
        
        if transaction_type == 'income':
            new_revenue = current + amount
        else:
            new_revenue = current  # Expense doesn't reduce revenue target
        
        cursor.execute('''
            UPDATE sbus SET actual_revenue = ?, updated_at = ? WHERE id = ?
        ''', (new_revenue, datetime.now().isoformat(), sbu_id))
        
        # Record transaction
        cursor.execute('''
            INSERT INTO finances (id, sbu_id, type, category, amount, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"fin_{datetime.now().timestamp()}",
            sbu_id,
            transaction_type,
            'revenue',
            amount,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "new_revenue": new_revenue}
    
    # ══════════════════════════════════════════════════════════════
    # EMPLOYEE MANAGEMENT
    # ══════════════════════════════════════════════════════════════
    
    def add_employee(self, employee_data: Dict) -> Dict:
        """Add new employee"""
        employee_id = f"emp_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO employees 
            (id, name, position, department, sbu_id, email, phone, salary, hire_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            employee_id,
            employee_data.get('name'),
            employee_data.get('position'),
            employee_data.get('department'),
            employee_data.get('sbu_id'),
            employee_data.get('email'),
            employee_data.get('phone'),
            employee_data.get('salary', 0),
            datetime.now().isoformat()
        ))
        
        # Update SBU employee count
        cursor.execute('''
            UPDATE sbus SET current_employees = current_employees + 1 WHERE id = ?
        ''', (employee_data.get('sbu_id'),))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "employee_id": employee_id}
    
    def get_employees(self, sbu_id: str = None) -> List[Dict]:
        """Get employees"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if sbu_id:
            cursor.execute('SELECT * FROM employees WHERE sbu_id = ?', (sbu_id,))
        else:
            cursor.execute('SELECT * FROM employees')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'name': row[1],
            'position': row[2],
            'department': row[3],
            'sbu_id': row[4],
            'email': row[5],
            'phone': row[6],
            'salary': row[7],
            'status': row[8],
            'hire_date': row[9]
        } for row in rows]
    
    # ══════════════════════════════════════════════════════════════
    # TASK MANAGEMENT
    # ══════════════════════════════════════════════════════════════
    
    def create_task(self, task_data: Dict) -> Dict:
        """Create new task"""
        task_id = f"task_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks 
            (id, title, description, sbu_id, assignee_id, priority, due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            task_data.get('title'),
            task_data.get('description'),
            task_data.get('sbu_id'),
            task_data.get('assignee_id'),
            task_data.get('priority', 2),
            task_data.get('due_date'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "task_id": task_id}
    
    def get_tasks(self, filters: Dict = None) -> List[Dict]:
        """Get tasks with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if filters:
            if filters.get('sbu_id'):
                query += ' AND sbu_id = ?'
                params.append(filters['sbu_id'])
            if filters.get('status'):
                query += ' AND status = ?'
                params.append(filters['status'])
            if filters.get('priority'):
                query += ' AND priority = ?'
                params.append(filters['priority'])
        
        query += ' ORDER BY priority DESC, created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'sbu_id': row[3],
            'assignee_id': row[4],
            'priority': row[5],
            'status': row[6],
            'due_date': row[7],
            'created_at': row[8]
        } for row in rows]
    
    def update_task_status(self, task_id: str, status: str) -> Dict:
        """Update task status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?
        ''', (status, datetime.now().isoformat(), task_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "status": status}
    
    # ══════════════════════════════════════════════════════════════
    # KPI & ANALYTICS
    # ══════════════════════════════════════════════════════════════
    
    def set_kpi(self, kpi_data: Dict) -> Dict:
        """Set KPI target"""
        kpi_id = f"kpi_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO kpis 
            (id, sbu_id, category, metric, target, unit, period, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kpi_id,
            kpi_data.get('sbu_id'),
            kpi_data.get('category'),
            kpi_data.get('metric'),
            kpi_data.get('target', 0),
            kpi_data.get('unit', 'percent'),
            kpi_data.get('period', 'monthly'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "kpi_id": kpi_id}
    
    def update_kpi_actual(self, kpi_id: str, actual: float) -> Dict:
        """Update KPI actual value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE kpis SET actual = ? WHERE id = ?
        ''', (actual, kpi_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    def get_kpis(self, sbu_id: str = None) -> List[Dict]:
        """Get KPIs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if sbu_id:
            cursor.execute('SELECT * FROM kpis WHERE sbu_id = ?', (sbu_id,))
        else:
            cursor.execute('SELECT * FROM kpis')
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'sbu_id': row[1],
                'category': row[2],
                'metric': row[3],
                'target': row[4],
                'actual': row[5],
                'unit': row[6],
                'achievement': round((row[5] / row[4] * 100), 2) if row[4] > 0 else 0
            })
        
        return results
    
    def get_executive_dashboard(self) -> Dict:
        """Get executive dashboard summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total revenue
        cursor.execute('SELECT SUM(actual_revenue) FROM sbus')
        total_revenue = cursor.fetchone()[0] or 0
        
        # Total target
        cursor.execute('SELECT SUM(target_revenue) FROM sbus')
        total_target = cursor.fetchone()[0] or 0
        
        # Total employees
        cursor.execute('SELECT COUNT(*) FROM employees')
        total_employees = cursor.fetchone()[0]
        
        # Active tasks
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status != "completed"')
        active_tasks = cursor.fetchone()[0]
        
        # Pending tasks
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "pending"')
        pending_tasks = cursor.fetchone()[0]
        
        # Financial summary
        cursor.execute('SELECT SUM(CASE WHEN type="income" THEN amount ELSE 0 END) FROM finances')
        total_income = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(CASE WHEN type="expense" THEN amount ELSE 0 END) FROM finances')
        total_expense = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "company": self.company,
            "owner": self.owner,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_revenue": total_revenue,
                "total_target": total_target,
                "revenue_achievement": round((total_revenue / total_target * 100), 2) if total_target > 0 else 0,
                "total_sbus": len(self.sbus),
                "total_employees": total_employees,
                "active_tasks": active_tasks,
                "pending_tasks": pending_tasks,
                "total_income": total_income,
                "total_expense": total_expense,
                "net_profit": total_income - total_expense
            },
            "sbus_performance": self.get_all_sbus(),
            "top_tasks": self.get_tasks({"status": "pending"})[:5]
        }
    
    # ══════════════════════════════════════════════════════════════
    # MEETING MANAGEMENT
    # ══════════════════════════════════════════════════════════════
    
    def schedule_meeting(self, meeting_data: Dict) -> Dict:
        """Schedule new meeting"""
        meeting_id = f"meet_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO meetings 
            (id, title, description, sbu_id, participants, scheduled_at, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            meeting_id,
            meeting_data.get('title'),
            meeting_data.get('description'),
            meeting_data.get('sbu_id'),
            json.dumps(meeting_data.get('participants', [])),
            meeting_data.get('scheduled_at'),
            meeting_data.get('duration_minutes', 60)
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "meeting_id": meeting_id}
    
    def get_upcoming_meetings(self, days: int = 7) -> List[Dict]:
        """Get upcoming meetings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM meetings 
            WHERE scheduled_at >= ? AND scheduled_at <= ?
            ORDER BY scheduled_at
        ''', (
            datetime.now().isoformat(),
            (datetime.now() + timedelta(days=days)).isoformat()
        ))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'sbu_id': row[3],
            'participants': json.loads(row[4]),
            'scheduled_at': row[5],
            'duration_minutes': row[6],
            'status': row[7]
        } for row in rows]
    
    # ══════════════════════════════════════════════════════════════
    # PROJECT MANAGEMENT
    # ══════════════════════════════════════════════════════════════
    
    def create_project(self, project_data: Dict) -> Dict:
        """Create new project"""
        project_id = f"proj_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO projects 
            (id, name, sbu_id, start_date, end_date, budget, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            project_data.get('name'),
            project_data.get('sbu_id'),
            project_data.get('start_date', datetime.now().date().isoformat()),
            project_data.get('end_date'),
            project_data.get('budget', 0),
            'planning'
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "project_id": project_id}
    
    def get_projects(self, sbu_id: str = None) -> List[Dict]:
        """Get projects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if sbu_id:
            cursor.execute('SELECT * FROM projects WHERE sbu_id = ?', (sbu_id,))
        else:
            cursor.execute('SELECT * FROM projects')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'name': row[1],
            'sbu_id': row[2],
            'status': row[3],
            'start_date': row[4],
            'end_date': row[5],
            'budget': row[6],
            'spent': row[7],
            'progress': row[8]
        } for row in rows]
    
    def update_project_progress(self, project_id: str, progress: int) -> Dict:
        """Update project progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        status = 'completed' if progress >= 100 else 'in_progress' if progress > 0 else 'planning'
        
        cursor.execute('''
            UPDATE projects SET progress = ?, status = ? WHERE id = ?
        ''', (progress, status, project_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    # ══════════════════════════════════════════════════════════════
    # FINANCIAL MANAGEMENT
    # ══════════════════════════════════════════════════════════════
    
    def record_transaction(self, transaction_data: Dict) -> Dict:
        """Record financial transaction"""
        trans_id = f"trans_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO finances 
            (id, sbu_id, type, category, amount, description, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trans_id,
            transaction_data.get('sbu_id'),
            transaction_data.get('type'),  # income or expense
            transaction_data.get('category'),
            transaction_data.get('amount'),
            transaction_data.get('description'),
            transaction_data.get('date', datetime.now().isoformat()),
            datetime.now().isoformat()
        ))
        
        # Update SBU revenue if income
        if transaction_data.get('type') == 'income':
            self.update_sbu_revenue(
                transaction_data.get('sbu_id'),
                transaction_data.get('amount'),
                'income'
            )
        
        conn.commit()
        conn.close()
        
        return {"success": True, "transaction_id": trans_id}
    
    def get_financial_report(self, period: str = 'monthly') -> Dict:
        """Get financial report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get totals
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as total_expense,
                category,
                type
            FROM finances 
            GROUP BY type, category
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        income_by_category = {}
        expense_by_category = {}
        total_income = 0
        total_expense = 0
        
        for row in rows:
            if row[3] == 'income':
                total_income += row[0] or 0
                income_by_category[row[2]] = row[0] or 0
            else:
                total_expense += row[0] or 0
                expense_by_category[row[2]] = row[0] or 0
        
        return {
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "total_income": total_income,
            "total_expense": total_expense,
            "net_profit": total_income - total_expense,
            "profit_margin": round(((total_income - total_expense) / total_income * 100), 2) if total_income > 0 else 0,
            "income_by_category": income_by_category,
            "expense_by_category": expense_by_category,
            "sbu_contribution": self.get_all_sbus()
        }
    
    # ══════════════════════════════════════════════════════════════
    # AI ASSISTANT INTEGRATION
    # ══════════════════════════════════════════════════════════════
    
    def generate_report(self, report_type: str = 'executive') -> str:
        """Generate report based on type"""
        if report_type == 'executive':
            dashboard = self.get_executive_dashboard()
            return self._format_executive_report(dashboard)
        elif report_type == 'financial':
            return self._format_financial_report(self.get_financial_report())
        elif report_type == 'sbu':
            return self._format_sbu_report(self.get_all_sbus())
        elif report_type == 'tasks':
            return self._format_task_report(self.get_tasks())
        else:
            return "Report type not recognized"
    
    def _format_executive_report(self, data: Dict) -> str:
        """Format executive report"""
        summary = data['summary']
        
        return f"""
📊 LAPORAN EXECUTIVE - {data['company']}

👤 Pemilik: {data['owner']}
📅 Tanggal: {datetime.now().strftime('%d %B %Y')}

═══════════════════════════════════════
📈 PERFORMANCE SUMMARY
═══════════════════════════════════════

💰 Total Revenue: Rp {summary['total_revenue']:,.0f}
🎯 Total Target: Rp {summary['total_target']:,.0f}
📊 Pencapaian: {summary['revenue_achievement']}%

👥 Total SBU: {summary['total_sbus']}
👷 Total Karyawan: {summary['total_employees']}

📋 Active Tasks: {summary['active_tasks']}
⏳ Pending Tasks: {summary['pending_tasks']}

═══════════════════════════════════════
💵 FINANCIAL SUMMARY
═══════════════════════════════════════

💵 Total Income: Rp {summary['total_income']:,.0f}
💸 Total Expense: Rp {summary['total_expense']:,.0f}
✅ Net Profit: Rp {summary['net_profit']:,.0f}

═══════════════════════════════════════
📈 SBU PERFORMANCE
═══════════════════════════════════════
"""
    
    def _format_financial_report(self, data: Dict) -> str:
        """Format financial report"""
        return f"""
💰 FINANCIAL REPORT

Total Income: Rp {data['total_income']:,.0f}
Total Expense: Rp {data['total_expense']:,.0f}
Net Profit: Rp {data['net_profit']:,.0f}
Profit Margin: {data['profit_margin']}%
"""
    
    def _format_sbu_report(self, sbus: List[Dict]) -> str:
        """Format SBU report"""
        result = "📈 SBU PERFORMANCE REPORT\n\n"
        for sbu in sbus:
            result += f"""
{sbu['name']}
Pencapaian: {sbu['achievement']}%
Revenue: Rp {sbu['actual_revenue']:,.0f} / Rp {sbu['target_revenue']:,.0f}
Karyawan: {sbu['employees']}
Tasks: {sbu['tasks']}
"""
        return result
    
    def _format_task_report(self, tasks: List[Dict]) -> str:
        """Format task report"""
        result = "📋 TASK REPORT\n\n"
        for task in tasks:
            result += f"""
{task['title']}
Status: {task['status']}
Priority: {task['priority']}
Due: {task.get('due_date', 'N/A')}
"""
        return result


# ══════════════════════════════════════════════════════════════
# SALES & CRM MODULE
# ══════════════════════════════════════════════════════════════

class SalesCRM:
    """Sales and Customer Relationship Management"""
    
    def __init__(self, db_path: str = "./data/company.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_crm_tables()
    
    def _init_crm_tables(self):
        """Initialize CRM tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                company TEXT,
                email TEXT,
                phone TEXT,
                sbu_id TEXT,
                status TEXT DEFAULT 'prospect',
                total_deals REAL DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        # Deals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                title TEXT NOT NULL,
                amount REAL DEFAULT 0,
                stage TEXT DEFAULT 'lead',
                probability INTEGER DEFAULT 0,
                expected_close TEXT,
                sbu_id TEXT,
                created_at TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        ''')
        
        # Activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                deal_id TEXT,
                type TEXT NOT NULL,
                description TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_client(self, client_data: Dict) -> Dict:
        """Add new client"""
        client_id = f"client_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clients (id, name, company, email, phone, sbu_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id,
            client_data.get('name'),
            client_data.get('company'),
            client_data.get('email'),
            client_data.get('phone'),
            client_data.get('sbu_id'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "client_id": client_id}
    
    def create_deal(self, deal_data: Dict) -> Dict:
        """Create new deal"""
        deal_id = f"deal_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO deals (id, client_id, title, amount, stage, probability, expected_close, sbu_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deal_id,
            deal_data.get('client_id'),
            deal_data.get('title'),
            deal_data.get('amount', 0),
            deal_data.get('stage', 'lead'),
            deal_data.get('probability', 10),
            deal_data.get('expected_close'),
            deal_data.get('sbu_id'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "deal_id": deal_id}
    
    def get_sales_pipeline(self) -> Dict:
        """Get sales pipeline summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT stage, COUNT(*), SUM(amount), AVG(probability)
            FROM deals GROUP BY stage
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        pipeline = {}
        total_value = 0
        
        for row in rows:
            stage = row[0]
            count = row[1]
            amount = row[2] or 0
            avg_prob = row[3] or 0
            
            pipeline[stage] = {
                "count": count,
                "value": amount,
                "avg_probability": round(avg_prob, 1),
                "weighted_value": amount * avg_prob / 100
            }
            total_value += amount
        
        return {
            "pipeline": pipeline,
            "total_value": total_value,
            "stages": ["lead", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]
        }


# Global instances
_company_manager = None
_sales_crm = None

def get_company_manager(config: Dict = None) -> CompanyManager:
    """Get or create company manager"""
    global _company_manager
    if _company_manager is None:
        _company_manager = CompanyManager(config)
    return _company_manager

def get_sales_crm() -> SalesCRM:
    """Get or create sales CRM"""
    global _sales_crm
    if _sales_crm is None:
        _sales_crm = SalesCRM()
    return _sales_crm
