"""
MAHALAKSMI AIOS v2.0 - Volume V: Enterprise Architecture Suite
Chapter 42: ERP Sync | Chapter 43: Business Intelligence
Chapter 44: Audit Trail | Chapter 46: Security Shield
Chapter 47: Multi-Tenant Router | Chapter 48: High-Performance Cache
"""
import os
import sys
import sqlite3
import json
import uuid
import hashlib
import re
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class TenantType(Enum):
    SBU_FINANCE = "sbu_finance"
    SBU_IT = "sbu_it"
    SBU_OPERATIONS = "sbu_operations"
    SBU_HOSPITAL = "sbu_hospital"
    SBU_ECOMMERCE = "sbu_ecommerce"


class AuditAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    TRANSFER = "transfer"
    PAYMENT = "payment"


@dataclass
class AuditEntry:
    """Audit log entry."""
    entry_id: str
    timestamp: str
    user_id: str
    action: AuditAction
    resource: str
    resource_id: str
    ip_address: str
    user_agent: str
    details: Dict
    hash: str


@dataclass
class Tenant:
    """Multi-tenant workspace."""
    tenant_id: str
    name: str
    tenant_type: TenantType
    db_schema: str
    api_key: str
    status: str = "active"
    created_at: str = ""


# ============================================================================
# ERP SYNC ENGINE (Chapter 42)
# ============================================================================

class ERPSyncEngine:
    """
    Unified data model consolidating:
    - Ledger/Finance
    - Human Resources
    - Procurement
    """
    
    def __init__(self):
        self.sync_status = "idle"
        self.last_sync = None
        logger.info("ERPSyncEngine initialized")
    
    def sync_finance_to_hr(self, finance_data: Dict) -> Dict:
        """Sync financial data to HR for payroll."""
        # Convert revenue to payroll allocation
        total_revenue = finance_data.get("total_revenue", 0)
        payroll_budget = total_revenue * 0.15  # 15% for payroll
        
        return {
            "payroll_budget": payroll_budget,
            "employee_count": finance_data.get("employee_count", 0),
            "avg_salary": payroll_budget / max(1, finance_data.get("employee_count", 1)),
            "synced_at": datetime.now().isoformat()
        }
    
    def sync_hr_to_procurement(self, hr_data: Dict) -> Dict:
        """Sync HR data to procurement for equipment."""
        # Equipment budget based on headcount
        employee_count = hr_data.get("employee_count", 0)
        equipment_budget = employee_count * 5000000  # 5M per employee
        
        return {
            "equipment_budget": equipment_budget,
            "employee_count": employee_count,
            "departments": hr_data.get("departments", []),
            "synced_at": datetime.now().isoformat()
        }
    
    def get_unified_dashboard(self) -> Dict:
        """Get unified ERP dashboard data."""
        from app.business.revenue import get_revenue_manager
        from app.business.operations import get_hr_manager
        
        revenue = get_revenue_manager()
        hr = get_hr_manager()
        
        revenue_summary = revenue.get_summary()
        employees = hr.get_employees()
        
        return {
            "finance": {
                "total_revenue": revenue_summary.get("total_revenue", 0),
                "ceo_share": revenue_summary.get("allocation", {}).get("ceo_share", 0),
                "operational": revenue_summary.get("allocation", {}).get("operational_share", 0)
            },
            "hr": {
                "total_employees": len(employees),
                "active": sum(1 for e in employees if e.get("status") == "active")
            },
            "sync_status": self.sync_status,
            "last_sync": self.last_sync,
            "generated_at": datetime.now().isoformat()
        }
    
    def trigger_sync(self, data_type: str) -> Dict:
        """Trigger data synchronization."""
        self.sync_status = "syncing"
        
        # Simulate sync
        time.sleep(0.1)
        
        self.sync_status = "idle"
        self.last_sync = datetime.now().isoformat()
        
        return {
            "status": "completed",
            "data_type": data_type,
            "synced_at": self.last_sync
        }


