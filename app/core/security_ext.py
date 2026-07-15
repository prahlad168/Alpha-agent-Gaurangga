"""
MAHALAKSMI AIOS v1.0 - Volume I Chapter 5: Enterprise Security Extension
Advanced cryptographic protections, JWT verification, and API security middleware
"""
import os
import re
import logging
import hashlib
import secrets
import sqlite3
import sys
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from functools import wraps

# Fix path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.settings import settings

logger = logging.getLogger(__name__)


# ============================================================================
# CRYPTOGRAPHIC UTILITIES
# ============================================================================

class CryptoManager:
    """
    Fernet symmetric encryption manager for secure data storage.
    """
    
    def __init__(self, key: str = None):
        if key is None:
            key = settings.secret_key
        
        # Derive a proper Fernet key from the secret
        self.fernet = self._derive_fernet_key(key)
        logger.info("CryptoManager initialized with Fernet encryption")
    
    def _derive_fernet_key(self, password: str) -> Fernet:
        """Derive a Fernet-compatible key from password."""
        # Use PBKDF2 to derive key
        salt = b'mahalaksmi_salt_v1'  # In production, use random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode())
        # Convert to Fernet-compatible format (URL-safe base64)
        import base64
        fernet_key = base64.urlsafe_b64encode(key)
        
        return Fernet(fernet_key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data, return base64 encoded."""
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data, return string."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Invalid encrypted data")
    
    def encrypt_dict(self, data: Dict) -> str:
        """Encrypt dictionary as JSON."""
        return self.encrypt(json.dumps(data))
    
    def decrypt_dict(self, encrypted_data: str) -> Dict:
        """Decrypt to dictionary."""
        return json.loads(self.decrypt(encrypted_data))
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> str:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            salt, pwd_hash = hashed.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            )
            return new_hash.hex() == pwd_hash
        except:
            return False


# ============================================================================
# JWT TOKEN MANAGER
# ============================================================================

class JWTManager:
    """
    JWT token verification with expiration controls.
    """
    
    def __init__(self):
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.expire_minutes = settings.access_token_expire_minutes
        logger.info("JWTManager initialized")
    
    def create_token(self, payload: Dict, expires_delta: timedelta = None) -> str:
        """Create JWT token with expiration."""
        to_encode = payload.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_hex(16)  # Unique token ID
        })
        
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def decode_optional(self, token: str) -> Optional[Dict]:
        """Decode token without verification (for inspection)."""
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False}
            )
        except:
            return None


# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    FastAPI security middleware for logging and injection prevention.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.blocked_ips: set = set()
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        
        # SQL injection patterns
        self.sql_patterns = [
            r"(\bunion\b|\bselect\b|\binsert\b|\bupdate\b|\bdelete\b|\bdrop\b)",
            r"(--|;|\/\*|\*\/)",
            r"(\bor\b.*=.*\bor\b|\band\b.*=.*\band\b)",
        ]
        
        # Command injection patterns
        self.cmd_patterns = [
            r"[;&|`$]",
            r"(\brm\b|\bcat\b|\bcp\b|\bmv\b|\becho\b|\bwget\b|\bcurl\b)",
        ]
        
        # Initialize audit database
        self._init_audit_db()
        
        logger.info("SecurityMiddleware initialized")
    
    def _init_audit_db(self):
        """Initialize audit database."""
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "security_audit.db"
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                ip_address TEXT,
                user_agent TEXT,
                endpoint TEXT,
                method TEXT,
                status_code INTEGER,
                blocked_reason TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failed_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                timestamp TEXT,
                endpoint TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through security checks."""
        client_ip = self._get_client_ip(request)
        path = request.url.path
        method = request.method
        
        # Check for blocked IP
        if client_ip in self.blocked_ips:
            await self._log_event("ip_blocked", client_ip, request, 403, "IP blocked")
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        
        # Check for too many failed attempts
        if await self._check_rate_limit(client_ip):
            await self._log_event("rate_limited", client_ip, request, 429, "Too many attempts")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
        
        # Check for injection attempts
        injection_check = await self._check_injection(request)
        if injection_check:
            await self._record_failed_attempt(client_ip, path)
            await self._log_event("injection_blocked", client_ip, request, 400, injection_check)
            return JSONResponse(
                status_code=400,
                content={"detail": f"Request blocked: {injection_check}"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Log successful requests (optional - for audit)
        if response.status_code >= 400:
            await self._log_event(
                "error_response", client_ip, request, response.status_code
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    async def _check_injection(self, request: Request) -> Optional[str]:
        """Check for SQL and command injection attempts."""
        # Check query parameters
        query_params = str(request.query_params)
        
        for pattern in self.sql_patterns:
            if re.search(pattern, query_params, re.IGNORECASE):
                return f"SQL injection pattern detected: {pattern}"
        
        for pattern in self.cmd_patterns:
            if re.search(pattern, query_params, re.IGNORECASE):
                return f"Command injection pattern detected: {pattern}"
        
        # Check path
        for pattern in self.sql_patterns + self.cmd_patterns:
            if re.search(pattern, request.url.path, re.IGNORECASE):
                return f"Path injection pattern detected"
        
        return None
    
    async def _check_rate_limit(self, ip: str) -> bool:
        """Check if IP has too many failed attempts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now() - self.lockout_duration
        cursor.execute(
            "SELECT COUNT(*) FROM failed_attempts WHERE ip_address = ? AND timestamp > ?",
            (ip, cutoff.isoformat())
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count >= self.max_failed_attempts
    
    async def _record_failed_attempt(self, ip: str, endpoint: str):
        """Record a failed attempt."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO failed_attempts (ip_address, timestamp, endpoint) VALUES (?, ?, ?)",
            (ip, datetime.now().isoformat(), endpoint)
        )
        
        conn.commit()
        conn.close()
        
        # Check if should block
        if await self._check_rate_limit(ip):
            self.blocked_ips.add(ip)
            logger.warning(f"IP {ip} blocked due to too many failed attempts")
    
    async def _log_event(
        self,
        event_type: str,
        ip: str,
        request: Request,
        status_code: int,
        blocked_reason: str = None
    ):
        """Log security event to audit database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log 
            (timestamp, event_type, ip_address, user_agent, endpoint, method, status_code, blocked_reason, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            event_type,
            ip,
            request.headers.get("user-agent", "unknown"),
            request.url.path,
            request.method,
            status_code,
            blocked_reason,
            json.dumps(dict(request.query_params))
        ))
        
        conn.commit()
        conn.close()
        
        logger.warning(
            f"Security event: {event_type} from {ip} on {request.url.path} - {blocked_reason or 'OK'}"
        )
    
    def get_audit_log(self, limit: int = 100, event_type: str = None) -> List[Dict]:
        """Get audit log entries."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if event_type:
            cursor.execute(
                "SELECT * FROM audit_log WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?",
                (event_type, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# ============================================================================
# LICENSE KEY GENERATOR
# ============================================================================

class LicenseKeyGenerator:
    """
    Cryptographically secure product license key generator.
    """
    
    def __init__(self):
        self.crypto = CryptoManager()
        logger.info("LicenseKeyGenerator initialized")
    
    def generate_key(
        self,
        product_id: str,
        customer_id: str,
        expires_days: int = 365
    ) -> Dict[str, str]:
        """
        Generate a secure license key.
        
        Format: MLK-XXXX-XXXX-XXXX-XXXX-PRODUCTID
        """
        # Generate random key
        key_parts = [
            secrets.token_hex(4).upper(),
            secrets.token_hex(4).upper(),
            secrets.token_hex(4).upper(),
            secrets.token_hex(4).upper(),
        ]
        
        key = f"MLK-{'-'.join(key_parts)}-{product_id[:8].upper()}"
        
        # Create license data
        license_data = {
            "key": key,
            "product_id": product_id,
            "customer_id": customer_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=expires_days)).isoformat(),
            "status": "active"
        }
        
        # Encrypt license data
        encrypted = self.crypto.encrypt_dict(license_data)
        
        return {
            "license_key": key,
            "license_data": encrypted,
            "expires_at": license_data["expires_at"]
        }
    
    def validate_key(self, license_key: str, license_data: str) -> Dict:
        """Validate a license key."""
        try:
            # Decrypt license data
            data = self.crypto.decrypt_dict(license_data)
            
            # Check if key matches
            if data["key"] != license_key:
                return {"valid": False, "reason": "Key mismatch"}
            
            # Check expiration
            expires = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > expires:
                return {"valid": False, "reason": "License expired"}
            
            # Check status
            if data.get("status") != "active":
                return {"valid": False, "reason": f"License {data['status']}"}
            
            return {
                "valid": True,
                "product_id": data["product_id"],
                "customer_id": data["customer_id"],
                "expires_at": data["expires_at"]
            }
            
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return {"valid": False, "reason": str(e)}


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

_crypto: Optional[CryptoManager] = None
_jwt: Optional[JWTManager] = None
_license_gen: Optional[LicenseKeyGenerator] = None


def get_crypto() -> CryptoManager:
    """Get crypto manager instance."""
    global _crypto
    if _crypto is None:
        _crypto = CryptoManager()
    return _crypto


def get_jwt_manager() -> JWTManager:
    """Get JWT manager instance."""
    global _jwt
    if _jwt is None:
        _jwt = JWTManager()
    return _jwt


def get_license_generator() -> LicenseKeyGenerator:
    """Get license generator instance."""
    global _license_gen
    if _license_gen is None:
        _license_gen = LicenseKeyGenerator()
    return _license_gen
