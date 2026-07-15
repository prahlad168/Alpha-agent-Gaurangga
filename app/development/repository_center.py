"""
MAHALAKSMI AIOS v1.0 - Volume III Chapter 23: Repository Center
Local repository management with backup snapshots and revision history
"""
import os
import sys
import sqlite3
import json
import shutil
import hashlib
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

class ArchiveStatus(Enum):
    """Archive status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncStatus(Enum):
    """Sync status with remote."""
    SYNCED = "synced"
    AHEAD = "ahead"
    BEHIND = "behind"
    DIVERGED = "diverged"
    UNKNOWN = "unknown"


@dataclass
class Archive:
    """Local code archive snapshot."""
    archive_id: str
    commit_hash: str
    branch: str
    message: str
    author: str
    files_included: List[str]
    total_size_bytes: int
    status: ArchiveStatus
    created_at: str
    completed_at: str = ""


@dataclass
class RepositoryStatus:
    """Repository status info."""
    path: str
    branch: str
    remote: str
    commits_ahead: int
    commits_behind: int
    last_sync: str
    last_archive: str
    total_archives: int
    total_size_bytes: int
    sync_status: SyncStatus


# ============================================================================
# REPOSITORY DATABASE
# ============================================================================

class RepositoryDB:
    """SQLite database for repository center."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "repository_center.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archives (
                archive_id TEXT PRIMARY KEY,
                commit_hash TEXT,
                branch TEXT,
                message TEXT,
                author TEXT,
                files_included TEXT,
                total_size_bytes INTEGER,
                status TEXT,
                created_at TEXT,
                completed_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_type TEXT,
                remote TEXT,
                branch TEXT,
                status TEXT,
                commits_pushed INTEGER,
                commits_pulled INTEGER,
                synced_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repository_info (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                repo_path TEXT,
                remote_url TEXT,
                default_branch TEXT,
                last_sync TEXT,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_archive(self, archive: Archive) -> bool:
        """Save archive record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO archives VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                archive.archive_id,
                archive.commit_hash,
                archive.branch,
                archive.message,
                archive.author,
                json.dumps(archive.files_included),
                archive.total_size_bytes,
                archive.status.value,
                archive.created_at,
                archive.completed_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save archive: {e}")
            return False
    
    def get_archives(self, limit: int = 100) -> List[Archive]:
        """Get all archives."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM archives ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_archive(row) for row in rows]
    
    def _row_to_archive(self, row) -> Archive:
        """Convert row to Archive."""
        return Archive(
            archive_id=row['archive_id'],
            commit_hash=row['commit_hash'],
            branch=row['branch'],
            message=row['message'],
            author=row['author'],
            files_included=json.loads(row['files_included']) if row['files_included'] else [],
            total_size_bytes=row['total_size_bytes'],
            status=ArchiveStatus(row['status']),
            created_at=row['created_at'],
            completed_at=row['completed_at'] or ""
        )
    
    def get_archive(self, archive_id: str) -> Optional[Archive]:
        """Get archive by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM archives WHERE archive_id = ?", (archive_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_archive(row)
        return None
    
    def save_sync_history(self, sync_data: Dict) -> bool:
        """Save sync history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sync_history 
                (sync_type, remote, branch, status, commits_pushed, commits_pulled, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sync_data.get("type", "push"),
                sync_data.get("remote", "origin"),
                sync_data.get("branch", "main"),
                sync_data.get("status", "success"),
                sync_data.get("commits_pushed", 0),
                sync_data.get("commits_pulled", 0),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save sync history: {e}")
            return False
    
    def get_sync_history(self, limit: int = 20) -> List[Dict]:
        """Get sync history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sync_history ORDER BY synced_at DESC LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row['id'],
                "type": row['sync_type'],
                "remote": row['remote'],
                "branch": row['branch'],
                "status": row['status'],
                "commits_pushed": row['commits_pushed'],
                "commits_pulled": row['commits_pulled'],
                "synced_at": row['synced_at']
            }
            for row in rows
        ]


# ============================================================================
# REPOSITORY CENTER
# ============================================================================

class RepositoryCenter:
    """
    Repository Center.
    Manages local code backups, snapshots, and revision history.
    """
    
    def __init__(self):
        self.db = RepositoryDB()
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.archives_path = os.path.join(self.base_path, "archives")
        
        # Create archives directory
        os.makedirs(self.archives_path, exist_ok=True)
        
        logger.info("RepositoryCenter initialized")
    
    def get_repo_path(self) -> str:
        """Get repository path."""
        return self.base_path
    
    def get_current_status(self) -> RepositoryStatus:
        """Get current repository status."""
        import subprocess
        
        repo_path = self.base_path
        
        # Get current branch
        branch = "main"
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            branch = result.stdout.strip() or "main"
        except:
            pass
        
        # Get remote info
        remote = "origin"
        remote_url = ""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            remote_url = result.stdout.strip()
        except:
            pass
        
        # Get sync status
        sync_status = SyncStatus.UNKNOWN
        commits_ahead = 0
        commits_behind = 0
        
        try:
            result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", f"HEAD...@{u}upstream"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split()
                if len(parts) == 2:
                    commits_ahead = int(parts[0])
                    commits_behind = int(parts[1])
                    
                    if commits_ahead > 0 and commits_behind > 0:
                        sync_status = SyncStatus.DIVERGED
                    elif commits_ahead > 0:
                        sync_status = SyncStatus.AHEAD
                    elif commits_behind > 0:
                        sync_status = SyncStatus.BEHIND
                    else:
                        sync_status = SyncStatus.SYNCED
        except:
            pass
        
        # Get last archive
        archives = self.db.get_archives(limit=1)
        last_archive = archives[0].created_at if archives else ""
        
        # Calculate total archives and size
        all_archives = self.db.get_archives(limit=1000)
        total_archives = len(all_archives)
        total_size = sum(a.total_size_bytes for a in all_archives)
        
        return RepositoryStatus(
            path=repo_path,
            branch=branch,
            remote=remote,
            commits_ahead=commits_ahead,
            commits_behind=commits_behind,
            last_sync="",
            last_archive=last_archive,
            total_archives=total_archives,
            total_size_bytes=total_size,
            sync_status=sync_status
        )
    
    def create_archive(
        self,
        commit_hash: str = None,
        message: str = None,
        include_files: List[str] = None
    ) -> Archive:
        """Create a local archive snapshot."""
        import subprocess
        
        archive_id = hashlib.md5(
            datetime.now().isoformat().encode()
        ).hexdigest()[:12].upper()
        
        # Get current git info
        if not commit_hash:
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.base_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                commit_hash = result.stdout.strip()[:12]
            except:
                commit_hash = "local"
        
        if not message:
            message = f"Archive snapshot {archive_id}"
        
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            branch = result.stdout.strip() or "main"
        except:
            branch = "main"
        
        # Get author
        author = "system"
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%an"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            author = result.stdout.strip()
        except:
            pass
        
        # Determine files to archive
        if include_files is None:
            include_files = self._get_all_files()
        
        # Create archive
        archive_path = os.path.join(
            self.archives_path,
            f"archive-{archive_id}.tar.gz"
        )
        
        total_size = 0
        
        try:
            # Create tar.gz archive
            import tarfile
            
            with tarfile.open(archive_path, "w:gz") as tar:
                for file_path in include_files[:100]:  # Limit to 100 files
                    full_path = os.path.join(self.base_path, file_path)
                    if os.path.exists(full_path) and os.path.isfile(full_path):
                        try:
                            tar.add(full_path, arcname=file_path)
                            total_size += os.path.getsize(full_path)
                        except:
                            pass
            
            status = ArchiveStatus.COMPLETED
            completed_at = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Archive creation failed: {e}")
            status = ArchiveStatus.FAILED
            completed_at = ""
        
        archive = Archive(
            archive_id=f"ARCH-{archive_id}",
            commit_hash=commit_hash,
            branch=branch,
            message=message,
            author=author,
            files_included=include_files[:100],
            total_size_bytes=total_size,
            status=status,
            created_at=datetime.now().isoformat(),
            completed_at=completed_at
        )
        
        self.db.save_archive(archive)
        
        if status == ArchiveStatus.COMPLETED:
            logger.info(f"Archive created: {archive.archive_id}")
        else:
            logger.error(f"Archive failed: {archive.archive_id}")
        
        return archive
    
    def _get_all_files(self) -> List[str]:
        """Get list of all tracked files."""
        import subprocess
        
        files = []
        
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                files = [f for f in result.stdout.strip().split("\n") if f]
        
        except Exception as e:
            logger.warning(f"Could not get git files: {e}")
        
        return files
    
    def archive_after_push(self, push_info: Dict) -> Archive:
        """Create archive after successful push to remote."""
        message = push_info.get("message", "Post-push archive")
        commit_hash = push_info.get("commit_hash", "")
        
        # Log sync
        self.db.save_sync_history({
            "type": "push",
            "remote": push_info.get("remote", "origin"),
            "branch": push_info.get("branch", "main"),
            "status": "success",
            "commits_pushed": push_info.get("commits_count", 1)
        })
        
        # Create archive
        return self.create_archive(
            commit_hash=commit_hash,
            message=message,
            include_files=None
        )
    
    def get_archives(self, limit: int = 50) -> List[Dict]:
        """Get list of archives."""
        archives = self.db.get_archives(limit)
        
        return [
            {
                "id": a.archive_id,
                "commit": a.commit_hash,
                "branch": a.branch,
                "message": a.message,
                "author": a.author,
                "files_count": len(a.files_included),
                "size_bytes": a.total_size_bytes,
                "size_human": self._format_size(a.total_size_bytes),
                "status": a.status.value,
                "created_at": a.created_at
            }
            for a in archives
        ]
    
    def get_archive_details(self, archive_id: str) -> Dict:
        """Get archive details."""
        archive = self.db.get_archive(archive_id)
        
        if not archive:
            return {"error": "Archive not found"}
        
        return {
            "id": archive.archive_id,
            "commit": archive.commit_hash,
            "branch": archive.branch,
            "message": archive.message,
            "author": archive.author,
            "files": archive.files_included,
            "size_bytes": archive.total_size_bytes,
            "size_human": self._format_size(archive.total_size_bytes),
            "status": archive.status.value,
            "created_at": archive.created_at,
            "completed_at": archive.completed_at
        }
    
    def get_sync_history(self, limit: int = 20) -> List[Dict]:
        """Get sync history."""
        return self.db.get_sync_history(limit)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_repository_status(self) -> Dict:
        """Get comprehensive repository status."""
        status = self.get_current_status()
        archives = self.db.get_archives(limit=10)
        sync_history = self.db.get_sync_history(limit=5)
        
        return {
            "repository": {
                "path": status.path,
                "branch": status.branch,
                "remote": status.remote,
                "sync_status": status.sync_status.value,
                "commits_ahead": status.commits_ahead,
                "commits_behind": status.commits_behind
            },
            "archives": {
                "total": status.total_archives,
                "total_size": self._format_size(status.total_size_bytes),
                "last_archive": status.last_archive
            },
            "recent_archives": [
                {
                    "id": a.archive_id,
                    "commit": a.commit_hash,
                    "message": a.message,
                    "created_at": a.created_at
                }
                for a in archives[:5]
            ],
            "sync_history": sync_history
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_repository_center: Optional[RepositoryCenter] = None


def get_repository_center() -> RepositoryCenter:
    """Get or create global repository center."""
    global _repository_center
    if _repository_center is None:
        _repository_center = RepositoryCenter()
    return _repository_center
