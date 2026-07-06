"""
GAURANGA LLM Engine
Local LLM interface using Ollama
"""

import os
import json
import subprocess
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any

class LLMEngine:
    """
    Local LLM Engine using Ollama
    Supports offline operation
    """
    
    def __init__(self, config):
        self.config = config
        self.model = config.get("ai.model", "llama3.2:1b")
        self.embedding_model = config.get("ai.embedding", "nomic-embed-text")
        self.provider = config.get("ai.provider", "ollama")
        self.base_url = config.get("ai.base_url", "http://localhost:11434")
        self.status = "disconnected"
        self._conversation_history = []
    
    def initialize(self) -> bool:
        """Initialize LLM engine"""
        self.status = "connecting"
        
        # Check Ollama availability
        if self._check_connection():
            self.status = "online"
            print(f"✅ LLM Engine connected - Model: {self.model}")
            return True
        else:
            # Try to start Ollama
            if self._start_ollama():
                self.status = "online"
                return True
            
            self.status = "offline_fallback"
            print("⚠️ Ollama not available - using fallback mode")
            return False
    
    def _check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except:
            return False
    
    def _start_ollama(self) -> bool:
        """Try to start Ollama daemon"""
        try:
            # Check if ollama is installed
            result = subprocess.run(["which", "ollama"], capture_output=True)
            if result.returncode == 0:
                # Try to start in background
                subprocess.Popen(["ollama", "serve"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
                import time
                time.sleep(3)
                return self._check_connection()
        except:
            pass
        return False
    
    def generate(self, system: str, user: str, context: str = "") -> str:
        """Generate response using LLM"""
        
        if self.status == "offline_fallback":
            return self._fallback_response(user)
        
        # Build prompt
        full_prompt = f"""<system>
{system}
</system>

<context>
{context}
</context>

<user>
{user}
</user>

<assistant>"""
        
        try:
            response = self._call_ollama(full_prompt)
            return response
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_response(user)
    
    def generate_response(self, user_input: str, agent) -> str:
        """Generate response for agent"""
        
        system_prompt = agent.system_prompt
        context = agent._get_context_summary()
        
        return self.generate(system_prompt, user_input, context)
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API"""
        import urllib.request
        import urllib.error
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 512
            }
        }
        
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "").strip()
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        
        if self.status == "offline_fallback":
            return self._simple_embedding(text)
        
        try:
            data = {
                "model": self.embedding_model,
                "input": text
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/api/embeddings",
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("embedding", [])
        except:
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding"""
        import numpy as np
        
        # Simple hash-based embedding
        words = text.lower().split()
        vector = np.zeros(384)
        
        for i, word in enumerate(words[:384]):
            pos = hash(word) % 384
            vector[pos] += 1
        
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()
    
    def _fallback_response(self, user_input: str) -> str:
        """Fallback response when LLM is unavailable"""
        
        user_lower = user_input.lower()
        
        # Greetings
        if any(w in user_lower for w in ["halo", "hai", "hi", "hey"]):
            return "Halo! Saya GAURANGA. Maaf, LLM server belum aktif. Silakan pastikan Ollama berjalan di background, atau ketik perintah spesifik seperti 'status', 'help', atau 'jadwal'."
        
        # Help
        if any(w in user_lower for w in ["help", "bantu", "tolong"]):
            return """📚 COMMAND REFERENCE:

• status - Cek status sistem
• jadwal - Lihat jadwal
• ingat [text] - Simpan ke memory
• skill - Lihat daftar skills
• mode [executive/warm] - Ganti mode

• voice on/off - Toggle suara
• shutdown - Matikan agent"""
        
        # Status
        if "status" in user_lower:
            return "Status: Sistem berjalan. LLM Engine dalam mode fallback (Ollama belum terhubung)."
        
        # Default
        return "Pesan diterima. Saat ini dalam mode offline. Untuk fungsionalitas penuh, pastikan Ollama dengan model Llama berjalan."
    
    def list_models(self) -> List[str]:
        """List available models"""
        if self._check_connection():
            try:
                req = urllib.request.Request(f"{self.base_url}/api/tags")
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    return [m["name"] for m in data.get("models", [])]
            except:
                pass
        return [self.model]
    
    def pull_model(self, model: str = None) -> bool:
        """Pull a model from Ollama"""
        model = model or self.model
        
        try:
            subprocess.Popen(
                ["ollama", "pull", model],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except:
            return False
    
    def shutdown(self) -> None:
        """Shutdown LLM engine"""
        self.status = "disconnected"