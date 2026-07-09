#!/usr/bin/env python3
"""
GAURANGA - System AI v2.0
Main Entry Point for System-Level AI Agent
Author: I Made Purna Ananda (Pak Pur)
Company: MAHA LAKSHMI HOLDINGS
"""

import os
import sys
import time
import json
import logging
import threading
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import Config
from utils.logger import setup_logger
from core.agent import GaurangaAgent
from core.memory import MemoryManager
from core.intent import IntentClassifier
from core.skills import SkillManager
from engine.llm import LLMEngine
from engine.stt import STTEngine
from engine.tts import TTSEngine

class GaurangaSystem:
    """
    GAURANGA - System AI Main Controller
    Handles all system-level operations and AI processing
    """
    
    def __init__(self, config_path: str = None):
        self.version = "2.0"
        self.start_time = datetime.now()
        
        # Load configuration
        self.config = Config(config_path)
        
        # Setup logging
        self.logger = setup_logger("GAURANGA", self.config.log_path)
        
        # System components
        self.agent = None
        self.memory = None
        self.intent = None
        self.skills = None
        self.llm = None
        self.stt = None
        self.tts = None
        
        # System state
        self.is_running = False
        self.is_listening = False
        self.is_speaking = False
        
        # User context
        self.user = {
            "name": "I Made Purna Ananda",
            "nickname": "Pak Pur",
            "role": "CEO",
            "company": "Maha Lakshmi Holdings",
            "whatsapp": "081337558787"
        }
        
        self.family = {
            "wife": {"name": "Ni Wayan Lestiani", "nickname": "Bunda Lila"},
            "child1": {"name": "Putu Gaurangga Vishnu Bhakta"},
            "child2": {"name": "Kadek Srutakirti"}
        }
        
    def initialize(self):
        """Initialize all system components"""
        self.logger.info("=" * 50)
        self.logger.info("GAURANGA System AI v2.0 - INITIALIZING")
        self.logger.info("=" * 50)
        
        # Initialize components
        self.logger.info("📦 Initializing Memory System...")
        self.memory = MemoryManager(self.config)
        
        self.logger.info("🧠 Initializing Intent Classifier...")
        self.intent = IntentClassifier(self.config)
        
        self.logger.info("⚡ Initializing Skill Manager...")
        self.skills = SkillManager(self.config)
        
        self.logger.info("🤖 Initializing LLM Engine...")
        self.llm = LLMEngine(self.config)
        
        self.logger.info("🎤 Initializing STT Engine...")
        self.stt = STTEngine(self.config)
        
        self.logger.info("🔊 Initializing TTS Engine...")
        self.tts = TTSEngine(self.config)
        
        self.logger.info("🤖 Initializing Agent Core...")
        self.agent = GaurangaAgent(
            config=self.config,
            llm=self.llm,
            memory=self.memory,
            intent=self.intent,
            skills=self.skills,
            user=self.user
        )
        
        self.logger.info("✅ All systems initialized successfully!")
        return True
        
    def start(self):
        """Start GAURANGA System"""
        self.logger.info("🚀 Starting GAURANGA System...")
        self.is_running = True
        
        # Boot sequence
        self._boot_sequence()
        
        # Start background services
        self._start_background_services()
        
        self.logger.info("✅ GAURANGA System is now ACTIVE!")
        return True
        
    def _boot_sequence(self):
        """Display boot sequence"""
        boot_messages = [
            ("⚡", "Initializing core systems..."),
            ("🧠", "Loading AI brain..."),
            ("🎤", "Setting up voice engine..."),
            ("🔒", "Security protocols active..."),
            ("✅", "GAURANGA ready!"),
        ]
        
        for emoji, message in boot_messages:
            self.logger.info(f"{emoji} {message}")
            time.sleep(0.5)
            
    def _start_background_services(self):
        """Start background monitoring services"""
        
        def memory_cleanup():
            """Periodic memory cleanup"""
            while self.is_running:
                time.sleep(300)  # Every 5 minutes
                if self.memory:
                    self.memory.cleanup()
                    
        def health_check():
            """System health monitoring"""
            while self.is_running:
                time.sleep(60)  # Every minute
                self._log_status()
                
        # Start background threads
        threading.Thread(target=memory_cleanup, daemon=True).start()
        threading.Thread(target=health_check, daemon=True).start()
        
    def _log_status(self):
        """Log system status"""
        uptime = datetime.now() - self.start_time
        status = {
            "uptime": str(uptime),
            "memory_active": self.memory is not None,
            "llm_ready": self.llm is not None if self.llm else False,
            "stt_ready": self.stt is not None if self.stt else False,
            "tts_ready": self.tts is not None if self.tts else False,
        }
        self.logger.debug(f"System Status: {json.dumps(status)}")
        
    def process_voice(self, audio_data: bytes) -> str:
        """Process voice input and return response"""
        try:
            self.is_listening = True
            
            # Speech to text
            self.logger.info("🎤 Processing voice input...")
            text = self.stt.process(audio_data)
            
            if not text:
                return None
                
            self.logger.info(f"📝 Recognized: {text}")
            
            # Process with agent
            response = self.agent.process(text)
            
            # Text to speech
            if response:
                self.logger.info("🔊 Generating voice response...")
                self.tts.speak(response)
                
            self.is_listening = False
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing voice: {e}")
            self.is_listening = False
            return None
            
    def process_text(self, text: str) -> str:
        """Process text input and return response"""
        try:
            self.logger.info(f"💬 Input: {text}")
            response = self.agent.process(text)
            self.logger.info(f"🤖 Response: {response}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            return "Maaf, terjadi kesalahan dalam memproses permintaan Anda."
            
    def speak(self, text: str):
        """Speak text using TTS"""
        if self.tts:
            self.tts.speak(text)
            
    def stop(self):
        """Stop GAURANGA System"""
        self.logger.info("🛑 Stopping GAURANGA System...")
        self.is_running = False
        
        # Cleanup
        if self.memory:
            self.memory.save()
            
        self.logger.info("✅ GAURANGA System stopped.")
        
    def get_status(self) -> dict:
        """Get system status"""
        return {
            "version": self.version,
            "running": self.is_running,
            "uptime": str(datetime.now() - self.start_time),
            "components": {
                "agent": self.agent is not None,
                "memory": self.memory is not None,
                "llm": self.llm is not None if self.llm else False,
                "stt": self.stt is not None if self.stt else False,
                "tts": self.tts is not None if self.tts else False,
            }
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="GAURANGA System AI v2.0")
    parser.add_argument("--config", "-c", type=str, default=None, help="Path to config file")
    parser.add_argument("--mode", "-m", type=str, default="interactive", 
                       choices=["interactive", "voice", "api", "service"],
                       help="Operation mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Create GAURANGA instance
    gauranga = GaurangaSystem(config_path=args.config)
    
    # Initialize
    if not gauranga.initialize():
        print("❌ Failed to initialize GAURANGA System")
        sys.exit(1)
        
    print("✅ GAURANGA System AI v2.0 initialized successfully!")
    print(f"📁 Config: {gauranga.config.config_path}")
    print(f"🧠 Mode: {args.mode}")
    print()
    
    if args.mode == "interactive":
        # Interactive mode
        print("=" * 50)
        print("GAURANGA System AI - Interactive Mode")
        print("Type 'quit' or 'exit' to stop")
        print("=" * 50)
        
        gauranga.start()
        
        try:
            while True:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ["quit", "exit", "stop"]:
                    break
                    
                if not user_input:
                    continue
                    
                response = gauranga.process_text(user_input)
                print(f"\n🤖 GAURANGA: {response}")
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted by user")
            
    elif args.mode == "voice":
        # Voice mode
        print("🎤 Voice mode - Say 'Hey GAURANGA' to activate")
        gauranga.start()
        
        # Note: Full voice mode requires proper audio setup
        print("⚠️ Voice mode requires audio hardware")
        
    elif args.mode == "api":
        # API mode
        print("🌐 API mode - Starting REST API server...")
        gauranga.start()
        print("⚠️ API server not implemented yet")
        
    elif args.mode == "service":
        # Background service mode
        print("⚙️ Service mode - Running as background service")
        gauranga.start()
        
        try:
            while gauranga.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    # Stop GAURANGA
    gauranga.stop()
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
