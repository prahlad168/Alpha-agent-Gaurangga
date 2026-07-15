"""
MAHALAKSMI AIOS v1.0 - Volume I Chapter 4: Hierarchical RBAC System
Advanced Role-Based Access Control with resource-level permissions
"""
import os
import sys
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class Role(Enum):
    """Hierarchical user roles."""
    SUPER_ADMIN = "super_admin"      # Pak Pur - Full access
    ADMIN = "admin"                # Senior admin
    MANAGER = "manager"             # Department head
    OPERATOR = "operator"           # Regular user
    GUEST = "guest"                # Read-only access


class Permission(Enum):
    """Resource-level permissions."""
    # Finance permissions
    FINANCE_READ = "finance:read"
    FINANCE_WRITE = "finance:write"
    FINANCE_DELETE = "finance:delete"
    
    # Product permissions
    PRODUCT_READ = "product:read"
    PRODUCT_WRITE = "product:write"
    PRODUCT_LICENSE = "product:license"
    
    # Revenue permissions
    REVENUE_READ = "revenue:read"
    REVENUE_WRITE = "revenue:write"
    
    # Customer permissions
    CUSTOMER_READ = "customer:read"
    CUSTOMER_WRITE = "customer:write"
    CUSTOMER_DELETE = "customer:delete"
    
    # Disaster Recovery permissions
    DR_READ = "dr:read"
    DR_TRIGGER = "dr:trigger"
    DR_RECOVER = "dr:recover"
    
    # System permissions
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_CONFIG = "system:config"
    
    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Repository permissions
    REPO_READ = "repo:read"
    REPO_WRITE = "repo:write"
    REPO_ARCHIVE = "repo:archive"
    
    # Workflow permissions
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_WRITE = "workflow:write"
    WORKFLOW_EXECUTE = "workflow:execute"


class Resource(Enum):
    """System resources."""
    FINANCE = "finance"
    PRODUCT = "product"
    REVENUE = "revenue"
    CUSTOMER = "customer"
    DISASTER_RECOVERY = "disaster_recovery"
    SYSTEM = "system"
    USER = "user"
    REPOSITORY = "repository"
    WORKFLOW = "workflow"


@dataclass
class User:
    """User entity."""
    user_id: str
    username: str
    email: str
    role: Role
    permissions: Set[str] = field(default_factory=set)
    created_at: str = ""
    last_login: str = ""


@dataclass
class RolePermission:
    """Role permission mapping."""
    role: Role
    permissions: Set[Permission]


# ============================================================================
# RBAC DATABASE
# ============================================================================

class RBACDB:
    """SQLite database for RBAC."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "rbac.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT,
                role TEXT,
                permissions TEXT,
                created_at TEXT,
                last_login TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                role TEXT,
                assigned_by TEXT,
                assigned_at TEXT,
                expires_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_user(self, user: User) -> bool:
        """Save user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert Permission enum to strings
            perms_list = [p.value if isinstance(p, Permission) else str(p) for p in user.permissions]
            
            cursor.execute("""
                INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user.user_id,
                user.username,
                user.email,
                user.role.value,
                json.dumps(perms_list),
                user.created_at,
                user.last_login
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save user: {e}")
            return False
    
    def get_user(self, user_id: str = None, username: str = None) -> Optional[User]:
        """Get user by ID or username."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        elif username:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        else:
            return None
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_user(row)
        return None
    
    def _row_to_user(self, row) -> User:
        """Convert row to User."""
        perms_data = json.loads(row['permissions']) if row['permissions'] else []
        # Convert string permissions to Permission enum
        perms = set()
        for p in perms_data:
            try:
                perms.add(Permission(p))
            except ValueError:
                perms.add(p)  # Keep as string if not a valid Permission
        return User(
            user_id=row['user_id'],
            username=row['username'],
            email=row['email'] or "",
            role=Role(row['role']),
            permissions=perms,
            created_at=row['created_at'] or "",
            last_login=row['last_login'] or ""
        )
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_user(row) for row in rows]
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False


# ============================================================================
# ROLE HIERARCHY MATRIX
# ============================================================================

