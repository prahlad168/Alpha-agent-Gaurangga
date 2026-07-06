"""
GAURANGA TTS Engine
Text-to-Speech using Piper/Kokoro
"""

import os
import subprocess
import threading
from typing import Optional, List

class TTSEngine:
    """
    Text-to-Speech Engine
    Supports Piper, Kokoro, and system TTS
    """
    
    def __init__(self, config):
        self.config = config
        self.engine = config.get("voice.tts", "system")
        self.language = config.get("voice.language", "id")
        self.rate = config.get("voice.rate", 1.0)
        self.status = "disconnected"
        self._queue = []
        self._speaking = False
    
    def initialize(self) -> bool:
        """Initialize TTS engine"""
        self.status = "ready"
        print(f"🔊 TTS Engine initialized ({self.engine})")
        return True
    
    def speak(self, text: str, blocking: bool = False) -> None:
        """Convert text to speech"""
        if not text:
            return
        
        self._queue.append(text)
        
        if not self._speaking:
            if blocking:
                self._process_queue()
            else:
                thread = threading.Thread(target=self._process_queue)
                thread.daemon = True
                thread.start()
    
    def _process_queue(self) -> None:
        """Process speech queue"""
        self._speaking = True
        
        while self._queue:
            text = self._queue.pop(0)
            self._speak_text(text)
        
        self._speaking = False
    
    def _speak_text(self, text: str) -> None:
        """Speak single text"""
        
        if self.engine == "piper":
            self._speak_piper(text)
        elif self.engine == "kokoro":
            self._speak_kokoro(text)
        elif self.engine == "espeak":
            self._speak_espeak(text)
        else:
            self._speak_system(text)
    
    def _speak_piper(self, text: str) -> None:
        """Speak using Piper TTS"""
        try:
            # Would use piper here
            # echo "text" | piper -m model.onnx -c config.json
            print(f"[PIPER TTS] {text}")
        except Exception as e:
            print(f"Piper TTS error: {e}")
            self._speak_system(text)
    
    def _speak_kokoro(self, text: str) -> None:
        """Speak using Kokoro TTS"""
        try:
            # Would use kokoro here
            print(f"[KOKORO TTS] {text}")
        except Exception as e:
            print(f"Kokoro TTS error: {e}")
            self._speak_system(text)
    
    def _speak_espeak(self, text: str) -> None:
        """Speak using espeak"""
        try:
            subprocess.run(
                ["espeak", "-v", self.language, text],
                capture_output=True,
                timeout=10
            )
        except:
            self._speak_system(text)
    
    def _speak_system(self, text: str) -> None:
        """Speak using system TTS"""
        # Print for demo
        print(f"🔊 SPEAKING: {text}")
    
    def stop(self) -> None:
        """Stop current speech"""
        self._queue = []
        self._speaking = False
    
    def set_rate(self, rate: float) -> None:
        """Set speech rate"""
        self.rate = max(0.5, min(2.0, rate))
    
    def set_language(self, language: str) -> None:
        """Set language"""
        self.language = language

class WebSpeechTTS:
    """
    Web Speech API TTS (for browser)
    This is used by the web interface
    """
    
    def __init__(self):
        self.status = "ready"
    
    def speak(self, text: str) -> None:
        """Speak using Web Speech API - implemented in browser JS"""
        # This is called from Python but handled by JS in browser
        print(f"[Web Speech TTS] {text}")
    
    def stop(self) -> None:
        """Stop speech"""
        pass