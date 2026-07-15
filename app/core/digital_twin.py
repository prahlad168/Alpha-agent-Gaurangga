"""
MAHALAKSMI AIOS v1.0 - Volume I Chapter 6: Company Brain & Digital Twin
Digital profile synchronization and corporate memory system
"""
import os
import sys
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class EntityType(Enum):
    """Entity types in company brain."""
    COMPANY = "company"
    SBU = "sbu"  # Strategic Business Unit
    DEPARTMENT = "department"
    AGENT = "agent"
    EMPLOYEE = "employee"
    PRODUCT = "product"
    CUSTOMER = "customer"
    PARTNER = "partner"


@dataclass
class DigitalEntity:
    """Digital twin entity."""
    entity_id: str
    entity_type: EntityType
    name: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


@dataclass
class CompanyProfile:
    """MAHA LAKSHMI CORP company profile."""
    company_id: str = "MAHA-LAKSHMI-CORP"
    company_name: str = "MAHA LAKSHMI CORP"
    founded_date: str = "2024-01-01"
    
    # Contact
    website: str = "https://mahalakshmi.ai"
    email: str = "info@mahalakshmi.ai"
    phone: str = "+62-812-3456-7890"
    
    # Leadership
    founder: str = "I Made Purna Ananda (Pak Pur)"
    founder_whatsapp: str = "081337558787"
    co_workers: List[Dict] = field(default_factory=list)
    
    # Structure
    sbus: List[Dict] = field(default_factory=list)
    departments: List[Dict] = field(default_factory=list)
    
    # Financial targets
    monthly_revenue_target: float = 102000000  # Rp 102M for CEO
    revenue_share_ceo: float = 0.60
    revenue_share_operational: float = 0.40
    
    # Bank info
    bank_accounts: List[Dict] = field(default_factory=list)
    bitcoin_wallet: str = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    
    # Goals
    mission: str = "Dari nol menjadi satu, dari satu menjadi banyak"
    vision: List[str] = field(default_factory=list)
    
    # AI Systems
    ai_agents_count: int = 10
    ai_agents: List[Dict] = field(default_factory=list)
    
    # Metrics
    total_transactions: int = 0
    total_revenue: float = 0
    active_products: int = 0


# ============================================================================
# COMPANY BRAIN DATABASE
# ============================================================================

