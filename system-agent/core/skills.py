"""
GAURANGA Skill Manager
Manages agent skills and learning capabilities
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class Skill:
    name: str
    description: str
    category: str
    trigger_keywords: List[str]
    execute_func: Optional[Callable] = None
    code: Optional[str] = None
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    success_rate: float = 1.0
    metadata: Dict = field(default_factory=dict)

class SkillManager:
    """
    Manages GAURANGA skills - both built-in and learned
    """
    
    def __init__(self, config):
        self.config = config
        self.skills = {}
        self.learned_skills = {}
        
        # Built-in skills
        self._register_builtin_skills()
        
        # Load learned skills
        self._load_learned_skills()
    
    def _register_builtin_skills(self) -> None:
        """Register built-in skills"""
        
        # Report Generation
        self.skills["report"] = Skill(
            name="Report Generator",
            description="Generate business reports",
            category="business",
            trigger_keywords=["laporan", "report", "bulanan", "mingguan", "daily"],
            execute_func=self._skill_report
        )
        
        # Schedule Management
        self.skills["schedule"] = Skill(
            name="Schedule Manager",
            description="Manage schedules and reminders",
            category="productivity",
            trigger_keywords=["jadwal", "schedule", "reminder", "kalender", "meeting"],
            execute_func=self._skill_schedule
        )
        
        # File Management
        self.skills["file"] = Skill(
            name="File Manager",
            description="Manage files and folders",
            category="system",
            trigger_keywords=["file", "folder", "dokumen", "berkas", "cari", "buka"],
            execute_func=self._skill_file
        )
        
        # Contact Management
        self.skills["contact"] = Skill(
            name="Contact Manager",
            description="Manage contacts and communication",
            category="communication",
            trigger_keywords=["kontak", "contact", "hubungi", "telepon", "whatsapp", "wa"],
            execute_func=self._skill_contact
        )
        
        # Finance Tracking
        self.skills["finance"] = Skill(
            name="Finance Tracker",
            description="Track finances and transactions",
            category="business",
            trigger_keywords=["uang", "finance", "transaksi", "bayar", "invoice", "pembayaran"],
            execute_func=self._skill_finance
        )
        
        # Research
        self.skills["research"] = Skill(
            name="Research Assistant",
            description="Research topics and gather information",
            category="information",
            trigger_keywords=["cari", "research", "調べ", "telusuri", "investigasi"],
            execute_func=self._skill_research
        )
        
        # Writing
        self.skills["writing"] = Skill(
            name="Content Writer",
            description="Write content, emails, documents",
            category="productivity",
            trigger_keywords=["tulis", "buat", "write", "dokumen", "email", "surat"],
            execute_func=self._skill_writing
        )
        
        # Code Generation
        self.skills["code"] = Skill(
            name="Code Assistant",
            description="Generate and review code",
            category="development",
            trigger_keywords=["kode", "code", "program", "script", "coding", "python", "javascript"],
            execute_func=self._skill_code
        )
    
    def find_skill(self, intent: str) -> Optional[Skill]:
        """Find skill matching intent"""
        
        # Direct match
        if intent in self.skills:
            return self.skills[intent]
        
        # Check learned skills
        if intent in self.learned_skills:
            return self.learned_skills[intent]
        
        # Keyword matching
        for skill_name, skill in self.skills.items():
            for keyword in skill.trigger_keywords:
                if keyword in intent:
                    return skill
        
        # Check learned skills
        for skill_name, skill in self.learned_skills.items():
            for keyword in skill.trigger_keywords:
                if keyword in intent:
                    return skill
        
        return None
    
    def learn_skill(self, skill_data: Dict) -> Skill:
        """Learn a new skill from data"""
        
        skill_id = skill_data.get("id", f"skill_{int(time.time())}")
        
        skill = Skill(
            name=skill_data.get("name", "New Skill"),
            description=skill_data.get("description", ""),
            category=skill_data.get("category", "general"),
            trigger_keywords=skill_data.get("keywords", []),
            code=skill_data.get("code"),
            metadata=skill_data.get("metadata", {})
        )
        
        self.learned_skills[skill_id] = skill
        self._save_learned_skills()
        
        return skill
    
    def update_skill_usage(self, skill_id: str, success: bool) -> None:
        """Update skill usage statistics"""
        
        if skill_id in self.learned_skills:
            skill = self.learned_skills[skill_id]
            skill.usage_count += 1
            
            # Update success rate
            total = skill.usage_count
            successes = int(skill.success_rate * (total - 1))
            if success:
                successes += 1
            skill.success_rate = successes / total
            
            self._save_learned_skills()
    
    def count(self) -> int:
        """Get total skill count"""
        return len(self.skills) + len(self.learned_skills)
    
    def get_all_skills(self) -> List[Dict]:
        """Get all skills as list"""
        result = []
        
        for name, skill in self.skills.items():
            result.append({
                "id": name,
                "name": skill.name,
                "category": skill.category,
                "usage_count": skill.usage_count,
                "type": "builtin"
            })
        
        for name, skill in self.learned_skills.items():
            result.append({
                "id": name,
                "name": skill.name,
                "category": skill.category,
                "usage_count": skill.usage_count,
                "type": "learned"
            })
        
        return result
    
    # === BUILT-IN SKILL IMPLEMENTATIONS ===
    
    def _skill_report(self, user_input: str, agent) -> str:
        """Report generation skill"""
        
        if any(w in user_input for w in ["daily", "harian"]):
            return f"""
