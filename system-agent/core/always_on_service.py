"""
GAURANGA Always-On Service
24/7 Background Service - Selalu Aktif & Listening
Auto-save Skills dan Learn dari Percakapan
"""

import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging
import re

class AlwaysOnService:
    """
    GAURANGA Always-On Service
    
    Fitur:
    - 24/7 Running - Tidak pernah mati selama HP nyala
    - Always Listening - Dengarkan terus suara Pak Pur
    - Auto-Learn - Simpan skill baru dari percakapan
    - Hotword Detection - Aktif dengan "Hey Gaurangga"
    - Passive Listening - Dengarkan tanpa harus said "Hey"
    - Background Processing - Tidak ganggu aktivitas
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.owner = self.config.get("agent.owner", "I Made Purna Ananda")
        self.owner_nickname = self.config.get("agent.nickname", "Pak Pur")
        
        # State
        self.is_running = False
        self.is_listening = False
        self.is_passive = False
        
        # Services
        self._listening_thread = None
        self._learning_thread = None
        self._auto_save_thread = None
        self._health_check_thread = None
        
        # Skills database
        self.skills = {}
        self.learned_patterns = []
        self.learned_responses = []
        
        # Storage
        self.data_path = "./data/always_on"
        os.makedirs(self.data_path, exist_ok=True)
        
        # Hotwords
        self.hotwords = [
            "hey gauranga",
            "gauranga",
            "halo gauranga",
            "ok gauranga",
            "hei gaurangga"
        ]
        
        # Passive listening keywords
        self.passive_keywords = [
            "tolong", "bantu", "help", "buatkan", "cek",
            "jadwal", "reminder", "ingatkan", "apa", "siapa",
            "berapa", "bagaimana", "kapan", "dimana"
        ]
        
        # Logger
        self.logger = logging.getLogger("GAURANGA.AlwaysOn")
        
        # Load saved data
        self._load_data()
    
    def start(self) -> Dict[str, Any]:
        """
        Start always-on service
        """
        if self.is_running:
            return {
                "success": False,
                "message": "Service sudah berjalan"
            }
        
        self.is_running = True
        
        # Start all background services
        self._start_listening()
        self._start_learning()
        self._start_auto_save()
        self._start_health_check()
        
        self.logger.info(f"✅ GAURANGA Always-On Service started")
        self.logger.info(f"   Owner: {self.owner_nickname}")
        self.logger.info(f"   Passive Listening: {'Aktif' if self.is_passive else 'Nonaktif'}")
        
        return {
            "success": True,
            "message": f"GAURANGA Always-On Service aktif!",
            "status": {
                "running": True,
                "listening": self.is_listening,
                "passive": self.is_passive,
                "skills_learned": len(self.skills),
                "patterns_learned": len(self.learned_patterns)
            }
        }
    
    def stop(self) -> Dict[str, Any]:
        """
        Stop always-on service
        """
        if not self.is_running:
            return {
                "success": False,
                "message": "Service tidak berjalan"
            }
        
        self.is_running = False
        self.is_listening = False
        
        # Stop all threads
        if self._listening_thread:
            self._listening_thread.join(timeout=2)
        
        self._save_data()
        
        self.logger.info("🛑 GAURANGA Always-On Service stopped")
        
        return {
            "success": True,
            "message": "GAURANGA Always-On Service berhenti"
        }
    
    def pause(self) -> Dict[str, Any]:
        """Pause listening"""
        self.is_listening = False
        return {"success": True, "message": "Listening dijeda"}
    
    def resume(self) -> Dict[str, Any]:
        """Resume listening"""
        if not self.is_running:
            return {"success": False, "message": "Service tidak aktif"}
        
        self.is_listening = True
        return {"success": True, "message": "Listening dilanjutkan"}
    
    def set_passive_mode(self, enabled: bool) -> Dict[str, Any]:
        """Toggle passive listening mode"""
        self.is_passive = enabled
        self._save_data()
        
        return {
            "success": True,
            "message": f"Passive mode: {'Aktif' if enabled else 'Nonaktif'}",
            "passive": enabled
        }
    
    # ══════════════════════════════════════════════════════════════
    # LISTENING SERVICE
    # ══════════════════════════════════════════════════════════════
    
    def _start_listening(self):
        """Start listening thread"""
        self.is_listening = True
        self._listening_thread = threading.Thread(
            target=self._listening_loop,
            daemon=True
        )
        self._listening_thread.start()
        self.logger.info("🎤 Listening service started")
    
    def _listening_loop(self):
        """Main listening loop"""
        while self.is_running and self.is_listening:
            try:
                # Simulate listening (in real device, use microphone)
                audio_data = self._capture_audio()
                
                if audio_data:
                    # Check for hotword
                    if self._detect_hotword(audio_data):
                        self._on_hotword_detected()
                    # Passive listening
                    elif self.is_passive and self._detect_passive(audio_data):
                        self._on_passive_triggered(audio_data)
                
                # Small delay to prevent high CPU
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Listening error: {e}")
                time.sleep(1)
    
    def _capture_audio(self) -> str:
        """
        Capture audio from microphone
        In demo mode, returns simulated audio
        """
        # In real implementation, use microphone
        # For demo, return empty
        return ""
    
    def _detect_hotword(self, audio: str) -> bool:
        """Detect hotword in audio"""
        if not audio:
            return False
        
        audio_lower = audio.lower()
        return any(hw in audio_lower for hw in self.hotwords)
    
    def _detect_passive(self, audio: str) -> bool:
        """Detect passive trigger in audio"""
        if not audio or not self.is_passive:
            return False
        
        audio_lower = audio.lower()
        return any(kw in audio_lower for kw in self.passive_keywords)
    
    def _on_hotword_detected(self):
        """Called when hotword is detected"""
        self.logger.info(f"🎯 Hotword detected!")
        
        # In real implementation:
        # 1. Play acknowledgment sound
        # 2. Start recording command
        # 3. Process command
        # 4. Speak response
        
        # For now, just log
        print(f"🤖 GAURANGA: Ya Pak Pur, ada apa?")
    
    def _on_passive_triggered(self, audio: str):
        """Called when passive keyword is detected"""
        self.logger.info(f"👂 Passive trigger: {audio}")
        
        # Process as command
        self._process_passive_command(audio)
    
    def _process_passive_command(self, command: str):
        """Process command from passive listening"""
        # Learn from this command
        self._learn_from_interaction(command, "")
    
    # ══════════════════════════════════════════════════════════════
    # AUTO-LEARNING SERVICE
    # ══════════════════════════════════════════════════════════════
    
    def _start_learning(self):
        """Start learning thread"""
        self._learning_thread = threading.Thread(
            target=self._learning_loop,
            daemon=True
        )
        self._learning_thread.start()
        self.logger.info("🧠 Learning service started")
    
    def _learning_loop(self):
        """Continuously learn from interactions"""
        while self.is_running:
            try:
                # Analyze patterns
                self._analyze_patterns()
                
                # Learn from web/environment
                self._learn_from_environment()
                
                # Auto-save learned data
                self._save_data()
                
                # Run every 5 minutes
                for _ in range(300):  # 5 min * 60 sec
                    if self.is_running:
                        time.sleep(1)
                        
            except Exception as e:
                self.logger.error(f"Learning error: {e}")
                time.sleep(60)
    
    def _learn_from_interaction(self, command: str, response: str):
        """
        Learn from conversation interaction
        Auto-save patterns and responses
        """
        # Extract patterns
        patterns = self._extract_patterns(command)
        
        for pattern in patterns:
            # Check if already learned
            if pattern not in self.learned_patterns:
                self.learned_patterns.append({
                    "pattern": pattern,
                    "command": command,
                    "response": response,
                    "learned_at": datetime.now().isoformat(),
                    "usage_count": 0
                })
                
                self.logger.info(f"📝 New pattern learned: {pattern}")
        
        # Learn response style
        if response:
            self._learn_response_style(command, response)
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract learnable patterns from text"""
        patterns = []
        
        # Extract action patterns
        action_words = [
            "buatkan", "buat", "buat", "jadwalkan", "cek",
            "tolong", "bantu", "ingatkan", "carikan", "cari",
            "hitung", "analisa", "bandingkan", "rangkum"
        ]
        
        text_lower = text.lower()
        for word in action_words:
            if word in text_lower:
                patterns.append(word)
        
        # Extract topic patterns
        topic_patterns = [
            r"tentang (\w+)",
            r"info (\w+)",
            r"(\w+) hari ini",
            r"(\w+) besok",
            r"(\w+) minggu ini"
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, text_lower)
            patterns.extend(matches)
        
        return list(set(patterns))
    
    def _learn_response_style(self, command: str, response: str):
        """Learn response style from conversation"""
        style = {
            "command_type": self._classify_command(command),
            "response_length": len(response),
            "has_emojis": any(emoji in response for emoji in ['📊', '💰', '✅', '🔔']),
            "language": "id" if any(ind in response.lower() for ind in ['yang', 'dan', 'di']) else "en",
            "learned_at": datetime.now().isoformat()
        }
        
        if style not in self.learned_responses:
            self.learned_responses.append(style)
    
    def _classify_command(self, command: str) -> str:
        """Classify command type"""
        command_lower = command.lower()
        
        if any(w in command_lower for w in ['jadwal', 'meeting', 'appointment']):
            return "scheduling"
        elif any(w in command_lower for w in ['lapor', 'report', 'summary']):
            return "reporting"
        elif any(w in command_lower for w in ['ingatkan', 'reminder', 'alarm']):
            return "reminder"
        elif any(w in command_lower for w in ['cari', 'find', 'carikan']):
            return "search"
        elif any(w in command_lower for w in ['buatkan', 'buat', 'create']):
            return "creation"
        elif any(w in command_lower for w in ['itung', 'hitung', 'calculate']):
            return "calculation"
        else:
            return "general"
    
    def _analyze_patterns(self):
        """Analyze learned patterns for insights"""
        # Analyze usage frequency
        for pattern in self.learned_patterns:
            pattern['usage_count'] = pattern.get('usage_count', 0) + 1
        
        # Find trending topics
        if len(self.learned_patterns) > 10:
            self._identify_trends()
    
    def _identify_trends(self):
        """Identify trending topics/patterns"""
        # Count pattern frequency
        pattern_counts = {}
        for p in self.learned_patterns:
            pattern_text = p['pattern']
            pattern_counts[pattern_text] = pattern_counts.get(pattern_text, 0) + 1
        
        # Log top patterns
        top = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        if top:
            self.logger.info(f"📈 Top patterns: {top}")
    
    def _learn_from_environment(self):
        """Learn from environment and context"""
        # Learn from time of day
        hour = datetime.now().hour
        
        time_context = {
            "morning": hour >= 5 and hour < 12,
            "afternoon": hour >= 12 and hour < 15,
            "evening": hour >= 15 and hour < 18,
            "night": hour >= 18 or hour < 5
        }
        
        # Learn from location (if available)
        # In real implementation, get from GPS
        
        # Adapt response style based on context
        if time_context["morning"]:
            self.response_mode = "productive"
        elif time_context["evening"]:
            self.response_mode = "warm"
        else:
            self.response_mode = "neutral"
    
    # ══════════════════════════════════════════════════════════════
    # AUTO-SAVE SERVICE
    # ══════════════════════════════════════════════════════════════
    
    def _start_auto_save(self):
        """Start auto-save thread"""
        self._auto_save_thread = threading.Thread(
            target=self._auto_save_loop,
            daemon=True
        )
        self._auto_save_thread.start()
        self.logger.info("💾 Auto-save service started")
    
    def _auto_save_loop(self):
        """Auto-save learned data periodically"""
        while self.is_running:
            try:
                # Save every 1 minute
                time.sleep(60)
                
                if self.is_running:
                    self._save_data()
                    self.logger.info(f"💾 Auto-saved: {len(self.skills)} skills, {len(self.learned_patterns)} patterns")
                
            except Exception as e:
                self.logger.error(f"Auto-save error: {e}")
    
    # ══════════════════════════════════════════════════════════════
    # HEALTH CHECK SERVICE
    # ══════════════════════════════════════════════════════════════
    
    def _start_health_check(self):
        """Start health check thread"""
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()
        self.logger.info("🏥 Health check service started")
    
    def _health_check_loop(self):
        """Monitor service health"""
        while self.is_running:
            try:
                # Check every 30 seconds
                time.sleep(30)
                
                # Verify threads are alive
                if self.is_listening and not self._listening_thread.is_alive():
                    self.logger.warning("Listening thread died, restarting...")
                    self._start_listening()
                
                if self.is_running and not self._learning_thread.is_alive():
                    self.logger.warning("Learning thread died, restarting...")
                    self._start_learning()
                
                # Memory check
                self._check_memory()
                
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
    
    def _check_memory(self):
        """Check memory usage"""
        import psutil
        
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > 500:  # Over 500MB
                self.logger.warning(f"High memory usage: {memory_mb:.1f}MB")
                # Clean up old patterns
                if len(self.learned_patterns) > 1000:
                    self.learned_patterns = self.learned_patterns[-500:]
                    
        except:
            pass  # psutil not available
    
    # ══════════════════════════════════════════════════════════════
    # SKILL MANAGEMENT
    # ══════════════════════════════════════════════════════════════
    
    def add_skill(self, skill: Dict) -> Dict:
        """
        Add new skill to database
        Auto-learned or manually added
        """
        skill_id = skill.get('id', f"skill_{len(self.skills)}")
        
        self.skills[skill_id] = {
            **skill,
            "id": skill_id,
            "learned_at": datetime.now().isoformat(),
            "usage_count": 0,
            "auto_learned": skill.get('auto_learned', False)
        }
        
        self._save_data()
        
        self.logger.info(f"🎯 Skill added: {skill.get('name', skill_id)}")
        
        return {
            "success": True,
            "skill_id": skill_id
        }
    
    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """Get skill by ID"""
        return self.skills.get(skill_id)
    
    def find_skill_by_pattern(self, pattern: str) -> Optional[Dict]:
        """Find skill matching pattern"""
        pattern_lower = pattern.lower()
        
        for skill in self.skills.values():
            keywords = skill.get('keywords', [])
            for kw in keywords:
                if kw.lower() in pattern_lower:
                    skill['usage_count'] = skill.get('usage_count', 0) + 1
                    return skill
        
        # Check learned patterns
        for learned in self.learned_patterns:
            if learned['pattern'] in pattern_lower:
                return {
                    "name": learned['pattern'],
                    "type": "learned_pattern",
                    "response": learned.get('response', '')
                }
        
        return None
    
    def get_all_skills(self) -> List[Dict]:
        """Get all skills"""
        return list(self.skills.values())
    
    def get_learned_skills(self) -> List[Dict]:
        """Get auto-learned skills only"""
        return [s for s in self.skills.values() if s.get('auto_learned')]
    
    # ══════════════════════════════════════════════════════════════
    # DATA PERSISTENCE
    # ══════════════════════════════════════════════════════════════
    
    def _save_data(self):
        """Save all learned data"""
        data = {
            "version": self.VERSION,
            "saved_at": datetime.now().isoformat(),
            "skills": self.skills,
            "learned_patterns": self.learned_patterns,
            "learned_responses": self.learned_responses,
            "settings": {
                "is_passive": self.is_passive,
                "owner": self.owner,
                "owner_nickname": self.owner_nickname
            }
        }
        
        filepath = os.path.join(self.data_path, "always_on_data.json")
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Save error: {e}")
    
    def _load_data(self):
        """Load saved data"""
        filepath = os.path.join(self.data_path, "always_on_data.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                self.skills = data.get('skills', {})
                self.learned_patterns = data.get('learned_patterns', [])
                self.learned_responses = data.get('learned_responses', [])
                
                settings = data.get('settings', {})
                self.is_passive = settings.get('is_passive', False)
                
                self.logger.info(f"📂 Loaded: {len(self.skills)} skills, {len(self.learned_patterns)} patterns")
                
            except Exception as e:
                self.logger.error(f"Load error: {e}")
    
    # ══════════════════════════════════════════════════════════════
    # STATUS
    # ══════════════════════════════════════════════════════════════
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "running": self.is_running,
            "listening": self.is_listening,
            "passive_mode": self.is_passive,
            "skills_count": len(self.skills),
            "learned_skills_count": len(self.get_learned_skills()),
            "patterns_learned": len(self.learned_patterns),
            "uptime": self._get_uptime(),
            "version": self.VERSION
        }
    
    def _get_uptime(self) -> str:
        """Get service uptime"""
        if hasattr(self, '_start_time'):
            elapsed = time.time() - self._start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "N/A"
    
    # ══════════════════════════════════════════════════════════════
    # VOICE COMMAND INTERFACE
    # ══════════════════════════════════════════════════════════════
    
    def process_voice_command(self, audio: str) -> Dict[str, Any]:
        """
        Process voice command
        Used when hotword is detected
        """
        if not self.is_running:
            return {
                "success": False,
                "message": "Service tidak aktif"
            }
        
        # Find matching skill
        skill = self.find_skill_by_pattern(audio)
        
        if skill:
            return {
                "success": True,
                "skill_found": True,
                "skill": skill
            }
        
        # Learn from this command
        self._learn_from_interaction(audio, "")
        
        return {
            "success": True,
            "skill_found": False,
            "message": "Command received, learning from interaction"
        }


