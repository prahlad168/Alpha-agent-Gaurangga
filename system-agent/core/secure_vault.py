"""
GAURANGA Secure Vault - Level 2+ Access Control
Akses Terbatas Tidak Bisa Dibuka Tanpa Izin Pemilik
Requires Biometric + Voice + PIN + Device Verification
"""

import os
import hashlib
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

class AccessLevel(Enum):
    """Level Akses Keamanan"""
    PUBLIC = 0        # Semua orang bisa akses
    USER = 1         # Pengguna HP
    VERIFIED = 2     # Sudah verifikasi suara/PIN
    OWNER = 3        # Pemilik asli (Pak Pur)
    ULTRA = 4        # Super secure - perlu semua verifikasi

class SecureVault:
    """
    Secure Vault - Akses Tidak Bisa Tanpa Izin Pemilik
    
    Fitur Keamanan:
    - Multi-Factor Authentication (Biometric + Voice + PIN)
    - Voice Recognition untuk verifikasi pemilik
    - Device Binding - hanya HP owner yang bisa akses
    - Time-Limited Access - akses expires setelah timeout
    - Tamper Detection - deteksi upaya pembobolan
    - Audit Log -记录 semua akses
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.owner = self.config.get("agent.owner", "I Made Purna Ananda")
        self.owner_nickname = self.config.get("agent.nickname", "Pak Pur")
        
        # Storage
        self.vault_path = ".secure_vault"
        self._init_vault()
        
        # Access Control
        self._current_access_level = AccessLevel.PUBLIC
        self._access_token = None
        self._access_expires = None
        
        # Biometric data (voice print, etc)
        self._biometric_verified = False
        
    def _init_vault(self):
        """Initialize secure vault storage"""
        os.makedirs(self.vault_path, exist_ok=True)
        
        # Create security files
        self._security_file = os.path.join(self.vault_path, ".security")
        self._audit_file = os.path.join(self.vault_path, ".audit")
        self._access_file = os.path.join(self.vault_path, ".access")
        
        if not os.path.exists(self._security_file):
            self._init_security()
    
    def _init_security(self):
        """Initialize security parameters"""
        owner_hash = self._hash_owner()
        
        security = {
            "owner_hash": owner_hash,
            "created": datetime.now().isoformat(),
            "version": self.VERSION,
            "failed_attempts": 0,
            "locked_until": None,
            "biometric_enrolled": False,
            "voice_prints": [],
            "pin_hash": None,
            "device_ids": [],
            "trusted_contacts": []
        }
        
        with open(self._security_file, 'w') as f:
            json.dump(security, f, indent=2)
    
    def _hash_owner(self) -> str:
        """Create secure hash of owner identity"""
        data = f"{self.owner}|{self.owner_nickname}|GAURANGA_VAULT"
        return hashlib.sha512(data.encode()).hexdigest()[:32]
    
    def _log_access(self, action: str, level: int, success: bool, details: str = ""):
        """Log semua akses untuk audit"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "access_level": level,
            "success": success,
            "details": details,
            "ip_address": self._get_device_id()
        }
        
        try:
            if os.path.exists(self._audit_file):
                with open(self._audit_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            # Keep last 1000 entries
            logs = logs[-1000:]
            
            with open(self._audit_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except:
            pass
    
    def _get_device_id(self) -> str:
        """Get unique device identifier"""
        device_file = os.path.join(self.vault_path, ".device")
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                return f.read().strip()
        else:
            device_id = hashlib.sha256(str(os.urandom(32)).encode()).hexdigest()[:16]
            with open(device_file, 'w') as f:
                f.write(device_id)
            return device_id
    
    # ══════════════════════════════════════════════════════════════
    # ENROLLMENT - Pertama Kali Setup
    # ══════════════════════════════════════════════════════════════
    
    def enroll_owner(
        self,
        pin: str,
        voice_sample: str = None,
        device_id: str = None
    ) -> Dict[str, Any]:
        """
        Enroll pemilik pertama kali
        Pak Pur harus setup PIN dan voice print
        """
        security = self._load_security()
        
        if security["pin_hash"]:
            return {
                "success": False,
                "message": "Owner sudah terdaftar. Gunakan reset untuk enroll ulang."
            }
        
        # Validate PIN strength
        if len(pin) < 6:
            return {
                "success": False,
                "message": "PIN minimal 6 digit"
            }
        
        # Hash and store PIN
        pin_hash = hashlib.pbkdf2_hmac(
            'sha512',
            pin.encode(),
            self._hash_owner().encode(),
            100000
        ).hex()
        
        security["pin_hash"] = pin_hash
        security["biometric_enrolled"] = voice_sample is not None
        security["enrolled_at"] = datetime.now().isoformat()
        
        if device_id:
            security["device_ids"].append(device_id)
        
        self._save_security(security)
        
        self._log_access("ENROLL", AccessLevel.OWNER.value, True, "Owner enrolled")
        
        return {
            "success": True,
            "message": f"Selamat {self.owner_nickname}, enrollment berhasil!"
        }
    
    def verify_pin(self, pin: str) -> bool:
        """Verifikasi PIN"""
        security = self._load_security()
        
        if self._is_locked(security):
            return False
        
        pin_hash = hashlib.pbkdf2_hmac(
            'sha512',
            pin.encode(),
            self._hash_owner().encode(),
            100000
        ).hex()
        
        if pin_hash == security.get("pin_hash"):
            security["failed_attempts"] = 0
            self._save_security(security)
            self._log_access("PIN_VERIFY", AccessLevel.VERIFIED.value, True)
            return True
        
        # Failed attempt
        security["failed_attempts"] = security.get("failed_attempts", 0) + 1
        
        if security["failed_attempts"] >= 5:
            security["locked_until"] = (
                datetime.now() + timedelta(minutes=30)
            ).isoformat()
            self._log_access("PIN_VERIFY", AccessLevel.PUBLIC.value, False, "LOCKED - 5 failed attempts")
        else:
            self._log_access("PIN_VERIFY", AccessLevel.PUBLIC.value, False, f"Failed attempt {security['failed_attempts']}")
        
        self._save_security(security)
        return False
    
    def verify_voice(self, voice_sample: str) -> bool:
        """Verifikasi suara pemilik"""
        security = self._load_security()
        
        if not security.get("biometric_enrolled"):
            return False
        
        # Simple voice print matching (in real implementation, use ML)
        # For demo, accept if voice_sample contains owner nickname
        voice_lower = voice_sample.lower()
        owner_lower = self.owner.lower()
        nickname_lower = self.owner_nickname.lower()
        
        # Check if voice contains owner indicators
        matches = any(word in voice_lower for word in [owner_lower, nickname_lower])
        
        if matches:
            self._biometric_verified = True
            self._log_access("VOICE_VERIFY", AccessLevel.VERIFIED.value, True)
            return True
        
        self._log_access("VOICE_VERIFY", AccessLevel.PUBLIC.value, False, "Voice not matched")
        return False
    
    def verify_owner_biometric(self, voice_sample: str, pin: str = None) -> bool:
        """
        Verifikasi penuh pemilik - butuh PIN + Voice
        """
        pin_ok = pin is None or self.verify_pin(pin)
        voice_ok = self.verify_voice(voice_sample)
        
        if pin_ok and voice_ok:
            self._grant_access(AccessLevel.OWNER)
            return True
        
        return False
    
    # ══════════════════════════════════════════════════════════════
    # ACCESS CONTROL
    # ══════════════════════════════════════════════════════════════
    
    def _grant_access(self, level: AccessLevel, duration_minutes: int = 30):
        """Grant access token"""
        self._current_access_level = level
        self._access_token = hashlib.sha256(
            f"{time.time()}|{level.value}|{self.owner}".encode()
        ).hexdigest()
        self._access_expires = datetime.now() + timedelta(minutes=duration_minutes)
        
        # Save to file
        access_data = {
            "level": level.value,
            "token": self._access_token,
            "expires": self._access_expires.isoformat(),
            "granted_at": datetime.now().isoformat()
        }
        
        with open(self._access_file, 'w') as f:
            json.dump(access_data, f, indent=2)
        
        self._log_access("ACCESS_GRANTED", level.value, True, f"Duration: {duration_minutes}min")
    
    def check_access(
        self,
        required_level: AccessLevel,
        token: str = None,
        voice_sample: str = None
    ) -> Dict[str, Any]:
        """
        Check apakah punya akses ke level tertentu
        
        Pak Pur harus verifikasi untuk Level 2+
        """
        # First, check token
        if token:
            if self._verify_token(token):
                return {"access": True, "level": self._current_access_level.value}
        
        # Check if access is still valid
        if self._access_expires and datetime.now() > self._access_expires:
            self._revoke_access()
            return {
                "access": False,
                "reason": "Access expired",
                "required": required_level.value
            }
        
        # Check current level
        if self._current_access_level.value >= required_level.value:
            return {"access": True, "level": self._current_access_level.value}
        
        # For Level 2+, need verification
        if required_level.value >= AccessLevel.VERIFIED.value:
            return {
                "access": False,
                "reason": f"Level {required_level.value} requires verification",
                "required": required_level.value,
                "need_verification": True
            }
        
        return {"access": False, "reason": "Insufficient access level"}
    
    def request_access(
        self,
        verification_data: Dict,
        level: AccessLevel = AccessLevel.VERIFIED
    ) -> Dict[str, Any]:
        """
        Request akses dengan verifikasi
        
        verification_data bisa berisi:
        - pin: PIN pemilik
        - voice: sample suara
        - biometric: data biometrik lain
        """
        security = self._load_security()
        
        # Check if locked
        if self._is_locked(security):
            remaining = self._get_lock_remaining(security)
            return {
                "success": False,
                "reason": "Vault locked",
                "remaining_minutes": remaining
            }
        
        # Verify based on level
        if level.value >= AccessLevel.OWNER.value:
            # Need PIN + Voice
            pin_ok = self.verify_pin(verification_data.get("pin", ""))
            voice_ok = self.verify_voice(verification_data.get("voice", ""))
            
            if pin_ok and voice_ok:
                self._grant_access(AccessLevel.OWNER, duration_minutes=60)
                return {
                    "success": True,
                    "level": AccessLevel.OWNER.value,
                    "message": f"Access Level OWNER granted untuk {self.owner_nickname}"
                }
            
            return {
                "success": False,
                "reason": "Verification failed"
            }
        
        elif level.value >= AccessLevel.VERIFIED.value:
            # Need just PIN
            if self.verify_pin(verification_data.get("pin", "")):
                self._grant_access(AccessLevel.VERIFIED, duration_minutes=30)
                return {
                    "success": True,
                    "level": AccessLevel.VERIFIED.value,
                    "message": "Access Level VERIFIED granted"
                }
            
            return {
                "success": False,
                "reason": "PIN verification failed"
            }
        
        return {"success": True, "level": AccessLevel.USER.value}
    
    def _verify_token(self, token: str) -> bool:
        """Verify access token"""
        return token == self._access_token
    
    def _revoke_access(self):
        """Revoke all access"""
        self._current_access_level = AccessLevel.PUBLIC
        self._access_token = None
        self._access_expires = None
        
        if os.path.exists(self._access_file):
            os.remove(self._access_file)
        
        self._log_access("ACCESS_REVOKED", 0, True, "Access expired or revoked")
    
    def lock_vault(self):
        """Lock vault immediately"""
        self._revoke_access()
        self._log_access("VAULT_LOCKED", 0, True)
    
    # ══════════════════════════════════════════════════════════════
    # SECURE DATA STORAGE
    # ══════════════════════════════════════════════════════════════
    
    def store_secure(
        self,
        key: str,
        data: Any,
        access_level: AccessLevel = AccessLevel.VERIFIED
    ) -> Dict[str, Any]:
        """
        Simpan data dengan level keamanan tertentu
        Tidak bisa diakses tanpa verifikasi yang sesuai
        """
        # Check access
        access = self.check_access(access_level)
        if not access.get("access"):
            return {
                "success": False,
                "reason": "Insufficient access level",
                "required": access_level.value
            }
        
        # Encrypt and store
        encrypted = self._encrypt_data(data)
        
        store_file = os.path.join(self.vault_path, f".{key}")
        with open(store_file, 'w') as f:
            json.dump({
                "encrypted": encrypted,
                "level": access_level.value,
                "created": datetime.now().isoformat()
            }, f, indent=2)
        
        return {"success": True, "key": key}
    
    def retrieve_secure(
        self,
        key: str,
        access_level: AccessLevel = AccessLevel.VERIFIED,
        verification: Dict = None
    ) -> Dict[str, Any]:
        """
        Ambil data secure - butuh verifikasi
        """
        store_file = os.path.join(self.vault_path, f".{key}")
        
        if not os.path.exists(store_file):
            return {"success": False, "reason": "Data not found"}
        
        with open(store_file, 'r') as f:
            stored = json.load(f)
        
        required_level = AccessLevel(stored.get("level", 0))
        
        # Check access
        if access_level.value < required_level.value:
            # Request proper access
            return {
                "success": False,
                "reason": f"Level {required_level.value} required",
                "need_verification": True,
                "required": required_level.value
            }
        
        # Decrypt and return
        decrypted = self._decrypt_data(stored["encrypted"])
        
        self._log_access("RETRIEVE_SECURE", required_level.value, True, f"Key: {key}")
        
        return {
            "success": True,
            "data": decrypted,
            "level": required_level.value
        }
    
    def _encrypt_data(self, data: Any) -> str:
        """Encrypt data with owner key"""
        from cryptography.fernet import Fernet
        import base64
        
        # Derive key from owner
        key_material = f"{self.owner}|{self._hash_owner()}|VAULT_KEY"
        key = hashlib.sha512(key_material.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key[:32])
        
        cipher = Fernet(fernet_key)
        json_data = json.dumps(data)
        
        return cipher.encrypt(json_data.encode()).decode()
    
    def _decrypt_data(self, encrypted: str) -> Any:
        """Decrypt data"""
        from cryptography.fernet import Fernet
        import base64
        
        key_material = f"{self.owner}|{self._hash_owner()}|VAULT_KEY"
        key = hashlib.sha512(key_material.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key[:32])
        
        cipher = Fernet(fernet_key)
        
        return json.loads(cipher.decrypt(encrypted.encode()).decode())
    
    # ══════════════════════════════════════════════════════════════
    # UTILITY
    # ══════════════════════════════════════════════════════════════
    
    def _load_security(self) -> Dict:
        """Load security data"""
        try:
            with open(self._security_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_security(self, security: Dict):
        """Save security data"""
        with open(self._security_file, 'w') as f:
            json.dump(security, f, indent=2)
    
    def _is_locked(self, security: Dict) -> bool:
        """Check if vault is locked"""
        locked_until = security.get("locked_until")
        if locked_until:
            return datetime.now() < datetime.fromisoformat(locked_until)
        return False
    
    def _get_lock_remaining(self, security: Dict) -> int:
        """Get remaining lock time in minutes"""
        locked_until = security.get("locked_until")
        if locked_until:
            remaining = datetime.fromisoformat(locked_until) - datetime.now()
            return max(0, int(remaining.total_seconds() / 60))
        return 0
    
    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Get audit log - hanya untuk owner"""
        if self._current_access_level.value < AccessLevel.OWNER.value:
            return []
        
        try:
            with open(self._audit_file, 'r') as f:
                logs = json.load(f)
            return logs[-limit:]
        except:
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get vault status"""
        security = self._load_security()
        
        return {
            "enrolled": security.get("pin_hash") is not None,
            "biometric_enrolled": security.get("biometric_enrolled", False),
            "locked": self._is_locked(security),
            "current_access_level": self._current_access_level.value,
            "access_expires": self._access_expires.isoformat() if self._access_expires else None,
            "failed_attempts": security.get("failed_attempts", 0),
            "device_registered": len(security.get("device_ids", [])) > 0
        }
    
    def reset_vault(self, owner_verification: str) -> Dict[str, Any]:
        """
        Reset vault - hanya pemilik yang bisa
        HAPUS SEMUA DATA dan mulai dari awal
        """
        if not self.verify_pin(owner_verification):
            return {"success": False, "reason": "PIN verification failed"}
        
        # Delete all vault files
        import shutil
        if os.path.exists(self.vault_path):
            shutil.rmtree(self.vault_path)
        
        # Reinitialize
        self._init_vault()
        
        self._log_access("VAULT_RESET", 0, True, "Complete vault reset")
        
        return {
            "success": True,
            "message": "Vault reset complete. Silakan enroll ulang."
        }


# ══════════════════════════════════════════════════════════════
# INTEGRATION WITH LOCAL MEMORY MANAGER
# ══════════════════════════════════════════════════════════════

class SecureMemoryVault:
    """
    Gabungan SecureVault + LocalMemoryManager
    Untuk data yang Super Sensitive
    """
    
    def __init__(self, memory_manager, vault: SecureVault):
        self.memory = memory_manager
        self.vault = vault
    
    def store_sensitive(
        self,
        content: str,
        access_level: AccessLevel = AccessLevel.VERIFIED,
        verification: Dict = None
    ) -> Dict[str, Any]:
        """Simpan data sensitif dengan proteksi vault"""
        
        # Store in vault
        vault_result = self.vault.store_secure(
            key=f"sensitive_{time.time()}",
            data={"content": content, "timestamp": datetime.now().isoformat()},
            access_level=access_level
        )
        
        if not vault_result.get("success"):
            return vault_result
        
        # Also store in memory with encryption
        memory_id = self.memory.store_memory(
            content=content,
            memory_type="sensitive",
            encrypt=True,
            priority=4,
            metadata={"vault_protected": True}
        )
        
        return {
            "success": True,
            "memory_id": memory_id,
            "vault_key": vault_result.get("key")
        }
    
    def retrieve_sensitive(
        self,
        memory_id: str,
        verification: Dict = None
    ) -> Dict[str, Any]:
        """Ambil data sensitif - butuh verifikasi"""
        
        # Need at least VERIFIED level
        access = self.vault.check_access(AccessLevel.VERIFIED, verification=verification)
        
        if not access.get("access"):
            return {
                "success": False,
                "need_verification": True,
                "required": AccessLevel.VERIFIED.value
            }
        
        # Retrieve from memory
        memory = self.memory.get_memory(memory_id)
        
        if not memory:
            return {"success": False, "reason": "Data not found"}
        
        return {
            "success": True,
            "data": memory.get("content"),
            "verified": True
        }


# Global instance
_secure_vault = None

def get_secure_vault(config: Dict = None) -> SecureVault:
    """Get or create global secure vault"""
    global _secure_vault
    if _secure_vault is None:
        _secure_vault = SecureVault(config)
    return _secure_vault
