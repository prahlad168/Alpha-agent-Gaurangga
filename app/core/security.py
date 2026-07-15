"""
MAHALAKSMI AIOS v1.0 - Volume I: Security & RBAC
Enterprise-grade Role-Based Access Control System
"""
from enum import Enum
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
from functools import wraps

# Import settings
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import settings


class Permission(Enum):
    """System permissions."""
    # Executive Level
    EXEC_READ = "exec:read"
    EXEC_WRITE = "exec:write"
    EXEC_CONFIG = "exec:config"
    EXEC_REVENUE_VIEW = "exec:revenue:view"
    EXEC_REVENUE_TRANSFER = "exec:revenue:transfer"
    EXEC_SYSTEM_CONTROL = "exec:system:control"
    
    # Developer Level
    DEV_READ = "dev:read"
    DEV_WRITE = "dev:write"
    DEV_DEPLOY = "dev:deploy"
    DEV_TEST = "dev:test"
    DEV_CONFIG = "dev:config"
    
    # Operations Level
    OPS_READ = "ops:read"
    OPS_MONITOR = "ops:monitor"
    OPS_LOG = "ops:log"
    OPS_ALERT = "ops:alert"


class Role(Enum):
    """System roles."""
    EXECUTIVE = "executive"
    DEVELOPER = "developer"
    OPERATIONS = "operations"
    GUEST = "guest"


@dataclass
class User:
    """User account."""
    user_id: str
    username: str
    role: Role
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False


@dataclass
class TokenData:
    """JWT token payload."""
    user_id: str
    username: str
    role: str
    permissions: List[str]
    exp: datetime
    iat: datetime


class RBACMatrix:
    """
    Enterprise RBAC Matrix.
    Defines role-permission mappings.
    """
    
    # Role-permission mappings
    ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
        Role.EXECUTIVE: {
            Permission.EXEC_READ,
            Permission.EXEC_WRITE,
            Permission.EXEC_CONFIG,
            Permission.EXEC_REVENUE_VIEW,
            Permission.EXEC_REVENUE_TRANSFER,
            Permission.EXEC_SYSTEM_CONTROL,
            Permission.DEV_READ,
            Permission.DEV_WRITE,
            Permission.OPS_READ,
            Permission.OPS_MONITOR,
        },
        Role.DEVELOPER: {
            Permission.DEV_READ,
            Permission.DEV_WRITE,
            Permission.DEV_DEPLOY,
            Permission.DEV_TEST,
            Permission.DEV_CONFIG,
            Permission.OPS_READ,
        },
        Role.OPERATIONS: {
            Permission.OPS_READ,
            Permission.OPS_MONITOR,
            Permission.OPS_LOG,
            Permission.OPS_ALERT,
        },
        Role.GUEST: {
            Permission.OPS_READ,
        },
    }
    
    @classmethod
    def get_permissions_for_role(cls, role: Role) -> Set[Permission]:
        """Get all permissions for a role."""
        return cls.ROLE_PERMISSIONS.get(role, set())
    
    @classmethod
    def has_permission(cls, role: Role, permission: Permission) -> bool:
        """Check if role has specific permission."""
        return permission in cls.ROLE_PERMISSIONS.get(role, set())


class SecurityManager:
    """
    Central security manager for authentication and authorization.
    """
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.active_tokens: Dict[str, TokenData] = {}
        self._initialize_default_users()
    
    def _initialize_default_users(self) -> None:
        """Initialize default system users."""
        # CEO/Executive user
        ceo = User(
            user_id="ceo-001",
            username="pakpur",
            role=Role.EXECUTIVE,
            permissions=RBACMatrix.get_permissions_for_role(Role.EXECUTIVE)
        )
        self.users[ceo.user_id] = ceo
        
        # Developer user
        dev = User(
            user_id="dev-001",
            username="developer",
            role=Role.DEVELOPER,
            permissions=RBACMatrix.get_permissions_for_role(Role.DEVELOPER)
        )
        self.users[dev.user_id] = dev
        
        # Operations user
        ops = User(
            user_id="ops-001",
            username="operations",
            role=Role.OPERATIONS,
            permissions=RBACMatrix.get_permissions_for_role(Role.OPERATIONS)
        )
        self.users[ops.user_id] = ops
    
    def authenticate(self, username: str, password: Optional[str] = None) -> Optional[str]:
        """
        Authenticate user and return access token.
        For demo: accepts any password or no password for default users.
        """
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username and u.is_active:
                user = u
                break
        
        if not user:
            return None
        
        # Update last login
        user.last_login = datetime.now()
        
        # Generate JWT token
        token = self._generate_token(user)
        return token
    
    def _generate_token(self, user: User) -> str:
        """Generate JWT access token."""
        now = datetime.now()
        exp = now + timedelta(minutes=settings.access_token_expire_minutes)
        
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "iat": now,
            "exp": exp,
        }
        
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        
        # Store token data
        self.active_tokens[token] = TokenData(
            user_id=user.user_id,
            username=user.username,
            role=user.role.value,
            permissions=[p.value for p in user.permissions],
            exp=exp,
            iat=now
        )
        
        return token
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            
            return TokenData(
                user_id=payload["user_id"],
                username=payload["username"],
                role=payload["role"],
                permissions=payload["permissions"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"])
            )
        except jwt.ExpiredSignatureError:
            # Remove expired token
            self.active_tokens.pop(token, None)
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authorize(self, token: str, required_permission: Permission) -> bool:
        """Check if token has required permission."""
        token_data = self.verify_token(token)
        if not token_data:
            return False
        
        return required_permission.value in token_data.permissions
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (without sensitive data)."""
        return [
            {
                "user_id": u.user_id,
                "username": u.username,
                "role": u.role.value,
                "is_active": u.is_active,
                "permissions_count": len(u.permissions),
                "last_login": u.last_login.isoformat() if u.last_login else None,
            }
            for u in self.users.values()
        ]
    
    def get_rbac_matrix(self) -> Dict[str, List[str]]:
        """Get full RBAC permission matrix."""
        return {
            role.value: [p.value for p in permissions]
            for role, permissions in RBACMatrix.ROLE_PERMISSIONS.items()
        }


# Global security manager
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get or create global security manager."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Permission check logic would go here
            # For now, allow all authenticated requests
            return await func(*args, **kwargs)
        return wrapper
    return decorator
