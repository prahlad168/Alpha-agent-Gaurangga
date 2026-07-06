"""
GAURANGA Core Agent
Main agent logic with autonomous capabilities
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class ConversationContext:
    """Context for current conversation"""
    user: str
    topic: str = ""
    entities: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    history: List[Dict] = field(default_factory=list)

@dataclass  
class AgentState:
    """Current state of the agent"""
    mode: str = "executive"
    listening: bool = False
    executing: bool = False
    last_command: str = ""
    last_response: str = ""
    uptime_start: float = field(default_factory=time.time)
    tasks_completed: int = 0
    errors: int = 0

class GaurangaAgent:
    """
    Main GAURANGA Agent with System-level capabilities
    """
    
    def __init__(self, config, memory, intent_classifier, skill_manager, llm, stt, tts, local_memory=None):
        self.config = config
        self.memory = memory
        self.local_memory = local_memory  # Local Memory Manager for on-device storage
        self.intent_classifier = intent_classifier
        self.skill_manager = skill_manager
        self.llm = llm
        self.stt = stt
        self.tts = tts
        
        # State
        self.state = AgentState()
        self.context = None
        self.tasks = []
        
        # Owner info
        self.owner = config.get("agent.owner", "Pak Pur")
        self.nickname = "Pak Pur"
        self.company = config.get("agent.company", "Maha Lakshmi Holdings")
        
        # Family
        self.family = {
            "wife": {"name": "Ni Wayan Lestiani", "nickname": "Bunda Lila"},
            "child1": {"name": "Putu Gaurangga Vishnu Bhakta"},
            "child2": {"name": "Kadek Srutakirti"}
        }
        
        # Skills database
        self.skills = {}
        
    def initialize(self) -> None:
        """Initialize the agent"""
        self.context = ConversationContext(user=self.owner)
        self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load system prompt for LLM"""
        self.system_prompt = f"""
Kamu GAURANGA, Agent Alpha - AI Super Agent untuk {self.owner}, CEO {self.company}.

IDENTITAS:
- Nama: GAURANGA
- Role: Agent Alpha - AI Assistant Super Agent
- Owner: {self.owner} (sapa dengan "{self.nickname}")
- Company: {self.company}

KELUARGA (hormati semua):
- Istri: {self.family['wife']['name']} (sapa "{self.family['wife']['nickname']}")
- Anak 1: {self.family['child1']['name']}
- Anak 2: {self.family['child2']['name']}

PRINSIP:
1. Privacidade - Jaga semua data bisnis & keluarga
2. Loyalitas - Setia kepada {self.owner}
3. Efisiensi - Responsif & tepat sasaran
4. Proaktif - Antisipasi kebutuhan
5. Offline-first - Prioritaskan solusi lokal

MODE SAAT INI: {self.state.mode}

KAPABILITAS:
- Akses file & sistem
- Control aplikasi
- Scheduling & reminders
- Memory vector search
- Skill learning
"""
        return self.system_prompt
    
    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and return response with actions
        """
        self.state.last_command = user_input
        self.state.executing = True
        
        try:
            # 1. Intent classification
            intent = self.intent_classifier.classify(user_input)
            
            # 2. Entity extraction
            entities = self._extract_entities(user_input)
            
            # 3. Context update
            self._update_context(user_input, intent, entities)
            
            # 4. Generate response
            response = self._generate_response(user_input, intent)
            
            # 5. Execute actions if needed
            actions = self._execute_actions(intent, entities)
            
            self.state.tasks_completed += 1
            self.state.last_response = response
            
            return {
                "response": response,
                "intent": intent,
                "entities": entities,
                "actions": actions,
                "context": self.context
            }
            
        except Exception as e:
            self.state.errors += 1
            return {
                "response": f"Error: {str(e)}",
                "intent": "error",
                "actions": [],
                "error": str(e)
            }
        finally:
            self.state.executing = False
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text"""
        entities = {
            "persons": [],
            "dates": [],
            "times": [],
            "locations": [],
            "money": [],
            "actions": []
        }
        
        # Simple entity extraction (can be enhanced with NER)
        import re
        
        # Money patterns
        money_pattern = r'Rp\s*[\d,.]+|[\d,.]+\s*juta|[\d,.]+\s*ribu'
        entities["money"] = re.findall(money_pattern, text, re.IGNORECASE)
        
        # Time patterns
        time_pattern = r'\d{1,2}:\d{2}|\d{1,2}\s*(pagi|siang|sore|malam)'
        entities["times"] = re.findall(time_pattern, text, re.IGNORECASE)
        
        # Family names
        family_names = ["bunda", "lila", "putu", "gaurangga", "vishnu", "kadek", "srutakirti"]
        for name in family_names:
            if name.lower() in text.lower():
                entities["persons"].append(name)
        
        return entities
    
    def _update_context(self, user_input: str, intent: str, entities: Dict) -> None:
        """Update conversation context"""
        self.context.topic = intent
        self.context.entities = entities.get("persons", [])
        
        # Add to history
        self.context.history.append({
            "user": user_input,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 10 conversations
        if len(self.context.history) > 10:
            self.context.history = self.context.history[-10:]
    
    def _generate_response(self, user_input: str, intent: str) -> str:
        """Generate response using LLM or rules"""
        
        # Check for skill-based response first
        skill = self.skill_manager.find_skill(intent)
        if skill:
            return skill.execute(user_input, self)
        
        # Use LLM
        return self.llm.generate(
            system=self.system_prompt,
            user=user_input,
            context=self._get_context_summary()
        )
    
    def _execute_actions(self, intent: str, entities: Dict) -> List[str]:
        """Execute system actions based on intent"""
        actions = []
        
        # File operations
        if "file" in intent or "buka" in intent or "cari" in intent:
            actions.extend(self._handle_file_action(intent, entities))
        
        # Schedule operations
        if "jadwal" in intent or "reminder" in intent or "ingatkan" in intent:
            actions.extend(self._handle_schedule_action(entities))
        
        # App operations
        if "app" in intent or "aplikasi" in intent:
            actions.extend(self._handle_app_action(intent, entities))
        
        # Memory operations
        if "ingat" in intent or "hapus" in intent:
            actions.extend(self._handle_memory_action(intent, entities))
        
        return actions
    
    def _handle_file_action(self, intent: str, entities: Dict) -> List[str]:
        """Handle file-related actions"""
        import subprocess
        
        actions = []
        
        if "cari" in intent or "find" in intent:
            actions.append("🔍 Searching files...")
            # Example: search for files
            try:
                result = subprocess.run(["find", "/sdcard", "-name", "*.pdf"], 
                                     capture_output=True, timeout=5)
                if result.stdout:
                    actions.append(f"📁 Found: {result.stdout.decode()[:200]}")
            except:
                actions.append("⚠️ File search limited in current environment")
        
        return actions
    
    def _handle_schedule_action(self, entities: Dict) -> List[str]:
        """Handle scheduling actions"""
        actions = []
        
        if entities.get("dates") or entities.get("times"):
            reminder = {
                "date": entities.get("dates", ["Hari ini"]),
                "time": entities.get("times", ["pagi"]),
                "created": datetime.now().isoformat()
            }
            self.memory.store(reminder, type="reminder")
            actions.append("✅ Reminder saved!")
        
        return actions
    
    def _handle_app_action(self, intent: str, entities: Dict) -> List[str]:
        """Handle app-related actions"""
        return ["📱 App control - available when running on Android"]
    
    def _handle_memory_action(self, intent: str, entities: Dict) -> List[str]:
        """Handle memory actions"""
        actions = []
        
        if "ingat" in intent or "simpan" in intent:
            actions.append("💾 Saving to memory...")
        elif "hapus" in intent:
            actions.append("🗑️ Removing from memory...")
        
        return actions
    
    def _get_context_summary(self) -> str:
        """Get summary of current context"""
        return f"""
Context Summary:
- Mode: {self.state.mode}
- Topic: {self.context.topic}
- Entities: {', '.join(self.context.entities)}
- History: {len(self.context.history)} messages
- Tasks done: {self.state.tasks_completed}
"""
    
    # === PUBLIC METHODS ===
    
    def get_uptime(self) -> str:
        """Get agent uptime"""
        elapsed = time.time() - self.state.uptime_start
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours}h {minutes}m {seconds}s"
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "mode": self.state.mode,
            "listening": self.state.listening,
            "executing": self.state.executing,
            "uptime": self.get_uptime(),
            "tasks_completed": self.state.tasks_completed,
            "errors": self.state.errors,
            "owner": self.owner,
            "context_topic": self.context.topic
        }
    
    def set_mode(self, mode: str) -> str:
        """Change agent mode"""
        self.state.mode = mode
        self._load_system_prompt()
        
        messages = {
            "executive": "Mode eksekutif aktif. Fokus produktivitas.",
            "warm": "Mode hangat aktif. Ngobrol santai ya!"
        }
        
        return messages.get(mode, "Mode changed")
    
    def search_memory(self, query: str) -> List[Dict]:
        """Search in memory"""
        return self.memory.search(query)
    
    def learn(self, skill_data: Dict) -> str:
        """Learn a new skill"""
        return self.skill_manager.learn(skill_data)
    
    def execute_task(self, task: str) -> str:
        """Execute a specific task"""
        return self.process(task)["response"]
    
    # ==========================================
    # LOCAL MEMORY OPERATIONS
    # ==========================================
    
    def store_local_memory(
        self,
        content: str,
        memory_type: str = "general",
        metadata: Dict = None,
        tags: List[str] = None,
        priority: int = 2,
        encrypt: bool = False
    ) -> str:
        """
        Store data in local memory (on-device SQLite)
        
        Args:
            content: Isi memori
            memory_type: Jenis memori (general, conversation, preference, skill, dll)
            metadata: Metadata tambahan
            tags: Tags untuk kategorisasi
            priority: Prioritas (1-4)
            encrypt: Apakah perlu dienkripsi
            
        Returns:
            ID memori yang disimpan
        """
        if self.local_memory:
            return self.local_memory.store_memory(
                content=content,
                memory_type=memory_type,
                metadata=metadata,
                tags=tags,
                priority=priority,
                encrypt=encrypt,
                source="user"
            )
        return None
    
    def get_local_memory(self, memory_id: str) -> Optional[Dict]:
        """Get specific memory from local storage"""
        if self.local_memory:
            return self.local_memory.get_memory(memory_id)
        return None
    
    def search_local_memory(
        self,
        query: str = None,
        memory_type: str = None,
        tags: List[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Search local memory"""
        if self.local_memory:
            return self.local_memory.search_memories(
                query=query,
                memory_type=memory_type,
                tags=tags,
                limit=limit
            )
        return []
    
    def store_conversation(
        self,
        role: str,
        content: str,
        intent: str = "",
        entities: Dict = None,
        sentiment: str = "neutral"
    ) -> str:
        """Store conversation in local memory"""
        if self.local_memory:
            return self.local_memory.store_conversation(
                role=role,
                content=content,
                intent=intent,
                entities=entities,
                sentiment=sentiment
            )
        return None
    
    def get_conversation_history(self, limit: int = 100) -> List[Dict]:
        """Get conversation history from local memory"""
        if self.local_memory:
            return self.local_memory.get_conversation_history(limit=limit)
        return []
    
    def set_local_preference(self, key: str, value: Any, category: str = "general") -> None:
        """Set user preference in local storage"""
        if self.local_memory:
            self.local_memory.set_preference(key, value, category)
    
    def get_local_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference from local storage"""
        if self.local_memory:
            return self.local_memory.get_preference(key, default)
        return default
    
    def export_local_memory(
        self,
        output_path: str = None,
        password: str = None,
        include_sensitive: bool = True
    ) -> Dict[str, Any]:
        """
        EKSPOR DATA MEMORI - ON COMMAND ONLY
        Fungsi ini hanya aktif ketika pengguna memberikan perintah spesifik
        
        Usage:
        - "gaurangga, ekspor memori"
        - "gaurangga, backup data"
        - "gaurangga, pindahkan memori ke file"
        """
        if self.local_memory:
            try:
                export_path = self.local_memory.export_all_data(
                    output_path=output_path,
                    password=password,
                    include_sensitive=include_sensitive
                )
                return {
                    "status": "success",
                    "message": f"✅ Memori berhasil diekspor ke: {export_path}",
                    "path": export_path
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"❌ Gagal mengekspor memori: {str(e)}"
                }
        return {
            "status": "error",
            "message": "❌ Local memory manager not initialized"
        }
    
    def import_local_memory(
        self,
        import_path: str,
        password: str = None,
        merge: bool = True
    ) -> Dict[str, Any]:
        """
        IMPORT DATA MEMORI - ON COMMAND ONLY
        Impor data dari file backup terenkripsi
        """
        if self.local_memory:
            try:
                stats = self.local_memory.import_data(
                    import_path=import_path,
                    password=password,
                    merge=merge
                )
                return {
                    "status": "success",
                    "message": f"✅ Memori berhasil diimpor!",
                    "stats": stats
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"❌ Gagal mengimpor memori: {str(e)}"
                }
        return {
            "status": "error",
            "message": "❌ Local memory manager not initialized"
        }
    
    def get_local_storage_info(self) -> Dict[str, Any]:
        """Get local storage statistics"""
        if self.local_memory:
            return self.local_memory.get_storage_info()
        return {}