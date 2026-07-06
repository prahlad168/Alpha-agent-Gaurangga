#!/usr/bin/env python3
"""
GAURANGA - System Agent Alpha
Offline AI Agent untuk Android
Author: GAURANGA Team
Owner: I Made Purna Ananda (Pak Pur)
"""

import os
import sys
import time
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any

# Core modules
from core.agent import GaurangaAgent
from core.memory import VectorMemory
from core.intent import IntentClassifier
from core.skills import SkillManager

# AI Engines
from engine.llm import LLMEngine
from engine.stt import STTEngine
from engine.tts import TTSEngine

# Utils
from utils.logger import Logger
from utils.config import Config

class GaurangaSystemAgent:
    """Main System Agent Class"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config(config_path)
        self.logger = Logger("GAURANGA")
        
        # Initialize components
        self.memory = VectorMemory(self.config)
        self.intent_classifier = IntentClassifier(self.config)
        self.skill_manager = SkillManager(self.config)
        self.llm = LLMEngine(self.config)
        self.stt = STTEngine(self.config)
        self.tts = TTSEngine(self.config)
        
        # Main agent
        self.agent = GaurangaAgent(
            config=self.config,
            memory=self.memory,
            intent_classifier=self.intent_classifier,
            skill_manager=self.skill_manager,
            llm=self.llm,
            stt=self.stt,
            tts=self.tts
        )
        
        # State
        self.is_running = False
        self.is_listening = False
        self.mode = "executive"  # or "warm"
        
        # Owner info
        self.owner = self.config.get("agent.owner", "Pak Pur")
        self.company = self.config.get("agent.company", "Maha Lakshmi Holdings")
        
        self.logger.info(f"🤖 GAURANGA System Agent initialized for {self.owner}")
    
    def boot(self) -> str:
        """Boot up the agent"""
        self.logger.info("🚀 Starting GAURANGA System Agent...")
        
        # Check dependencies
        checks = self._preflight_checks()
        
        # Initialize AI models
        self.logger.info("🧠 Initializing AI brain...")
        llm_ok = self.llm.initialize()
        self.stt.initialize()
        self.tts.initialize()
        
        # Load memory
        self.logger.info("💾 Loading memory...")
        self.memory.load()
        
        # Load skills
        self.logger.info("🛠️ Loading skills...")
        self.skill_manager.load_skills()
        
        self.is_running = True
        
        # Determine status
        brain_status = "🧠 ONLINE" if llm_ok else "🧠 OFFLINE (Fallback Mode)"
        
        boot_msg = f"""
╔══════════════════════════════════════════════╗
║     🤖 GAURANGA SYSTEM AGENT ONLINE          ║
╠══════════════════════════════════════════════╣
║  Owner   : {self.owner:<32}║
║  Company : {self.company:<32}║
║  Mode    : {self.mode:<32}║
║  Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<32}║
╠══════════════════════════════════════════════╣
║  Status  : ✅ OPERATIONAL                    ║
║  Brain   : {brain_status:<32}║
║  Voice   : 🎤 READY                          ║
║  Memory  : 💾 CONNECTED                      ║
╚══════════════════════════════════════════════╝

