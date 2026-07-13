"""
GAURANGA - Revenue Database Module
SQLite Database untuk tracking pendapatan real-time
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'gauranga_revenue.db')

class RevenueDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # SBU (Strategic Business Units)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sbu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                icon TEXT,
                target_monthly INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clients
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                email TEXT,
                sbu_id INTEGER,
                status TEXT DEFAULT 'lead',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sbu_id) REFERENCES sbu(id)
            )
        ''')
        
        # Projects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                sbu_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                value INTEGER DEFAULT 0,
                status TEXT DEFAULT 'prospect',
                start_date DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id),
                FOREIGN KEY (sbu_id) REFERENCES sbu(id)
            )
        ''')
        
        # Transactions (Revenue/Expense)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sbu_id INTEGER,
                project_id INTEGER,
                type TEXT NOT NULL,
                category TEXT,
                description TEXT,
                amount INTEGER NOT NULL,
                payment_method TEXT,
                date DATE NOT NULL,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sbu_id) REFERENCES sbu(id),
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        
        # CEO Transfers (Bitcoin)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ceo_transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_idr INTEGER NOT NULL,
                amount_btc_satoshi INTEGER NOT NULL,
                btc_rate INTEGER,
                sbu_source TEXT,
                note TEXT,
                date DATE NOT NULL,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Invoices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                client_id INTEGER,
                project_id INTEGER,
                sbu_id INTEGER,
                amount INTEGER NOT NULL,
                tax_amount INTEGER DEFAULT 0,
                total_amount INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                due_date DATE,
                paid_date DATE,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id),
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (sbu_id) REFERENCES sbu(id)
            )
        ''')
        
        # Seed default SBUs if empty
        cursor.execute('SELECT COUNT(*) FROM sbu')
        if cursor.fetchone()[0] == 0:
            default_sbus = [
                ('hospital', '🏥 Hospital', 'hospital', 50000000),
                ('ecommerce', '🛒 E-Commerce', 'ecommerce', 30000000),
                ('education', '📚 Education', 'education', 25000000),
                ('travel', '✈️ Travel', 'travel', 20000000),
                ('property', '🏠 Property', 'property', 25000000),
                ('food', '🍔 Food', 'food', 20000000),
                ('general', '💼 General', 'general', 0),
            ]
            cursor.executemany(
                'INSERT INTO sbu (name, display_name, icon, target_monthly) VALUES (?, ?, ?, ?)',
                default_sbus
            )
        
        conn.commit()
        conn.close()
    
    # ============ SBU OPERATIONS ============
    
    def get_all_sbus(self) -> List[Dict]:
        """Get all SBUs with revenue summary"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, 
                   COALESCE(SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END), 0) as total_income,
                   COALESCE(SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END), 0) as total_expense
            FROM sbu s
            LEFT JOIN transactions t ON s.id = t.sbu_id
            GROUP BY s.id
        ''')
        
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def get_sbu_by_name(self, name: str) -> Optional[Dict]:
        """Get SBU by name"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sbu WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    # ============ CLIENT OPERATIONS ============
    
    def add_client(self, name: str, company: str = None, phone: str = None, 
                   email: str = None, sbu_id: int = None) -> int:
        """Add new client"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (name, company, phone, email, sbu_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, company, phone, email, sbu_id))
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return client_id
    
    def get_all_clients(self) -> List[Dict]:
        """Get all clients"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, s.display_name as sbu_name 
            FROM clients c
            LEFT JOIN sbu s ON c.sbu_id = s.id
            ORDER BY c.created_at DESC
        ''')
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def update_client_status(self, client_id: int, status: str):
        """Update client status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE clients SET status = ? WHERE id = ?', (status, client_id))
        conn.commit()
        conn.close()
    
    # ============ PROJECT OPERATIONS ============
    
    def add_project(self, name: str, client_id: int = None, sbu_id: int = None,
                    value: int = 0, status: str = 'prospect', description: str = None) -> int:
        """Add new project"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, client_id, sbu_id, value, status, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, client_id, sbu_id, value, status, description))
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, c.name as client_name, s.display_name as sbu_name
            FROM projects p
            LEFT JOIN clients c ON p.client_id = c.id
            LEFT JOIN sbu s ON p.sbu_id = s.id
            ORDER BY p.created_at DESC
        ''')
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def update_project_status(self, project_id: int, status: str):
        """Update project status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE projects SET status = ? WHERE id = ?', (status, project_id))
        conn.commit()
        conn.close()
    
    # ============ TRANSACTION OPERATIONS ============
    
    def add_transaction(self, sbu_id: int, type: str, amount: int, 
                        description: str = None, category: str = None,
                        payment_method: str = None, date: str = None,
                        project_id: int = None) -> int:
        """Add new transaction"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions 
            (sbu_id, type, amount, description, category, payment_method, date, project_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (sbu_id, type, amount, description, category, payment_method, today, project_id))
        tx_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tx_id
    
    def get_transactions(self, limit: int = 50, sbu_id: int = None) -> List[Dict]:
        """Get transactions"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if sbu_id:
            cursor.execute('''
                SELECT t.*, s.display_name as sbu_name
                FROM transactions t
                LEFT JOIN sbu s ON t.sbu_id = s.id
                WHERE t.sbu_id = ?
                ORDER BY t.date DESC, t.id DESC
                LIMIT ?
            ''', (sbu_id, limit))
        else:
            cursor.execute('''
                SELECT t.*, s.display_name as sbu_name
                FROM transactions t
                LEFT JOIN sbu s ON t.sbu_id = s.id
                ORDER BY t.date DESC, t.id DESC
                LIMIT ?
            ''', (limit,))
        
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def get_revenue_summary(self) -> Dict:
        """Get overall revenue summary"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total income
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'income'
        ''')
        total_income = cursor.fetchone()[0] or 0
        
        # Total expense
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'expense'
        ''')
        total_expense = cursor.fetchone()[0] or 0
        
        # Monthly income
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'income' AND date >= date('now', 'start of month')
        ''')
        monthly_income = cursor.fetchone()[0] or 0
        
        # Monthly expense
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'expense' AND date >= date('now', 'start of month')
        ''')
        monthly_expense = cursor.fetchone()[0] or 0
        
        # SBU breakdown
        cursor.execute('''
            SELECT s.name, s.display_name, s.icon,
                   COALESCE(SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END), 0) as income,
                   COALESCE(SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END), 0) as expense,
                   s.target_monthly
            FROM sbu s
            LEFT JOIN transactions t ON s.id = t.sbu_id
            GROUP BY s.id
            ORDER BY income DESC
        ''')
        
        sbu_breakdown = []
        for row in cursor.fetchall():
            sbu_breakdown.append({
                'name': row[0],
                'display_name': row[1],
                'icon': row[2],
                'income': row[3] or 0,
                'expense': row[4] or 0,
                'target_monthly': row[5] or 0
            })
        
        conn.close()
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'total_profit': total_income - total_expense,
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'monthly_profit': monthly_income - monthly_expense,
            'sbu_breakdown': sbu_breakdown
        }
    
    # ============ INVOICE OPERATIONS ============
    
    def generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        today = datetime.now().strftime('%Y%m%d')
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM invoices 
            WHERE invoice_number LIKE ?
        ''', (f'INV-{today}%',))
        count = cursor.fetchone()[0]
        conn.close()
        return f"INV-{today}-{count + 1:03d}"
    
    def create_invoice(self, client_id: int, amount: int, sbu_id: int = None,
                       project_id: int = None, due_days: int = 14, tax_rate: float = 0.11) -> int:
        """Create new invoice"""
        tax_amount = int(amount * tax_rate)
        total = amount + tax_amount
        
        due_date = datetime.now().replace(
            day=min(datetime.now().day + due_days, 28)
        ).strftime('%Y-%m-%d')
        
        invoice_number = self.generate_invoice_number()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO invoices 
            (invoice_number, client_id, project_id, sbu_id, amount, tax_amount, total_amount, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_number, client_id, project_id, sbu_id, amount, tax_amount, total, due_date))
        invoice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return invoice_id
    
    def get_invoices(self, status: str = None) -> List[Dict]:
        """Get invoices"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT i.*, c.name as client_name, s.display_name as sbu_name
                FROM invoices i
                LEFT JOIN clients c ON i.client_id = c.id
                LEFT JOIN sbu s ON i.sbu_id = s.id
                WHERE i.status = ?
                ORDER BY i.created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT i.*, c.name as client_name, s.display_name as sbu_name
                FROM invoices i
                LEFT JOIN clients c ON i.client_id = c.id
                LEFT JOIN sbu s ON i.sbu_id = s.id
                ORDER BY i.created_at DESC
            ''')
        
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def mark_invoice_paid(self, invoice_id: int, payment_method: str = None):
        """Mark invoice as paid"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get invoice details
        cursor.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
        invoice = cursor.fetchone()
        
        if invoice:
            # Update invoice status
            cursor.execute('''
                UPDATE invoices 
                SET status = 'paid', paid_date = date('now'), payment_method = ?
                WHERE id = ?
            ''', (payment_method, invoice_id))
            
            # Add transaction
            cursor.execute('''
                INSERT INTO transactions 
                (sbu_id, project_id, type, description, amount, payment_method, date)
                VALUES (?, ?, 'income', ?, ?, ?, date('now'))
            ''', (invoice[3], invoice[2], f"Invoice {invoice[1]}", invoice[6], payment_method))
            
            conn.commit()
        conn.close()
    
    # ============ CEO TRANSFER OPERATIONS ============
    
    def add_ceo_transfer(self, amount_idr: int, btc_rate: int = 1500000000, 
                         sbu_source: str = 'general', note: str = None) -> Dict:
        """Add CEO Bitcoin transfer"""
        satoshi = int((amount_idr / btc_rate) * 100000000)
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ceo_transfers (amount_idr, amount_btc_satoshi, btc_rate, sbu_source, note, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (amount_idr, satoshi, btc_rate, sbu_source, note, today))
        
        # Add expense transaction
        cursor.execute('SELECT id FROM sbu WHERE name = ?', (sbu_source,))
        sbu = cursor.fetchone()
        if sbu:
            cursor.execute('''
                INSERT INTO transactions (sbu_id, type, description, amount, date)
                VALUES (?, 'expense', ?, ?, ?)
            ''', (sbu[0], f"CEO Transfer - Bitcoin", amount_idr, today))
        
        transfer_id = cursor.lastrowid
        conn.commit()
        
        # Get total BTC
        cursor.execute('SELECT COALESCE(SUM(amount_btc_satoshi), 0) FROM ceo_transfers')
        total_btc = cursor.fetchone()[0]
        conn.close()
        
        return {
            'id': transfer_id,
            'amount_idr': amount_idr,
            'amount_btc': satoshi / 100000000,
            'btc_rate': btc_rate,
            'total_btc': total_btc / 100000000,
            'status': 'completed'
        }
    
    def get_ceo_transfers(self) -> Dict:
        """Get CEO transfer history and totals"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM ceo_transfers ORDER BY date DESC')
        transfers = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT COALESCE(SUM(amount_btc_satoshi), 0) FROM ceo_transfers')
        total_satoshi = cursor.fetchone()[0]
        
        cursor.execute('SELECT btc_rate FROM ceo_transfers ORDER BY id DESC LIMIT 1')
        last_rate = cursor.fetchone()
        btc_rate = last_rate[0] if last_rate else 1500000000
        
        conn.close()
        
        return {
            'transfers': transfers,
            'total_btc': total_satoshi / 100000000,
            'total_idr': (total_satoshi / 100000000) * btc_rate,
            'btc_address': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
        }

# Global database instance
db = RevenueDatabase()
