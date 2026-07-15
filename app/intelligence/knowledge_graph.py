"""
MAHALAKSMI AIOS v1.0 - Volume II Chapter 17: Knowledge Graph System
Semantic graph manager for mapping complex data relationships
"""
import os
import sys
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class NodeType(Enum):
    """Node types in the knowledge graph."""
    ENTITY = "entity"          # Generic entity
    COMPANY = "company"
    SBU = "sbu"               # Strategic Business Unit
    PRODUCT = "product"
    AGENT = "agent"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"
    TRANSACTION = "transaction"
    REVENUE = "revenue"
    EVENT = "event"


class RelationType(Enum):
    """Relationship types between nodes."""
    OWNS = "owns"
    PART_OF = "part_of"
    GENERATED_BY = "generated_by"
    OWED_TO = "owed_to"
    PAID_TO = "paid_to"
    LINKED_TO = "linked_to"
    CREATED_BY = "created_by"
    BELONGS_TO = "belongs_to"
    RELATED_TO = "related_to"


@dataclass
class GraphNode:
    """Node in the knowledge graph."""
    node_id: str
    node_type: NodeType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class GraphEdge:
    """Edge/Relationship between nodes."""
    edge_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class QueryResult:
    """Result from graph query."""
    path: List[str]  # Node IDs in path
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    score: float = 0.0


# ============================================================================
# KNOWLEDGE GRAPH DATABASE
# ============================================================================

