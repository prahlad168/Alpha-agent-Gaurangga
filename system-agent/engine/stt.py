"""
GAURANGA STT Engine
Speech-to-Text using Whisper
"""

import os
import subprocess
import threading
from typing import Optional, Callable
from abc import ABC, abstractmethod

class STTEngine:
    """
    STT Engine - Uses Whisper for offline operation
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
        return ""

# Alias for compatibility
WhisperSTT = STTEngine