Saya GAURANGA, Agent Alpha, siap melayani, {self.owner}!
"""
        
        self.logger.info(boot_msg)
        return boot_msg
    
    def _preflight_checks(self) -> Dict[str, bool]:
        """Check all dependencies"""
        return {
            "python": sys.version_info >= (3, 8),
            "ollama": self._check_ollama(),
            "storage": os.path.exists("/data/data/com.termux/files/home"),
            "config": self.config.is_valid()
        }
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        import subprocess
        try:
            result = subprocess.run(["which", "ollama"], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def start(self) -> None:
        """Start the agent in interactive mode"""
        if not self.is_running:
            self.boot()
        
        print(f"\n🎤 GAURANGA Agent Alpha - Interactive Mode")
        print(f"Type 'help' for commands, 'exit' to quit\n")
        
        self.speak("GAURANGA Agent Alpha siap menerima perintah!")
        
        while self.is_running:
            try:
                user_input = input(f"\n👤 {self.owner}: ").strip()
                
                if not user_input:
                    continue
                
                response = self.process(user_input)
                print(f"\n🤖 GAURANGA: {response}")
                self.speak(response)
                
            except KeyboardInterrupt:
                self.shutdown()
                break
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(f"\n❌ {error_msg}")
                self.logger.error(error_msg)
    
    def start_voice(self) -> None:
        """Start voice listening mode"""
        if not self.is_running:
            self.boot()
        
        self.is_listening = True
        self.speak("Voice mode aktif. Katakan 'Hey GAURANGA' untuk memulai.")
        
        print("\n🎤 Voice Mode Active - Say 'Hey GAURANGA' to start")
        
        while self.is_listening:
            try:
                # Listen for hotword
                audio = self.stt.listen_for_hotword()
                
                if audio:
                    print("\n🎤 Hotword detected!")
                    self.speak("Ya, ada apa?")
                    
                    # Listen for command
                    command = self.stt.listen()
                    
                    if command:
                        response = self.process(command)
                        self.speak(response)
                        
            except KeyboardInterrupt:
                self.stop_listening()
            except Exception as e:
                self.logger.error(f"Voice error: {e}")
    
    def process(self, user_input: str) -> str:
        """Process user input and return response"""
        
        # Detect intent
        intent = self.intent_classifier.classify(user_input)
        
        # Check for skills
        skill = self.skill_manager.find_skill(intent)
        
        if skill:
            return skill.execute(user_input, self.agent)
        
        # Use LLM for general response
        return self.llm.generate_response(user_input, self.agent)
    
    def speak(self, text: str) -> None:
        """Convert text to speech"""
        self.tts.speak(text)
    
    def learn(self, skill_data: Dict[str, Any]) -> str:
        """Learn a new skill"""
        skill = self.skill_manager.learn_skill(skill_data)
        return f"✅ New skill learned: {skill.name}"
    
    def remember(self, data: Dict[str, Any]) -> str:
        """Store data in memory"""
        self.memory.store(data)
        return "💾 Data saved to memory"
    
    def recall(self, query: str) -> str:
        """Recall from memory"""
        results = self.memory.recall(query)
        if results:
            return f"📝 Found {len(results)} memories:\n" + "\n".join(results)
        return "Tidak ada yang ditemukan"
    
    def set_mode(self, mode: str) -> str:
        """Change agent mode"""
        valid_modes = ["executive", "warm"]
        
        if mode not in valid_modes:
            return f"Mode tidak valid. Pilihan: {', '.join(valid_modes)}"
        
        self.mode = mode
        self.config.set("agent.mode", mode)
        
        messages = {
            "executive": "Mode eksekutif aktif. Fokus pada produktivitas.",
            "warm": "Mode hangat aktif. Nada bicara lebih santai."
        }
        
        msg = messages[mode]
        self.speak(msg)
        return msg
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "running": self.is_running,
            "listening": self.is_listening,
            "mode": self.mode,
            "owner": self.owner,
            "company": self.company,
            "skills_count": self.skill_manager.count(),
            "memory_size": self.memory.size(),
            "llm_status": self.llm.status,
            "stt_status": self.stt.status,
            "tts_status": self.tts.status,
            "uptime": self.agent.get_uptime()
        }
    
    def stop_listening(self) -> None:
        """Stop voice listening"""
        self.is_listening = False
        self.speak("Voice mode dimatikan.")
    
    def shutdown(self) -> None:
        """Shutdown the agent"""
        self.logger.info("🛑 Shutting down GAURANGA...")
        
        self.is_running = False
        self.is_listening = False
        
        # Save state
        self.memory.save()
        self.skill_manager.save()
        
        self.speak("GAURANGA Agent Alpha offline. Sampai jumpa!")
        self.logger.info("👋 GAURANGA System Agent stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GAURANGA System Agent")
    parser.add_argument("--config", "-c", default="config.yaml", help="Config file path")
    parser.add_argument("--voice", "-v", action="store_true", help="Start in voice mode")
    parser.add_argument("--daemon", "-d", action="store_true", help="Run as daemon")
    parser.add_argument("--test", "-t", action="store_true", help="Test mode")
    
    args = parser.parse_args()
    
    # Create agent
    agent = GaurangaSystemAgent(args.config)
    
    if args.test:
        # Test mode
        print(agent.boot())
        print("\n✅ Test completed!")
        return
    
    # Boot
    print(agent.boot())
    
    if args.voice:
        # Voice mode
        agent.start_voice()
    else:
        # Interactive mode
        agent.start()


if __name__ == "__main__":
    main()