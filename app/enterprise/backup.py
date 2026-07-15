"""
MAHALAKSMI AIOS v1.0 - Volume V Chapter 44: Backup Center
Automated periodic database backup system
"""
import os
import sys
import sqlite3
import json
import shutil
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

class BackupStatus(Enum):
    """Backup status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class BackupType(Enum):
    """Backup type."""
    FULL = "full"
    INCREMENTAL = "incremental"
    SCHEDULED = "scheduled"


@dataclass
class Backup:
    """Backup record."""
    backup_id: str
    backup_type: BackupType
    status: BackupStatus
    source_path: str
    destination_path: str
    size_bytes: int = 0
    checksum: str = ""
    created_at: str = ""
    completed_at: str = ""
    error_message: str = ""


@dataclass
class RestorePoint:
    """Restore point."""
    restore_id: str
    backup_id: str
    created_at: str
    description: str = ""


# ============================================================================
# BACKUP CENTER
# ============================================================================

class BackupCenter:
    """
    Automated Backup Center.
    Handles periodic database backups and restore operations.
    """
    
    def __init__(self):
        # Backup directory
        self.backup_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "backups"
        )
        
        # Database directory
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data"
        )
        
        # Create directories
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Backup metadata file
        self.metadata_file = os.path.join(self.backup_dir, "backup_metadata.json")
        
        # Initialize metadata
        self._init_metadata()
        
        logger.info("BackupCenter initialized")
    
    def _init_metadata(self):
        """Initialize backup metadata."""
        if not os.path.exists(self.metadata_file):
            self._save_metadata({"backups": [], "restore_points": []})
    
    def _load_metadata(self) -> Dict:
        """Load backup metadata."""
        try:
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        except:
            return {"backups": [], "restore_points": []}
    
    def _save_metadata(self, metadata: Dict):
        """Save backup metadata."""
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
    
    def _generate_backup_id(self) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"BACKUP-{timestamp}"
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def backup_database(self, db_name: str, backup_type: BackupType = BackupType.FULL) -> Backup:
        """
        Create backup of a database.
        """
        source_path = os.path.join(self.data_dir, db_name)
        
        # Check if source exists
        if not os.path.exists(source_path):
            # Try with .db extension
            source_path = f"{source_path}.db"
            if not os.path.exists(source_path):
                return Backup(
                    backup_id=self._generate_backup_id(),
                    backup_type=backup_type,
                    status=BackupStatus.FAILED,
                    source_path=db_name,
                    destination_path="",
                    error_message="Source database not found"
                )
        
        backup_id = self._generate_backup_id()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{db_name}_{timestamp}.backup"
        destination_path = os.path.join(self.backup_dir, backup_filename)
        
        backup = Backup(
            backup_id=backup_id,
            backup_type=backup_type,
            status=BackupStatus.IN_PROGRESS,
            source_path=source_path,
            destination_path=destination_path,
            created_at=datetime.now().isoformat()
        )
        
        try:
            # Copy database file
            shutil.copy2(source_path, destination_path)
            
            # Calculate checksum
            checksum = self._calculate_checksum(destination_path)
            
            # Get file size
            size_bytes = os.path.getsize(destination_path)
            
            # Update backup record
            backup.status = BackupStatus.COMPLETED
            backup.completed_at = datetime.now().isoformat()
            backup.size_bytes = size_bytes
            backup.checksum = checksum
            
            # Save to metadata
            metadata = self._load_metadata()
            metadata["backups"].append({
                "backup_id": backup.backup_id,
                "backup_type": backup.backup_type.value,
                "status": backup.status.value,
                "source": backup.source_path,
                "destination": backup.destination_path,
                "size_bytes": backup.size_bytes,
                "checksum": backup.checksum,
                "created_at": backup.created_at,
                "completed_at": backup.completed_at
            })
            self._save_metadata(metadata)
            
            logger.info(f"Backup completed: {backup_id} ({size_bytes} bytes)")
        
        except Exception as e:
            backup.status = BackupStatus.FAILED
            backup.error_message = str(e)
            logger.error(f"Backup failed: {e}")
        
        return backup
    
    def backup_all_databases(self) -> List[Backup]:
        """Backup all databases in data directory."""
        backups = []
        
        # List all database files
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".db"):
                    backup = self.backup_database(filename)
                    backups.append(backup)
        
        return backups
    
    def restore_database(self, backup_id: str, target_db: str = None) -> bool:
        """
        Restore database from backup.
        """
        metadata = self._load_metadata()
        
        # Find backup
        backup_info = None
        for b in metadata.get("backups", []):
            if b["backup_id"] == backup_id:
                backup_info = b
                break
        
        if not backup_info:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        source_path = backup_info["destination"]
        if not os.path.exists(source_path):
            logger.error(f"Backup file not found: {source_path}")
            return False
        
        # Determine target
        if target_db is None:
            target_db = os.path.basename(backup_info["source"])
        
        target_path = os.path.join(self.data_dir, target_db)
        
        try:
            # Create restore point of current database
            if os.path.exists(target_path):
                self._create_restore_point(target_path, f"Pre-restore of {target_db}")
            
            # Restore
            shutil.copy2(source_path, target_path)
            
            logger.info(f"Restore completed: {target_db} from {backup_id}")
            return True
        
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def _create_restore_point(self, db_path: str, description: str):
        """Create restore point."""
        metadata = self._load_metadata()
        
        restore_id = f"RESTORE-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        metadata["restore_points"].append({
            "restore_id": restore_id,
            "database": os.path.basename(db_path),
            "description": description,
            "created_at": datetime.now().isoformat()
        })
        
        self._save_metadata(metadata)
    
    def list_backups(self, db_name: str = None) -> List[Dict]:
        """List available backups."""
        metadata = self._load_metadata()
        backups = metadata.get("backups", [])
        
        if db_name:
            backups = [b for b in backups if db_name in b.get("source", "")]
        
        return sorted(backups, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics."""
        metadata = self._load_metadata()
        backups = metadata.get("backups", [])
        
        completed = [b for b in backups if b.get("status") == "completed"]
        failed = [b for b in backups if b.get("status") == "failed"]
        
        total_size = sum(b.get("size_bytes", 0) for b in completed)
        
        return {
            "total_backups": len(backups),
            "completed_backups": len(completed),
            "failed_backups": len(failed),
            "total_backup_size_bytes": total_size,
            "total_backup_size_formatted": self._format_bytes(total_size),
            "last_backup": completed[0] if completed else None,
            "backup_directory": self.backup_dir
        }
    
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human readable."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.2f} TB"
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backups, keeping only the most recent."""
        metadata = self._load_metadata()
        backups = sorted(
            metadata.get("backups", []),
            key=lambda x: x.get("completed_at", ""),
            reverse=True
        )
        
        removed = 0
        for backup in backups[keep_count:]:
            backup_path = backup.get("destination")
            if backup_path and os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                    removed += 1
                    logger.info(f"Removed old backup: {backup_path}")
                except Exception as e:
                    logger.error(f"Failed to remove backup: {e}")
        
        # Update metadata
        metadata["backups"] = backups[:keep_count]
        self._save_metadata(metadata)
        
        return removed


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_backup_center: Optional[BackupCenter] = None


def get_backup_center() -> BackupCenter:
    """Get or create global backup center."""
    global _backup_center
    if _backup_center is None:
        _backup_center = BackupCenter()
    return _backup_center