class RoleHierarchy:
    """
    Role hierarchy and permission matrix.
    Higher roles inherit permissions from lower roles.
    """
    
    # Role hierarchy (higher index = higher privilege)
    ROLE_LEVELS = {
        Role.GUEST: 1,
        Role.OPERATOR: 2,
        Role.MANAGER: 3,
        Role.ADMIN: 4,
        Role.SUPER_ADMIN: 5
    }
    
    # Base permissions per role
    BASE_PERMISSIONS = {
        Role.SUPER_ADMIN: {
            Permission.FINANCE_READ, Permission.FINANCE_WRITE, Permission.FINANCE_DELETE,
            Permission.PRODUCT_READ, Permission.PRODUCT_WRITE, Permission.PRODUCT_LICENSE,
            Permission.REVENUE_READ, Permission.REVENUE_WRITE,
            Permission.CUSTOMER_READ, Permission.CUSTOMER_WRITE, Permission.CUSTOMER_DELETE,
            Permission.DR_READ, Permission.DR_TRIGGER, Permission.DR_RECOVER,
            Permission.SYSTEM_READ, Permission.SYSTEM_WRITE, Permission.SYSTEM_CONFIG,
            Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE,
            Permission.REPO_READ, Permission.REPO_WRITE, Permission.REPO_ARCHIVE,
            Permission.WORKFLOW_READ, Permission.WORKFLOW_WRITE, Permission.WORKFLOW_EXECUTE,
        },
        Role.ADMIN: {
            Permission.FINANCE_READ, Permission.FINANCE_WRITE,
            Permission.PRODUCT_READ, Permission.PRODUCT_WRITE, Permission.PRODUCT_LICENSE,
            Permission.REVENUE_READ, Permission.REVENUE_WRITE,
            Permission.CUSTOMER_READ, Permission.CUSTOMER_WRITE,
            Permission.DR_READ, Permission.DR_TRIGGER,
            Permission.SYSTEM_READ, Permission.SYSTEM_WRITE,
            Permission.USER_READ, Permission.USER_WRITE,
            Permission.REPO_READ, Permission.REPO_WRITE, Permission.REPO_ARCHIVE,
            Permission.WORKFLOW_READ, Permission.WORKFLOW_WRITE, Permission.WORKFLOW_EXECUTE,
        },
        Role.MANAGER: {
            Permission.FINANCE_READ,
            Permission.PRODUCT_READ,
            Permission.REVENUE_READ,
            Permission.CUSTOMER_READ, Permission.CUSTOMER_WRITE,
            Permission.DR_READ,
            Permission.SYSTEM_READ,
            Permission.USER_READ,
            Permission.REPO_READ,
            Permission.WORKFLOW_READ, Permission.WORKFLOW_WRITE,
        },
        Role.OPERATOR: {
            Permission.PRODUCT_READ,
            Permission.REVENUE_READ,
            Permission.CUSTOMER_READ,
            Permission.DR_READ,
            Permission.SYSTEM_READ,
            Permission.REPO_READ,
            Permission.WORKFLOW_READ,
        },
        Role.GUEST: {
            Permission.PRODUCT_READ,
            Permission.REVENUE_READ,
            Permission.DR_READ,
            Permission.SYSTEM_READ,
            Permission.REPO_READ,
        },
    }
    
    @classmethod
    def get_all_permissions(cls, role: Role) -> Set[Permission]:
        """Get all permissions for a role (including inherited)."""
        perms = set()
        level = cls.ROLE_LEVELS[role]
        
        # Inherit from lower roles
        for r, l in cls.ROLE_LEVELS.items():
            if l <= level:
                perms.update(cls.BASE_PERMISSIONS.get(r, set()))
        
        return perms
    
    @classmethod
    def has_role(cls, user_role: Role, required_role: Role) -> bool:
        """Check if user role meets required role level."""
        return cls.ROLE_LEVELS[user_role] >= cls.ROLE_LEVELS[required_role]
    
    @classmethod
    def can_access(cls, user_role: Role, permission: Permission) -> bool:
        """Check if role has permission."""
        return permission in cls.get_all_permissions(user_role)


# ============================================================================
# RBAC ENGINE
# ============================================================================

