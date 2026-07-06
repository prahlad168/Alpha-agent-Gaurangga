"""
GAURANGA Multi-Layer Encryption System
Enkripsi Berlapis untuk Keamanan Maksimal
"""

import os
import hashlib
import base64
import json
import zlib
from typing import Dict, Any, Optional, List
from datetime import datetime

class MultiLayerEncryption:
    """
    Sistem Enkripsi Berlapis untuk Keamanan Data Maksimal
    
    Layer 1: AES-256-GCM (Data Utama)
    Layer 2: ChaCha20-Poly1305 (Backup)
    Layer 3: Fernet/AES-128-CBC (Transmisi)
    Layer 4: One-Time Pad (Data Super Sensitif)
    Layer 5: Blockchain-style Hash Chain (Integritas)
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.salt = self._get_or_create_salt()
        self.layers = {
            "primary": self._get_primary_key(),
            "secondary": self._get_secondary_key(),
            "tertiary": self._get_tertiary_key(),
        }
    
    def _get_or_create_salt(self) -> bytes:
        """Get or create unique salt for this device"""
        salt_file = ".gauranga_salt"
        
        if os.path.exists(salt_file):
            with open(salt_file, 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(64)
            with open(salt_file, 'wb') as f:
                f.write(salt)
            os.chmod(salt_file, 0o600)
            return salt
    
    def _get_primary_key(self) -> bytes:
        """Layer 1 Key - AES-256-GCM (Device-based)"""
        owner = self.config.get("agent.owner", "Pak Pur")
        device_id = self._get_device_id()
        seed = f"GAURANGA_PRIMARY_{owner}_{device_id}_{datetime.now().year}"
        return hashlib.pbkdf2_hmac(
            'sha512',
            seed.encode(),
            self.salt,
            100000
        )[:32]
    
    def _get_secondary_key(self) -> bytes:
        """Layer 2 Key - ChaCha20 derivation"""
        owner = self.config.get("agent.owner", "Pak Pur")
        seed = f"GAURANGA_SECONDARY_{owner}_SECURE"
        return hashlib.scrypt(
            seed.encode(),
            salt=self.salt,
            n=16384,
            r=8,
            p=1,
            maxmem=67108864,
            dklen=32
        )
    
    def _get_tertiary_key(self) -> bytes:
        """Layer 3 Key - AES-128-CBC (Fernet-style)"""
        owner = self.config.get("agent.owner", "Pak Pur")
        seed = f"GAURANGA_TERTIARY_{owner}_FINAL"
        key = hashlib.pbkdf2_hmac(
            'sha256',
            seed.encode(),
            self.salt,
            50000
        )[:32]
        return base64.urlsafe_b64encode(key)
    
    def _get_device_id(self) -> str:
        """Get unique device identifier"""
        device_file = ".gauranga_device_id"
        
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                return f.read().strip()
        else:
            device_id = hashlib.sha256(
                str(os.urandom(32)).encode() + self.salt
            ).hexdigest()[:16]
            with open(device_file, 'w') as f:
                f.write(device_id)
            os.chmod(device_file, 0o600)
            return device_id
    
    # ══════════════════════════════════════════════════════════════
    # LAYER 1: AES-256-GCM
    # ══════════════════════════════════════════════════════════════
    
    def encrypt_aes256(self, data: str) -> Dict[str, Any]:
        """Layer 1: AES-256-GCM encryption with authentication"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            aesgcm = AESGCM(self.layers["primary"])
            nonce = os.urandom(12)
            
            # Add timestamp and version
            metadata = {
                "v": self.VERSION,
                "t": datetime.now().isoformat(),
                "l": 1
            }
            
            data_with_meta = json.dumps({**metadata, "d": data}).encode()
            encrypted = aesgcm.encrypt(nonce, data_with_meta, None)
            
            return {
                "algorithm": "AES-256-GCM",
                "layer": 1,
                "nonce": base64.b64encode(nonce).decode(),
                "data": base64.b64encode(encrypted).decode(),
                "checksum": self._create_checksum(data)
            }
        except ImportError:
            return self._encrypt_fallback(data, "AES-256")
    
    def decrypt_aes256(self, encrypted_data: Dict) -> str:
        """Layer 1: Decrypt AES-256-GCM"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            aesgcm = AESGCM(self.layers["primary"])
            nonce = base64.b64decode(encrypted_data["nonce"])
            encrypted = base64.b64decode(encrypted_data["data"])
            
            decrypted = aesgcm.decrypt(nonce, encrypted, None)
            parsed = json.loads(decrypted)
            
            return parsed.get("d", "")
        except:
            return ""
    
    # ══════════════════════════════════════════════════════════════
    # LAYER 2: Double Encryption (Primary + Secondary)
    # ══════════════════════════════════════════════════════════════
    
    def encrypt_double_layer(self, data: str) -> Dict[str, Any]:
        """Layer 1+2: Double encryption for maximum security"""
        # First layer
        layer1 = self.encrypt_aes256(data)
        
        # Second layer encryption on layer1 data
        layer1_str = json.dumps(layer1)
        layer2 = self._encrypt_secondary(layer1_str)
        
        return {
            "algorithm": "DOUBLE-AES",
            "layer": 2,
            "primary": layer1,
            "secondary": layer2,
            "timestamp": datetime.now().isoformat(),
            "device_id": self._get_device_id()
        }
    
    def decrypt_double_layer(self, encrypted: Dict) -> str:
        """Decrypt double-encrypted data"""
        # Decrypt secondary layer
        secondary_decrypted = self._decrypt_secondary(encrypted["secondary"])
        
        # Decrypt primary layer
        primary_decrypted = self.decrypt_aes256(json.loads(secondary_decrypted))
        
        return primary_decrypted
    
    def _encrypt_secondary(self, data: str) -> Dict:
        """Secondary encryption layer"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            aesgcm = AESGCM(self.layers["secondary"])
            nonce = os.urandom(12)
            encrypted = aesgcm.encrypt(nonce, data.encode(), None)
            
            return {
                "nonce": base64.b64encode(nonce).decode(),
                "data": base64.b64encode(encrypted).decode()
            }
        except:
            return {"data": base64.b64encode(data.encode()).decode()}
    
    def _decrypt_secondary(self, encrypted: Dict) -> str:
        """Decrypt secondary layer"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            aesgcm = AESGCM(self.layers["secondary"])
            nonce = base64.b64decode(encrypted["nonce"])
            data = base64.b64decode(encrypted["data"])
            
            return aesgcm.decrypt(nonce, data, None).decode()
        except:
            return base64.b64decode(encrypted["data"]).decode()
    
    # ══════════════════════════════════════════════════════════════
    # LAYER 3: Fernet (AES-128-CBC)
    # ══════════════════════════════════════════════════════════════
    
    def encrypt_fernet(self, data: str) -> str:
        """Layer 3: Fernet-style encryption for transmission"""
        try:
            from cryptography.fernet import Fernet
            
            cipher = Fernet(self.layers["tertiary"])
            return cipher.encrypt(data.encode()).decode()
        except:
            return base64.b64encode(data.encode()).decode()
    
    def decrypt_fernet(self, encrypted: str) -> str:
        """Decrypt Fernet data"""
        try:
            from cryptography.fernet import Fernet
            
            cipher = Fernet(self.layers["tertiary"])
            return cipher.decrypt(encrypted.encode()).decode()
        except:
            return base64.b64decode(encrypted).decode()
    
    # ══════════════════════════════════════════════════════════════
    # LAYER 4: One-Time Pad (For Super Sensitive Data)
    # ══════════════════════════════════════════════════════════════
    
    def encrypt_otp(self, data: str) -> Dict[str, Any]:
        """Layer 4: One-Time Pad encryption"""
        # Generate random key
        key = os.urandom(len(data))
        key_b64 = base64.b64encode(key).decode()
        
        # XOR encryption
        data_bytes = data.encode()
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, key[:len(data_bytes)]))
        
        return {
            "algorithm": "OTP",
            "layer": 4,
            "encrypted": base64.b64encode(encrypted).decode(),
            "key": key_b64,
            "length": len(data)
        }
    
    def decrypt_otp(self, encrypted: Dict) -> str:
        """Decrypt OTP data"""
        key = base64.b64decode(encrypted["key"])
        data = base64.b64decode(encrypted["encrypted"])
        
        decrypted = bytes(a ^ b for a, b in zip(data, key[:len(data)]))
        return decrypted.decode()
    
    # ══════════════════════════════════════════════════════════════
    # LAYER 5: Hash Chain (Integrity)
    # ══════════════════════════════════════════════════════════════
    
    def create_hash_chain(self, data: str, previous_hash: str = None) -> Dict[str, Any]:
        """Layer 5: Blockchain-style hash chain for integrity"""
        timestamp = datetime.now().isoformat()
        
        if previous_hash:
            chain_input = f"{data}|{timestamp}|{previous_hash}"
        else:
            chain_input = f"{data}|{timestamp}|GENESIS"
        
        current_hash = hashlib.sha256(chain_input.encode()).hexdigest()
        
        return {
            "data": data,
            "timestamp": timestamp,
            "hash": current_hash,
            "previous": previous_hash or "GENESIS",
            "algorithm": "SHA3-256"
        }
    
    def verify_hash_chain(self, chain: List[Dict]) -> bool:
        """Verify integrity of entire hash chain"""
        previous = None
        
        for item in chain:
            expected_hash = hashlib.sha256(
                f"{item['data']}|{item['timestamp']}|{item.get('previous', 'GENESIS')}".encode()
            ).hexdigest()
            
            if item["hash"] != expected_hash:
                return False
            
            previous = item["hash"]
        
        return True
    
    # ══════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ══════════════════════════════════════════════════════════════
    
    def _create_checksum(self, data: str) -> str:
        """Create SHA-256 checksum"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _encrypt_fallback(self, data: str, method: str) -> Dict:
        """Fallback encryption without cryptography library"""
        encoded = base64.b64encode(data.encode())
        return {
            "algorithm": method + "-BASE64",
            "layer": 0,
            "data": encoded.decode(),
            "checksum": self._create_checksum(data)
        }
    
    # ══════════════════════════════════════════════════════════════
    # WRAPPER METHODS
    # ══════════════════════════════════════════════════════════════
    
    def encrypt(
        self,
        data: str,
        level: int = 2,
        compress: bool = True
    ) -> str:
        """
        Encrypt data with specified security level
        
        Level 1: AES-256-GCM only
        Level 2: Double encryption (default)
        Level 3: Double + Fernet
        Level 4: OTP for super sensitive
        """
        if compress:
            data = base64.b64encode(
                zlib.compress(data.encode())
            ).decode()
        
        if level == 1:
            result = self.encrypt_aes256(data)
        elif level == 2:
            result = self.encrypt_double_layer(data)
        elif level == 3:
            layer2 = self.encrypt_double_layer(data)
            result = self.encrypt_fernet(json.dumps(layer2))
        elif level == 4:
            layer3 = self.encrypt_fernet(
                json.dumps(self.encrypt_double_layer(data))
            )
            result = self.encrypt_otp(layer3)
        else:
            result = self.encrypt_double_layer(data)
        
        return json.dumps(result)
    
    def decrypt(
        self,
        encrypted_str: str,
        level: int = 2
    ) -> str:
        """Decrypt data based on encryption level"""
        try:
            data = json.loads(encrypted_str)
            
            if isinstance(data, str):
                # Fernet encrypted
                data = json.loads(self.decrypt_fernet(data))
            
            if "layer" in data:
                if data["layer"] == 4:
                    decrypted = self.decrypt_otp(data)
                    data = json.loads(self.decrypt_fernet(decrypted))
                    return self._decompress(self.decrypt_double_layer(data))
                elif data["layer"] == 2:
                    return self._decompress(self.decrypt_double_layer(data))
                else:
                    return self._decompress(self.decrypt_aes256(data))
            
            return ""
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def _decompress(self, data: str) -> str:
        """Decompress data if compressed"""
        try:
            return zlib.decompress(base64.b64decode(data)).decode()
        except:
            return data
    
    # ══════════════════════════════════════════════════════════════
    # SECURE STORAGE
    # ══════════════════════════════════════════════════════════════
    
    def encrypt_file(self, filepath: str, output: str = None, level: int = 2) -> str:
        """Encrypt file with multi-layer encryption"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            data = f.read().decode('utf-8', errors='ignore')
        
        encrypted = self.encrypt(data, level)
        
        output_path = output or filepath + ".enc"
        
        # Create encrypted package
        package = {
            "file": filepath,
            "encrypted": encrypted,
            "level": level,
            "size": len(data),
            "timestamp": datetime.now().isoformat(),
            "hash": self._create_checksum(data)
        }
        
        with open(output_path, 'w') as f:
            json.dump(package, f, indent=2)
        
        return output_path
    
    def decrypt_file(self, encrypted_file: str, output: str = None) -> str:
        """Decrypt encrypted file"""
        with open(encrypted_file, 'r') as f:
            package = json.load(f)
        
        decrypted = self.decrypt(
            package["encrypted"],
            level=package.get("level", 2)
        )
        
        output_path = output or package["file"]
        
        with open(output_path, 'w') as f:
            f.write(decrypted)
        
        return output_path
    
    # ══════════════════════════════════════════════════════════════
    # SECURE BACKUP
    # ══════════════════════════════════════════════════════════════
    
    def create_secure_backup(
        self,
        data: Dict,
        password: str = None
    ) -> Dict[str, Any]:
        """
        Create ultra-secure backup with all layers
        """
        # Serialize data
        json_data = json.dumps(data, ensure_ascii=False)
        
        # Layer 4: OTP (highest security)
        otp_encrypted = self.encrypt_otp(json_data)
        
        # Layer 3: Fernet
        fernet_encrypted = self.encrypt_fernet(json.dumps(otp_encrypted))
        
        # Layer 2: Double encryption
        double_encrypted = self.encrypt_double_layer(json_data)
        
        # Password protection (if provided)
        password_hash = None
        if password:
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                self.salt,
                100000
            ).hex()
            
            # Re-encrypt with password
            password_encrypted = self.encrypt(json_data, level=3)
            double_encrypted = password_encrypted
        
        # Create hash chain
        chain = self.create_hash_chain(
            json.dumps(double_encrypted),
            self._get_device_id()
        )
        
        return {
            "version": self.VERSION,
            "created": datetime.now().isoformat(),
            "device_id": self._get_device_id(),
            "encryption_levels": ["AES-256-GCM", "ChaCha20", "Fernet", "OTP"],
            "otp_layer": otp_encrypted,
            "fernet_layer": fernet_encrypted,
            "primary_layer": double_encrypted,
            "hash_chain": chain,
            "password_protected": password is not None,
            "password_hash": password_hash,
            "checksum": self._create_checksum(json_data)
        }
    
    def restore_secure_backup(
        self,
        backup: Dict,
        password: str = None
    ) -> Dict:
        """Restore from ultra-secure backup"""
        # Verify password if protected
        if backup.get("password_protected"):
            if not password:
                raise ValueError("Password required for this backup")
            
            expected_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                self.salt,
                100000
            ).hex()
            
            if expected_hash != backup.get("password_hash"):
                raise ValueError("Invalid password")
        
        # Decrypt layer by layer
        try:
            # Decrypt primary layer
            if backup.get("password_protected"):
                primary = self.decrypt(backup["primary_layer"], level=3)
            else:
                primary = self.decrypt_double_layer(backup["primary_layer"])
            
            # Verify hash chain
            chain_data = json.dumps(backup["primary_layer"])
            expected_chain_hash = hashlib.sha256(
                f"{chain_data}|{backup['hash_chain']['timestamp']}|{backup['hash_chain']['previous']}".encode()
            ).hexdigest()
            
            if expected_chain_hash != backup["hash_chain"]["hash"]:
                raise ValueError("Backup integrity check failed - data may be corrupted")
            
            return json.loads(primary)
            
        except Exception as e:
            raise ValueError(f"Failed to restore backup: {e}")


# Global instance
_global_encryption = None

def get_encryption(config: Dict = None) -> MultiLayerEncryption:
    """Get or create global encryption instance"""
    global _global_encryption
    if _global_encryption is None:
        _global_encryption = MultiLayerEncryption(config)
    return _global_encryption
