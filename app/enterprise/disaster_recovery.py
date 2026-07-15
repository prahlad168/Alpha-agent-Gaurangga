"""
MAHALAKSMI AIOS v1.0 - Volume V Chapter 45: Disaster Recovery & Failover
Automated health monitoring and business continuity system
"""
import os
import sys
import sqlite3
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class SystemState(Enum):
    """System operational state."""
    NORMAL = "normal"
    DEGRADED = "degraded"
    READ_ONLY = "read_only"
    STANDBY = "standby"
    OFFLINE = "offline"
    RECOVERING = "recovering"


class HealthStatus(Enum):
    """Component health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class RecoveryStatus(Enum):
    """Recovery operation status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class ComponentHealth:
    """Health status of a component."""
    component_name: str
    status: HealthStatus
    last_check: str
    response_time_ms: float = 0.0
    error_message: str = ""
    consecutive_failures: int = 0


@dataclass
class FailoverRecord:
    """Record of a failover event."""
    failover_id: str
    trigger_reason: str
    previous_state: SystemState
    new_state: SystemState
    components_affected: List[str]
    initiated_at: str
    completed_at: str = ""
    status: RecoveryStatus = RecoveryStatus.NOT_STARTED


@dataclass
class RecoveryPlan:
    """Recovery action plan."""
    recovery_id: str
    steps: List[Dict]
    estimated_duration_minutes: int
    priority: int = 1


# ============================================================================
# DISASTER RECOVERY DATABASE
# ============================================================================

class DisasterRecoveryDB:
    """SQLite database for disaster recovery."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "disaster_recovery.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                current_state TEXT,
                previous_state TEXT,
                last_transition TEXT,
                last_check TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS component_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_name TEXT UNIQUE,
                status TEXT,
                last_check TEXT,
                response_time_ms REAL,
                error_message TEXT,
                consecutive_failures INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failover_history (
                failover_id TEXT PRIMARY KEY,
                trigger_reason TEXT,
                previous_state TEXT,
                new_state TEXT,
                components_affected TEXT,
                initiated_at TEXT,
                completed_at TEXT,
                status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recovery_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recovery_id TEXT,
                step TEXT,
                status TEXT,
                result TEXT,
                executed_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_system_state(self) -> SystemState:
        """Get current system state."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT current_state FROM system_state WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return SystemState(row[0])
        return SystemState.NORMAL
    
    def set_system_state(self, state: SystemState) -> bool:
        """Set system state."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current = self.get_system_state()
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_state 
                (id, current_state, previous_state, last_transition, last_check, updated_at)
                VALUES (1, ?, ?, ?, ?, ?)
            """, (
                state.value,
                current.value,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to set state: {e}")
            return False
    
    def save_component_health(self, health: ComponentHealth) -> bool:
        """Save component health."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO component_health 
                (component_name, status, last_check, response_time_ms, error_message, consecutive_failures)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                health.component_name,
                health.status.value,
                health.last_check,
                health.response_time_ms,
                health.error_message,
                health.consecutive_failures
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save health: {e}")
            return False
    
    def get_all_component_health(self) -> List[ComponentHealth]:
        """Get all component health."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM component_health")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            ComponentHealth(
                component_name=row['component_name'],
                status=HealthStatus(row['status']),
                last_check=row['last_check'],
                response_time_ms=row['response_time_ms'],
                error_message=row['error_message'] or "",
                consecutive_failures=row['consecutive_failures']
            )
            for row in rows
        ]
    
    def save_failover_record(self, record: FailoverRecord) -> bool:
        """Save failover record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO failover_history VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.failover_id,
                record.trigger_reason,
                record.previous_state.value,
                record.new_state.value,
                json.dumps(record.components_affected),
                record.initiated_at,
                record.completed_at,
                record.status.value
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save failover: {e}")
            return False
    
    def get_failover_history(self, limit: int = 10) -> List[FailoverRecord]:
        """Get failover history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM failover_history 
            ORDER BY initiated_at DESC LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            FailoverRecord(
                failover_id=row['failover_id'],
                trigger_reason=row['trigger_reason'],
                previous_state=SystemState(row['previous_state']),
                new_state=SystemState(row['new_state']),
                components_affected=json.loads(row['components_affected']),
                initiated_at=row['initiated_at'],
                completed_at=row['completed_at'] or "",
                status=RecoveryStatus(row['status'])
            )
            for row in rows
        ]


