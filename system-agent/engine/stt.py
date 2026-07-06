"""
GAURANGA STT Engine
Speech-to-Text using Whisper
"""

import os
import subprocess
import threading
from typing import Optional, Callable
from abc import ABC, abstractmethod

class STTEngine(ABC):
    """Abstract STT Engine"""
    
    @abstractmethod
    def listen(self) -> str:
        pass
    
    @abstractmethod
    def listen_for_hotword(self) -> bool:
        pass

class WhisperSTT(STTEngine):
    """
    Whisper-based STT Engine
    Uses whisper.cpp for offline operation
    """
    
    def __init__(self, config):
        self.config = config
        self.model = config.get("voice.stt_model", "base")
        self.language = config.get("voice.language", "id")
        self.status = "disconnected"
        self._listening = False
        self._hotword_detected = False
        self._hotword = config.get("system.hotword", "hey gauranga").lower()
    
    def initialize(self) -> bool:
        """Initialize STT engine"""
        self.status = "ready"
        print("🎤 STT Engine initialized (Whisper)")
        return True
    
    def listen(self, timeout: int = 10) -> str:
        """Listen for audio and convert to text"""
        # For demo, return empty (would use microphone in real device)
        return ""
    
    def listen_for_hotword(self) -> bool:
        """Listen for hotword detection"""
        # For demo, return False (would use actual hotword detection in real device)
        return False
    
    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe audio file"""
        # Would use whisper.cpp here
        return ""

class WebSpeechSTT(STTEngine):
    """
    Web Speech API STT (for browser/web usage)
    """
    
    def __init__(self, config):
        self.config = config
        self.language = config.get("voice.language", "id-ID")
        self.status = "disconnected"
    
    def initialize(self) -> bool:
        """Initialize Web Speech STT"""
        self.status = "ready"
        print("🎤 STT Engine initialized (Web Speech API)")
        return True
    
    def listen(self) -> str:
        """Listen using Web Speech API - implemented in browser JS"""
        return ""
    
    def listen_for_hotword(self) -> bool:
        """Listen for hotword - requires additional setup"""
        return False

class STTFactory:
    """Factory for creating STT engines"""
    
    @staticmethod
    def create(config, platform: str = "auto"):
        """Create appropriate STT engine"""
        
        if platform == "auto":
            # Detect platform
            if os.path.exists("/data/data/com.termux"):
                platform = "termux"
            elif os.path.exists("/system/app"):
                platform = "android"
            else:
                platform = "generic"
        
        if platform in ["termux", "android"]:
            return WhisperSTT(config)
        else:
            return WebSpeechSTT(config)