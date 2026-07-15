"""
MAHALAKSMI AIOS v2.0 - Volume IV: Business Operations Suite
Chapter 33: Asset Manager | Chapter 34: Legal Engine | Chapter 35: HR Manager | Chapter 36: Supply Chain
"""
import os
import sys
import sqlite3
import json
import uuid
import hashlib
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

class AssetType(Enum):
    SOFTWARE_LICENSE = "software_license"
    HARDWARE = "hardware"
    EQUIPMENT = "equipment"
    VEHICLE = "vehicle"
    FURNITURE = "furniture"


class LeaveType(Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    PNS_CUTI = "pns_cuti"  # Indonesian Civil Servant Leave


class LeaveStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ProcurementStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class VendorStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"


@dataclass
class Asset:
    """Asset record."""
    asset_id: str
    name: str
    asset_type: AssetType
    purchase_date: str
    purchase_cost: float
    current_value: float
    depreciation_rate: float
    useful_life_years: int
    location: str
    assigned_to: str = ""
    status: str = "active"
    notes: str = ""


@dataclass
class Employee:
    """Employee record."""
    employee_id: str
    name: str
    email: str
    phone: str
    department: str
    position: str
    hire_date: str
    status: str = "active"
    salary: float = 0


@dataclass
class LeaveRequest:
    """Leave request."""
    request_id: str
    employee_id: str
    leave_type: LeaveType
    start_date: str
    end_date: str
    reason: str
    status: LeaveStatus
    approved_by: str = ""
    approved_at: str = ""


@dataclass
class Vendor:
    """Vendor record."""
    vendor_id: str
    name: str
    contact_person: str
    email: str
    phone: str
    address: str
    category: str
    status: VendorStatus


@dataclass
class ProcurementOrder:
    """Procurement order."""
    order_id: str
    vendor_id: str
    items: List[Dict]
    total_amount: float
    status: ProcurementStatus
    requested_by: str
    requested_at: str


# ============================================================================
# DATABASE
# ============================================================================

class OperationsDB:
    """Database for business operations."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "operations.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Assets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                asset_type TEXT,
                purchase_date TEXT,
                purchase_cost REAL,
                current_value REAL,
                depreciation_rate REAL,
                useful_life_years INTEGER,
                location TEXT,
                assigned_to TEXT,
                status TEXT,
                notes TEXT
            )
        """)
        
        # Employees
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                department TEXT,
                position TEXT,
                hire_date TEXT,
                status TEXT,
                salary REAL
            )
        """)
        
        # Leave requests
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_requests (
                request_id TEXT PRIMARY KEY,
                employee_id TEXT,
                leave_type TEXT,
                start_date TEXT,
                end_date TEXT,
                reason TEXT,
                status TEXT,
                approved_by TEXT,
                approved_at TEXT
            )
        """)
        
        # Vendors
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                vendor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                category TEXT,
                status TEXT
            )
        """)
        
        # Procurement orders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS procurement_orders (
                order_id TEXT PRIMARY KEY,
                vendor_id TEXT,
                items TEXT,
                total_amount REAL,
                status TEXT,
                requested_by TEXT,
                requested_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()


# ============================================================================
# ASSET MANAGER (Chapter 33)
# ============================================================================

class AssetManager:
    """
    Asset tracking system.
    Manages software licenses, hardware, and depreciation schedules.
    """
    
    def __init__(self):
        self.db = OperationsDB()
        logger.info("AssetManager initialized")
    
    def add_asset(self, asset: Asset) -> bool:
        """Add new asset."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO assets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset.asset_id, asset.name, asset.asset_type.value,
            asset.purchase_date, asset.purchase_cost, asset.current_value,
            asset.depreciation_rate, asset.useful_life_years,
            asset.location, asset.assigned_to, asset.status, asset.notes
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Asset added: {asset.name}")
        return True
    
    def calculate_depreciation(self, asset_id: str) -> Dict:
        """Calculate current depreciation value."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM assets WHERE asset_id = ?", (asset_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"error": "Asset not found"}
        
        purchase_date = datetime.fromisoformat(row["purchase_date"])
        years_owned = (datetime.now() - purchase_date).days / 365.25
        
        # Straight-line depreciation
        annual_depreciation = row["purchase_cost"] * (row["depreciation_rate"] / 100)
        total_depreciation = annual_depreciation * years_owned
        current_value = max(0, row["purchase_cost"] - total_depreciation)
        
        return {
            "asset_id": row["asset_id"],
            "name": row["name"],
            "purchase_cost": row["purchase_cost"],
            "current_value": current_value,
            "total_depreciation": total_depreciation,
            "years_owned": round(years_owned, 2),
            "remaining_life": max(0, row["useful_life_years"] - years_owned)
        }
    
    def get_assets(
        self,
        asset_type: AssetType = None,
        status: str = None
    ) -> List[Dict]:
        """Get assets with filters."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM assets WHERE 1=1"
        params = []
        
        if asset_type:
            query += " AND asset_type = ?"
            params.append(asset_type.value)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_licenses(self) -> List[Dict]:
        """Get all software licenses."""
        return self.get_assets(AssetType.SOFTWARE_LICENSE)
    
    def assign_asset(self, asset_id: str, employee_id: str) -> bool:
        """Assign asset to employee."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE assets SET assigned_to = ? WHERE asset_id = ?",
            (employee_id, asset_id)
        )
        
        conn.commit()
        conn.close()
        
        return True


# ============================================================================
# LEGAL ENGINE (Chapter 34)
# ============================================================================

class LegalEngine:
    """
    Legal document generator.
    Auto-generates contracts and NDA templates.
    """
    
    def __init__(self):
        logger.info("LegalEngine initialized")
    
    def generate_contract(
        self,
        contract_type: str,
        party_a: Dict,
        party_b: Dict,
        terms: List[str],
        effective_date: str = None
    ) -> Dict:
        """Generate business contract."""
        if effective_date is None:
            effective_date = datetime.now().strftime("%Y-%m-%d")
        
        contract_id = f"CONTRACT-{uuid.uuid4().hex[:8].upper()}"
        
        contract_body = f"""
        BUSINESS AGREEMENT
        
        Contract ID: {contract_id}
        Effective Date: {effective_date}
        
        PARTY A:
        Name: {party_a.get('name', '')}
        Address: {party_a.get('address', '')}
        Representative: {party_a.get('representative', '')}
        
        PARTY B:
        Name: {party_b.get('name', '')}
        Address: {party_b.get('address', '')}
        Representative: {party_b.get('representative', '')}
        
        TERMS AND CONDITIONS:
        """
        
        for i, term in enumerate(terms, 1):
            contract_body += f"\n{i}. {term}"
        
        contract_body += f"""
        
        SIGNATURES:
        
        Party A: ____________________    Date: ________
        
        Party B: ____________________    Date: ________
        """
        
        return {
            "contract_id": contract_id,
            "type": contract_type,
            "effective_date": effective_date,
            "party_a": party_a,
            "party_b": party_b,
            "body": contract_body.strip(),
            "status": "draft"
        }
    
    def generate_nda(
        self,
        disclosing_party: str,
        receiving_party: str,
        purpose: str,
        duration_months: int = 24
    ) -> Dict:
        """Generate NDA template."""
        nda_id = f"NDA-{uuid.uuid4().hex[:8].upper()}"
        effective_date = datetime.now().strftime("%Y-%m-%d")
        expiry_date = (datetime.now() + timedelta(days=duration_months * 30)).strftime("%Y-%m-%d")
        
        nda_body = f"""
        NON-DISCLOSURE AGREEMENT
        
        NDA ID: {nda_id}
        Effective Date: {effective_date}
        Expiry Date: {expiry_date}
        
        DISCLOSING PARTY: {disclosing_party}
        RECEIVING PARTY: {receiving_party}
        
        PURPOSE:
        {purpose}
        
        CONFIDENTIAL INFORMATION:
        All information, materials, and data disclosed by either party
        shall be considered confidential and proprietary.
        
        OBLIGATIONS:
        1. The Receiving Party shall maintain the confidentiality of all
           information received.
        2. The Receiving Party shall not disclose, copy, or distribute
           any confidential information without prior written consent.
        3. This agreement shall remain in effect for {duration_months} months
           from the effective date.
        
        SIGNATURES:
        
        For Disclosing Party: ____________________    Date: ________
        
        For Receiving Party: ____________________    Date: ________
        """
        
        return {
            "nda_id": nda_id,
            "effective_date": effective_date,
            "expiry_date": expiry_date,
            "disclosing_party": disclosing_party,
            "receiving_party": receiving_party,
            "purpose": purpose,
            "body": nda_body.strip(),
            "status": "draft"
        }


# ============================================================================
# HR MANAGER (Chapter 35)
# ============================================================================

class HRManager:
    """
    Human Resources management.
    Employee directory, leave requests, performance metrics.
    """
    
    def __init__(self):
        self.db = OperationsDB()
        logger.info("HRManager initialized")
    
    def add_employee(self, employee: Employee) -> bool:
        """Add new employee."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee.employee_id, employee.name, employee.email,
            employee.phone, employee.department, employee.position,
            employee.hire_date, employee.status, employee.salary
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Employee added: {employee.name}")
        return True
    
    def request_leave(
        self,
        employee_id: str,
        leave_type: LeaveType,
        start_date: str,
        end_date: str,
        reason: str
    ) -> LeaveRequest:
        """Submit leave request."""
        request_id = f"LEAVE-{uuid.uuid4().hex[:8].upper()}"
        
        leave_request = LeaveRequest(
            request_id=request_id,
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status=LeaveStatus.PENDING
        )
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO leave_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            leave_request.request_id, leave_request.employee_id,
            leave_request.leave_type.value, leave_request.start_date,
            leave_request.end_date, leave_request.reason,
            leave_request.status.value, leave_request.approved_by,
            leave_request.approved_at
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Leave request created: {request_id}")
        return leave_request
    
    def approve_leave(self, request_id: str, approved_by: str) -> bool:
        """Approve leave request."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE leave_requests SET status = ?, approved_by = ?, approved_at = ? WHERE request_id = ?",
            (LeaveStatus.APPROVED.value, approved_by, datetime.now().isoformat(), request_id)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Leave approved: {request_id}")
        return True
    
    def get_employees(self, department: str = None) -> List[Dict]:
        """Get employee list."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if department:
            cursor.execute("SELECT * FROM employees WHERE department = ?", (department,))
        else:
            cursor.execute("SELECT * FROM employees")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_leave_requests(
        self,
        employee_id: str = None,
        status: LeaveStatus = None
    ) -> List[Dict]:
        """Get leave requests."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM leave_requests WHERE 1=1"
        params = []
        
        if employee_id:
            query += " AND employee_id = ?"
            params.append(employee_id)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def calculate_leave_balance(self, employee_id: str) -> Dict:
        """Calculate leave balance for employee."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get employee hire date
        cursor.execute("SELECT hire_date FROM employees WHERE employee_id = ?", (employee_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"error": "Employee not found"}
        
        hire_date = datetime.fromisoformat(row[0])
        years_employed = (datetime.now() - hire_date).days / 365.25
        
        # Calculate entitlements (Indonesian standard)
        annual_leave = min(12, int(years_employed))  # Max 12 days
        sick_leave = 14  # Indonesian standard
        
        # Get used leaves
        cursor.execute(
            "SELECT COUNT(*) FROM leave_requests WHERE employee_id = ? AND status = 'approved'",
            (employee_id,)
        )
        used_leaves = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "employee_id": employee_id,
            "annual_entitled": annual_leave,
            "annual_used": used_leaves,
            "annual_remaining": max(0, annual_leave - used_leaves),
            "sick_entitled": sick_leave,
            "sick_used": 0,
            "sick_remaining": sick_leave
        }


