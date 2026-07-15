"""
MAHALAKSMI AIOS v1.0 - Volume III Chapter 22: GitHub Center
Advanced git repository operations and automation
"""
import os
import sys
import subprocess
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class GitStatus(Enum):
    """Git status types."""
    CLEAN = "clean"
    DIRTY = "dirty"
    CONFLICT = "conflict"
    AHEAD = "ahead"
    BEHIND = "behind"


class BranchType(Enum):
    """Branch types."""
    MAIN = "main"
    FEATURE = "feature"
    HOTFIX = "hotfix"
    RELEASE = "release"


@dataclass
class GitBranch:
    """Git branch information."""
    name: str
    is_current: bool
    is_remote: bool
    last_commit: str = ""
    last_commit_message: str = ""


@dataclass
class GitCommit:
    """Git commit information."""
    sha: str
    short_sha: str
    message: str
    author: str
    date: str
    branch: str


@dataclass
class ConflictInfo:
    """Merge conflict information."""
    file: str
    conflicts: List[str] = field(default_factory=list)


@dataclass
class RepoSyncStatus:
    """Repository synchronization status."""
    is_clean: bool
    current_branch: str
    ahead: int
    behind: int
    untracked: int
    modified: int
    staged: int
    conflicts: List[str] = field(default_factory=list)


# ============================================================================
# GITHUB CENTER DATABASE
# ============================================================================

