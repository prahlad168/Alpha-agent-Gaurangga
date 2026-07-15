"""
MAHALAKSMI AIOS v1.0 - Volume V Chapter 43: Monitoring Center
Live server health telemetry and performance monitoring
"""
import os
import sys
import time
import psutil
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

class MetricType(Enum):
    """Metric types."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"


@dataclass
class MetricSample:
    """Single metric sample."""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class SystemMetrics:
    """Complete system metrics snapshot."""
    timestamp: str = ""
    cpu_percent: float = 0
    memory_percent: float = 0
    memory_used_mb: float = 0
    memory_available_mb: float = 0
    disk_percent: float = 0
    disk_used_gb: float = 0
    disk_free_gb: float = 0
    network_sent_mb: float = 0
    network_recv_mb: float = 0
    uptime_seconds: float = 0
    process_count: int = 0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class EndpointHealth:
    """API endpoint health."""
    endpoint: str
    status: str  # healthy, degraded, down
    response_time_ms: float = 0
    last_checked: str = ""


# ============================================================================
# METRICS DATABASE
# ============================================================================

class MetricsDB:
    """SQLite database for metrics storage."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "monitoring.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT,
                value REAL,
                unit TEXT,
                timestamp TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_data TEXT,
                timestamp TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS endpoint_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                status TEXT,
                response_time_ms REAL,
                last_checked TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_metric(self, sample: MetricSample) -> bool:
        """Save metric sample."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO metrics (metric_type, value, unit, timestamp)
                VALUES (?, ?, ?, ?)
            """, (sample.metric_type.value, sample.value, sample.unit, sample.timestamp))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save metric: {e}")
            return False
    
    def get_metrics(self, metric_type: MetricType, limit: int = 100) -> List[MetricSample]:
        """Get recent metrics."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM metrics 
            WHERE metric_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (metric_type.value, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [MetricSample(
            metric_type=MetricType(row['metric_type']),
            value=row['value'],
            unit=row['unit'],
            timestamp=row['timestamp']
        ) for row in rows]
    
    def save_snapshot(self, metrics: SystemMetrics) -> bool:
        """Save system snapshot."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_snapshots (snapshot_data, timestamp)
                VALUES (?, ?)
            """, (json.dumps(metrics.__dict__), metrics.timestamp))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return False
    
    def save_endpoint_health(self, endpoint: EndpointHealth) -> bool:
        """Save endpoint health."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO endpoint_health (endpoint, status, response_time_ms, last_checked)
                VALUES (?, ?, ?, ?)
            """, (endpoint.endpoint, endpoint.status, endpoint.response_time_ms, endpoint.last_checked))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save endpoint health: {e}")
            return False


# ============================================================================
# MONITORING CENTER
# ============================================================================

class MonitoringCenter:
    """
    Live Server Health Monitoring Center.
    Collects and reports system telemetry.
    """
    
    def __init__(self):
        self.db = MetricsDB()
        self.boot_time = time.time()
        self.last_snapshot = None
        
        logger.info("MonitoringCenter initialized")
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Uptime
            uptime = time.time() - self.boot_time
            
            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_percent=disk.percent,
                disk_used_gb=disk.used / (1024 * 1024 * 1024),
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                network_sent_mb=network.bytes_sent / (1024 * 1024),
                network_recv_mb=network.bytes_recv / (1024 * 1024),
                uptime_seconds=uptime,
                process_count=process_count
            )
            
            # Save to database
            self.db.save_snapshot(metrics)
            self.last_snapshot = metrics
            
            return metrics
        
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return SystemMetrics()
    
    def record_metric(self, metric_type: MetricType, value: float, unit: str = "") -> bool:
        """Record a metric sample."""
        sample = MetricSample(
            metric_type=metric_type,
            value=value,
            unit=unit
        )
        return self.db.save_metric(sample)
    
    def check_endpoint(self, url: str, timeout: float = 5.0) -> EndpointHealth:
        """Check endpoint health."""
        import urllib.request
        import urllib.error
        
        start = time.time()
        health = EndpointHealth(
            endpoint=url,
            status="down",
            response_time_ms=0,
            last_checked=datetime.now().isoformat()
        )
        
        try:
            req = urllib.request.Request(url)
            urllib.request.urlopen(req, timeout=timeout)
            
            health.response_time_ms = (time.time() - start) * 1000
            health.status = "healthy"
        
        except urllib.error.HTTPError as e:
            health.response_time_ms = (time.time() - start) * 1000
            health.status = "degraded" if e.code < 500 else "down"
        
        except Exception:
            health.response_time_ms = (time.time() - start) * 1000
            health.status = "down"
        
        self.db.save_endpoint_health(health)
        return health
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        if self.last_snapshot:
            return {
                "timestamp": self.last_snapshot.timestamp,
                "cpu": {
                    "percent": round(self.last_snapshot.cpu_percent, 1),
                    "status": "warning" if self.last_snapshot.cpu_percent > 80 else "healthy"
                },
                "memory": {
                    "percent": round(self.last_snapshot.memory_percent, 1),
                    "used_mb": round(self.last_snapshot.memory_used_mb, 1),
                    "available_mb": round(self.last_snapshot.memory_available_mb, 1),
                    "status": "warning" if self.last_snapshot.memory_percent > 85 else "healthy"
                },
                "disk": {
                    "percent": round(self.last_snapshot.disk_percent, 1),
                    "used_gb": round(self.last_snapshot.disk_used_gb, 1),
                    "free_gb": round(self.last_snapshot.disk_free_gb, 1),
                    "status": "warning" if self.last_snapshot.disk_percent > 90 else "healthy"
                },
                "network": {
                    "sent_mb": round(self.last_snapshot.network_sent_mb, 2),
                    "recv_mb": round(self.last_snapshot.network_recv_mb, 2)
                },
                "system": {
                    "uptime_seconds": round(self.last_snapshot.uptime_seconds),
                    "uptime_formatted": self._format_uptime(self.last_snapshot.uptime_seconds),
                    "process_count": self.last_snapshot.process_count
                }
            }
        
        # Collect fresh metrics
        metrics = self.collect_system_metrics()
        return self.get_current_metrics()
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime string."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{days}d {hours}h {minutes}m"
    
    def get_api_health(self) -> Dict[str, Any]:
        """Check API health."""
        base_url = "http://127.0.0.1:8000"
        
        endpoints = [
            "/health",
            "/revenue/summary",
            "/analytics/summary"
        ]
        
        results = []
        all_healthy = True
        
        for endpoint in endpoints:
            health = self.check_endpoint(f"{base_url}{endpoint}")
            results.append({
                "endpoint": endpoint,
                "status": health.status,
                "response_time_ms": round(health.response_time_ms, 2)
            })
            if health.status != "healthy":
                all_healthy = False
        
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "endpoints": results
        }
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get complete monitoring dashboard."""
        # Collect fresh metrics
        self.collect_system_metrics()
        
        # Get API health
        api_health = self.get_api_health()
        
        # Overall status
        metrics = self.get_current_metrics()
        
        cpu_ok = metrics["cpu"]["percent"] < 80
        memory_ok = metrics["memory"]["percent"] < 85
        disk_ok = metrics["disk"]["percent"] < 90
        api_ok = api_health["overall_status"] == "healthy"
        
        if cpu_ok and memory_ok and disk_ok and api_ok:
            overall_status = "healthy"
        elif not (cpu_ok or memory_ok or disk_ok):
            overall_status = "critical"
        else:
            overall_status = "degraded"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "system": metrics,
            "api": api_health,
            "alerts": self._generate_alerts(metrics)
        }
    
    def _generate_alerts(self, metrics: Dict) -> List[Dict]:
        """Generate alerts based on metrics."""
        alerts = []
        
        if metrics["cpu"]["percent"] > 80:
            alerts.append({
                "level": "warning",
                "component": "cpu",
                "message": f"CPU usage at {metrics['cpu']['percent']}%"
            })
        
        if metrics["memory"]["percent"] > 85:
            alerts.append({
                "level": "warning",
                "component": "memory",
                "message": f"Memory usage at {metrics['memory']['percent']}%"
            })
        
        if metrics["disk"]["percent"] > 90:
            alerts.append({
                "level": "critical",
                "component": "disk",
                "message": f"Disk space critical: {metrics['disk']['percent']}%"
            })
        
        return alerts


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_monitoring_center: Optional[MonitoringCenter] = None


def get_monitoring_center() -> MonitoringCenter:
    """Get or create global monitoring center."""
    global _monitoring_center
    if _monitoring_center is None:
        _monitoring_center = MonitoringCenter()
    return _monitoring_center