class CompanyBrainDB:
    """SQLite database for company brain."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "company_brain.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT,
                name TEXT NOT NULL,
                description TEXT,
                metadata TEXT,
                relationships TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                relationship_type TEXT,
                metadata TEXT,
                created_at TEXT,
                FOREIGN KEY (source_id) REFERENCES entities(entity_id),
                FOREIGN KEY (target_id) REFERENCES entities(entity_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_profile (
                id INTEGER PRIMARY KEY,
                profile_data TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                content TEXT,
                tags TEXT,
                source TEXT,
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Company brain database initialized: {self.db_path}")
    
    def save_entity(self, entity: DigitalEntity) -> bool:
        """Save entity to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO entities 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.entity_id,
                entity.entity_type.value,
                entity.name,
                entity.description,
                json.dumps(entity.metadata),
                json.dumps(entity.relationships),
                entity.created_at,
                entity.updated_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save entity: {e}")
            return False
    
    def get_entity(self, entity_id: str) -> Optional[DigitalEntity]:
        """Get entity by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM entities WHERE entity_id = ?", (entity_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_entity(row)
        return None
    
    def _row_to_entity(self, row) -> DigitalEntity:
        """Convert row to DigitalEntity."""
        return DigitalEntity(
            entity_id=row['entity_id'],
            entity_type=EntityType(row['entity_type']),
            name=row['name'],
            description=row['description'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            relationships=json.loads(row['relationships']) if row['relationships'] else [],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def save_company_profile(self, profile: CompanyProfile) -> bool:
        """Save company profile."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO company_profile (id, profile_data, updated_at)
                VALUES (1, ?, ?)
            """, (json.dumps(profile.__dict__), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            return False
    
    def get_company_profile(self) -> CompanyProfile:
        """Get company profile."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT profile_data FROM company_profile WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = json.loads(row['profile_data'])
            return CompanyProfile(**data)
        
        return CompanyProfile()
    
    def add_knowledge(self, topic: str, content: str, tags: List[str] = None, source: str = "system") -> bool:
        """Add knowledge to knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO knowledge_base (topic, content, tags, source, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (topic, content, json.dumps(tags or []), source, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to add knowledge: {e}")
            return False


# ============================================================================
# COMPANY BRAIN (DIGITAL TWIN)
# ============================================================================

class CompanyBrain:
    """
    Company Brain & Digital Twin System.
    Synchronizes and maintains digital profile of MAHA LAKSHMI CORP.
    """
    
    def __init__(self):
        self.db = CompanyBrainDB()
        self._init_default_entities()
        self._init_default_profile()
        
        logger.info("Company Brain initialized")
    
    def _init_default_entities(self):
        """Initialize default company entities."""
        # Main company
        company = DigitalEntity(
            entity_id="MAHA-LAKSHMI-CORP",
            entity_type=EntityType.COMPANY,
            name="MAHA LAKSHMI CORP",
            description="Multi-SBU Corporation based in Indonesia",
            metadata={
                "industry": "Technology & Services",
                "founded": "2024",
                "employees_target": 10,
                "ai_agents_target": 75
            }
        )
        self.db.save_entity(company)
        
        # Founder
        founder = DigitalEntity(
            entity_id="PAK-PUR",
            entity_type=EntityType.EMPLOYEE,
            name="I Made Purna Ananda",
            description="Founder & CEO",
            metadata={
                "role": "CEO",
                "phone": "081337558787",
                "bank_account": "BCA 6485086645",
                "bitcoin_wallet": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
            },
            relationships=[{"type": "founded", "target": "MAHA-LAKSHMI-CORP"}]
        )
        self.db.save_entity(founder)
        
        # SBUs
        sbus = [
            {"id": "SBU-HOSPITAL", "name": "Hospital Management", "target": 50000000},
            {"id": "SBU-ECOMMERCE", "name": "E-Commerce", "target": 30000000},
            {"id": "SBU-EDUCATION", "name": "Education Tech", "target": 25000000},
            {"id": "SBU-TRAVEL", "name": "Travel Tech", "target": 20000000},
            {"id": "SBU-PROPERTY", "name": "Property Tech", "target": 25000000},
            {"id": "SBU-FOOD", "name": "Food Tech", "target": 20000000},
        ]
        
        for sbu in sbus:
            entity = DigitalEntity(
                entity_id=sbu["id"],
                entity_type=EntityType.SBU,
                name=sbu["name"],
                description=f"Strategic Business Unit: {sbu['name']}",
                metadata={"monthly_target": sbu["target"]},
                relationships=[{"type": "part_of", "target": "MAHA-LAKSHMI-CORP"}]
            )
            self.db.save_entity(entity)
        
        logger.info(f"Initialized {len(sbus)} SBU entities")
    
    def _init_default_profile(self):
        """Initialize default company profile."""
        profile = CompanyProfile()
        profile.sbus = [
            {"name": "Hospital Management", "target": 50000000, "ceo_share": 30000000},
            {"name": "E-Commerce", "target": 30000000, "ceo_share": 18000000},
            {"name": "Education Tech", "target": 25000000, "ceo_share": 15000000},
            {"name": "Travel Tech", "target": 20000000, "ceo_share": 12000000},
            {"name": "Property Tech", "target": 25000000, "ceo_share": 15000000},
            {"name": "Food Tech", "target": 20000000, "ceo_share": 12000000},
        ]
        profile.vision = [
            "Build 75+ AI agents for enterprise automation",
            "Achieve Rp 100M monthly revenue in 6 months",
            "Enable Bitcoin-based revenue sharing",
            "Scale to 10 strategic business units"
        ]
        profile.bank_accounts = [
            {"bank": "BCA", "account": "6485086645", "holder": "Owner/Shareholder"},
            {"type": "Bitcoin", "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", "preferred": True}
        ]
        self.db.save_company_profile(profile)
    
    def get_profile(self) -> CompanyProfile:
        """Get company profile."""
        return self.db.get_company_profile()
    
    def get_entity(self, entity_id: str) -> Optional[DigitalEntity]:
        """Get entity by ID."""
        return self.db.get_entity(entity_id)
    
    def list_entities(self, entity_type: EntityType = None) -> List[DigitalEntity]:
        """List all entities."""
        # For simplicity, return all from database
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if entity_type:
            cursor.execute("SELECT * FROM entities WHERE entity_type = ?", (entity_type.value,))
        else:
            cursor.execute("SELECT * FROM entities")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self.db._row_to_entity(row) for row in rows]
    
    def sync_revenue(self, source: str, amount: float) -> bool:
        """Sync revenue data to company brain."""
        profile = self.get_profile()
        profile.total_revenue += amount
        profile.total_transactions += 1
        return self.db.save_company_profile(profile)
    
    def add_product(self, product_id: str, name: str, price: float) -> bool:
        """Add product to company brain."""
        entity = DigitalEntity(
            entity_id=product_id,
            entity_type=EntityType.PRODUCT,
            name=name,
            metadata={"price": price},
            relationships=[{"type": "belongs_to", "target": "MAHA-LAKSHMI-CORP"}]
        )
        return self.db.save_entity(entity)
    
    def get_kpis(self) -> Dict[str, Any]:
        """Get company KPIs."""
        profile = self.get_profile()
        
        return {
            "company": {
                "name": profile.company_name,
                "founded": profile.founded_date,
                "founder": profile.founder
            },
            "financial": {
                "total_revenue": profile.total_revenue,
                "monthly_target": profile.monthly_revenue_target,
                "target_achieved": (profile.total_revenue / profile.monthly_revenue_target) * 100,
                "ceo_share_pct": profile.revenue_share_ceo * 100,
                "operational_share_pct": profile.revenue_share_operational * 100
            },
            "structure": {
                "sbus_count": len(profile.sbus),
                "departments_count": len(profile.departments),
                "ai_agents_count": profile.ai_agents_count
            },
            "products": {
                "active": profile.active_products
            },
            "transactions": {
                "total": profile.total_transactions
            }
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_company_brain: Optional[CompanyBrain] = None


def get_company_brain() -> CompanyBrain:
    """Get or create global company brain instance."""
    global _company_brain
    if _company_brain is None:
        _company_brain = CompanyBrain()
    return _company_brain
