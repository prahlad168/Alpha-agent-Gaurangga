"""
GAURANGA Vector Memory System
Stores and retrieves memories using embeddings
"""

import os
import json
import time
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

class VectorMemory:
    """
    Local Vector Memory Database
    Uses simple embeddings for offline operation
    """
    
    def __init__(self, config):
        self.config = config
        self.memories = []
        self.index = {}
        self.tags = defaultdict(list)
        self.vectors = {}
        
        # Storage path
        self.storage_path = config.get("memory.path", "./data/memory.json")
        self.embedding_dim = 384  # For nomic-embed-text
        
    def initialize(self) -> None:
        """Initialize memory system"""
        self._load()
    
    def load(self) -> None:
        """Alias for initialize"""
        self._load()
        
    def store(self, data: Any, type: str = "general", metadata: Dict = None) -> str:
        """Store data in memory"""
        
        memory_id = f"mem_{int(time.time() * 1000)}"
        
        memory = {
            "id": memory_id,
            "type": type,
            "data": data,
            "metadata": metadata or {},
            "created": datetime.now().isoformat(),
            "accessed": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # Calculate simple embedding
        memory["embedding"] = self._create_embedding(str(data))
        
        # Store
        self.memories.append(memory)
        self.index[memory_id] = len(self.memories) - 1
        
        # Index by tags
        if "tags" in memory["metadata"]:
            for tag in memory["metadata"]["tags"]:
                self.tags[tag].append(memory_id)
        
        # Auto-save
        self._save()
        
        return memory_id
    
    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """Recall memories similar to query"""
        
        query_embedding = self._create_embedding(query)
        
        # Calculate similarities
        scores = []
        for memory in self.memories:
            similarity = self._cosine_similarity(query_embedding, memory["embedding"])
            scores.append((memory, similarity))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Update access info
        results = []
        for memory, score in scores[:limit]:
            memory["access_count"] += 1
            memory["accessed"] = datetime.now().isoformat()
            memory["relevance"] = round(score, 3)
            results.append(memory)
        
        self._save()
        return results
    
    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Advanced search with filters"""
        
        results = self.recall(query)
        
        if filters:
            # Apply filters
            filtered = []
            for result in results:
                match = True
                for key, value in filters.items():
                    if result.get("metadata", {}).get(key) != value:
                        match = False
                        break
                if match:
                    filtered.append(result)
            results = filtered
        
        return results
    
    def get(self, memory_id: str) -> Optional[Dict]:
        """Get specific memory by ID"""
        if memory_id in self.index:
            memory = self.memories[self.index[memory_id]]
            memory["access_count"] += 1
            memory["accessed"] = datetime.now().isoformat()
            return memory
        return None
    
    def update(self, memory_id: str, data: Any) -> bool:
        """Update existing memory"""
        if memory_id in self.index:
            idx = self.index[memory_id]
            self.memories[idx]["data"] = data
            self.memories[idx]["embedding"] = self._create_embedding(str(data))
            self.memories[idx]["updated"] = datetime.now().isoformat()
            self._save()
            return True
        return False
    
    def delete(self, memory_id: str) -> bool:
        """Delete memory"""
        if memory_id in self.index:
            idx = self.index[memory_id]
            self.memories.pop(idx)
            
            # Rebuild index
            self._rebuild_index()
            self._save()
            return True
        return False
    
    def get_by_tag(self, tag: str) -> List[Dict]:
        """Get all memories with a tag"""
        memory_ids = self.tags.get(tag, [])
        return [self.get(mid) for mid in memory_ids if self.get(mid)]
    
    def get_by_type(self, type: str) -> List[Dict]:
        """Get all memories of a type"""
        return [m for m in self.memories if m.get("type") == type]
    
    def size(self) -> int:
        """Get number of memories"""
        return len(self.memories)
    
    def clear(self, type: str = None) -> int:
        """Clear memories, optionally by type"""
        if type:
            original = len(self.memories)
            self.memories = [m for m in self.memories if m.get("type") != type]
            deleted = original - len(self.memories)
        else:
            deleted = len(self.memories)
            self.memories = []
            self.index = {}
            self.tags = defaultdict(list)
        
        self._save()
        return deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        types = defaultdict(int)
        for memory in self.memories:
            types[memory.get("type", "unknown")] += 1
        
        return {
            "total": len(self.memories),
            "by_type": dict(types),
            "tags_count": len(self.tags),
            "top_tags": sorted(self.tags.keys(), 
                             key=lambda x: len(self.tags[x]), 
                             reverse=True)[:10]
        }
    
    # === Private Methods ===
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create simple embedding from text (TF-IDF style)"""
        # Simple bag-of-words embedding for offline use
        words = text.lower().split()
        vector = np.zeros(self.embedding_dim)
        
        for i, word in enumerate(words[:self.embedding_dim]):
            # Simple hash-based position
            pos = hash(word) % self.embedding_dim
            vector[pos] += 1
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(dot / (norm1 * norm2))
    
    def _rebuild_index(self) -> None:
        """Rebuild memory index"""
        self.index = {}
        for i, memory in enumerate(self.memories):
            self.index[memory["id"]] = i
            
        # Rebuild tags
        self.tags = defaultdict(list)
        for memory in self.memories:
            if "tags" in memory.get("metadata", {}):
                for tag in memory["metadata"]["tags"]:
                    self.tags[tag].append(memory["id"])
    
    def _save(self) -> None:
        """Save memories to disk"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Don't save embeddings (can be recalculated)
        to_save = []
        for memory in self.memories:
            mem_copy = memory.copy()
            mem_copy.pop("embedding", None)
            to_save.append(mem_copy)
        
        with open(self.storage_path, 'w') as f:
            json.dump({
                "memories": to_save,
                "tags": dict(self.tags),
                "saved": datetime.now().isoformat()
            }, f, indent=2)
    
    def _load(self) -> None:
        """Load memories from disk"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    
                self.memories = data.get("memories", [])
                self.tags = defaultdict(list, data.get("tags", {}))
                
                # Recreate index
                self._rebuild_index()
                
                # Recreate embeddings
                for memory in self.memories:
                    memory["embedding"] = self._create_embedding(str(memory.get("data", "")))
                    
            except Exception as e:
                print(f"Error loading memories: {e}")
                self.memories = []
                self.tags = defaultdict(list)