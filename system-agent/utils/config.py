"""
GAURANGA Config
Configuration management
"""

import os
import yaml
from typing import Any, Dict, Optional

class Config:
    """Configuration manager for GAURANGA"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = {}
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self._save()
    
    def _default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "agent": {
                "name": "GAURANGA",
                "owner": "I Made Purna Ananda",
                "nickname": "Pak Pur",
                "company": "Maha Lakshmi Holdings",
                "mode": "executive"
            },
            "ai": {
                "model": "llama3.2:1b",
                "embedding": "nomic-embed-text",
                "provider": "ollama",
                "base_url": "http://localhost:11434"
            },
            "voice": {
                "stt": "whisper",
                "tts": "piper",
                "language": "id",
                "rate": 1.0
            },
            "memory": {
                "type": "local",
                "path": "./data/memory.json",
                "persist": True
            },
            "system": {
                "background": True,
                "hotword": "hey gauranga",
                "permissions": ["storage", "notification"]
            }
        }
    
    def _save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set config value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save()
    
    def is_valid(self) -> bool:
        """Check if config is valid"""
        required = ["agent.owner", "agent.name"]
        return all(self.get(key) for key in required)
    
    def reload(self) -> None:
        """Reload configuration"""
        self._load()