"""
MAHALAKSMI AIOS v1.0 - Volume II Chapter 16: Enterprise Memory System
Persistent memory manager with text similarity search and context retrieval
"""
import json
import os
import sqlite3
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class MemoryEntry:
    """A single memory entry."""
    entry_id: str
    memory_type: str  # conversation, system, revenue, operational
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)  # TF-IDF style vector
    created_at: str = ""
    updated_at: str = ""
    access_count: int = 0
    relevance_score: float = 0.0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class SessionMetadata:
    """Session metadata."""
    session_id: str
    user_id: str
    started_at: str
    last_active: str
    message_count: int = 0
    memory_ids: List[str] = field(default_factory=list)


# ============================================================================
# TEXT EMBEDDING (TF-IDF STYLE)
# ============================================================================

class TextEmbedder:
    """
    Lightweight text embedder using word frequency and n-grams.
    Provides similarity scoring without heavy ML dependencies.
    """
    
    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.doc_count = 0
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
            'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [w for w in words if w not in self.stop_words and len(w) > 2]
    
    def compute_tfidf_vector(self, text: str) -> List[float]:
        """Compute TF-IDF style vector for text."""
        tokens = self.tokenize(text)
        
        # Term frequency
        tf = defaultdict(int)
        for token in tokens:
            tf[token] += 1
        
        # Build vocabulary if new words
        for token in tokens:
            if token not in self.vocabulary:
                self.vocabulary[token] = len(self.vocabulary)
        
        # Create vector
        vector = [0.0] * max(len(self.vocabulary), 1)
        for token, freq in tf.items():
            if token in self.vocabulary:
                # TF * IDF approximation
                tf_score = freq / max(len(tokens), 1)
                idf_score = 1.0  # Simplified
                vector[self.vocabulary[token]] = tf_score * idf_score
        
        # Normalize
        magnitude = sum(v * v for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        
        self.doc_count += 1
        return vector
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)


# ============================================================================
# PERSISTENT MEMORY STORAGE
# ============================================================================