class KnowledgeGraphDB:
    """SQLite database for knowledge graph."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "knowledge_graph.db"
            )
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                name TEXT NOT NULL,
                properties TEXT,
                metadata TEXT,
                created_at TEXT
            )
        """)
        
        # Edges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                edge_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                properties TEXT,
                created_at TEXT,
                FOREIGN KEY (source_id) REFERENCES nodes(node_id),
                FOREIGN KEY (target_id) REFERENCES nodes(node_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_type ON nodes(node_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_name ON nodes(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edge_source ON edges(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edge_target ON edges(target_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation_type ON edges(relation_type)")
        
        conn.commit()
        conn.close()
        logger.info(f"Knowledge graph database initialized: {self.db_path}")
    
    def save_node(self, node: GraphNode) -> bool:
        """Save node to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO nodes 
                (node_id, node_type, name, properties, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                node.node_id,
                node.node_type.value,
                node.name,
                json.dumps(node.properties),
                json.dumps(node.metadata),
                node.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save node: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get node by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM nodes WHERE node_id = ?", (node_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_node(row)
        return None
    
    def _row_to_node(self, row) -> GraphNode:
        """Convert row to GraphNode."""
        return GraphNode(
            node_id=row['node_id'],
            node_type=NodeType(row['node_type']),
            name=row['name'],
            properties=json.loads(row['properties']) if row['properties'] else {},
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            created_at=row['created_at']
        )
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        """Get all nodes of a specific type."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM nodes WHERE node_type = ?", (node_type.value,))
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_node(row) for row in rows]
    
    def get_all_nodes(self) -> List[GraphNode]:
        """Get all nodes."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM nodes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_node(row) for row in rows]
    
    def save_edge(self, edge: GraphEdge) -> bool:
        """Save edge to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO edges 
                (edge_id, source_id, target_id, relation_type, weight, properties, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                edge.edge_id,
                edge.source_id,
                edge.target_id,
                edge.relation_type.value,
                edge.weight,
                json.dumps(edge.properties),
                edge.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save edge: {e}")
            return False
    
    def get_edges(self, source_id: str = None, target_id: str = None) -> List[GraphEdge]:
        """Get edges, optionally filtered by source or target."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if source_id and target_id:
            cursor.execute(
                "SELECT * FROM edges WHERE source_id = ? AND target_id = ?",
                (source_id, target_id)
            )
        elif source_id:
            cursor.execute("SELECT * FROM edges WHERE source_id = ?", (source_id,))
        elif target_id:
            cursor.execute("SELECT * FROM edges WHERE target_id = ?", (target_id,))
        else:
            cursor.execute("SELECT * FROM edges")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_edge(row) for row in rows]
    
    def _row_to_edge(self, row) -> GraphEdge:
        """Convert row to GraphEdge."""
        return GraphEdge(
            edge_id=row['edge_id'],
            source_id=row['source_id'],
            target_id=row['target_id'],
            relation_type=RelationType(row['relation_type']),
            weight=row['weight'],
            properties=json.loads(row['properties']) if row['properties'] else {},
            created_at=row['created_at']
        )
    
    def get_all_edges(self) -> List[GraphEdge]:
        """Get all edges."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM edges")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_edge(row) for row in rows]
    
    def delete_node(self, node_id: str) -> bool:
        """Delete node and its edges."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete edges
            cursor.execute("DELETE FROM edges WHERE source_id = ? OR target_id = ?", (node_id, node_id))
            # Delete node
            cursor.execute("DELETE FROM nodes WHERE node_id = ?", (node_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to delete node: {e}")
            return False


# ============================================================================
# KNOWLEDGE GRAPH SYSTEM
# ============================================================================

class KnowledgeGraph:
    """
    Semantic Knowledge Graph System.
    Maps complex data relationships between entities.
    """
    
    def __init__(self):
        self.db = KnowledgeGraphDB()
        self._initialized = False
        
        logger.info("KnowledgeGraph initialized")
    
    def initialize(self):
        """Initialize graph with data from other systems."""
        if self._initialized:
            return
        
        self._load_company_entities()
        self._load_revenue_relationships()
        self._load_product_relationships()
        
        self._initialized = True
        logger.info("Knowledge graph fully initialized with relationships")
    
    def _load_company_entities(self):
        """Load entities from Company Brain."""
        try:
            from app.core.digital_twin import get_company_brain
            
            brain = get_company_brain()
            profile = brain.get_profile()
            
            # Add company node
            self.add_node(
                node_id="MAHA-LAKSHMI-CORP",
                node_type=NodeType.COMPANY,
                name="MAHA LAKSHMI CORP",
                properties={
                    "founded": profile.founded_date,
                    "founder": profile.founder,
                    "mission": profile.mission
                }
            )
            
            # Add SBU nodes
            for sbu in profile.sbus:
                sbu_id = f"SBU-{sbu.get('name', 'UNKNOWN').upper().replace(' ', '-')}"
                self.add_node(
                    node_id=sbu_id,
                    node_type=NodeType.SBU,
                    name=sbu.get("name", "Unknown SBU"),
                    properties={
                        "target": sbu.get("target", 0),
                        "ceo_share": sbu.get("ceo_share", 0)
                    }
                )
                
                # Link SBU to company
                self.add_edge(
                    source_id=sbu_id,
                    target_id="MAHA-LAKSHMI-CORP",
                    relation_type=RelationType.PART_OF
                )
            
            # Add CEO/Founder node
            self.add_node(
                node_id="CEO-PAK-PUR",
                node_type=NodeType.EMPLOYEE,
                name="I Made Purna Ananda (Pak Pur)",
                properties={
                    "role": "CEO",
                    "bank_account": "BCA 6485086645",
                    "whatsapp": "081337558787",
                    "bitcoin_wallet": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
                }
            )
            
            # Link CEO to company
            self.add_edge(
                source_id="CEO-PAK-PUR",
                target_id="MAHA-LAKSHMI-CORP",
                relation_type=RelationType.OWNS
            )
            
            logger.info("Loaded company entities into knowledge graph")
        
        except Exception as e:
            logger.error(f"Failed to load company entities: {e}")
    
    def _load_revenue_relationships(self):
        """Load revenue-related nodes and relationships."""
        try:
            from app.business.revenue import get_revenue_manager
            
            revenue = get_revenue_manager()
            summary = revenue.get_summary()
            
            # Add Revenue Engine node
            self.add_node(
                node_id="REVENUE-ENGINE",
                node_type=NodeType.REVENUE,
                name="Revenue Engine",
                properties={
                    "total_revenue": summary.get("total_revenue", 0),
                    "transactions": summary.get("total_transactions", 0),
                    "ceo_share_pct": 60,
                    "operational_share_pct": 40
                }
            )
            
            # Link to company
            self.add_edge(
                source_id="REVENUE-ENGINE",
                target_id="MAHA-LAKSHMI-CORP",
                relation_type=RelationType.GENERATED_BY
            )
            
            # Add CEO share relationship
            self.add_edge(
                source_id="REVENUE-ENGINE",
                target_id="CEO-PAK-PUR",
                relation_type=RelationType.OWED_TO,
                weight=0.6,
                properties={"percentage": 60}
            )
            
            # Add recent transactions as nodes
            transactions = summary.get("recent_transactions", [])
            for txn in transactions[:10]:
                txn_id = txn.get("id", f"TXN-{len(transactions)}")
                self.add_node(
                    node_id=txn_id,
                    node_type=NodeType.TRANSACTION,
                    name=f"Transaction {txn_id}",
                    properties={
                        "amount": txn.get("amount", 0),
                        "source": txn.get("source", "unknown"),
                        "status": txn.get("status", "unknown")
                    }
                )
                
                # Link transaction to revenue engine
                self.add_edge(
                    source_id=txn_id,
                    target_id="REVENUE-ENGINE",
                    relation_type=RelationType.GENERATED_BY
                )
            
            logger.info("Loaded revenue relationships into knowledge graph")
        
        except Exception as e:
            logger.error(f"Failed to load revenue relationships: {e}")
    
    def _load_product_relationships(self):
        """Load product-related nodes and relationships."""
        try:
            from app.business.product import get_product_center
            
            product_center = get_product_center()
            products = product_center.list_products()
            
            for product in products:
                product_id = product.get("product_id", "UNKNOWN")
                self.add_node(
                    node_id=product_id,
                    node_type=NodeType.PRODUCT,
                    name=product.get("name", "Unknown Product"),
                    properties={
                        "price": product.get("price", 0),
                        "type": product.get("type", "unknown"),
                        "pricing_model": product.get("pricing_model", "unknown")
                    }
                )
                
                # Link product to company
                self.add_edge(
                    source_id=product_id,
                    target_id="MAHA-LAKSHMI-CORP",
                    relation_type=RelationType.BELONGS_TO
                )
                
                # Link product to revenue
                self.add_edge(
                    source_id=product_id,
                    target_id="REVENUE-ENGINE",
                    relation_type=RelationType.GENERATED_BY
                )
            
            logger.info("Loaded product relationships into knowledge graph")
        
        except Exception as e:
            logger.error(f"Failed to load product relationships: {e}")
    
    def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        name: str,
        properties: Dict = None,
        metadata: Dict = None
    ) -> GraphNode:
        """Add a node to the graph."""
        node = GraphNode(
            node_id=node_id,
            node_type=node_type,
            name=name,
            properties=properties or {},
            metadata=metadata or {}
        )
        
        self.db.save_node(node)
        return node
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        weight: float = 1.0,
        properties: Dict = None
    ) -> GraphEdge:
        """Add an edge between nodes."""
        import hashlib
        edge_id = hashlib.md5(
            f"{source_id}{target_id}{relation_type.value}".encode()
        ).hexdigest()[:16]
        
        edge = GraphEdge(
            edge_id=f"EDGE-{edge_id}",
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            properties=properties or {}
        )
        
        self.db.save_edge(edge)
        return edge
    
    def get_nodes(
        self,
        node_type: NodeType = None,
        search: str = None
    ) -> List[Dict]:
        """Get nodes, optionally filtered."""
        if node_type:
            nodes = self.db.get_nodes_by_type(node_type)
        else:
            nodes = self.db.get_all_nodes()
        
        result = []
        for node in nodes:
            if search:
                if search.lower() not in node.name.lower():
                    continue
            
            result.append({
                "id": node.node_id,
                "type": node.node_type.value,
                "name": node.name,
                "properties": node.properties,
                "created_at": node.created_at
            })
        
        return result
    
    def get_edges(
        self,
        source_id: str = None,
        target_id: str = None,
        relation_type: RelationType = None
    ) -> List[Dict]:
        """Get edges, optionally filtered."""
        edges = self.db.get_edges(source_id, target_id)
        
        result = []
        for edge in edges:
            if relation_type and edge.relation_type != relation_type:
                continue
            
            result.append({
                "id": edge.edge_id,
                "source": edge.source_id,
                "target": edge.target_id,
                "relation": edge.relation_type.value,
                "weight": edge.weight,
                "properties": edge.properties,
                "created_at": edge.created_at
            })
        
        return result
    
    def query(
        self,
        start_node_id: str = None,
        end_node_id: str = None,
        relation_type: RelationType = None,
        max_hops: int = 3
    ) -> List[Dict]:
        """
        Query the graph for relationships.
        Can find multi-hop paths between nodes.
        """
        results = []
        
        if start_node_id and end_node_id:
            # Find path between two nodes
            path = self._find_path(start_node_id, end_node_id, max_hops)
            if path:
                results.append({
                    "type": "path",
                    "path": path,
                    "hops": len(path) - 1
                })
        elif start_node_id:
            # Find all nodes reachable from start
            reachable = self._find_reachable(start_node_id, max_hops)
            results.append({
                "type": "reachable",
                "start": start_node_id,
                "nodes": reachable,
                "count": len(reachable)
            })
        elif relation_type:
            # Find all edges of a type
            edges = self.get_edges(relation_type=relation_type)
            results.append({
                "type": "by_relation",
                "relation": relation_type.value,
                "edges": edges,
                "count": len(edges)
            })
        
        return results
    
    def _find_path(
        self,
        start_id: str,
        end_id: str,
        max_hops: int
    ) -> List[str]:
        """Find shortest path between two nodes (BFS)."""
        from collections import deque
        
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        
        while queue:
            current, path = queue.popleft()
            
            if current == end_id:
                return path
            
            if len(path) >= max_hops + 1:
                continue
            
            # Get outgoing edges
            edges = self.db.get_edges(source_id=current)
            for edge in edges:
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, path + [edge.target_id]))
        
        return []
    
    def _find_reachable(
        self,
        start_id: str,
        max_hops: int
    ) -> List[Dict]:
        """Find all nodes reachable from start node."""
        reachable = []
        visited = {start_id}
        queue = [(start_id, 0)]
        
        while queue:
            current, depth = queue.pop(0)
            
            if depth > max_hops:
                continue
            
            edges = self.db.get_edges(source_id=current)
            for edge in edges:
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    node = self.db.get_node(edge.target_id)
                    
                    if node:
                        reachable.append({
                            "id": node.node_id,
                            "name": node.name,
                            "type": node.node_type.value,
                            "hops": depth + 1,
                            "relation": edge.relation_type.value
                        })
                    
                    queue.append((edge.target_id, depth + 1))
        
        return reachable
    
    def get_graph_stats(self) -> Dict:
        """Get knowledge graph statistics."""
        nodes = self.db.get_all_nodes()
        edges = self.db.get_all_edges()
        
        # Count by type
        node_types = {}
        for node in nodes:
            t = node.node_type.value
            node_types[t] = node_types.get(t, 0) + 1
        
        # Count by relation
        relation_types = {}
        for edge in edges:
            r = edge.relation_type.value
            relation_types[r] = relation_types.get(r, 0) + 1
        
        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes_by_type": node_types,
            "edges_by_relation": relation_types,
            "avg_connections": len(edges) / max(len(nodes), 1)
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_knowledge_graph: Optional[KnowledgeGraph] = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get or create global knowledge graph instance."""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
        _knowledge_graph.initialize()
    return _knowledge_graph
