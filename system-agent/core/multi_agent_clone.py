"""
GAURANGA Multi-Agent Clone System
Alpha Gaurangga sebagai LEAD AGENT & COMMAND CENTER
Semua instruksi dari Pak Pur HARUS lewat Alpha Gaurangga
Kloning agent mengeksekusi tugas dari Alpha Gaurangga
"""

import os
import json
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import sqlite3
from enum import Enum

class AgentType(Enum):
    """Jenis Agent"""
    LEAD = "lead"           # Alpha Gaurangga (Master - COMMAND CENTER)
    CLONE = "clone"         # Kloning dengan kemampuan sama - WORKER
    SPECIALIST = "specialist" # Agent spesialis - TARGETED WORKER
    WORKER = "worker"        # Agent worker - EXECUTOR

class AgentStatus(Enum):
    """Status Agent"""
    ACTIVE = "active"
    STANDBY = "standby"
    OFFLINE = "offline"
    SYNCING = "syncing"
    EXECUTING = "executing"

class CommandPriority(Enum):
    """Prioritas Command"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class CommandStatus(Enum):
    """Status Command"""
    PENDING = "pending"
    SENT = "sent"
    RECEIVED = "received"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Command:
    """Command dari Lead ke Clone"""
    id: str
    from_lead: bool
    to_agent_id: str
    command_text: str
    priority: CommandPriority
    status: CommandStatus
    created_at: str
    executed_at: str = None
    result: str = None

@dataclass
class AgentProfile:
    """Profil Agent"""
    id: str
    name: str
    type: AgentType
    role: str
    owner: str
    device_id: str
    status: AgentStatus
    skills: List[str]
    memory_size: int
    created_at: str
    last_sync: str
    lead_agent_id: str  # ID agent lead (Alpha Gaurangga)
    commands_received: int = 0
    commands_executed: int = 0

class MultiAgentSystem:
    """
    Sistem Multi-Agent dengan Alpha Gaurangga sebagai LEAD & COMMAND CENTER
    
    ARsitektur:
    ┌──────────────────────────────────────────────────────────────┐
    │                    👑 PAK PUR (OWNER)                         │
    └──────────────────────────┬───────────────────────────────────┘
                               │ INSTRUKSI
    ┌──────────────────────────▼───────────────────────────────────┐
    │              👑 ALPHA GAURANGA (LEAD / COMMAND CENTER)      │
    │                                                              │
    │  • Menerima instruksi dari Pak Pur                          │
    │  • Menerjemahkan ke bahasa agent                            │
    │  • Membagi tugas ke sub-agents                             │
    │  • Monitoring & reporting ke Pak Pur                         │
    └──────────────────────────┬───────────────────────────────────┘
                               │ COMMAND (LEAD)
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │ CLONE 1 │         │ CLONE 2 │         │ CLONE 3 │
    │  Alpha  │         │  Beta   │         │  Gamma  │
    │ Worker  │         │ Worker  │         │ Worker  │
    └────┬────┘         └────┬────┘         └────┬────┘
         │                     │                     │
         └─────────────────────┴─────────────────────┘
                          │ RESULT
    ┌─────────────────────▼───────────────────────────────────┐
    │              👑 ALPHA GAURANGA (REPORT)                  │
    │  • Kompilasi hasil dari semua clone                     │
    │  • Report ke Pak Pur                                    │
    │  • Sync memory baru ke semua agent                      │
    └──────────────────────────────────────────────────────────┘
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.owner = self.config.get("agent.owner", "I Made Purna Ananda")
        self.owner_nickname = self.config.get("agent.nickname", "Pak Pur")
        self.lead_agent_id = "alpha_gauranga_lead"
        
        # Storage
        self.db_path = "./data/multi_agent.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Initialize lead agent
        self._init_lead_agent()
        
        # Command queue
        self.pending_commands = []
        self.command_history = []
    
    def _init_database(self):
        """Initialize multi-agent database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                role TEXT,
                owner TEXT NOT NULL,
                device_id TEXT,
                status TEXT DEFAULT 'active',
                skills TEXT,
                memory_size INTEGER DEFAULT 0,
                created_at TEXT,
                last_sync TEXT,
                lead_agent_id TEXT,
                config TEXT,
                FOREIGN KEY (lead_agent_id) REFERENCES agents(id)
            )
        ''')
        
        # Agent memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_memories (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                memory_type TEXT,
                content TEXT,
                encrypted INTEGER DEFAULT 1,
                created_at TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        ''')
        
        # Sync log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_logs (
                id TEXT PRIMARY KEY,
                from_agent TEXT,
                to_agent TEXT,
                sync_type TEXT,
                data_hash TEXT,
                timestamp TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_lead_agent(self):
        """Initialize Alpha Gaurangga as Lead Agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if lead exists
        cursor.execute('SELECT id FROM agents WHERE id = ?', (self.lead_agent_id,))
        if not cursor.fetchone():
            # Create lead agent
            cursor.execute('''
                INSERT INTO agents 
                (id, name, type, role, owner, status, skills, created_at, last_sync)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.lead_agent_id,
                "Alpha Gaurangga",
                AgentType.LEAD.value,
                "Master Agent - CEO AI Assistant",
                self.owner,
                AgentStatus.ACTIVE.value,
                json.dumps(["all_skills"]),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
        
        conn.close()
    
    # ══════════════════════════════════════════════════════════════
    # CLONE AGENT
    # ══════════════════════════════════════════════════════════════
    
    def create_clone(
        self,
        name: str,
        role: str,
        device_id: str = None,
        copy_skills: bool = True,
        copy_memory: bool = True
    ) -> Dict:
        """
        Buat kloning agent dengan kemampuan setara Alpha Gaurangga
        """
        clone_id = f"clone_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get lead agent skills
        cursor.execute('SELECT skills FROM agents WHERE id = ?', (self.lead_agent_id,))
        lead_skills = cursor.fetchone()[0] if cursor.fetchone else "[]"
        
        # Create clone agent
        cursor.execute('''
            INSERT INTO agents 
            (id, name, type, role, owner, device_id, status, skills, created_at, last_sync, lead_agent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            clone_id,
            name,
            AgentType.CLONE.value,
            role,
            self.owner,
            device_id or f"device_{clone_id}",
            AgentStatus.STANDBY.value,
            lead_skills if copy_skills else "[]",
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            self.lead_agent_id
        ))
        
        # Copy memory if requested
        if copy_memory:
            self._copy_lead_memory(clone_id)
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "clone_id": clone_id,
            "name": name,
            "role": role,
            "message": f"Clone '{name}' berhasil dibuat dengan kemampuan Alpha Gaurangga!"
        }
    
    def _copy_lead_memory(self, clone_id: str):
        """Copy memory dari lead ke clone"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get lead memories
        cursor.execute('SELECT * FROM agent_memories WHERE agent_id = ?', (self.lead_agent_id,))
        memories = cursor.fetchall()
        
        # Copy to clone
        for mem in memories:
            cursor.execute('''
                INSERT INTO agent_memories 
                (id, agent_id, memory_type, content, encrypted, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                f"{mem[0]}_copy_{clone_id}",
                clone_id,
                mem[2],
                mem[3],
                mem[4],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    # ══════════════════════════════════════════════════════════════
    # LIST AGENTS
    # ══════════════════════════════════════════════════════════════
    
    def get_all_agents(self) -> List[Dict]:
        """Get semua agent termasuk lead"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM agents ORDER BY type DESC, created_at ASC')
        rows = cursor.fetchall()
        conn.close()
        
        agents = []
        for row in rows:
            agents.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "role": row[3],
                "owner": row[4],
                "device_id": row[5],
                "status": row[6],
                "skills": json.loads(row[7]) if row[7] else [],
                "created_at": row[9],
                "last_sync": row[10],
                "is_lead": row[0] == self.lead_agent_id
            })
        
        return agents
    
    def get_lead_agent(self) -> Dict:
        """Get Alpha Gaurangga (Lead Agent)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM agents WHERE id = ?', (self.lead_agent_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "role": row[3],
                "status": row[6],
                "is_lead": True,
                "sub_agents_count": self._count_sub_agents()
            }
        
        return None
    
    def _count_sub_agents(self) -> int:
        """Count sub-agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM agents WHERE lead_agent_id = ?', (self.lead_agent_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # ══════════════════════════════════════════════════════════════
    # SYNC & TRANSFER
    # ══════════════════════════════════════════════════════════════
    
    def sync_agent(self, agent_id: str, direction: str = "to_agent") -> Dict:
        """
        Sync memory antara lead dan sub-agent
        direction: "to_agent" atau "from_agent"
        """
        if agent_id == self.lead_agent_id:
            return {"success": False, "message": "Lead agent tidak perlu sync"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update status
        cursor.execute('''
            UPDATE agents SET status = ?, last_sync = ? WHERE id = ?
        ''', (AgentStatus.SYNCING.value, datetime.now().isoformat(), agent_id))
        
        # Create sync log
        sync_id = f"sync_{int(time.time())}"
        cursor.execute('''
            INSERT INTO sync_logs 
            (id, from_agent, to_agent, sync_type, data_hash, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            sync_id,
            self.lead_agent_id if direction == "to_agent" else agent_id,
            agent_id if direction == "to_agent" else self.lead_agent_id,
            direction,
            hashlib.sha256(str(time.time()).encode()).hexdigest()[:16],
            datetime.now().isoformat(),
            "completed"
        ))
        
        # Update status to active
        cursor.execute('''
            UPDATE agents SET status = ? WHERE id = ?
        ''', (AgentStatus.ACTIVE.value, agent_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "sync_id": sync_id,
            "message": f"Sync {'dari Lead ke' if direction == 'to_agent' else 'dari'} {agent_id} selesai!"
        }
    
    def export_agent(
        self,
        agent_id: str,
        password: str = None
    ) -> Dict:
        """
        Export agent untuk transfer ke device lain
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get agent data
        cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
        agent_row = cursor.fetchone()
        
        if not agent_row:
            conn.close()
            return {"success": False, "message": "Agent tidak ditemukan"}
        
        # Get memories
        cursor.execute('SELECT * FROM agent_memories WHERE agent_id = ?', (agent_id,))
        memories = cursor.fetchall()
        conn.close()
        
        # Create export package
        package = {
            "version": self.VERSION,
            "exported_at": datetime.now().isoformat(),
            "agent": {
                "id": agent_row[0],
                "name": agent_row[1],
                "type": agent_row[2],
                "role": agent_row[3],
                "owner": agent_row[4],
                "device_id": f"new_device_{uuid.uuid4().hex[:8]}",
                "skills": json.loads(agent_row[7]) if agent_row[7] else [],
                "created_at": agent_row[9]
            },
            "memories": [
                {
                    "type": m[2],
                    "content": m[3],
                    "created_at": m[5]
                }
                for m in memories
            ],
            "from_lead": agent_row[0] == self.lead_agent_id or agent_row[11] == self.lead_agent_id
        }
        
        # Encrypt if password provided
        if password:
            package = self._encrypt_package(package, password)
        
        # Save to file
        filename = f"agent_{package['agent']['name'].lower().replace(' ', '_')}_{int(time.time())}.gauranga"
        filepath = f"./exports/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "filepath": filepath,
            "filename": filename,
            "agent_name": package['agent']['name'],
            "message": f"Agent '{package['agent']['name']}' siap ditransfer!"
        }
    
    def import_agent(self, filepath: str, password: str = None) -> Dict:
        """
        Import agent dari file
        """
        if not os.path.exists(filepath):
            return {"success": False, "message": "File tidak ditemukan"}
        
        with open(filepath, 'r') as f:
            package = json.load(f)
        
        # Decrypt if needed
        if password and package.get("encrypted"):
            package = self._decrypt_package(package, password)
        
        # Create new agent ID
        new_id = f"imported_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert agent
        cursor.execute('''
            INSERT INTO agents 
            (id, name, type, role, owner, device_id, status, skills, created_at, last_sync, lead_agent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_id,
            package['agent']['name'],
            package['agent']['type'],
            package['agent']['role'],
            package['agent']['owner'],
            package['agent']['device_id'],
            AgentStatus.ACTIVE.value,
            json.dumps(package['agent'].get('skills', [])),
            package['agent']['created_at'],
            datetime.now().isoformat(),
            self.lead_agent_id if package.get('from_lead') else None
        ))
        
        # Insert memories
        for mem in package.get('memories', []):
            cursor.execute('''
                INSERT INTO agent_memories
                (id, agent_id, memory_type, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                f"mem_{uuid.uuid4().hex[:8]}",
                new_id,
                mem['type'],
                mem['content'],
                mem['created_at']
            ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "agent_id": new_id,
            "name": package['agent']['name'],
            "message": f"Agent '{package['agent']['name']}' berhasil diimpor!"
        }
    
    def _encrypt_package(self, package: Dict, password: str) -> Dict:
        """Encrypt export package"""
        # Simple XOR encryption for demo
        # In real, use proper encryption
        import base64
        
        data = json.dumps(package)
        key = hashlib.sha256(password.encode()).digest()
        
        encrypted = ''.join(
            chr(ord(a) ^ ord(b)) for a, b in zip(data, key * (len(data) // len(key) + 1))
        )
        
        return {
            "encrypted": True,
            "data": base64.b64encode(encrypted.encode()).decode()
        }
    
    def _decrypt_package(self, package: Dict, password: str) -> Dict:
        """Decrypt export package"""
        import base64
        
        encrypted = base64.b64decode(package['data']).decode()
        key = hashlib.sha256(password.encode()).digest()
        
        decrypted = ''.join(
            chr(ord(a) ^ ord(b)) for a, b in zip(encrypted, key * (len(encrypted) // len(key) + 1))
        )
        
        return json.loads(decrypted)
    
    # ══════════════════════════════════════════════════════════════
    # COMMAND CENTER - Alpha Gaurangga sebagai LEAD
    # ══════════════════════════════════════════════════════════════
    
    def issue_command(
        self,
        instruction: str,
        target_agents: List[str] = None,
        priority: CommandPriority = CommandPriority.NORMAL,
        broadcast: bool = False
    ) -> Dict:
        """
        Alpha Gaurangga menerima instruksi dari Pak Pur
        dan menerjemahkan ke command untuk sub-agents
        
        Args:
            instruction: Instruksi dari Pak Pur (dalam bahasa natural)
            target_agents: List ID agent yang dituju
            priority: Prioritas command
            broadcast: True = kirim ke semua clone
        """
        # Pak Pur instruksi ke Alpha Gaurangga
        # Alpha Gaurangga menerjemahkan
        
        if broadcast:
            agents = self.get_all_agents()
            clones = [a for a in agents if a['type'] != AgentType.LEAD.value]
            target_agents = [c['id'] for c in clones]
        
        if not target_agents:
            return {
                "success": False,
                "message": "Tidak ada agent yang dituju"
            }
        
        # Create command for each agent
        command_id = f"cmd_{int(time.time())}"
        results = []
        
        for agent_id in target_agents:
            cmd = {
                "id": f"{command_id}_{agent_id}",
                "from_lead": True,
                "to_agent_id": agent_id,
                "command_text": instruction,
                "priority": priority.value,
                "status": CommandStatus.SENT.value,
                "created_at": datetime.now().isoformat()
            }
            
            self.pending_commands.append(cmd)
            self.command_history.append(cmd)
            
            # Update agent stats
            self._update_agent_stats(agent_id, commands_received=1)
            
            results.append({
                "agent_id": agent_id,
                "command_id": cmd["id"],
                "status": "SENT"
            })
        
        return {
            "success": True,
            "command_id": command_id,
            "total_targets": len(target_agents),
            "results": results,
            "message": f"✅ Command dari Pak Pur sudah diteruskan ke {len(target_agents)} agent!"
        }
    
    def execute_instruction(self, pak_pur_instruction: str) -> Dict:
        """
        Eksekusi instruksi dari Pak Pur
        Alpha Gaurangga sebagai mediator
        """
        # Parse instruksi
        parsed = self._parse_instruction(pak_pur_instruction)
        
        # Determine target agents
        targets = self._get_target_agents(parsed.get("targets", []))
        
        if not targets:
            return {
                "success": False,
                "message": "Tidak ada agent yang sesuai dengan instruksi Pak Pur"
            }
        
        # Issue command
        result = self.issue_command(
            instruction=pak_pur_instruction,
            target_agents=[a['id'] for a in targets],
            priority=CommandPriority[parsed.get("priority", "NORMAL").upper()]
        )
        
        # Add report for Pak Pur
        result["report_to_pak_pur"] = {
            "instruction_received": pak_pur_instruction,
            "agents_deployed": len(targets),
            "agent_names": [a['name'] for a in targets],
            "estimated_completion": "Tergantung kompleksitas tugas"
        }
        
        return result
    
    def _parse_instruction(self, instruction: str) -> Dict:
        """Parse instruksi dari Pak Pur"""
        instruction_lower = instruction.lower()
        
        parsed = {
            "original": instruction,
            "targets": [],
            "priority": "NORMAL",
            "action": None
        }
        
        # Detect targets
        if "semua" in instruction_lower or "all" in instruction_lower:
            parsed["targets"] = ["broadcast"]
        
        # Detect priority
        if any(w in instruction_lower for w in ["urgent", "segera", "kritis"]):
            parsed["priority"] = "URGENT"
        elif any(w in instruction_lower for w in ["penting", "high"]):
            parsed["priority"] = "HIGH"
        
        # Detect action
        actions = ["report", "update", "create", "delete", "check", "monitor"]
        for action in actions:
            if action in instruction_lower:
                parsed["action"] = action
                break
        
        return parsed
    
    def _get_target_agents(self, criteria: List[str]) -> List[Dict]:
        """Get agents berdasarkan criteria"""
        all_agents = self.get_all_agents()
        
        if "broadcast" in criteria:
            return [a for a in all_agents if a['type'] != AgentType.LEAD.value]
        
        # Filter by criteria
        targets = []
        for c in criteria:
            for a in all_agents:
                if c.lower() in a['name'].lower() or c.lower() in a['role'].lower():
                    if a not in targets:
                        targets.append(a)
        
        return targets or all_agents[1:]  # Default: semua clone
    
    def _update_agent_stats(self, agent_id: str, commands_received: int = 0, commands_executed: int = 0):
        """Update agent statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agents 
            SET commands_received = commands_received + ?,
                commands_executed = commands_executed + ?
            WHERE id = ?
        ''', (commands_received, commands_executed, agent_id))
        
        conn.commit()
        conn.close()
    
    # ══════════════════════════════════════════════════════════════
    # AGENT COMMANDS (From Lead)
    # ══════════════════════════════════════════════════════════════
    
    def command_clone(
        self,
        clone_id: str,
        command: str,
        broadcast: bool = False
    ) -> Dict:
        """
        Kirim command ke clone dari lead
        Jika broadcast=True, kirim ke semua clone
        """
        if broadcast:
            agents = self.get_all_agents()
            clones = [a for a in agents if a['type'] == AgentType.CLONE.value]
            
            results = []
            for clone in clones:
                results.append({
                    "clone_id": clone['id'],
                    "status": "command_sent"
                })
            
            return {
                "success": True,
                "broadcast": True,
                "recipients": len(clones),
                "results": results
            }
        
        # Single command
        return {
            "success": True,
            "clone_id": clone_id,
            "command": command,
            "status": "command_sent"
        }
    
    def get_pending_commands(self, agent_id: str = None) -> List[Dict]:
        """Get semua pending commands"""
        if agent_id:
            return [c for c in self.pending_commands if c['to_agent_id'] == agent_id]
        return self.pending_commands
    
    def complete_command(self, command_id: str, result: str) -> Dict:
        """Mark command sebagai completed"""
        for cmd in self.pending_commands:
            if cmd['id'] == command_id:
                cmd['status'] = CommandStatus.COMPLETED.value
                cmd['executed_at'] = datetime.now().isoformat()
                cmd['result'] = result
                
                # Update agent stats
                self._update_agent_stats(cmd['to_agent_id'], commands_executed=1)
                
                return {
                    "success": True,
                    "message": f"Command {command_id} completed"
                }
        
        return {"success": False, "message": "Command not found"}
    
    def get_agent_status(self, agent_id: str = None) -> Dict:
        """Get status agent"""
        if agent_id:
            agents = [a for a in self.get_all_agents() if a['id'] == agent_id]
            if agents:
                return agents[0]
            return None
        
        lead = self.get_lead_agent()
        clones = [a for a in self.get_all_agents() if a['type'] != AgentType.LEAD.value]
        
        return {
            "lead": lead,
            "total_agents": len(clones) + 1,
            "active_clones": len([c for c in clones if c['status'] == 'active']),
            "standby_clones": len([c for c in clones if c['status'] == 'standby']),
            "clones": clones
        }
    
    # ══════════════════════════════════════════════════════════════
    # PRE-DEFINED AGENT TEMPLATES
    # ══════════════════════════════════════════════════════════════
    
    def create_from_template(self, template: str) -> Dict:
        """
        Buat agent dari template
        
        Templates:
        - "sales": Agent sales dengan skill terkait
        - "marketing": Agent marketing
        - "assistant": Assistant umum
        - "security": Agent keamanan
        """
        templates = {
            "sales": {
                "name": "Sales Agent",
                "role": "Sales & Business Development",
                "skills": ["lead_generation", "crm", "negotiation", "proposal"]
            },
            "marketing": {
                "name": "Marketing Agent",
                "role": "Marketing & Content",
                "skills": ["content_creation", "social_media", "seo", "ads"]
            },
            "assistant": {
                "name": "Personal Assistant",
                "role": "Personal Helper",
                "skills": ["scheduling", "email", "research", "reminders"]
            },
            "security": {
                "name": "Security Agent",
                "role": "Security Monitor",
                "skills": ["monitoring", "alert", "encryption", "backup"]
            }
        }
        
        if template not in templates:
            return {"success": False, "message": f"Template '{template}' tidak ditemukan"}
        
        t = templates[template]
        return self.create_clone(
            name=t['name'],
            role=t['role'],
            copy_skills=True,
            copy_memory=True
        )
    
    # ══════════════════════════════════════════════════════════════
    # QUICK COMMANDS
    # ══════════════════════════════════════════════════════════════
    
    def quick_clone(self, name: str) -> Dict:
        """Quick clone dengan nama saja"""
        return self.create_clone(
            name=name,
            role="Assistant Clone",
            copy_skills=True,
            copy_memory=True
        )
    
    def delete_agent(self, agent_id: str) -> Dict:
        """Hapus agent (tidak bisa hapus lead)"""
        if agent_id == self.lead_agent_id:
            return {"success": False, "message": "Tidak bisa hapus Lead Agent!"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM agent_memories WHERE agent_id = ?', (agent_id,))
        cursor.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"Agent {agent_id} dihapus"}


# ══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════

def main():
    """CLI untuk multi-agent system"""
    system = MultiAgentSystem()
    
    print("""
╔═══════════════════════════════════════════════╗
║   GAURANGA MULTI-AGENT SYSTEM                ║
║   Alpha Gaurangga - Lead Agent               ║
╚═══════════════════════════════════════════════╝
    """)
    
    print("Perintah:")
    print("1. clone <nama>     - Buat clone agent")
    print("2. list            - Lihat semua agent")
    print("3. status          - Status system")
    print("4. export <id>    - Export agent")
    print("5. import <file>   - Import agent")
    print("6. sync <id>        - Sync agent")
    print("7. delete <id>     - Hapus agent")
    print("8. template <type> - Buat dari template")
    print("q. Quit")
    print()
    
    while True:
        cmd = input("GAURANGA> ").strip()
        
        if cmd == 'q':
            break
        
        elif cmd.startswith('clone '):
            name = cmd[6:].strip()
            result = system.quick_clone(name)
            print(result['message'])
        
        elif cmd == 'list':
            agents = system.get_all_agents()
            for a in agents:
                lead = "👑 " if a['is_lead'] else "  "
                print(f"{lead}{a['name']} ({a['type']}) - {a['status']}")
        
        elif cmd == 'status':
            status = system.get_agent_status()
            print(f"Lead: {status['lead']['name']}")
            print(f"Total Agents: {status['total_agents']}")
            print(f"Active Clones: {status['active_clones']}")
        
        elif cmd.startswith('template '):
            template = cmd[9:].strip()
            result = system.create_from_template(template)
            if result['success']:
                print(result['message'])
            else:
                print(result['message'])
        
        elif cmd == 'help':
            print("1. clone <nama>     - Buat clone agent")
            print("2. list            - Lihat semua agent")
            print("3. status          - Status system")
            print("4. export <id>    - Export agent")
            print("5. import <file>   - Import agent")
            print("6. sync <id>        - Sync agent")
            print("7. delete <id>     - Hapus agent")
            print("8. template <type> - Buat dari template")


if __name__ == "__main__":
    main()