# ══════════════════════════════════════════════════════════════
# ANDROID BOOT SERVICE INTEGRATION
# ══════════════════════════════════════════════════════════════

class AndroidBootService:
    """
    Auto-start GAURANGA when Android boots
    Uses Termux:Boot or similar
    """
    
    BOOT_SCRIPT = """#!/data/data/com.termux/files/usr/bin/bash
# GAURANGA Auto-Start Script
# Place in ~/.termux/boot/ to auto-start

cd /data/data/com.termux/files/home/gauranga
python3 gauranga_agent.py --daemon --always-on
"""
    
    @staticmethod
    def generate_boot_script(path: str = "./install/gauranga-boot.sh"):
        """Generate boot script"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as f:
            f.write(AndroidBootService.BOOT_SCRIPT)
        
        os.chmod(path, 0o755)
        
        return path
    
    @staticmethod
    def get_termux_boot_instructions() -> str:
        """Get instructions for Termux:Boot setup"""
        return """
📱 AUTO-START ON ANDROID BOOT

1. Install Termux:Boot from F-Droid
2. Create folder: ~/.termux/boot/
3. Copy gauranga-boot.sh to that folder
4. Make executable: chmod +x gauranga-boot.sh
5. Reboot device

GAURANGA will auto-start when device boots!
"""


# ══════════════════════════════════════════════════════════════
# BACKGROUND LISTENING (Termux Service)
# ══════════════════════════════════════════════════════════════

class BackgroundListeningService:
    """
    Background listening using Termux:Microphone
    """
    
    SERVICE_SCRIPT = """#!/data/data/com.termux/files/usr/bin/bash
# GAURANGA Background Listener
# Runs continuously listening for commands

while true; do
    # Listen with VOSK or Whisper
    audio=$(termux-microphone-record -f)
    
    # Check for hotword
    if echo "$audio" | grep -qi "gauranga"; then
        # Process command
        termux-tts-speak "Ya Pak Pur, ada apa?"
        
        # Record command
        sleep 0.5
        command=$(termux-microphone-record -d 5)
        
        # Process with Python
        cd /data/data/com.termux/files/home/gauranga
        python3 -c "from core.always_on_service import *; s=AlwaysOnService(); s.process_command('$command')"
    fi
    
    sleep 1
done
"""
    
    @staticmethod
    def generate_service_script(path: str = "./install/gauranga-listener.sh"):
        """Generate background listener script"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as f:
            f.write(BackgroundListeningService.SERVICE_SCRIPT)
        
        os.chmod(path, 0o755)
        
        return path


# Global instance
_always_on_service = None

def get_always_on_service(config: Dict = None) -> AlwaysOnService:
    """Get or create always-on service"""
    global _always_on_service
    if _always_on_service is None:
        _always_on_service = AlwaysOnService(config)
    return _always_on_service