class GitHubCenterDB:
    """SQLite database for GitHub operations."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "github_center.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS git_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT,
                target TEXT,
                status TEXT,
                result TEXT,
                executed_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_name TEXT,
                created_from TEXT,
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_operation(
        self,
        operation_type: str,
        target: str,
        status: str,
        result: str = ""
    ) -> bool:
        """Log a git operation."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO git_operations 
                (operation_type, target, status, result, executed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (operation_type, target, status, result, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")
            return False


# ============================================================================
# GITHUB CENTER
# ============================================================================

class GitHubCenter:
    """
    Advanced GitHub Center for automated git operations.
    Provides branch management, PR generation, conflict detection.
    """
    
    def __init__(self, repo_path: str = None):
        if repo_path is None:
            repo_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        self.repo_path = repo_path
        self.db = GitHubCenterDB()
        
        # Verify git repo
        self._is_git_repo = self._verify_git_repo()
        
        logger.info(f"GitHub Center initialized for: {repo_path}")
    
    def _verify_git_repo(self) -> bool:
        """Verify this is a git repository."""
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def _run_git(self, args: List[str]) -> Tuple[int, str, str]:
        """Run a git command."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def get_status(self) -> RepoSyncStatus:
        """Get current repository sync status."""
        if not self._is_git_repo:
            return RepoSyncStatus(
                is_clean=False,
                current_branch="",
                ahead=0,
                behind=0,
                untracked=0,
                modified=0,
                staged=0,
                conflicts=["Not a git repository"]
            )
        
        # Get status porcelain
        code, stdout, _ = self._run_git(["status", "--porcelain"])
        
        untracked = 0
        modified = 0
        staged = 0
        conflicts = []
        
        for line in stdout.strip().split("\n"):
            if not line:
                continue
            
            if line.startswith("??"):
                untracked += 1
            elif line.startswith("UU") or "UU" in line or "AA" in line or "DD" in line:
                conflicts.append(line[3:].strip())
            elif line[0] in "MADRC":
                staged += 1
            elif line[3] in "MADRC":
                modified += 1
        
        # Get branch
        code, branch, _ = self._run_git(["branch", "--show-current"])
        current_branch = branch.strip()
        
        # Get ahead/behind
        code, fetch_output, _ = self._run_git(["rev-list", "--left-right", "--count", f"HEAD...origin/{current_branch}"])
        
        ahead = 0
        behind = 0
        if fetch_output:
            parts = fetch_output.strip().split()
            if len(parts) >= 2:
                ahead = int(parts[0])
                behind = int(parts[1])
        
        return RepoSyncStatus(
            is_clean=(untracked + modified + len(conflicts)) == 0,
            current_branch=current_branch,
            ahead=ahead,
            behind=behind,
            untracked=untracked,
            modified=modified,
            staged=staged,
            conflicts=conflicts
        )
    
    def get_branches(self, remote: bool = False) -> List[GitBranch]:
        """Get list of branches."""
        branches = []
        
        if remote:
            code, stdout, _ = self._run_git(["branch", "-r", "--format=%(refname:short)|%(objectname:short)|%(subject)"])
        else:
            code, stdout, _ = self._run_git(["branch", "-v", "--format=%(refname:short)|%(objectname:short)|%(subject)"])
        
        if code != 0:
            return branches
        
        current, _, _ = self._run_git(["branch", "--show-current"])
        
        current_branch = str(current.strip()) if current else ""
        
        for line in stdout.strip().split("\n"):
            if not line or "->" in line:
                continue
            
            parts = line.split("|")
            if len(parts) >= 1:
                name = parts[0].strip()
                short_sha = parts[1].strip() if len(parts) > 1 else ""
                message = parts[2].strip() if len(parts) > 2 else ""
                
                branches.append(GitBranch(
                    name=name,
                    is_current=(name == current_branch),
                    is_remote=remote,
                    last_commit=short_sha,
                    last_commit_message=message
                ))
        
        return branches
    
    def create_branch(
        self,
        branch_name: str,
        from_branch: str = None,
        branch_type: BranchType = BranchType.FEATURE
    ) -> Dict:
        """Create a new branch."""
        if not self._is_git_repo:
            return {"success": False, "error": "Not a git repository"}
        
        # Determine source branch
        if from_branch is None:
            code, current, _ = self._run_git(["branch", "--show-current"])
            from_branch = current.strip() if code == 0 else "main"
        
        # Create branch
        code, stdout, stderr = self._run_git(["checkout", "-b", branch_name])
        
        if code == 0:
            self.db.log_operation("create_branch", branch_name, "success", from_branch)
            self.db.log_operation(
                "create_branch",
                branch_name,
                "success",
                f"Created from {from_branch}"
            )
            
            return {
                "success": True,
                "branch": branch_name,
                "created_from": from_branch,
                "message": f"Branch '{branch_name}' created from '{from_branch}'"
            }
        else:
            self.db.log_operation("create_branch", branch_name, "failed", stderr)
            return {
                "success": False,
                "error": stderr
            }
    
    def switch_branch(self, branch_name: str) -> Dict:
        """Switch to a branch."""
        if not self._is_git_repo:
            return {"success": False, "error": "Not a git repository"}
        
        # First save any changes
        status = self.get_status()
        if not status.is_clean:
            return {
                "success": False,
                "error": "Working directory has uncommitted changes. Commit or stash first."
            }
        
        code, stdout, stderr = self._run_git(["checkout", branch_name])
        
        if code == 0:
            self.db.log_operation("switch_branch", branch_name, "success")
            return {
                "success": True,
                "branch": branch_name,
                "message": f"Switched to branch '{branch_name}'"
            }
        else:
            return {
                "success": False,
                "error": stderr
            }
    
    def commit_changes(self, message: str, files: List[str] = None) -> Dict:
        """Commit changes."""
        if not self._is_git_repo:
            return {"success": False, "error": "Not a git repository"}
        
        # Stage files
        if files:
            for file in files:
                self._run_git(["add", file])
        else:
            code, _, _ = self._run_git(["add", "-A"])
            if code != 0:
                return {"success": False, "error": "Failed to stage files"}
        
        # Commit
        code, stdout, stderr = self._run_git(["commit", "-m", message])
        
        if code == 0:
            sha = stdout.strip().split("\n")[-1] if stdout else ""
            self.db.log_operation("commit", sha[:8], "success", message)
            
            return {
                "success": True,
                "commit_sha": sha,
                "message": message
            }
        else:
            return {
                "success": False,
                "error": stderr
            }
    
    def push(self, remote: str = "origin", branch: str = None) -> Dict:
        """Push to remote."""
        if not self._is_git_repo:
            return {"success": False, "error": "Not a git repository"}
        
        # Get current branch if not specified
        if branch is None:
            code, current, _ = self._run_git(["branch", "--show-current"])
            branch = current.strip() if code == 0 else "main"
        
        # Push
        code, stdout, stderr = self._run_git(["push", "-u", remote, branch])
        
        if code == 0:
            self.db.log_operation("push", f"{remote}/{branch}", "success")
            return {
                "success": True,
                "remote": remote,
                "branch": branch,
                "message": f"Pushed to {remote}/{branch}"
            }
        else:
            return {
                "success": False,
                "error": stderr
            }
    
    def pull(self, remote: str = "origin", branch: str = None) -> Dict:
        """Pull from remote."""
        if not self._is_git_repo:
            return {"success": False, "error": "Not a git repository"}
        
        if branch is None:
            code, current, _ = self._run_git(["branch", "--show-current"])
            branch = current.strip() if code == 0 else "main"
        
        code, stdout, stderr = self._run_git(["pull", remote, branch])
        
        if code == 0:
            self.db.log_operation("pull", f"{remote}/{branch}", "success")
            return {
                "success": True,
                "message": f"Pulled from {remote}/{branch}"
            }
        else:
            self.db.log_operation("pull", f"{remote}/{branch}", "failed", stderr)
            return {
                "success": False,
                "error": stderr
            }
    
    def detect_conflicts(self) -> List[ConflictInfo]:
        """Detect merge conflicts."""
        conflicts = []
        
        code, stdout, _ = self._run_git(["ls-files", "-u"])
        
        conflict_files = {}
        for line in stdout.strip().split("\n"):
            if not line:
                continue
            
            parts = line.split("\t")
            if len(parts) >= 2:
                file = parts[1]
                
                if file not in conflict_files:
                    conflict_files[file] = ConflictInfo(file=file)
                
                if "<<<<<<" in line or "======" in line or ">>>>>>" in line:
                    conflict_files[file].conflicts.append(line)
        
        return list(conflict_files.values())
    
    def get_remote_info(self) -> Dict:
        """Get remote repository information."""
        code, stdout, _ = self._run_git(["remote", "-v"])
        
        remotes = {}
        for line in stdout.strip().split("\n"):
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                url = parts[1]
                remotes[name] = url
        
        return {
            "remotes": remotes,
            "origin_url": remotes.get("origin", "")
        }
    
    def sync_with_remote(self) -> Dict:
        """Full sync: fetch, pull, merge status."""
        result = {
            "success": True,
            "steps": []
        }
        
        # Fetch
        code, _, stderr = self._run_git(["fetch", "--all"])
        result["steps"].append({
            "step": "fetch",
            "success": code == 0,
            "message": "Fetched all remotes" if code == 0 else stderr
        })
        
        if code != 0:
            result["success"] = False
        
        # Get status before pull
        status_before = self.get_status()
        result["steps"].append({
            "step": "status_before",
            "ahead": status_before.ahead,
            "behind": status_before.behind,
            "conflicts": len(status_before.conflicts)
        })
        
        # Pull if behind
        if status_before.behind > 0:
            pull_result = self.pull()
            result["steps"].append({
                "step": "pull",
                "success": pull_result["success"],
                "message": pull_result.get("message", "") or pull_result.get("error", "")
            })
            
            if not pull_result["success"]:
                result["success"] = False
        
        # Check for conflicts
        conflicts = self.detect_conflicts()
        if conflicts:
            result["steps"].append({
                "step": "conflicts",
                "success": False,
                "conflicts": [c.file for c in conflicts]
            })
            result["success"] = False
        
        # Get final status
        status_after = self.get_status()
        result["final_status"] = {
            "branch": status_after.current_branch,
            "ahead": status_after.ahead,
            "behind": status_after.behind,
            "is_clean": status_after.is_clean
        }
        
        return result
    
    def get_operation_history(self, limit: int = 20) -> List[Dict]:
        """Get git operation history."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM git_operations 
            ORDER BY executed_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row['id'],
                "type": row['operation_type'],
                "target": row['target'],
                "status": row['status'],
                "result": row['result'],
                "executed_at": row['executed_at']
            }
            for row in rows
        ]


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_github_center: Optional[GitHubCenter] = None


def get_github_center(repo_path: str = None) -> GitHubCenter:
    """Get or create global GitHub center instance."""
    global _github_center
    if _github_center is None:
        _github_center = GitHubCenter(repo_path)
    return _github_center