📊 LAPORAN HARIAN

Tanggal: {datetime.now().strftime('%d %B %Y')}

Status Sistem:
- GAURANGA: ✅ Online
- Memory: {agent.memory.size()} items
- Tasks: {agent.state.tasks_completed} completed

📅 Jadwal Hari Ini:
- Tidak ada jadwal

💰 Target Revenue:
- Month 1: Rp 5.000.000
- Progress: Monitoring

 siap untuk Pak Pur!
"""
        return "Report skill ready. Katakan 'laporan harian' atau 'laporan bulanan'."
    
    def _skill_schedule(self, user_input: str, agent) -> str:
        """Schedule management skill"""
        
        if "tambah" in user_input or "buat" in user_input:
            return "Baik, saya akan mencatat jadwal baru. Katakan tanggal dan waktu serta activity nya."
        
        if "lihat" in user_input or "cek" in user_input:
            reminders = agent.memory.get_by_type("reminder")
            if reminders:
                return "📅 Jadwal Anda:\n" + "\n".join([f"- {r['data']}" for r in reminders])
            return "Belum ada jadwal yang tercatat."
        
        return "Skill schedule aktif. Saya bisa membuat dan mengingatkan jadwal."
    
    def _skill_file(self, user_input: str, agent) -> str:
        """File management skill"""
        
        if "cari" in user_input:
            return "Saya akan mencari file tersebut. Bisa beritahu nama filenya?"
        
        if "buka" in user_input:
            return "File manager siap. File apa yang ingin dibuka?"
        
        return "Skill file manager aktif. Saya bisa mencari, membuka, dan mengelola file."
    
    def _skill_contact(self, user_input: str, agent) -> str:
        """Contact management skill"""
        
        contacts = {
            "bunda lila": {"name": "Ni Wayan Lestiani", "relation": "Istri"},
            "putu": {"name": "Putu Gaurangga Vishnu Bhakta", "relation": "Anak 1"},
            "kadek": {"name": "Kadek Srutakirti", "relation": "Anak 2"}
        }
        
        for name, info in contacts.items():
            if name in user_input.lower():
                return f"📱 {info['name']} ({info['relation']})"
        
        return "Skill contact manager aktif. Saya bisa membantu menghubungi kontak Anda."
    
    def _skill_finance(self, user_input: str, agent) -> str:
        """Finance tracking skill"""
        
        if "balance" in user_input or "saldo" in user_input:
            return "💰 Informasi saldo dapat dilihat melalui sistem accounting."
        
        if "transaksi" in user_input:
            return "Saya akan mencatat transaksi tersebut. Katakan nominal dan kategori."
        
        return "💵 Skill finance aktif. Saya bisa membantu tracking keuangan Anda."
    
    def _skill_research(self, user_input: str, agent) -> str:
        """Research skill"""
        return "🔍 Research mode. Katakan topik yang ingin ditelusuri."
    
    def _skill_writing(self, user_input: str, agent) -> str:
        """Writing skill"""
        return "✍️ Writing assistant aktif. Katakan apa yang ingin Anda tulis."
    
    def _skill_code(self, user_input: str, agent) -> str:
        """Code generation skill"""
        return "💻 Code assistant aktif. Katakan bahasa pemrograman dan apa yang ingin dibuat."
    
    # === PERSISTENCE ===
    
    def load(self) -> None:
        """Load all skills"""
        self._load_learned_skills()
    
    def save(self) -> None:
        """Save all skills"""
        self._save_learned_skills()
    
    def _load_learned_skills(self) -> None:
        """Load learned skills from disk"""
        path = "./data/learned_skills.json"
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    for skill_id, skill_data in data.items():
                        self.learned_skills[skill_id] = Skill(**skill_data)
            except:
                pass
    
    def load_skills(self) -> None:
        """Alias for load"""
        self.load()
    
    def _save_learned_skills(self) -> None:
        """Save learned skills to disk"""
        os.makedirs("./data", exist_ok=True)
        path = "./data/learned_skills.json"
        
        data = {}
        for skill_id, skill in self.learned_skills.items():
            data[skill_id] = {
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
                "trigger_keywords": skill.trigger_keywords,
                "code": skill.code,
                "created": skill.created,
                "usage_count": skill.usage_count,
                "success_rate": skill.success_rate,
                "metadata": skill.metadata
            }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_skills(self) -> None:
        """Load all skills"""
        self._load_learned_skills()
    
    def save(self) -> None:
        """Save all skills"""
        self._save_learned_skills()