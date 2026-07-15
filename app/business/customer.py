"""
MAHALAKSMI AIOS v1.0 - Volume IV Chapter 37: Customer Center / CRM
Automated customer management with CLV and churn analysis
"""
import os
import sys
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class CustomerStatus(Enum):
    """Customer status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"
    PROSPECT = "prospect"


class TicketPriority(Enum):
    """Support ticket priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(Enum):
    """Support ticket status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class CustomerProfile:
    """Customer profile."""
    customer_id: str
    name: str
    email: str
    phone: str = ""
    status: CustomerStatus = CustomerStatus.PROSPECT
    first_contact: str = ""
    last_contact: str = ""
    total_purchases: int = 0
    total_spent: float = 0.0
    ticket_count: int = 0
    clv_score: float = 0.0
    churn_probability: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SupportTicket:
    """Support ticket."""
    ticket_id: str
    customer_id: str
    subject: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    created_at: str = ""
    updated_at: str = ""
    resolved_at: str = ""


@dataclass
class PurchaseRecord:
    """Purchase record for customer."""
    purchase_id: str
    customer_id: str
    product_id: str
    product_name: str
    amount: float
    purchase_date: str


# ============================================================================
# CUSTOMER DATABASE
# ============================================================================

class CustomerDB:
    """SQLite database for customer management."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "customer.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                status TEXT,
                first_contact TEXT,
                last_contact TEXT,
                total_purchases INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0.0,
                ticket_count INTEGER DEFAULT 0,
                clv_score REAL DEFAULT 0.0,
                churn_probability REAL DEFAULT 0.0,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                customer_id TEXT,
                subject TEXT,
                description TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                resolved_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id TEXT PRIMARY KEY,
                customer_id TEXT,
                product_id TEXT,
                product_name TEXT,
                amount REAL,
                purchase_date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_customer(self, customer: CustomerProfile) -> bool:
        """Save customer."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer.customer_id,
                customer.name,
                customer.email,
                customer.phone,
                customer.status.value,
                customer.first_contact,
                customer.last_contact,
                customer.total_purchases,
                customer.total_spent,
                customer.ticket_count,
                customer.clv_score,
                customer.churn_probability,
                json.dumps(customer.metadata)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save customer: {e}")
            return False
    
    def get_customer(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get customer by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_customer(row)
        return None
    
    def _row_to_customer(self, row) -> CustomerProfile:
        """Convert row to CustomerProfile."""
        return CustomerProfile(
            customer_id=row['customer_id'],
            name=row['name'],
            email=row['email'] or "",
            phone=row['phone'] or "",
            status=CustomerStatus(row['status']),
            first_contact=row['first_contact'] or "",
            last_contact=row['last_contact'] or "",
            total_purchases=row['total_purchases'],
            total_spent=row['total_spent'],
            ticket_count=row['ticket_count'],
            clv_score=row['clv_score'],
            churn_probability=row['churn_probability'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def get_all_customers(self) -> List[CustomerProfile]:
        """Get all customers."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers ORDER BY last_contact DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_customer(row) for row in rows]
    
    def save_ticket(self, ticket: SupportTicket) -> bool:
        """Save ticket."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket.ticket_id,
                ticket.customer_id,
                ticket.subject,
                ticket.description,
                ticket.priority.value,
                ticket.status.value,
                ticket.created_at,
                ticket.updated_at,
                ticket.resolved_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save ticket: {e}")
            return False
    
    def get_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """Get ticket by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_ticket(row)
        return None
    
    def _row_to_ticket(self, row) -> SupportTicket:
        """Convert row to SupportTicket."""
        return SupportTicket(
            ticket_id=row['ticket_id'],
            customer_id=row['customer_id'],
            subject=row['subject'],
            description=row['description'],
            priority=TicketPriority(row['priority']),
            status=TicketStatus(row['status']),
            created_at=row['created_at'],
            updated_at=row['updated_at'] or "",
            resolved_at=row['resolved_at'] or ""
        )
    
    def get_tickets_by_customer(self, customer_id: str) -> List[SupportTicket]:
        """Get tickets by customer."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_ticket(row) for row in rows]
    
    def save_purchase(self, purchase: PurchaseRecord) -> bool:
        """Save purchase record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO purchases VALUES (?, ?, ?, ?, ?, ?)
            """, (
                purchase.purchase_id,
                purchase.customer_id,
                purchase.product_id,
                purchase.product_name,
                purchase.amount,
                purchase.purchase_date
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save purchase: {e}")
            return False
    
    def get_purchases_by_customer(self, customer_id: str) -> List[PurchaseRecord]:
        """Get purchases by customer."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM purchases WHERE customer_id = ? ORDER BY purchase_date DESC",
            (customer_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            PurchaseRecord(
                purchase_id=row['purchase_id'],
                customer_id=row['customer_id'],
                product_id=row['product_id'],
                product_name=row['product_name'],
                amount=row['amount'],
                purchase_date=row['purchase_date']
            )
            for row in rows
        ]