# ============================================================================
# BUSINESS INTELLIGENCE (Chapter 43)
# ============================================================================

class BusinessIntelligence:
    """
    Real-time analytics engine.
    Sales velocity, revenue forecasting, trend analysis.
    """
    
    def __init__(self):
        self.forecasting_model = "linear_regression"
        logger.info("BusinessIntelligence initialized")
    
    def calculate_sales_velocity(self, transactions: List[Dict], period_days: int = 30) -> Dict:
        """Calculate sales velocity."""
        if not transactions:
            return {"velocity": 0, "trend": "no_data"}
        
        total_sales = sum(t.get("amount", 0) for t in transactions)
        velocity = total_sales / period_days
        
        # Calculate trend
        mid_point = len(transactions) // 2
        recent_avg = sum(t.get("amount", 0) for t in transactions[-mid_point:]) / max(1, mid_point)
        older_avg = sum(t.get("amount", 0) for t in transactions[:mid_point]) / max(1, mid_point)
        
        trend = "stable"
        if recent_avg > older_avg * 1.1:
            trend = "increasing"
        elif recent_avg < older_avg * 0.9:
            trend = "decreasing"
        
        return {
            "velocity": velocity,
            "total_sales": total_sales,
            "period_days": period_days,
            "transaction_count": len(transactions),
            "trend": trend
        }
    
    def forecast_revenue(self, historical_data: List[Dict], forecast_days: int = 30) -> Dict:
        """Simple revenue forecasting."""
        if len(historical_data) < 7:
            return {"forecast": 0, "confidence": 0, "note": "insufficient_data"}
        
        # Calculate average
        avg_daily = sum(d.get("amount", 0) for d in historical_data) / len(historical_data)
        
        # Simple linear forecast
        forecast = avg_daily * forecast_days
        
        # Calculate variance for confidence
        variance = sum((d.get("amount", 0) - avg_daily) ** 2 for d in historical_data) / len(historical_data)
        std_dev = variance ** 0.5
        
        # Confidence decreases with variance
        confidence = max(0, min(100, 100 - (std_dev / avg_daily * 100))) if avg_daily > 0 else 0
        
        return {
            "forecast": forecast,
            "forecast_days": forecast_days,
            "avg_daily": avg_daily,
            "confidence": confidence,
            "model": self.forecasting_model
        }
    
    def analyze_trends(self, data: List[Dict], metric: str = "amount") -> Dict:
        """Analyze trends in data."""
        if len(data) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate moving average
        window_size = min(7, len(data) // 2)
        
        values = [d.get(metric, 0) for d in data]
        
        # Calculate growth rate
        growth_rate = ((values[-1] - values[0]) / max(1, values[0])) * 100 if values[0] > 0 else 0
        
        # Determine trend
        trend = "stable"
        if growth_rate > 10:
            trend = "growth"
        elif growth_rate < -10:
            trend = "decline"
        
        return {
            "metric": metric,
            "current_value": values[-1],
            "initial_value": values[0],
            "growth_rate": growth_rate,
            "trend": trend,
            "data_points": len(data)
        }
    
    def generate_insights(self, data: Dict) -> List[str]:
        """Generate business insights."""
        insights = []
        
        # Revenue insights
        if "revenue" in data:
            rev = data["revenue"]
            if rev > 100000000:
                insights.append("Revenue exceeded Rp 100M threshold - consider expansion")
            if rev < 50000000:
                insights.append("Revenue below Rp 50M - review pricing strategy")
        
        # Customer insights
        if "customers" in data:
            cust = data["customers"]
            if cust.get("at_risk", 0) > cust.get("active", 0) * 0.2:
                insights.append("High customer attrition risk - prioritize retention")
        
        return insights


# ============================================================================
# AUDIT TRAIL ENGINE (Chapter 44)
# ============================================================================

class AuditTrailEngine:
    """
    Immutable audit logging.
    Hash verification prevents tampering.
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "audit.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
        logger.info("AuditTrailEngine initialized")
    
    def _init_db(self):
        """Initialize audit database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                entry_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                resource_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                details TEXT,
                hash TEXT NOT NULL,
                previous_hash TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)
        """)
        
        conn.commit()
        conn.close()
    
    def _generate_hash(self, entry_data: Dict, previous_hash: str = "") -> str:
        """Generate SHA256 hash for entry."""
        data_str = json.dumps(entry_data, sort_keys=True)
        return hashlib.sha256(f"{previous_hash}{data_str}".encode()).hexdigest()
    
    def log(
        self,
        user_id: str,
        action: AuditAction,
        resource: str,
        resource_id: str = "",
        ip_address: str = "",
        user_agent: str = "",
        details: Dict = None
    ) -> AuditEntry:
        """Create immutable audit entry."""
        # Get previous hash
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM audit_logs ORDER BY rowid DESC LIMIT 1")
        row = cursor.fetchone()
        previous_hash = row[0] if row else "genesis"
        conn.close()
        
        entry_id = f"AUDIT-{uuid.uuid4().hex[:12].upper()}"
        timestamp = datetime.now().isoformat()
        
        entry_data = {
            "entry_id": entry_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "action": action.value,
            "resource": resource,
            "resource_id": resource_id,
            "details": details or {}
        }
        
        hash_value = self._generate_hash(entry_data, previous_hash)
        
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            hash=hash_value
        )
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.entry_id, entry.timestamp, entry.user_id,
            entry.action.value, entry.resource, entry.resource_id,
            entry.ip_address, entry.user_agent,
            json.dumps(entry.details), entry.hash, previous_hash
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Audit logged: {entry_id} - {action.value} on {resource}")
        return entry
    
    def verify_chain_integrity(self, limit: int = 100) -> Dict:
        """Verify audit chain integrity."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_logs ORDER BY rowid DESC LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"valid": True, "entries_checked": 0}
        
        # Verify in reverse order (newest first)
        previous_hash = rows[0]["hash"] if rows else "genesis"
        valid = True
        
        for i, row in enumerate(rows):
            # Regenerate hash
            entry_data = {
                "entry_id": row["entry_id"],
                "timestamp": row["timestamp"],
                "user_id": row["user_id"],
                "action": row["action"],
                "resource": row["resource"],
                "resource_id": row["resource_id"],
                "details": json.loads(row["details"]) if row["details"] else {}
            }
            
            expected_hash = self._generate_hash(entry_data, row["previous_hash"])
            
            if row["hash"] != expected_hash:
                valid = False
                break
            
            previous_hash = row["previous_hash"]
        
        return {
            "valid": valid,
            "entries_checked": len(rows),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_logs(
        self,
        user_id: str = None,
        action: AuditAction = None,
        since: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Retrieve audit logs."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if action:
            query += " AND action = ?"
            params.append(action.value)
        
        if since:
            query += " AND timestamp >= ?"
            params.append(since)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# ============================================================================
# SECURITY SHIELD (Chapter 46)
# ============================================================================

class SecurityShield:
    """
    Security middleware.
    IP rate-limiting, SQL injection detection, JWT defense.
    """
    
    def __init__(self):
        self.rate_limit_storage: Dict[str, List[float]] = {}
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max = 100  # requests per window
        self.blocked_ips: Dict[str, datetime] = {}
        
        self.sql_injection_patterns = [
            r"(\bOR\b|\bAND\b).*=.*",  # OR 1=1
            r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)",
            r"(--|;|/\*|\*/)",
            r"(\bDROP\b|\bEXEC\b|\bEXECUTE\b)",
        ]
        
        logger.info("SecurityShield initialized")
    
    def check_rate_limit(self, ip_address: str) -> Dict:
        """Check if IP is rate limited."""
        now = time.time()
        
        # Clean old entries
        if ip_address in self.rate_limit_storage:
            self.rate_limit_storage[ip_address] = [
                t for t in self.rate_limit_storage[ip_address]
                if now - t < self.rate_limit_window
            ]
        else:
            self.rate_limit_storage[ip_address] = []
        
        # Check limit
        request_count = len(self.rate_limit_storage[ip_address])
        
        if request_count >= self.rate_limit_max:
            self.blocked_ips[ip_address] = datetime.now()
            return {
                "allowed": False,
                "reason": "rate_limit_exceeded",
                "requests": request_count,
                "blocked_until": datetime.now() + timedelta(seconds=self.rate_limit_window)
            }
        
        # Record request
        self.rate_limit_storage[ip_address].append(now)
        
        return {
            "allowed": True,
            "requests": request_count + 1,
            "remaining": self.rate_limit_max - request_count - 1
        }
    
    def detect_sql_injection(self, input_string: str) -> bool:
        """Detect SQL injection attempts."""
        input_lower = input_string.lower()
        
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                logger.warning(f"SQL injection detected: {pattern}")
                return True
        
        return False
    
    def sanitize_input(self, input_string: str) -> str:
        """Sanitize input to prevent injection."""
        # Remove common injection characters
        sanitized = re.sub(r"['\";\\]", "", input_string)
        return sanitized
    
    def validate_jwt_payload(self, payload: Dict) -> Dict:
        """Validate JWT payload structure."""
        issues = []
        
        # Check required claims
        required_claims = ["sub", "exp", "iat"]
        for claim in required_claims:
            if claim not in payload:
                issues.append(f"Missing required claim: {claim}")
        
        # Check expiration
        if "exp" in payload:
            exp = payload["exp"]
            if isinstance(exp, int) and exp < time.time():
                issues.append("Token expired")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def block_ip(self, ip_address: str, reason: str, duration_minutes: int = 30):
        """Block an IP address."""
        self.blocked_ips[ip_address] = datetime.now() + timedelta(minutes=duration_minutes)
        logger.warning(f"IP blocked: {ip_address} - {reason}")
    
    def is_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked."""
        if ip_address in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip_address]:
                return True
            else:
                del self.blocked_ips[ip_address]
        return False


# ============================================================================
# MULTI-TENANT ROUTER (Chapter 47)
# ============================================================================

class MultiTenantRouter:
    """
    Multi-tenant workspace isolation.
    SBU-based database schema separation.
    """
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self._init_default_tenants()
        logger.info("MultiTenantRouter initialized")
    
    def _init_default_tenants(self):
        """Initialize default SBU tenants."""
        default_tenants = [
            Tenant(
                tenant_id="SBU-FINANCE-001",
                name="SBU Finance",
                tenant_type=TenantType.SBU_FINANCE,
                db_schema="sbu_finance",
                api_key=hashlib.sha256("finance-key".encode()).hexdigest()[:32],
                status="active",
                created_at=datetime.now().isoformat()
            ),
            Tenant(
                tenant_id="SBU-IT-001",
                name="SBU IT",
                tenant_type=TenantType.SBU_IT,
                db_schema="sbu_it",
                api_key=hashlib.sha256("it-key".encode()).hexdigest()[:32],
                status="active",
                created_at=datetime.now().isoformat()
            ),
            Tenant(
                tenant_id="SBU-OPS-001",
                name="SBU Operations",
                tenant_type=TenantType.SBU_OPERATIONS,
                db_schema="sbu_operations",
                api_key=hashlib.sha256("ops-key".encode()).hexdigest()[:32],
                status="active",
                created_at=datetime.now().isoformat()
            ),
        ]
        
        for tenant in default_tenants:
            self.tenants[tenant.tenant_id] = tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_api_key(self, api_key: str) -> Optional[Tenant]:
        """Get tenant by API key."""
        for tenant in self.tenants.values():
            if tenant.api_key == api_key:
                return tenant
        return None
    
    def create_tenant(
        self,
        name: str,
        tenant_type: TenantType
    ) -> Tenant:
        """Create new tenant."""
        tenant_id = f"SBU-{tenant_type.name}-{uuid.uuid4().hex[:6].upper()}"
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            tenant_type=tenant_type,
            db_schema=f"sbu_{tenant_type.value}",
            api_key=hashlib.sha256(tenant_id.encode()).hexdigest()[:32],
            status="active",
            created_at=datetime.now().isoformat()
        )
        
        self.tenants[tenant_id] = tenant
        
        logger.info(f"Tenant created: {tenant_id}")
        return tenant
    
    def isolate_data(self, tenant_id: str, data: Any) -> Dict:
        """Isolate data for tenant."""
        tenant = self.get_tenant(tenant_id)
        
        if not tenant:
            return {"error": "Tenant not found"}
        
        return {
            "tenant_id": tenant.tenant_id,
            "tenant_name": tenant.name,
            "schema": tenant.db_schema,
            "data": data,
            "isolated_at": datetime.now().isoformat()
        }
    
    def get_all_tenants(self) -> List[Dict]:
        """Get all tenants."""
        return [
            {
                "tenant_id": t.tenant_id,
                "name": t.name,
                "type": t.tenant_type.value,
                "schema": t.db_schema,
                "status": t.status
            }
            for t in self.tenants.values()
        ]


# ============================================================================
# HIGH-PERFORMANCE CACHE (Chapter 48)
# ============================================================================

class HighPerformanceCache:
    """
    In-memory cache for fast configuration lookups.
    LRU eviction policy.
    """
    
    def __init__(self, max_size: int = 1000):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        logger.info(f"HighPerformanceCache initialized (max_size={max_size})")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]["value"]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL."""
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)
        
        self.cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time()
        }
        self.cache.move_to_end(key)
    
    def delete(self, key: str):
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def cleanup_expired(self):
        """Remove expired entries."""
        now = time.time()
        expired_keys = [
            k for k, v in self.cache.items()
            if v["expires_at"] < now
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }
    
    def preload_configs(self, configs: Dict):
        """Preload configuration into cache."""
        for key, value in configs.items():
            self.set(key, value, ttl=86400)  # 24 hour TTL
        logger.info(f"Preloaded {len(configs)} configurations into cache")


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

