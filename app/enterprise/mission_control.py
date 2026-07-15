"""
MAHALAKSMI AIOS v1.0 - Volume I Chapter 7: Mission Control
Central operational command console for system-wide monitoring and control
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

class MissionStatus(Enum):
    """Mission/Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(Enum):
    """Mission priority."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Mission:
    """Mission/Task definition."""
    mission_id: str
    title: str
    description: str
    status: MissionStatus
    priority: Priority
    assigned_to: str = ""
    created_at: str = ""
    updated_at: str = ""
    due_date: str = ""
    completed_at: str = ""
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemAlert:
    """System alert/warning."""
    alert_id: str
    level: str  # critical, warning, info
    component: str
    message: str
    timestamp: str = ""
    acknowledged: bool = False


# ============================================================================
# MISSION CONTROL DATABASE
# ============================================================================

class MissionControlDB:
    """SQLite database for mission control."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "mission_control.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                mission_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                status TEXT,
                priority INTEGER,
                assigned_to TEXT,
                created_at TEXT,
                updated_at TEXT,
                due_date TEXT,
                completed_at TEXT,
                progress REAL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                level TEXT,
                component TEXT,
                message TEXT,
                timestamp TEXT,
                acknowledged INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                issued_by TEXT,
                issued_at TEXT,
                status TEXT,
                result TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_mission(self, mission: Mission) -> bool:
        """Save mission."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO missions 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mission.mission_id,
                mission.title,
                mission.description,
                mission.status.value,
                mission.priority.value,
                mission.assigned_to,
                mission.created_at,
                mission.updated_at,
                mission.due_date,
                mission.completed_at,
                mission.progress,
                json.dumps(mission.metadata)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save mission: {e}")
            return False
    
    def get_missions(self, status: MissionStatus = None) -> List[Mission]:
        """Get missions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM missions WHERE status = ? ORDER BY priority", (status.value,))
        else:
            cursor.execute("SELECT * FROM missions ORDER BY priority")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_mission(row) for row in rows]
    
    def _row_to_mission(self, row) -> Mission:
        """Convert row to Mission."""
        return Mission(
            mission_id=row['mission_id'],
            title=row['title'],
            description=row['description'],
            status=MissionStatus(row['status']),
            priority=Priority(row['priority']),
            assigned_to=row['assigned_to'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            due_date=row['due_date'],
            completed_at=row['completed_at'],
            progress=row['progress'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def save_alert(self, alert: SystemAlert) -> bool:
        """Save alert."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO alerts VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id,
                alert.level,
                alert.component,
                alert.message,
                alert.timestamp,
                1 if alert.acknowledged else 0
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
            return False
    
    def get_alerts(self, level: str = None, unacknowledged_only: bool = False) -> List[SystemAlert]:
        """Get alerts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM alerts"
        params = []
        
        if level:
            query += " WHERE level = ?"
            params.append(level)
        
        if unacknowledged_only:
            query += " AND acknowledged = 0" if level else " WHERE acknowledged = 0"
        
        query += " ORDER BY timestamp DESC LIMIT 100"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [SystemAlert(
            alert_id=row['alert_id'],
            level=row['level'],
            component=row['component'],
            message=row['message'],
            timestamp=row['timestamp'],
            acknowledged=bool(row['acknowledged'])
        ) for row in rows]


# ============================================================================
# MISSION CONTROL
# ============================================================================

class MissionControl:
    """
    Mission Control Center.
    Central command console for system operations and monitoring.
    """
    
    def __init__(self):
        self.db = MissionControlDB()
        self._init_default_missions()
        
        logger.info("MissionControl initialized")
    
    def _init_default_missions(self):
        """Initialize default missions."""
        default_missions = [
            {
                "title": "Build 75+ AI Agents",
                "description": "Develop Genesis Council with 75+ specialized AI agents",
                "priority": Priority.HIGH,
                "status": MissionStatus.IN_PROGRESS
            },
            {
                "title": "Achieve Rp 100M Monthly Revenue",
                "description": "Scale revenue to Rp 100,000,000/month across all SBUs",
                "priority": Priority.CRITICAL,
                "status": MissionStatus.IN_PROGRESS
            },
            {
                "title": "Deploy Bitcoin Revenue Sharing",
                "description": "Implement automatic 60% CEO share to Bitcoin wallet",
                "priority": Priority.HIGH,
                "status": MissionStatus.COMPLETED
            },
            {
                "title": "Scale to 10 SBUs",
                "description": "Expand to 10 Strategic Business Units",
                "priority": Priority.NORMAL,
                "status": MissionStatus.PENDING
            },
        ]
        
        for i, m in enumerate(default_missions):
            mission = Mission(
                mission_id=f"MISSION-{i+1:03d}",
                title=m["title"],
                description=m["description"],
                status=m["status"],
                priority=m["priority"],
                created_at=datetime.now().isoformat()
            )
            self.db.save_mission(mission)
    
    def create_mission(
        self,
        title: str,
        description: str,
        priority: Priority = Priority.NORMAL,
        assigned_to: str = "",
        due_date: str = ""
    ) -> Mission:
        """Create new mission."""
        import hashlib
        mission_id = hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:12].upper()
        
        mission = Mission(
            mission_id=f"MISSION-{mission_id}",
            title=title,
            description=description,
            status=MissionStatus.PENDING,
            priority=priority,
            assigned_to=assigned_to,
            due_date=due_date,
            created_at=datetime.now().isoformat()
        )
        
        self.db.save_mission(mission)
        logger.info(f"Mission created: {mission.mission_id}")
        return mission
    
    def update_mission_status(self, mission_id: str, status: MissionStatus, progress: float = None) -> bool:
        """Update mission status."""
        missions = self.db.get_missions()
        
        for mission in missions:
            if mission.mission_id == mission_id:
                mission.status = status
                mission.updated_at = datetime.now().isoformat()
                
                if status == MissionStatus.COMPLETED:
                    mission.completed_at = datetime.now().isoformat()
                    mission.progress = 100.0
                
                if progress is not None:
                    mission.progress = progress
                
                return self.db.save_mission(mission)
        
        return False
    
    def get_missions(self, status: MissionStatus = None) -> List[Dict]:
        """Get missions as dict."""
        missions = self.db.get_missions(status)
        return [
            {
                "id": m.mission_id,
                "title": m.title,
                "description": m.description,
                "status": m.status.value,
                "priority": m.priority.name,
                "assigned_to": m.assigned_to,
                "progress": m.progress,
                "due_date": m.due_date,
                "created_at": m.created_at,
                "completed_at": m.completed_at
            }
            for m in missions
        ]
    
    def create_alert(self, level: str, component: str, message: str) -> SystemAlert:
        """Create system alert."""
        import hashlib
        alert_id = hashlib.md5(f"{component}{message}{datetime.now().isoformat()}".encode()).hexdigest()[:12].upper()
        
        alert = SystemAlert(
            alert_id=f"ALERT-{alert_id}",
            level=level,
            component=component,
            message=message,
            timestamp=datetime.now().isoformat()
        )
        
        self.db.save_alert(alert)
        logger.warning(f"Alert created: {alert.level} - {alert.component}: {alert.message}")
        return alert
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE alerts SET acknowledged = 1 WHERE alert_id = ?",
            (alert_id,)
        )
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def get_alerts(self, level: str = None, unacknowledged_only: bool = False) -> List[Dict]:
        """Get alerts."""
        alerts = self.db.get_alerts(level, unacknowledged_only)
        return [
            {
                "id": a.alert_id,
                "level": a.level,
                "component": a.component,
                "message": a.message,
                "timestamp": a.timestamp,
                "acknowledged": a.acknowledged
            }
            for a in alerts
        ]
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get mission control dashboard data."""
        missions = self.db.get_missions()
        
        # Count by status
        status_counts = {
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }
        
        for m in missions:
            status_counts[m.status.value] = status_counts.get(m.status.value, 0) + 1
        
        # Count by priority
        priority_counts = {
            "critical": 0,
            "high": 0,
            "normal": 0,
            "low": 0
        }
        
        for m in missions:
            priority_counts[m.priority.name.lower()] = priority_counts.get(m.priority.name.lower(), 0) + 1
        
        # Recent alerts
        recent_alerts = self.get_alerts(unacknowledged_only=True)[:5]
        critical_alerts = self.get_alerts(level="critical")
        
        return {
            "missions": {
                "total": len(missions),
                "by_status": status_counts,
                "by_priority": priority_counts,
                "completion_rate": (
                    status_counts["completed"] / max(len(missions), 1) * 100
                )
            },
            "alerts": {
                "unacknowledged": len(self.get_alerts(unacknowledged_only=True)),
                "critical": len(critical_alerts),
                "recent": recent_alerts
            },
            "system_status": "operational" if len(critical_alerts) == 0 else "alert",
            "last_updated": datetime.now().isoformat()
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_mission_control: Optional[MissionControl] = None


def get_mission_control() -> MissionControl:
    """Get or create global mission control instance."""
    global _mission_control
    if _mission_control is None:
        _mission_control = MissionControl()
    return _mission_control