# ============================================================================
# CUSTOMER CENTER / CRM
# ============================================================================

class CustomerCenter:
    """
    Enterprise Customer Center / CRM.
    Manages customer profiles, support tickets, and calculates CLV.
    """
    
    # CLV calculation parameters
    AVG_PURCHASE_VALUE = 100000  # Average purchase value
    PURCHASE_FREQUENCY = 2       # Purchases per month
    CUSTOMER_LIFESPAN = 12       # Months
    TICKET_IMPACT = 0.05         # Each ticket reduces CLV by 5%
    
    def __init__(self):
        self.db = CustomerDB()
        
        logger.info("CustomerCenter initialized")
    
    def create_customer(
        self,
        name: str,
        email: str,
        phone: str = "",
        metadata: Dict = None
    ) -> CustomerProfile:
        """Create a new customer."""
        import hashlib
        
        customer_id = hashlib.md5(
            f"{email}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        
        customer = CustomerProfile(
            customer_id=f"CUST-{customer_id}",
            name=name,
            email=email,
            phone=phone,
            status=CustomerStatus.PROSPECT,
            first_contact=datetime.now().isoformat(),
            last_contact=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.db.save_customer(customer)
        
        logger.info(f"Customer created: {customer.customer_id}")
        return customer
    
    def get_customer(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get customer by ID."""
        return self.db.get_customer(customer_id)
    
    def list_customers(self, status: CustomerStatus = None) -> List[Dict]:
        """List all customers."""
        customers = self.db.get_all_customers()
        
        if status:
            customers = [c for c in customers if c.status == status]
        
        return [
            {
                "id": c.customer_id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "status": c.status.value,
                "total_purchases": c.total_purchases,
                "total_spent": c.total_spent,
                "clv_score": round(c.clv_score, 2),
                "churn_probability": round(c.churn_probability * 100, 1),
                "last_contact": c.last_contact
            }
            for c in customers
        ]
    
    def create_ticket(
        self,
        customer_id: str,
        subject: str,
        description: str,
        priority: TicketPriority = TicketPriority.MEDIUM
    ) -> SupportTicket:
        """Create support ticket."""
        import hashlib
        
        ticket_id = hashlib.md5(
            f"{customer_id}{subject}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        
        ticket = SupportTicket(
            ticket_id=f"TICKET-{ticket_id}",
            customer_id=customer_id,
            subject=subject,
            description=description,
            priority=priority,
            status=TicketStatus.OPEN,
            created_at=datetime.now().isoformat()
        )
        
        self.db.save_ticket(ticket)
        
        # Update customer ticket count
        customer = self.db.get_customer(customer_id)
        if customer:
            customer.ticket_count += 1
            customer.churn_probability = self._calculate_churn_probability(customer)
            self.db.save_customer(customer)
        
        logger.info(f"Ticket created: {ticket.ticket_id}")
        return ticket
    
    def get_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """Get ticket by ID."""
        return self.db.get_ticket(ticket_id)
    
    def update_ticket_status(self, ticket_id: str, status: TicketStatus) -> bool:
        """Update ticket status."""
        ticket = self.db.get_ticket(ticket_id)
        if not ticket:
            return False
        
        ticket.status = status
        ticket.updated_at = datetime.now().isoformat()
        
        if status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now().isoformat()
        
        return self.db.save_ticket(ticket)
    
    def get_customer_tickets(self, customer_id: str) -> List[Dict]:
        """Get tickets for a customer."""
        tickets = self.db.get_tickets_by_customer(customer_id)
        
        return [
            {
                "id": t.ticket_id,
                "subject": t.subject,
                "priority": t.priority.value,
                "status": t.status.value,
                "created_at": t.created_at,
                "resolved_at": t.resolved_at
            }
            for t in tickets
        ]
    
    def record_purchase(
        self,
        customer_id: str,
        product_id: str,
        product_name: str,
        amount: float
    ) -> bool:
        """Record customer purchase."""
        import hashlib
        
        purchase_id = hashlib.md5(
            f"{customer_id}{product_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        
        purchase = PurchaseRecord(
            purchase_id=f"PURCH-{purchase_id}",
            customer_id=customer_id,
            product_id=product_id,
            product_name=product_name,
            amount=amount,
            purchase_date=datetime.now().isoformat()
        )
        
        self.db.save_purchase(purchase)
        
        # Update customer
        customer = self.db.get_customer(customer_id)
        if customer:
            customer.total_purchases += 1
            customer.total_spent += amount
            customer.last_contact = datetime.now().isoformat()
            
            # Upgrade to ACTIVE if first purchase
            if customer.status == CustomerStatus.PROSPECT:
                customer.status = CustomerStatus.ACTIVE
            
            # Recalculate CLV and churn
            customer.clv_score = self._calculate_clv(customer)
            customer.churn_probability = self._calculate_churn_probability(customer)
            
            self.db.save_customer(customer)
        
        return True
    
    def _calculate_clv(self, customer: CustomerProfile) -> float:
        """Calculate Customer Lifetime Value."""
        base_clv = self.AVG_PURCHASE_VALUE * self.PURCHASE_FREQUENCY * self.CUSTOMER_LIFESPAN
        
        # Adjust for actual purchase frequency
        if customer.total_purchases > 0:
            months_active = 1
            if customer.first_contact:
                try:
                    first = datetime.fromisoformat(customer.first_contact)
                    months_active = max(1, (datetime.now() - first).days / 30)
                except:
                    pass
            
            actual_frequency = customer.total_purchases / months_active
            frequency_multiplier = actual_frequency / self.PURCHASE_FREQUENCY
        else:
            frequency_multiplier = 1.0
        
        # Ticket impact
        ticket_impact = 1.0 - (customer.ticket_count * self.TICKET_IMPACT)
        ticket_impact = max(0.5, ticket_impact)  # Min 50%
        
        return base_clv * frequency_multiplier * ticket_impact
    
    def _calculate_churn_probability(self, customer: CustomerProfile) -> float:
        """Calculate churn probability (0.0 - 1.0)."""
        probability = 0.0
        
        # Days since last contact
        if customer.last_contact:
            try:
                last = datetime.fromisoformat(customer.last_contact)
                days_since = (datetime.now() - last).days
                
                # Increase probability for inactive customers
                if days_since > 60:
                    probability += 0.4
                elif days_since > 30:
                    probability += 0.2
                elif days_since > 14:
                    probability += 0.1
            except:
                pass
        
        # High ticket count
        if customer.ticket_count > 5:
            probability += 0.3
        elif customer.ticket_count > 3:
            probability += 0.15
        
        # No purchases despite being active
        if customer.status == CustomerStatus.ACTIVE and customer.total_purchases == 0:
            probability += 0.2
        
        # Low spend relative to CLV
        if customer.clv_score > 0:
            spend_ratio = customer.total_spent / customer.clv_score
            if spend_ratio < 0.3:
                probability += 0.15
        
        return min(1.0, probability)
    
    def get_customer_analytics(self, customer_id: str) -> Dict:
        """Get analytics for a customer."""
        customer = self.db.get_customer(customer_id)
        if not customer:
            return {"error": "Customer not found"}
        
        tickets = self.db.get_tickets_by_customer(customer_id)
        purchases = self.db.get_purchases_by_customer(customer_id)
        
        # Ticket metrics
        open_tickets = sum(1 for t in tickets if t.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
        resolved_tickets = sum(1 for t in tickets if t.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED])
        
        # Purchase metrics
        avg_purchase = customer.total_spent / customer.total_purchases if customer.total_purchases > 0 else 0
        
        # Engagement score
        engagement_score = 100
        if customer.churn_probability > 0.5:
            engagement_score = 50
        elif customer.churn_probability > 0.3:
            engagement_score = 70
        elif customer.churn_probability > 0.1:
            engagement_score = 85
        
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "status": customer.status.value,
            "clv_score": round(customer.clv_score, 2),
            "churn_probability": round(customer.churn_probability * 100, 1),
            "engagement_score": engagement_score,
            "total_purchases": customer.total_purchases,
            "total_spent": customer.total_spent,
            "average_purchase": round(avg_purchase, 2),
            "tickets": {
                "total": customer.ticket_count,
                "open": open_tickets,
                "resolved": resolved_tickets
            },
            "last_contact": customer.last_contact
        }
    
    def get_overall_analytics(self) -> Dict:
        """Get overall customer analytics."""
        customers = self.db.get_all_customers()
        
        total_customers = len(customers)
        active = sum(1 for c in customers if c.status == CustomerStatus.ACTIVE)
        prospects = sum(1 for c in customers if c.status == CustomerStatus.PROSPECT)
        churned = sum(1 for c in customers if c.status == CustomerStatus.CHURNED)
        
        # Calculate average metrics
        avg_clv = sum(c.clv_score for c in customers) / max(total_customers, 1)
        avg_churn = sum(c.churn_probability for c in customers) / max(total_customers, 1)
        total_revenue = sum(c.total_spent for c in customers)
        
        # High-value customers
        high_value = [c for c in customers if c.clv_score > avg_clv * 1.5]
        at_risk = [c for c in customers if c.churn_probability > 0.5]
        
        return {
            "total_customers": total_customers,
            "active": active,
            "prospects": prospects,
            "churned": churned,
            "avg_clv": round(avg_clv, 2),
            "avg_churn_probability": round(avg_churn * 100, 1),
            "total_revenue": total_revenue,
            "high_value_customers": len(high_value),
            "at_risk_customers": len(at_risk),
            "retention_rate": round((active / max(total_customers, 1)) * 100, 1)
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_customer_center: Optional[CustomerCenter] = None


def get_customer_center() -> CustomerCenter:
    """Get or create global customer center."""
    global _customer_center
    if _customer_center is None:
        _customer_center = CustomerCenter()
    return _customer_center
