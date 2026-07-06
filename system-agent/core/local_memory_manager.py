"""
GAURANGA Local Memory Manager
On-Device Memory Management System dengan SQLite dan Enkripsi
- Penyimpanan lokal menggunakan SQLite (tidak ada cloud sync)
- Enkripsi AES-256 untuk data sensitif
- Ekspor/Migrasi data memori dengan perintah khusus
- Format eksport terenkripsi (.gaurangga.db)

Author: GAURANGA Team
Owner: I Made Purna Ananda (Pak Pur)
"""

import os
import json
import sqlite3
import hashlib
import base64
import zlib
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

# Crypto imports
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography library not available. Using basic encoding for export.")


class MemoryType(Enum):
    """Jenis-jenis memori"""
    GENERAL = "general"
    CONVERSATION = "conversation"
    PREFERENCE = "preference"
    SKILL = "skill"
    LEARNED = "learned"
    REMINDER = "reminder"
    BUSINESS = "business"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"


class MemoryPriority(Enum):
    """Prioritas memori"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryEntry:
    """Struktur data memori"""
    id: str = ""
    type: str = MemoryType.GENERAL.value
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    priority: int = MemoryPriority.MEDIUM.value
    is_encrypted: bool = False
    created_at: str = ""
    updated_at: str = ""
    accessed_at: str = ""
    access_count: int = 0
    source: str = "system"  # system, user, skill, import

    def __post_init__(self):
        if not self.id:
            self.id = f"mem_{uuid.uuid4().hex[:16]}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if not self.accessed_at:
            self.accessed_at = self.created_at


@dataclass
class ConversationEntry:
    """Struktur percakapan"""
    id: str = ""
    role: str = "user"  # user, assistant, system
    content: str = ""
    intent: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    sentiment: str = "neutral"
    timestamp: str = ""
    session_id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"conv_{uuid.uuid4().hex[:16]}"
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class UserPreference:
    """Preferensi pengguna"""
    key: str = ""
    value: Any = None
    category: str = "general"
    updated_at: str = ""

    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class ExportMetadata:
    """Metadata untuk file export"""
    version: str = "1.0.0"
    agent_name: str = "GAURANGA"
    owner: str = ""
    export_date: str = ""
    device_id: str = ""
    total_memories: int = 0
    total_conversations: int = 0
    total_preferences: int = 0
    encrypted: bool = True
    checksum: str = ""
    compression: str = "zlib"


class LocalMemoryManager:
    """
    Local Memory Manager - On-Device Memory Storage
    Menyimpan semua data secara lokal tanpa cloud sync
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Dict[str, Any] = None, storage_path: str = None):
        """Initialize Local Memory Manager
        
        Args:
            config: Konfigurasi sistem
            storage_path: Path untuk penyimpanan data (default: ./data/local_memory)
        """
        self.config = config or {}
        self.storage_path = storage_path or self._get_default_path()
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Database paths
        self.db_path = os.path.join(self.storage_path, "gauranga_memory.db")
        self.preferences_path = os.path.join(self.storage_path, "preferences.json")
        
        # Encryption key (derived from device-specific data)
        self._encryption_key = None
        self._cipher = None
        
        # Logger
        self.logger = logging.getLogger("GAURANGA.LocalMemory")
        
        # Initialize database
        self._init_database()
        
    def _get_default_path(self) -> str:
        """Get default storage path"""
        base_path = self.config.get("memory.local_path", "./data/local_memory")
        return os.path.abspath(base_path)
    
    def _init_database(self) -> None:
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                tags TEXT,
                priority INTEGER DEFAULT 2,
                is_encrypted INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                accessed_at TEXT,
                access_count INTEGER DEFAULT 0,
                source TEXT DEFAULT 'system'
            )
        ''')
        
        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                intent TEXT,
                entities TEXT,
                sentiment TEXT DEFAULT 'neutral',
                timestamp TEXT,
                session_id TEXT
            )
        ''')
        
        # Create preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                category TEXT DEFAULT 'general',
                updated_at TEXT
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_session ON conversations(session_id)')
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Database initialized at: {self.db_path}")
    
    # ===============================
    # ENCRYPTION METHODS
    # ===============================
    
    def _get_device_key(self) -> bytes:
        """Generate device-specific encryption key"""
        if CRYPTO_AVAILABLE:
            # Use PBKDF2 to derive key from device info + stored salt
            salt_file = os.path.join(self.storage_path, ".salt")
            
            if os.path.exists(salt_file):
                with open(salt_file, 'rb') as f:
                    salt = f.read()
            else:
                # Generate new salt
                salt = os.urandom(32)
                with open(salt_file, 'wb') as f:
                    f.write(salt)
            
            # Use owner name + salt as password
            owner = self.config.get("agent.owner", "Pak Pur")
            password = f"GAURANGA_{owner}_{datetime.now().year}".encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            return base64.urlsafe_b64encode(kdf.derive(password))
        else:
            # Fallback - return hash of storage path
            return hashlib.sha256(self.storage_path.encode()).digest()
    
    def _get_cipher(self):
        """Get Fernet cipher for encryption/decryption"""
        if self._cipher is None and CRYPTO_AVAILABLE:
            key = self._get_device_key()
            self._cipher = Fernet(key)
        return self._cipher
    
    def _encrypt(self, data: str) -> str:
        """Encrypt data using Fernet (AES-128-CBC)"""
        if CRYPTO_AVAILABLE and self._get_cipher():
            encrypted = self._get_cipher().encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        return data
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt Fernet-encrypted data"""
        if CRYPTO_AVAILABLE and self._get_cipher():
            try:
                data = base64.b64decode(encrypted_data.encode())
                return self._get_cipher().decrypt(data).decode()
            except Exception:
                return encrypted_data
        return encrypted_data
    
    # ===============================
    # MEMORY OPERATIONS
    # ===============================
    
    def store_memory(
        self,
        content: str,
        memory_type: str = MemoryType.GENERAL.value,
        metadata: Dict = None,
        tags: List[str] = None,
        priority: int = MemoryPriority.MEDIUM.value,
        encrypt: bool = False,
        source: str = "system"
    ) -> str:
        """Simpan memori baru
        
        Args:
            content: Isi memori
            memory_type: Jenis memori
            metadata: Metadata tambahan
            tags: Tags untuk kategorisasi
            priority: Prioritas (1-4)
            encrypt: Apakah perlu dienkripsi
            source: Sumber memori
            
        Returns:
            ID memori yang disimpan
        """
        entry = MemoryEntry(
            type=memory_type,
            content=self._encrypt(content) if encrypt else content,
            metadata=metadata or {},
            tags=tags or [],
            priority=priority,
            is_encrypted=encrypt,
            source=source
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memories 
            (id, type, content, metadata, tags, priority, is_encrypted, 
             created_at, updated_at, accessed_at, access_count, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.id,
            entry.type,
            entry.content,
            json.dumps(entry.metadata),
            json.dumps(entry.tags),
            entry.priority,
            1 if entry.is_encrypted else 0,
            entry.created_at,
            entry.updated_at,
            entry.accessed_at,
            entry.access_count,
            entry.source
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Memory stored: {entry.id} ({memory_type})")
        return entry.id
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Ambil memori berdasarkan ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            memory = self._row_to_memory(row)
            self._update_access(memory)
            return memory
        return None
    
    def search_memories(
        self,
        query: str = None,
        memory_type: str = None,
        tags: List[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Cari memori berdasarkan berbagai kriteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = 'SELECT * FROM memories WHERE 1=1'
        params = []
        
        if query:
            sql += ' AND (content LIKE ? OR metadata LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%'])
        
        if memory_type:
            sql += ' AND type = ?'
            params.append(memory_type)
        
        if tags:
            for tag in tags:
                sql += ' AND tags LIKE ?'
                params.append(f'%"{tag}"%')
        
        sql += ' ORDER BY priority DESC, updated_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in rows:
            memory = self._row_to_memory(row)
            # Decrypt if needed
            if memory.get('is_encrypted'):
                memory['content'] = self._decrypt(memory['content'])
            memories.append(memory)
        
        return memories
    
    def update_memory(self, memory_id: str, content: str = None, metadata: Dict = None) -> bool:
        """Update memori"""
        updates = []
        params = []
        now = datetime.now().isoformat()
        
        if content is not None:
            updates.append('content = ?')
            params.append(content)
        if metadata is not None:
            updates.append('metadata = ?')
            params.append(json.dumps(metadata))
        
        if not updates:
            return False
        
        updates.append('updated_at = ?')
        params.append(now)
        params.append(memory_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'UPDATE memories SET {", ".join(updates)} WHERE id = ?', params)
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def delete_memory(self, memory_id: str) -> bool:
        """Hapus memori"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def _update_access(self, memory: Dict) -> None:
        """Update access count and timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE memories 
            SET access_count = access_count + 1, accessed_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), memory['id']))
        conn.commit()
        conn.close()
    
    def _row_to_memory(self, row: sqlite3.Row) -> Dict:
        """Convert database row to memory dict"""
        return {
            'id': row[0],
            'type': row[1],
            'content': row[2],
            'metadata': json.loads(row[3]) if row[3] else {},
            'tags': json.loads(row[4]) if row[4] else [],
            'priority': row[5],
            'is_encrypted': bool(row[6]),
            'created_at': row[7],
            'updated_at': row[8],
            'accessed_at': row[9],
            'access_count': row[10],
            'source': row[11]
        }
    
    # ===============================
    # CONVERSATION OPERATIONS
    # ===============================
    
    def store_conversation(
        self,
        role: str,
        content: str,
        intent: str = "",
        entities: Dict = None,
        sentiment: str = "neutral",
        session_id: str = None
    ) -> str:
        """Simpan percakapan"""
        entry = ConversationEntry(
            role=role,
            content=content,
            intent=intent,
            entities=entities or {},
            sentiment=sentiment,
            session_id=session_id or self._get_or_create_session()
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (id, role, content, intent, entities, sentiment, timestamp, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.id, entry.role, entry.content, entry.intent,
            json.dumps(entry.entities), entry.sentiment,
            entry.timestamp, entry.session_id
        ))
        
        # Update session message count
        cursor.execute('''
            UPDATE sessions SET message_count = message_count + 1 WHERE id = ?
        ''', (entry.session_id,))
        
        conn.commit()
        conn.close()
        
        return entry.id
    
    def get_conversation_history(self, session_id: str = None, limit: int = 100) -> List[Dict]:
        """Ambil riwayat percakapan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM conversations 
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        conversations = []
        for row in rows:
            conversations.append({
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'intent': row[3],
                'entities': json.loads(row[4]) if row[4] else {},
                'sentiment': row[5],
                'timestamp': row[6],
                'session_id': row[7]
            })
        
        return list(reversed(conversations))
    
    def _get_or_create_session(self) -> str:
        """Get or create current session"""
        today = datetime.now().strftime('%Y%m%d')
        session_id = f"session_{today}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM sessions WHERE id = ?', (session_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO sessions (id, started_at, message_count)
                VALUES (?, ?, 0)
            ''', (session_id, datetime.now().isoformat()))
            conn.commit()
        
        conn.close()
        return session_id
    
    # ===============================
    # PREFERENCES OPERATIONS
    # ===============================
    
    def set_preference(self, key: str, value: Any, category: str = "general") -> None:
        """Set user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (key, value, category, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (key, json.dumps(value), category, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return default
    
    def get_all_preferences(self, category: str = None) -> Dict[str, Any]:
        """Get all preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT key, value FROM preferences WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT key, value FROM preferences')
        
        rows = cursor.fetchall()
        conn.close()
        
        return {row[0]: json.loads(row[1]) for row in rows}
    
    # ===============================
    # MEMORY EXPORT/IMPORT (ON COMMAND)
    # ===============================
    
    def export_all_data(
        self,
        output_path: str = None,
        password: str = None,
        include_sensitive: bool = True
    ) -> str:
        """
        EKSPOR DATA MEMORI - ON COMMAND ONLY
        Fungsi ini hanya aktif ketika pengguna memberikan perintah spesifik
        
        Args:
            output_path: Path untuk file export
            password: Password untuk file terenkripsi (opsional - akan diminta jika None)
            include_sensitive: Sertakan data sensitif
            
        Returns:
            Path ke file export yang sudah dienkripsi
        """
        self.logger.info("🔐 Starting memory export process...")
        
        # Get all data
        data = {
            'metadata': self._create_export_metadata(),
            'memories': self._export_memories(include_sensitive),
            'conversations': self._export_conversations(),
            'preferences': self._export_preferences()
        }
        
        # Compress data
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        compressed = zlib.compress(json_data.encode('utf-8'), level=9)
        
        # Encrypt if crypto available or password provided
        if CRYPTO_AVAILABLE:
            if password:
                # Use password-based encryption
                encrypted = self._encrypt_with_password(compressed, password)
            else:
                # Use device key encryption
                cipher = self._get_cipher()
                if cipher:
                    encrypted = cipher.encrypt(compressed)
                else:
                    encrypted = compressed
        else:
            encrypted = compressed
        
        # Generate output path
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(
                self.storage_path, 
                f'gauranga_backup_{timestamp}.gmem'
            )
        
        # Save encrypted file
        with open(output_path, 'wb') as f:
            # Write header
            f.write(b'GAURANGA_MEM\x00')  # Magic bytes
            f.write(b'\x01')  # Version 1
            f.write(b'\x01' if CRYPTO_AVAILABLE or password else b'\x00')  # Encrypted flag
            f.write(b'\x01')  # Compressed flag
            
            # Write checksum
            checksum = hashlib.sha256(encrypted).hexdigest()
            f.write(checksum.encode())
            f.write(b'\n')
            
            # Write encrypted data
            f.write(base64.b64encode(encrypted))
        
        self.logger.info(f"✅ Export completed: {output_path}")
        return output_path
    
    def import_data(
        self,
        import_path: str,
        password: str = None,
        merge: bool = True
    ) -> Dict[str, Any]:
        """
        IMPORT DATA MEMORI - ON COMMAND ONLY
        Impor data dari file backup terenkripsi
        
        Args:
            import_path: Path ke file backup
            password: Password untuk dekripsi (jika diperlukan)
            merge: Gabungkan dengan data existing (True) atau replace (False)
            
        Returns:
            Statistik import
        """
        self.logger.info(f"📥 Starting memory import from: {import_path}")
        
        if not os.path.exists(import_path):
            raise FileNotFoundError(f"Import file not found: {import_path}")
        
        # Read encrypted file
        with open(import_path, 'rb') as f:
            header = f.read(16)
            checksum = f.read(64).decode()
            data = f.read()
        
        # Decode and decrypt
        encrypted = base64.b64decode(data)
        
        # Verify checksum
        if hashlib.sha256(encrypted).hexdigest() != checksum:
            raise ValueError("Data integrity check failed!")
        
        if CRYPTO_AVAILABLE:
            if password:
                decrypted = self._decrypt_with_password(encrypted, password)
            else:
                cipher = self._get_cipher()
                if cipher:
                    decrypted = cipher.decrypt(encrypted)
                else:
                    decrypted = encrypted
        else:
            decrypted = encrypted
        
        # Decompress
        data = json.loads(zlib.decompress(decrypted).decode('utf-8'))
        
        # Import data
        stats = {
            'memories_imported': 0,
            'conversations_imported': 0,
            'preferences_imported': 0,
            'errors': []
        }
        
        if merge:
            stats['memories_imported'] = self._import_memories(data.get('memories', []))
            stats['conversations_imported'] = self._import_conversations(data.get('conversations', []))
            stats['preferences_imported'] = self._import_preferences(data.get('preferences', {}))
        else:
            # Clear and replace
            self._clear_all_data()
            stats['memories_imported'] = self._import_memories(data.get('memories', []))
            stats['conversations_imported'] = self._import_conversations(data.get('conversations', []))
            stats['preferences_imported'] = self._import_preferences(data.get('preferences', {}))
        
        self.logger.info(f"✅ Import completed: {stats}")
        return stats
    
    def _create_export_metadata(self) -> Dict:
        """Create export metadata"""
        meta = ExportMetadata(
            version=self.VERSION,
            agent_name="GAURANGA",
            owner=self.config.get("agent.owner", "Pak Pur"),
            export_date=datetime.now().isoformat(),
            device_id=self._get_device_id(),
            total_memories=self.count_memories(),
            total_conversations=self.count_conversations(),
            total_preferences=self.count_preferences(),
            encrypted=CRYPTO_AVAILABLE,
            checksum=""
        )
        return asdict(meta)
    
    def _get_device_id(self) -> str:
        """Get or create device ID"""
        device_file = os.path.join(self.storage_path, ".device_id")
        
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                return f.read().strip()
        else:
            device_id = uuid.uuid4().hex[:16]
            with open(device_file, 'w') as f:
                f.write(device_id)
            return device_id
    
    def _encrypt_with_password(self, data: bytes, password: str) -> bytes:
        """Encrypt data with custom password"""
        salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher = Fernet(key)
        encrypted = cipher.encrypt(data)
        
        # Prepend salt for decryption
        return salt + encrypted
    
    def _decrypt_with_password(self, data: bytes, password: str) -> bytes:
        """Decrypt data with custom password"""
        salt = data[:32]
        encrypted = data[32:]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher = Fernet(key)
        return cipher.decrypt(encrypted)
    
    def _export_memories(self, include_sensitive: bool) -> List[Dict]:
        """Export all memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if include_sensitive:
            cursor.execute('SELECT * FROM memories ORDER BY created_at')
        else:
            cursor.execute('''
                SELECT * FROM memories 
                WHERE type != ? 
                ORDER BY created_at
            ''', (MemoryType.SENSITIVE.value,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_memory(row) for row in rows]
    
    def _export_conversations(self) -> List[Dict]:
        """Export conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM conversations ORDER BY timestamp')
        rows = cursor.fetchall()
        conn.close()
        
        conversations = []
        for row in rows:
            conversations.append({
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'intent': row[3],
                'entities': json.loads(row[4]) if row[4] else {},
                'sentiment': row[5],
                'timestamp': row[6],
                'session_id': row[7]
            })
        return conversations
    
    def _export_preferences(self) -> Dict:
        """Export preferences"""
        return self.get_all_preferences()
    
    def _import_memories(self, memories: List[Dict]) -> int:
        """Import memories"""
        count = 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for memory in memories:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO memories 
                    (id, type, content, metadata, tags, priority, is_encrypted,
                     created_at, updated_at, accessed_at, access_count, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    memory.get('id', f"mem_{uuid.uuid4().hex[:16]}"),
                    memory.get('type', MemoryType.GENERAL.value),
                    memory.get('content', ''),
                    json.dumps(memory.get('metadata', {})),
                    json.dumps(memory.get('tags', [])),
                    memory.get('priority', 2),
                    1 if memory.get('is_encrypted') else 0,
                    memory.get('created_at', datetime.now().isoformat()),
                    memory.get('updated_at', datetime.now().isoformat()),
                    memory.get('accessed_at', datetime.now().isoformat()),
                    memory.get('access_count', 0),
                    memory.get('source', 'import')
                ))
                count += 1
            except Exception as e:
                self.logger.error(f"Error importing memory: {e}")
        
        conn.commit()
        conn.close()
        return count
    
    def _import_conversations(self, conversations: List[Dict]) -> int:
        """Import conversations"""
        count = 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for conv in conversations:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO conversations 
                    (id, role, content, intent, entities, sentiment, timestamp, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    conv.get('id', f"conv_{uuid.uuid4().hex[:16]}"),
                    conv.get('role', 'user'),
                    conv.get('content', ''),
                    conv.get('intent', ''),
                    json.dumps(conv.get('entities', {})),
                    conv.get('sentiment', 'neutral'),
                    conv.get('timestamp', datetime.now().isoformat()),
                    conv.get('session_id', 'imported')
                ))
                count += 1
            except Exception as e:
                self.logger.error(f"Error importing conversation: {e}")
        
        conn.commit()
        conn.close()
        return count
    
    def _import_preferences(self, preferences: Dict) -> int:
        """Import preferences"""
        count = 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for key, value in preferences.items():
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO preferences (key, value, category, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (key, json.dumps(value), 'general', datetime.now().isoformat()))
                count += 1
            except Exception as e:
                self.logger.error(f"Error importing preference: {e}")
        
        conn.commit()
        conn.close()
        return count
    
    def _clear_all_data(self) -> None:
        """Clear all data (for non-merge import)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM memories')
        cursor.execute('DELETE FROM conversations')
        cursor.execute('DELETE FROM preferences')
        cursor.execute('DELETE FROM sessions')
        conn.commit()
        conn.close()
    
    # ===============================
    # UTILITY METHODS
    # ===============================
    
    def count_memories(self) -> int:
        """Count total memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_conversations(self) -> int:
        """Count total conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conversations')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_preferences(self) -> int:
        """Count total preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM preferences')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage statistics"""
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        return {
            'storage_path': self.storage_path,
            'database_size_bytes': db_size,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'total_memories': self.count_memories(),
            'total_conversations': self.count_conversations(),
            'total_preferences': self.count_preferences(),
            'encryption_enabled': CRYPTO_AVAILABLE,
            'version': self.VERSION
        }
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Hapus percakapan lama"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now().timestamp() - (days * 86400)
        cursor.execute('DELETE FROM conversations WHERE timestamp < ?', 
                      (datetime.fromtimestamp(cutoff).isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def optimize_database(self) -> None:
        """Optimize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('VACUUM')
        cursor.execute('ANALYZE')
        conn.commit()
        conn.close()
        self.logger.info("Database optimized")
    
    def close(self) -> None:
        """Close database connection"""
        # SQLite connections are closed automatically
        pass


# ==========================================
# STANDALONE FUNCTIONS FOR COMMAND-LINE USE
# ==========================================

def create_memory_export(
    storage_path: str,
    output_path: str = None,
    password: str = None
) -> str:
    """Create memory export - standalone function"""
    config = ConfigManager(storage_path)
    manager = LocalMemoryManager({'agent': {'owner': config.get('owner', 'Pak Pur')}}, storage_path)
    return manager.export_all_data(output_path, password)


def restore_memory_backup(
    storage_path: str,
    backup_path: str,
    password: str = None,
    merge: bool = True
) -> Dict:
    """Restore from backup - standalone function"""
    config = ConfigManager(storage_path)
    manager = LocalMemoryManager({'agent': {'owner': config.get('owner', 'Pak Pur')}}, storage_path)
    return manager.import_data(backup_path, password, merge)


class ConfigManager:
    """Simple config manager for storage"""
    
    def __init__(self, storage_path: str):
        self.config_file = os.path.join(storage_path, "config.json")
        self.config = self._load()
    
    def _load(self) -> Dict:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