# ============================================================================
# SUPPLY CHAIN ORCHESTRATOR (Chapter 36)
# ============================================================================

class SupplyChainOrchestrator:
    """
    Supply chain management.
    Vendor directory, procurement, and auto-restocking.
    """
    
    def __init__(self):
        self.db = OperationsDB()
        self.restock_thresholds: Dict[str, float] = {}
        logger.info("SupplyChainOrchestrator initialized")
    
    def add_vendor(self, vendor: Vendor) -> bool:
        """Add new vendor."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO vendors VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vendor.vendor_id, vendor.name, vendor.contact_person,
            vendor.email, vendor.phone, vendor.address,
            vendor.category, vendor.status.value
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Vendor added: {vendor.name}")
        return True
    
    def create_procurement(
        self,
        vendor_id: str,
        items: List[Dict],
        requested_by: str
    ) -> ProcurementOrder:
        """Create procurement order."""
        order_id = f"PO-{uuid.uuid4().hex[:8].upper()}"
        
        total_amount = sum(item.get("quantity", 0) * item.get("unit_price", 0) for item in items)
        
        order = ProcurementOrder(
            order_id=order_id,
            vendor_id=vendor_id,
            items=items,
            total_amount=total_amount,
            status=ProcurementStatus.DRAFT,
            requested_by=requested_by,
            requested_at=datetime.now().isoformat()
        )
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO procurement_orders VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order.order_id, order.vendor_id, json.dumps(order.items),
            order.total_amount, order.status.value,
            order.requested_by, order.requested_at
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Procurement order created: {order_id}")
        return order
    
    def approve_procurement(self, order_id: str) -> bool:
        """Approve procurement order."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE procurement_orders SET status = ? WHERE order_id = ?",
            (ProcurementStatus.APPROVED.value, order_id)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Procurement approved: {order_id}")
        return True
    
    def set_restock_threshold(self, product_id: str, threshold: float):
        """Set auto-restock threshold."""
        self.restock_thresholds[product_id] = threshold
        logger.info(f"Restock threshold set for {product_id}: {threshold}")
    
    def check_restock(self, product_id: str, current_stock: float) -> Dict:
        """Check if product needs restocking."""
        threshold = self.restock_thresholds.get(product_id, 10)
        
        if current_stock < threshold:
            return {
                "product_id": product_id,
                "current_stock": current_stock,
                "threshold": threshold,
                "needs_restock": True,
                "recommended_order": threshold * 2 - current_stock
            }
        
        return {
            "product_id": product_id,
            "current_stock": current_stock,
            "threshold": threshold,
            "needs_restock": False
        }
    
    def get_vendors(self, status: VendorStatus = None) -> List[Dict]:
        """Get vendor list."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM vendors WHERE status = ?", (status.value,))
        else:
            cursor.execute("SELECT * FROM vendors")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_procurement_orders(
        self,
        vendor_id: str = None,
        status: ProcurementStatus = None
    ) -> List[Dict]:
        """Get procurement orders."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM procurement_orders WHERE 1=1"
        params = []
        
        if vendor_id:
            query += " AND vendor_id = ?"
            params.append(vendor_id)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                **dict(row),
                "items": json.loads(row["items"]) if row["items"] else []
            }
            for row in rows
        ]


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

_asset_manager: Optional[AssetManager] = None
_legal_engine: Optional[LegalEngine] = None
_hr_manager: Optional[HRManager] = None
_supply_chain: Optional[SupplyChainOrchestrator] = None


def get_asset_manager() -> AssetManager:
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AssetManager()
    return _asset_manager


def get_legal_engine() -> LegalEngine:
    global _legal_engine
    if _legal_engine is None:
        _legal_engine = LegalEngine()
    return _legal_engine


def get_hr_manager() -> HRManager:
    global _hr_manager
    if _hr_manager is None:
        _hr_manager = HRManager()
    return _hr_manager


def get_supply_chain() -> SupplyChainOrchestrator:
    global _supply_chain
    if _supply_chain is None:
        _supply_chain = SupplyChainOrchestrator()
    return _supply_chain