class MemoryStorage:
    """SQLite-based persistent storage for memory entries."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "memory.db"
            )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Memory entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                entry_id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                embedding TEXT,
                created_at TEXT,
                updated_at TEXT,
                access_count INTEGER DEFAULT 0,
                relevance_score REAL DEFAULT 0.0
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                started_at TEXT,
                last_active TEXT,
                message_count INTEGER DEFAULT 0,
                memory_ids TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memory_entries(created_at)")
        
        self.conn.commit()
        logger.info(f"Memory database initialized: {self.db_path}")
    
    def save_entry(self, entry: MemoryEntry) -> bool:
        """Save memory entry to database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memory_entries 
                (entry_id, memory_type, content, metadata, embedding, created_at, updated_at, access_count, relevance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.entry_id,
                entry.memory_type,
                entry.content,
                json.dumps(entry.metadata),
                json.dumps(entry.embedding),
                entry.created_at,
                entry.updated_at,
                entry.access_count,
                entry.relevance_score
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save entry: {e}")
            return False
    
    def get_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get single entry by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM memory_entries WHERE entry_id = ?", (entry_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_entry(row)
        return None
    
    def get_entries_by_type(self, memory_type: str, limit: int = 100) -> List[MemoryEntry]:
        """Get entries by memory type."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_entries 
            WHERE memory_type = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (memory_type, limit))
        
        return [self._row_to_entry(row) for row in cursor.fetchall()]
    
    def get_recent_entries(self, limit: int = 100) -> List[MemoryEntry]:
        """Get most recent entries."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_entries 
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        return [self._row_to_entry(row) for row in cursor.fetchall()]
    
    def increment_access(self, entry_id: str) -> None:
        """Increment access count for an entry."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE memory_entries 
            SET access_count = access_count + 1
            WHERE entry_id = ?
        """, (entry_id,))
        self.conn.commit()
    
    def update_relevance(self, entry_id: str, score: float) -> None:
        """Update relevance score."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE memory_entries 
            SET relevance_score = ?
            WHERE entry_id = ?
        """, (score, entry_id))
        self.conn.commit()
    
    def _row_to_entry(self, row) -> MemoryEntry:
        """Convert database row to MemoryEntry."""
        return MemoryEntry(
            entry_id=row['entry_id'],
            memory_type=row['memory_type'],
            content=row['content'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            embedding=json.loads(row['embedding']) if row['embedding'] else [],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            access_count=row['access_count'],
            relevance_score=row['relevance_score']
        )
    
    def save_session(self, session: SessionMetadata) -> bool:
        """Save session metadata."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, user_id, started_at, last_active, message_count, memory_ids)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.user_id,
                session.started_at,
                session.last_active,
                session.message_count,
                json.dumps(session.memory_ids)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[SessionMetadata]:
        """Get session by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            return SessionMetadata(
                session_id=row['session_id'],
                user_id=row['user_id'],
                started_at=row['started_at'],
                last_active=row['last_active'],
                message_count=row['message_count'],
                memory_ids=json.loads(row['memory_ids']) if row['memory_ids'] else []
            )
        return None
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# ============================================================================
# ENTERPRISE MEMORY SYSTEM
# ============================================================================

class EnterpriseMemory:
    """
    Enterprise Memory System for MAHALAKSMI AIOS.
    Provides persistent storage, context retrieval, and similarity search.
    """
    
    def __init__(self, db_path: str = None):
        self.storage = MemoryStorage(db_path)
        self.embedder = TextEmbedder()
        
        # Memory type configurations
        self.memory_types = {
            "conversation": "User conversation context",
            "system": "System events and logs",
            "revenue": "Revenue transactions and analytics",
            "operational": "Operational events and metrics"
        }
        
        logger.info("Enterprise Memory System initialized")
    
    def store(
        self,
        content: str,
        memory_type: str = "conversation",
        metadata: Dict = None,
        session_id: str = None
    ) -> MemoryEntry:
        """Store new memory entry with embedding."""
        entry_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Compute embedding
        embedding = self.embedder.compute_tfidf_vector(content)
        
        entry = MemoryEntry(
            entry_id=entry_id,
            memory_type=memory_type,
            content=content,
            metadata=metadata or {},
            embedding=embedding
        )
        
        self.storage.save_entry(entry)
        
        # Update session if provided
        if session_id:
            self._update_session(session_id, entry_id)
        
        logger.info(f"Memory stored: {entry_id} ({memory_type})")
        return entry
    
    def retrieve(
        self,
        query: str,
        memory_type: str = None,
        limit: int = 5,
        min_similarity: float = 0.1
    ) -> List[MemoryEntry]:
        """
        Retrieve memories similar to query using cosine similarity.
        """
        query_vector = self.embedder.compute_tfidf_vector(query)
        
        # Get entries to search
        if memory_type:
            entries = self.storage.get_entries_by_type(memory_type)
        else:
            entries = self.storage.get_recent_entries(limit=500)
        
        # Calculate similarities
        scored_entries = []
        for entry in entries:
            if entry.embedding:
                similarity = self.embedder.cosine_similarity(query_vector, entry.embedding)
                if similarity >= min_similarity:
                    entry.relevance_score = similarity
                    scored_entries.append(entry)
                    self.storage.increment_access(entry.entry_id)
        
        # Sort by relevance
        scored_entries.sort(key=lambda e: (e.relevance_score, e.access_count), reverse=True)
        
        return scored_entries[:limit]
    
    def get_context(
        self,
        query: str,
        memory_types: List[str] = None,
        time_range_days: int = 30,
        limit: int = 10
    ) -> str:
        """
        Get contextual summary from memory for AI queries.
        Returns formatted context string.
        """
        types = memory_types or list(self.memory_types.keys())
        
        context_parts = []
        seen_contents = set()
        
        for mem_type in types:
            entries = self.retrieve(query, memory_type=mem_type, limit=limit // len(types))
            for entry in entries:
                if entry.content not in seen_contents:
                    seen_contents.add(entry.content)
                    context_parts.append(f"[{mem_type.upper()}] {entry.content}")
        
        if context_parts:
            return "\n".join(context_parts[:limit])
        return ""
    
    def store_revenue_event(
        self,
        transaction_id: str,
        source: str,
        amount: float,
        ceo_share: float,
        operational_share: float
    ) -> MemoryEntry:
        """Store revenue event for analytics."""
        content = f"Revenue transaction: {source} amount Rp {amount:,.0f}, CEO share Rp {ceo_share:,.0f}, operational Rp {operational_share:,.0f}"
        return self.store(
            content=content,
            memory_type="revenue",
            metadata={
                "transaction_id": transaction_id,
                "source": source,
                "amount": amount,
                "ceo_share": ceo_share,
                "operational_share": operational_share
            }
        )
    
    def store_system_event(
        self,
        event_type: str,
        message: str,
        details: Dict = None
    ) -> MemoryEntry:
        """Store system event."""
        content = f"System event [{event_type}]: {message}"
        return self.store(
            content=content,
            memory_type="system",
            metadata={
                "event_type": event_type,
                "details": details or {}
            }
        )
    
    def get_revenue_history(self, days: int = 30) -> List[Dict]:
        """Get revenue history from memory."""
        entries = self.storage.get_entries_by_type("revenue", limit=1000)
        
        cutoff = datetime.now() - timedelta(days=days)
        history = []
        
        for entry in entries:
            created = datetime.fromisoformat(entry.created_at)
            if created >= cutoff:
                history.append({
                    "transaction_id": entry.metadata.get("transaction_id"),
                    "source": entry.metadata.get("source"),
                    "amount": entry.metadata.get("amount"),
                    "ceo_share": entry.metadata.get("ceo_share"),
                    "operational_share": entry.metadata.get("operational_share"),
                    "created_at": entry.created_at
                })
        
        return history
    
    def _update_session(self, session_id: str, memory_id: str) -> None:
        """Update session with new memory ID."""
        session = self.storage.get_session(session_id)
        
        if session:
            session.memory_ids.append(memory_id)
            session.last_active = datetime.now().isoformat()
            session.message_count += 1
        else:
            session = SessionMetadata(
                session_id=session_id,
                user_id="default",
                started_at=datetime.now().isoformat(),
                last_active=datetime.now().isoformat(),
                message_count=1,
                memory_ids=[memory_id]
            )
        
        self.storage.save_session(session)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        recent = self.storage.get_recent_entries(limit=1000)
        
        by_type = defaultdict(int)
        for entry in recent:
            by_type[entry.memory_type] += 1
        
        return {
            "total_entries": len(recent),
            "by_type": dict(by_type),
            "vocabulary_size": len(self.embedder.vocabulary),
            "documents_indexed": self.embedder.doc_count,
            "storage_path": self.storage.db_path
        }


# Global memory instance
_memory: Optional[EnterpriseMemory] = None


def get_memory() -> EnterpriseMemory:
    """Get or create global memory instance."""
    global _memory
    if _memory is None:
        _memory = EnterpriseMemory()
    return _memory