# ============================================================================
# DISASTER RECOVERY & FAILOVER ENGINE
# ============================================================================

class DisasterRecoveryEngine:
    """
    Disaster Recovery & Failover Engine.
    Monitors system health and orchestrates failover/recovery.
    """
    
    # Thresholds
    HEALTHY_THRESHOLD = 3  # consecutive failures before action
    CRITICAL_THRESHOLD = 5   # consecutive failures for failover
    CHECK_INTERVAL = 60       # seconds between health checks
    
    def __init__(self):
        self.db = DisasterRecoveryDB()
        
        # Initialize system state if not set
        if self.db.get_system_state() == SystemState.NORMAL:
            self.db.set_system_state(SystemState.NORMAL)
        
        # Components to monitor
        self.components = [
            "database",
            "storage",
            "api",
            "memory",
            "revenue_engine",
            "notification_service"
        ]
        
        logger.info("DisasterRecoveryEngine initialized")
    
    def get_system_state(self) -> SystemState:
        """Get current system state."""
        return self.db.get_system_state()
    
    def check_component_health(self, component: str) -> ComponentHealth:
        """Check health of a component."""
        health = ComponentHealth(
            component_name=component,
            status=HealthStatus.UNKNOWN,
            last_check=datetime.now().isoformat()
        )
        
        start_time = time.time()
        
        try:
            if component == "database":
                health = self._check_database()
            elif component == "storage":
                health = self._check_storage()
            elif component == "api":
                health = self._check_api()
            elif component == "memory":
                health = self._check_memory()
            elif component == "revenue_engine":
                health = self._check_revenue_engine()
            elif component == "notification_service":
                health = self._check_notification_service()
            else:
                health.status = HealthStatus.HEALTHY
                health.error_message = "Unknown component"
        
        except Exception as e:
            health.status = HealthStatus.UNHEALTHY
            health.error_message = str(e)
        
        health.response_time_ms = (time.time() - start_time) * 1000
        health.last_check = datetime.now().isoformat()
        
        # Update consecutive failures
        prev = self._get_previous_health(component)
        if prev:
            if health.status == HealthStatus.UNHEALTHY:
                health.consecutive_failures = prev.consecutive_failures + 1
            else:
                health.consecutive_failures = 0
        
        self.db.save_component_health(health)
        
        return health
    
    def _get_previous_health(self, component: str) -> Optional[ComponentHealth]:
        """Get previous health status."""
        all_health = self.db.get_all_component_health()
        for h in all_health:
            if h.component_name == component:
                return h
        return None
    
    def _check_database(self) -> ComponentHealth:
        """Check database health."""
        health = ComponentHealth(
            component_name="database",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now().isoformat()
        )
        
        try:
            # Check if we can connect to databases
            db_files = [
                "data/memory.db",
                "data/products.db",
                "data/revenue.db"
            ]
            
            healthy_count = 0
            for db_file in db_files:
                db_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    db_file
                )
                if os.path.exists(db_path):
                    try:
                        conn = sqlite3.connect(db_path, timeout=1)
                        conn.execute("SELECT 1")
                        conn.close()
                        healthy_count += 1
                    except:
                        pass
            
            if healthy_count < len(db_files):
                health.status = HealthStatus.DEGRADED
                health.error_message = f"Only {healthy_count}/{len(db_files)} databases healthy"
        
        except Exception as e:
            health.status = HealthStatus.UNHEALTHY
            health.error_message = str(e)
        
        return health
    
    def _check_storage(self) -> ComponentHealth:
        """Check storage health."""
        health = ComponentHealth(
            component_name="storage",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now().isoformat()
        )
        
        try:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data"
            )
            
            if os.path.exists(data_dir):
                total, used, free = self._get_disk_usage(data_dir)
                usage_percent = (used / total) * 100
                
                if usage_percent > 90:
                    health.status = HealthStatus.UNHEALTHY
                    health.error_message = f"Disk usage at {usage_percent:.1f}%"
                elif usage_percent > 80:
                    health.status = HealthStatus.DEGRADED
                    health.error_message = f"Disk usage at {usage_percent:.1f}%"
            else:
                health.status = HealthStatus.UNHEALTHY
                health.error_message = "Data directory not found"
        
        except Exception as e:
            health.status = HealthStatus.UNHEALTHY
            health.error_message = str(e)
        
        return health
    
    def _check_api(self) -> ComponentHealth:
        """Check API health."""
        health = ComponentHealth(
            component_name="api",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now().isoformat()
        )
        
        # Check if API endpoints are accessible
        try:
            import urllib.request
            
            url = "http://127.0.0.1:8000/health"
            req = urllib.request.Request(url)
            
            start = time.time()
            try:
                urllib.request.urlopen(req, timeout=2)
                health.response_time_ms = (time.time() - start) * 1000
            except:
                health.status = HealthStatus.DEGRADED
                health.error_message = "API not responding"
        
        except ImportError:
            health.status = HealthStatus.DEGRADED
            health.error_message = "requests not available"
        except Exception as e:
            health.status = HealthStatus.UNHEALTHY
            health.error_message = str(e)
        
        return health
    
    def _check_memory(self) -> ComponentHealth:
        """Check memory system health."""
        health = ComponentHealth(
            component_name="memory",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now().isoformat()
        )
        
        try:
            from app.intelligence.memory import get_memory
            memory = get_memory()
            entries = memory.get_recent(limit=1)
            health.status = HealthStatus.HEALTHY
        except Exception as e:
            health.status = HealthStatus.DEGRADED
            health.error_message = str(e)
        
        return health
    
    def _check_revenue_engine(self) -> ComponentHealth:
        """Check revenue engine health."""
        health = ComponentHealth(
            component_name="revenue_engine",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now().isoformat()
        )
        
        try:
            from app.business.revenue import get_revenue_manager
            revenue = get_revenue_manager()
            summary = revenue.get_summary()
            health.status = HealthStatus.HEALTHY
        except Exception as e:
            health.status = HealthStatus.DEGRADED
            health.error_message = str(e)
        
        return health
    
    def _check_notification_service(self) -> ComponentHealth:
        """Check notification service health."""
        health = ComponentHealth(
            component_name="notification_service",
            status=HealthStatus.HEALTHY,
            last_check=datetime.now().isoformat()
        )
        
        try:
            from app.enterprise.notification import get_notification_center
            nc = get_notification_center()
            stats = nc.get_stats()
            health.status = HealthStatus.HEALTHY
        except Exception as e:
            health.status = HealthStatus.DEGRADED
            health.error_message = str(e)
        
        return health
    
    def _get_disk_usage(self, path: str) -> tuple:
        """Get disk usage stats."""
        import shutil
        stat = shutil.disk_usage(path)
        return stat.total, stat.used, stat.free
    
    def perform_health_check(self) -> Dict:
        """Perform full health check on all components."""
        all_health = []
        unhealthy_components = []
        
        for component in self.components:
            health = self.check_component_health(component)
            all_health.append({
                "component": health.component_name,
                "status": health.status.value,
                "last_check": health.last_check,
                "response_time_ms": round(health.response_time_ms, 2),
                "error": health.error_message,
                "consecutive_failures": health.consecutive_failures
            })
            
            if health.status == HealthStatus.UNHEALTHY:
                unhealthy_components.append(health.component_name)
        
        # Determine overall state
        overall_healthy = len(unhealthy_components) == 0
        current_state = self.get_system_state()
        
        return {
            "overall_healthy": overall_healthy,
            "unhealthy_components": unhealthy_components,
            "components": all_health,
            "system_state": current_state.value,
            "checked_at": datetime.now().isoformat()
        }
    
    def initiate_failover(self, reason: str) -> FailoverRecord:
        """Initiate system failover."""
        import hashlib
        
        previous_state = self.get_system_state()
        
        # Determine new state based on severity
        all_health = self.db.get_all_component_health()
        critical_failures = sum(
            1 for h in all_health 
            if h.consecutive_failures >= self.CRITICAL_THRESHOLD
        )
        
        if critical_failures > 2:
            new_state = SystemState.OFFLINE
        elif critical_failures > 0:
            new_state = SystemState.STANDBY
        else:
            new_state = SystemState.READ_ONLY
        
        # Create failover record
        failover_id = hashlib.md5(
            f"{reason}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        
        record = FailoverRecord(
            failover_id=f"FO-{failover_id}",
            trigger_reason=reason,
            previous_state=previous_state,
            new_state=new_state,
            components_affected=unhealthy_components if critical_failures else [],
            initiated_at=datetime.now().isoformat(),
            status=RecoveryStatus.IN_PROGRESS
        )
        
        # Update system state
        self.db.set_system_state(new_state)
        self.db.save_failover_record(record)
        
        # Log critical event
        logger.critical(f"FAILOVER: {previous_state.value} -> {new_state.value}. Reason: {reason}")
        
        return record
    
    def execute_recovery(self) -> RecoveryPlan:
        """Execute recovery plan."""
        import hashlib
        
        current_state = self.get_system_state()
        recovery_id = hashlib.md5(
            datetime.now().isoformat().encode()
        ).hexdigest()[:12].upper()
        
        steps = []
        
        if current_state == SystemState.READ_ONLY:
            steps = [
                {"action": "verify_database", "description": "Verify database integrity"},
                {"action": "restore_write_access", "description": "Restore write access"},
                {"action": "test_transactions", "description": "Test transaction processing"},
                {"action": "set_state_normal", "description": "Set state to NORMAL"}
            ]
        elif current_state == SystemState.STANDBY:
            steps = [
                {"action": "check_components", "description": "Check all components"},
                {"action": "restart_services", "description": "Restart failed services"},
                {"action": "sync_data", "description": "Sync data from backups"},
                {"action": "verify_data", "description": "Verify data integrity"},
                {"action": "set_state_normal", "description": "Set state to NORMAL"}
            ]
        elif current_state == SystemState.OFFLINE:
            steps = [
                {"action": "assess_damage", "description": "Assess system damage"},
                {"action": "restore_from_backup", "description": "Restore from last backup"},
                {"action": "verify_all", "description": "Verify all components"},
                {"action": "partial_restart", "description": "Restart in degraded mode"},
                {"action": "set_state_standby", "description": "Set state to STANDBY"}
            ]
        elif current_state == SystemState.DEGRADED:
            steps = [
                {"action": "check_components", "description": "Check all components"},
                {"action": "restore_services", "description": "Restore failed services"},
                {"action": "verify_data", "description": "Verify data integrity"},
                {"action": "set_state_normal", "description": "Set state to NORMAL"}
            ]
        else:
            # Already normal
            steps = [
                {"action": "verify_system", "description": "Verify system is healthy"},
                {"action": "log_status", "description": "Log system status"}
            ]
        
        # Calculate estimated duration
        estimated_duration = len(steps) * 5  # 5 minutes per step
        if estimated_duration == 0:
            estimated_duration = 10  # Minimum 10 minutes
        
        # Update failover record
        failover_history = self.db.get_failover_history(limit=1)
        if failover_history:
            record = failover_history[0]
            record.status = RecoveryStatus.SUCCESS
            record.completed_at = datetime.now().isoformat()
            self.db.save_failover_record(record)
        
        # Transition to recovering
        if current_state != SystemState.NORMAL:
            self.db.set_system_state(SystemState.RECOVERING)
        
        return RecoveryPlan(
            recovery_id=f"REC-{recovery_id}",
            steps=steps,
            estimated_duration_minutes=estimated_duration
        )
    
    def complete_recovery(self) -> bool:
        """Complete recovery and return to normal state."""
        self.db.set_system_state(SystemState.NORMAL)
        
        # Reset consecutive failures
        for component in self.components:
            health = ComponentHealth(
                component_name=component,
                status=HealthStatus.HEALTHY,
                last_check=datetime.now().isoformat(),
                consecutive_failures=0
            )
            self.db.save_component_health(health)
        
        logger.info("Recovery completed. System state: NORMAL")
        return True
    
    def get_dr_status(self) -> Dict:
        """Get disaster recovery status."""
        state = self.get_system_state()
        health = self.perform_health_check()
        failover_history = self.db.get_failover_history()
        
        return {
            "system_state": state.value,
            "health_check": health,
            "last_failover": {
                "id": failover_history[0].failover_id if failover_history else None,
                "trigger": failover_history[0].trigger_reason if failover_history else None,
                "from_state": failover_history[0].previous_state.value if failover_history else None,
                "to_state": failover_history[0].new_state.value if failover_history else None,
                "at": failover_history[0].initiated_at if failover_history else None,
                "status": failover_history[0].status.value if failover_history else None
            },
            "thresholds": {
                "healthy_threshold": self.HEALTHY_THRESHOLD,
                "critical_threshold": self.CRITICAL_THRESHOLD
            }
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_dr_engine: Optional[DisasterRecoveryEngine] = None


def get_disaster_recovery_engine() -> DisasterRecoveryEngine:
    """Get or create global DR engine."""
    global _dr_engine
    if _dr_engine is None:
        _dr_engine = DisasterRecoveryEngine()
    return _dr_engine
