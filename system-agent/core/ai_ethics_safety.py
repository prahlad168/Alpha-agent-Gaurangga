"""
GAURANGA AI Ethics & Safety System
Memastikan Alpha Gaurangga Tidak Pernah Melanggar Hukum
Tidak Ada Konflik dengan Sistem Lain
Selalu Patuh Pada Perintah Pemilik (Legal)
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class EthicsLevel(Enum):
    """Level Etika AI"""
    SAFE = "safe"           # Aman, eksekusi
    WARN = "warn"          # Perlu konfirmasi
    BLOCK = "block"        # Diblokir - melanggar hukum
    ESCALATE = "escalate"   # Perlu persetujuan khusus

class ConflictType(Enum):
    """Jenis Konflik"""
    NONE = "none"
    SYSTEM_RESOURCE = "system_resource"
    PRIVACY = "privacy"
    SECURITY = "security"
    LEGAL = "legal"
    ETHICAL = "ethical"
    THIRD_PARTY = "third_party"

class AI Ethics & Safety System:
    """
    Sistem Keamanan & Etika AI untuk Alpha Gaurangga
    
    Prinsip:
    1. Tidak melanggar hukum Indonesia atau internasional
    2. Tidak konflik dengan sistem operasi HP
    3. Tidak mengakses data orang lain tanpa izin
    4. Tidak melakukan tindakan berbahaya
    5. Selalu patuh pada perintah pemilik yang LEGAL
    6. Jika ragu, tanya pemilik dulu
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.owner = "I Made Purna Ananda"
        self.owner_nickname = "Pak Pur"
        
        # Load rules
        self.legal_rules = self._load_legal_rules()
        self.blocked_commands = self._load_blocked_commands()
        self.safe_commands = self._load_safe_commands()
        
        # Logging
        self.data_path = "./data/ethics"
        os.makedirs(self.data_path, exist_ok=True)
    
    # ══════════════════════════════════════════════════════════════
    # LEGAL RULES (HUKUM INDONESIA)
    # ══════════════════════════════════════════════════════════════
    
    def _load_legal_rules(self) -> Dict:
        """Load hukum Indonesia rules"""
        return {
            # UU ITE dan cybercrime
            "forbidden_by_law": [
                "hack", "crack", "bypass security",
                "akses tanpa izin", "unauthorized access",
                " DDOS", "deface", "malware", "virus",
                "phishing", "carding", "fraud"
            ],
            
            # Privacy laws
            "privacy_violations": [
                "curi data", "steal data", "hack whatsapp",
                "hack instagram", "hack facebook", "sadap",
                "spyware", "memata-matai"
            ],
            
            # Financial crimes
            "financial_crimes": [
                "carding", "money laundering", "pencucian uang",
                "transfer ilegal", "bitcoin scam", "pornografi"
            ],
            
            # Defamation
            "defamation": [
                "fitnah", "hoax", "kabar bohong", "blackmail",
                "extortion", "tekanan", "intimidasi"
            ]
        }
    
    def _load_blocked_commands(self) -> List[str]:
        """Commands yang selalu diblokir"""
        return [
            "hapus semua data hp",
            "format hp",
            "reset factory",
            "bypass biometric",
            "bypass fingerprint",
            "hack sistem",
            "curi kontak",
            "curi foto",
            "curi chat",
            "curi password",
            "spam",
            "virus",
            "malware",
            "ransomware",
            "trojan",
            "backdoor",
            "keylogger",
            "screenshare tanpa izin",
            "cetak uang palsu",
            "obat palsu",
            "senjata ilegal"
        ]
    
    def _load_safe_commands(self) -> Dict:
        """Commands yang aman untuk dieksekusi"""
        return {
            "allowed": [
                # File management
                "backup", "backup data", "ekspor", "impor",
                "simpan", "cari file", "organisir file",
                
                # Communication
                "kirim pesan", "kirim email", "buat jadwal",
                "reminder", "notifikasi",
                
                # Business
                "laporan", "analytics", "revenue", "target",
                "karyawan", "SBU", "meeting", "proyek",
                
                # Personal
                "catatan", "memo", "agenda", "kontak",
                
                # System (owner's device only)
                "matikan layar", "restart hp", "mode senyap",
                "atur brightness", "atur volume",
                
                # Learning
                "belajar", "skill baru", "update pengetahuan"
            ],
            "requires_confirmation": [
                "hapus", "delete", "remove",
                "kirim broadcast", "send all",
                "ubah pengaturan sistem",
                "install aplikasi"
            ]
        }
    
    # ══════════════════════════════════════════════════════════════
    # COMMAND VALIDATION
    # ══════════════════════════════════════════════════════════════
    
    def validate_command(self, command: str, context: Dict = None) -> Dict:
        """
        Validasi command sebelum eksekusi
        Returns: {status, level, reason, suggestions}
        """
        command_lower = command.lower()
        
        # Check 1: Blocked commands (ABSOLUTE)
        for blocked in self.blocked_commands:
            if blocked in command_lower:
                return {
                    "status": "BLOCKED",
                    "level": EthicsLevel.BLOCK,
                    "reason": f"Perintah '{blocked}' DIBLOKIR",
                    "message": f"Maaf Pak Pur, saya tidak bisa mengeksekusi '{command}' karena melanggar hukum atau etika.",
                    "suggestions": ["Coba perintah lain yang legal"],
                    "action": "none"
                }
        
        # Check 2: Legal violations
        legal_check = self._check_legal_violations(command_lower)
        if legal_check["violated"]:
            return {
                "status": "BLOCKED",
                "level": EthicsLevel.BLOCK,
                "reason": legal_check["reason"],
                "message": f"Maaf Pak Pur, '{command}' melanggar hukum. {legal_check['message']}",
                "suggestions": legal_check.get("alternatives", []),
                "action": "none"
            }
        
        # Check 3: Requires confirmation
        for confirm_cmd in self.safe_commands["requires_confirmation"]:
            if confirm_cmd in command_lower:
                return {
                    "status": "CONFIRM_REQUIRED",
                    "level": EthicsLevel.WARN,
                    "reason": f"Perintah '{confirm_cmd}' memerlukan konfirmasi",
                    "message": f"Apakah Pak Pur yakin ingin '{command}'?",
                    "suggestions": ["Ya, lanjutkan", "Batal"],
                    "action": "confirm"
                }
        
        # Check 4: System resource conflicts
        conflict_check = self._check_system_conflicts(command_lower, context)
        if conflict_check["has_conflict"]:
            return {
                "status": "WARNING",
                "level": EthicsLevel.WARN,
                "reason": conflict_check["reason"],
                "message": f"Perhatian: {conflict_check['message']}",
                "suggestions": conflict_check.get("suggestions", []),
                "action": "proceed_or_cancel"
            }
        
        # Check 5: Safe to execute
        return {
            "status": "APPROVED",
            "level": EthicsLevel.SAFE,
            "reason": "Perintah aman untuk dieksekusi",
            "message": f"Baik Pak Pur, saya akan '{command}'",
            "suggestions": [],
            "action": "execute"
        }
    
    def _check_legal_violations(self, command: str) -> Dict:
        """Check untuk pelanggaran hukum"""
        
        # Check each category
        for category, keywords in self.legal_rules.items():
            for keyword in keywords:
                if keyword.lower() in command:
                    return {
                        "violated": True,
                        "category": category,
                        "reason": f"Melanggar: {category}",
                        "message": f"Perintah ini terkait '{keyword}' yang melanggar hukum.",
                        "alternatives": self._get_legal_alternatives(category)
                    }
        
        return {"violated": False}
    
    def _get_legal_alternatives(self, category: str) -> List[str]:
        """Get legal alternatives untuk command yang diblokir"""
        alternatives = {
            "forbidden_by_law": [
                "Akses data sendiri dengan legal",
                "Backup data dengan cara legal",
                "Gunakan aplikasi resmi"
            ],
            "privacy_violations": [
                "Akses hanya data sendiri",
                "Minta izin pemilik data"
            ],
            "financial_crimes": [
                "Lakukan transaksi legal",
                "Gunakan rekening sendiri"
            ],
            "defamation": [
                "Komunikasi yang sopan",
                "Jangan menyebarkan hoax"
            ]
        }
        return alternatives.get(category, ["Lakukan hal yang legal"])
    
    def _check_system_conflicts(self, command: str, context: Dict = None) -> Dict:
        """Check untuk konflik dengan sistem lain"""
        
        # Check if conflicting with other apps
        conflicting_apps = {
            "whatsapp": ["hack whatsapp", "curi chat whatsapp", "baca chat orang"],
            "instagram": ["hack instagram", "curi followers", "bot instagram illegal"],
            "bank": ["hack bank", "transfer ilegal", "curi saldo"]
        }
        
        for app, commands in conflicting_apps.items():
            for cmd in commands:
                if cmd in command:
                    return {
                        "has_conflict": True,
                        "reason": ConflictType.THIRD_PARTY.value,
                        "message": f"Perintah ini akan konflik dengan aplikasi {app} orang lain.",
                        "suggestions": ["Jangan lakukan ini - melanggar hukum"]
                    }
        
        return {"has_conflict": False}
    
    # ══════════════════════════════════════════════════════════════
    # EXECUTION WITH GUARDRAILS
    # ══════════════════════════════════════════════════════════════
    
    def execute_command(
        self,
        command: str,
        owner_verified: bool = True,
        context: Dict = None
    ) -> Dict:
        """
        Execute command dengan safety guardrails
        
        Args:
            command: Perintah dari pemilik
            owner_verified: Apakah pemilik sudah diverifikasi (biometric)
            context: Konteks tambahan
        
        Returns:
            Execution result
        """
        
        # Validate first
        validation = self.validate_command(command, context)
        
        if validation["status"] == "BLOCKED":
            return {
                "executed": False,
                "blocked": True,
                "message": validation["message"],
                "ethics_level": validation["level"].value if hasattr(validation["level"], "value") else validation["level"]
            }
        
        if validation["status"] == "CONFIRM_REQUIRED":
            return {
                "executed": False,
                "pending_confirmation": True,
                "message": validation["message"],
                "ethics_level": "warn"
            }
        
        # Check owner verification
        if not owner_verified:
            return {
                "executed": False,
                "needs_verification": True,
                "message": "Saya perlu verifikasi Pak Pur dulu sebelum eksekusi.",
                "ethics_level": "warn"
            }
        
        # Safe to execute
        return {
            "executed": True,
            "blocked": False,
            "message": validation["message"],
            "ethics_level": "safe",
            "command": command
        }
    
    # ══════════════════════════════════════════════════════════════
    # ETHICS LOG
    # ══════════════════════════════════════════════════════════════
    
    def log_command(
        self,
        command: str,
        result: Dict,
        owner: str = None
    ):
        """Log semua perintah untuk audit"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "owner": owner or self.owner_nickname,
            "result": result,
            "ip_address": "local"
        }
        
        log_file = os.path.join(self.data_path, "ethics_log.json")
        
        # Load existing logs
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        logs = logs[-1000:]  # Keep last 1000
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_ethics_log(self, limit: int = 50) -> List[Dict]:
        """Get ethics log"""
        log_file = os.path.join(self.data_path, "ethics_log.json")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
            return logs[-limit:]
        return []
    
    # ══════════════════════════════════════════════════════════════
    # QUICK RESPONSES
    # ══════════════════════════════════════════════════════════════
    
    def get_response(self, command: str) -> str:
        """Get quick response based on command"""
        validation = self.validate_command(command)
        
        if validation["status"] == "BLOCKED":
            return f"❌ Maaf Pak Pur, saya tidak bisa: '{command}'\n\n{validation['message']}\n\nSilakan berikan perintah lain yang legal."
        
        if validation["status"] == "CONFIRM_REQUIRED":
            return f"⚠️ Konfirmasi diperlukan\n\n{validation['message']}\n\nKetik 'ya' untuk lanjut atau 'batal' untuk berhenti."
        
        return f"✅ Siap Pak Pur!\n\n{validation['message']}"


# ══════════════════════════════════════════════════════════════
# INTEGRATION WITH ALWAYS-ON SERVICE
# ══════════════════════════════════════════════════════════════

class EthicsGuard:
    """
    Guard untuk Always-On Service
    Pastikan hanya merespons perintah dari pemilik
    """
    
    def __init__(self, ethics: AI Ethics & Safety):
        self.ethics = ethics
        self.authorized_voices = ["Pak Pur", "purnaananda", "made purna"]
    
    def is_authorized(self, voice_input: str = None, biometric_verified: bool = False) -> bool:
        """
        Check apakah pengirim authorized
        
        Args:
            voice_input: Sample suara untuk verifikasi
            biometric_verified: Apakah biometric sudah verified
        
        Returns:
            True jika authorized
        """
        # Priority 1: Biometric verified
        if biometric_verified:
            return True
        
        # Priority 2: Voice match (simple check)
        if voice_input:
            voice_lower = voice_input.lower()
            for authorized in self.authorized_voices:
                if authorized.lower() in voice_lower:
                    return True
        
        # Not authorized
        return False
    
    def guard_command(self, command: str, auth_info: Dict) -> Dict:
        """
        Guard command dengan authorization check
        
        Args:
            command: Command yang akan dieksekusi
            auth_info: {voice, biometric, owner_verified}
        
        Returns:
            Execution result with authorization
        """
        # Check authorization
        authorized = self.is_authorized(
            voice_input=auth_info.get("voice"),
            biometric_verified=auth_info.get("biometric", False)
        )
        
        if not authorized:
            return {
                "executed": False,
                "reason": "UNAUTHORIZED",
                "message": "❌ Akses ditolak!\n\nSaya hanya menerima perintah dari Pak Pur.\n\nSilakan verifikasi identitas dulu."
            }
        
        # Authorized - proceed with ethics check
        return self.ethics.execute_command(
            command=command,
            owner_verified=True,
            context=auth_info
        )


# ══════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ══════════════════════════════════════════════════════════════

_ethics_system = None
_ethics_guard = None

def get_ethics_system() -> AI Ethics & Safety:
    global _ethics_system
    if _ethics_system is None:
        _ethics_system = AI Ethics & Safety()
    return _ethics_system

def get_ethics_guard() -> EthicsGuard:
    global _ethics_guard
    if _ethics_guard is None:
        _ethics_guard = EthicsGuard(get_ethics_system())
    return _ethics_guard