_erp_sync: Optional[ERPSyncEngine] = None
_business_intelligence: Optional[BusinessIntelligence] = None
_audit_trail: Optional[AuditTrailEngine] = None
_security_shield: Optional[SecurityShield] = None
_multi_tenant: Optional[MultiTenantRouter] = None
_cache: Optional[HighPerformanceCache] = None


def get_erp_sync() -> ERPSyncEngine:
    global _erp_sync
    if _erp_sync is None:
        _erp_sync = ERPSyncEngine()
    return _erp_sync


def get_business_intelligence() -> BusinessIntelligence:
    global _business_intelligence
    if _business_intelligence is None:
        _business_intelligence = BusinessIntelligence()
    return _business_intelligence


def get_audit_trail() -> AuditTrailEngine:
    global _audit_trail
    if _audit_trail is None:
        _audit_trail = AuditTrailEngine()
    return _audit_trail


def get_security_shield() -> SecurityShield:
    global _security_shield
    if _security_shield is None:
        _security_shield = SecurityShield()
    return _security_shield


def get_multi_tenant() -> MultiTenantRouter:
    global _multi_tenant
    if _multi_tenant is None:
        _multi_tenant = MultiTenantRouter()
    return _multi_tenant


def get_cache() -> HighPerformanceCache:
    global _cache
    if _cache is None:
        _cache = HighPerformanceCache()
    return _cache