class RBACEngine:
    """
    Hierarchical Role-Based Access Control Engine.
    Manages users, roles, and resource-level permissions.
    """
    
    def __init__(self):
        self.db = RBACDB()
        
        # Initialize default super admin (Pak Pur)
        self._init_default_users()
        
        logger.info("RBACEngine initialized")
    
    def _init_default_users(self):
        """Initialize default users."""
        # Super Admin - Pak Pur
        if not self.db.get_user(username="pakpur"):
            import hashlib
            user_id = hashlib.md5("pakpur_system".encode()).hexdigest()[:12].upper()
            
            user = User(
                user_id=f"USER-{user_id}",
                username="pakpur",
                email="pakhpur@mahalakshmi.id",
                role=Role.SUPER_ADMIN,
                permissions=RoleHierarchy.get_all_permissions(Role.SUPER_ADMIN),
                created_at=datetime.now().isoformat()
            )
            self.db.save_user(user)
            logger.info(f"Created default SUPER_ADMIN: {user.username}")
        
        # Create test users for different roles
        test_users = [
            ("admin_test", Role.ADMIN),
            ("manager_test", Role.MANAGER),
            ("operator_test", Role.OPERATOR),
            ("guest_test", Role.GUEST),
        ]
        
        for username, role in test_users:
            if not self.db.get_user(username=username):
                import hashlib
                user_id = hashlib.md5(f"{username}_system".encode()).hexdigest()[:12].upper()
                
                user = User(
                    user_id=f"USER-{user_id}",
                    username=username,
                    email=f"{username}@test.local",
                    role=role,
                    permissions=RoleHierarchy.get_all_permissions(role),
                    created_at=datetime.now().isoformat()
                )
                self.db.save_user(user)
    
    def create_user(
        self,
        username: str,
        email: str,
        role: Role,
        created_by: str = "system"
    ) -> User:
        """Create a new user."""
        import hashlib
        
        user_id = hashlib.md5(
            f"{username}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        
        user = User(
            user_id=f"USER-{user_id}",
            username=username,
            email=email,
            role=role,
            permissions=RoleHierarchy.get_all_permissions(role),
            created_at=datetime.now().isoformat()
        )
        
        self.db.save_user(user)
        logger.info(f"User created: {username} with role {role.value}")
        
        return user
    
    def assign_role(self, user_id: str, role: Role, assigned_by: str) -> bool:
        """Assign a role to a user."""
        user = self.db.get_user(user_id=user_id)
        if not user:
            return False
        
        user.role = role
        user.permissions = RoleHierarchy.get_all_permissions(role)
        
        self.db.save_user(user)
        
        # Log assignment
        logger.info(f"Role {role.value} assigned to user {user_id} by {assigned_by}")
        
        return True
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission."""
        user = self.db.get_user(user_id=user_id)
        if not user:
            return False
        
        # Check base permissions
        if permission in RoleHierarchy.get_all_permissions(user.role):
            return True
        
        # Check explicit permissions
        return permission.value in user.permissions
    
    def check_resource_access(
        self,
        user_id: str,
        resource: Resource,
        access_type: str = "read"
    ) -> bool:
        """Check resource-level access."""
        user = self.db.get_user(user_id=user_id)
        if not user:
            return False
        
        # Map resource to permission prefix
        resource_map = {
            Resource.FINANCE: "finance",
            Resource.PRODUCT: "product",
            Resource.REVENUE: "revenue",
            Resource.CUSTOMER: "customer",
            Resource.DISASTER_RECOVERY: "dr",
            Resource.SYSTEM: "system",
            Resource.USER: "user",
            Resource.REPOSITORY: "repo",
            Resource.WORKFLOW: "workflow",
        }
        
        perm_map = {
            "read": "read",
            "write": "write",
            "delete": "delete",
            "execute": "execute",
            "trigger": "trigger",
            "recover": "recover",
            "config": "config",
            "license": "license",
        }
        
        access_suffix = perm_map.get(access_type, "read")
        resource_prefix = resource_map.get(resource, resource.value)
        permission_str = f"{resource_prefix}:{access_suffix}"
        
        try:
            perm = Permission(permission_str)
            return self.check_permission(user_id, perm)
        except ValueError:
            return False
    
    def get_user_permissions(self, user_id: str) -> Dict:
        """Get user's effective permissions."""
        user = self.db.get_user(user_id=user_id)
        if not user:
            return {"error": "User not found"}
        
        all_perms = RoleHierarchy.get_all_permissions(user.role)
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in all_perms],
            "permission_count": len(all_perms)
        }
    
    def get_role_matrix(self) -> Dict:
        """Get complete role-permission matrix."""
        matrix = {}
        
        for role in Role:
            perms = RoleHierarchy.get_all_permissions(role)
            matrix[role.value] = {
                "level": RoleHierarchy.ROLE_LEVELS[role],
                "permissions": sorted([p.value for p in perms]),
                "count": len(perms)
            }
        
        return {
            "roles": matrix,
            "total_roles": len(Role),
            "total_permissions": len(Permission)
        }
    
    def list_users(self, role: Role = None) -> List[Dict]:
        """List all users."""
        users = self.db.get_all_users()
        
        if role:
            users = [u for u in users if u.role == role]
        
        return [
            {
                "user_id": u.user_id,
                "username": u.username,
                "email": u.email,
                "role": u.role.value,
                "permissions_count": len(u.permissions),
                "created_at": u.created_at,
                "last_login": u.last_login
            }
            for u in users
        ]


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_rbac_engine: Optional[RBACEngine] = None


def get_rbac_engine() -> RBACEngine:
    """Get or create global RBAC engine."""
    global _rbac_engine
    if _rbac_engine is None:
        _rbac_engine = RBACEngine()
    return _rbac_engine
