"""
GAURANGA Intent Classifier
Classifies user intent from natural language
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Intent:
    name: str
    confidence: float
    entities: Dict
    original: str

class IntentClassifier:
    """
    Intent classifier for GAURANGA
    Uses rule-based + pattern matching for offline operation
    """
    
    def __init__(self, config):
        self.config = config
        self.intents = self._load_intents()
        self.fallback_intent = "general"
    
    def _load_intents(self) -> Dict:
        """Load intent definitions"""
        return {
            # Greetings
            "greeting": {
                "patterns": [
                    r"\b(halo|hai|hi|hey|pagi|siang|sore|malam)\b",
                    r"\b(apa kabar|gimana|baik|greeting)\b",
                    r"\bselamat\s\w+"
                ],
                "responses": [
                    "Halo! Ada yang bisa saya bantu?",
                    "Hai! Siap membantu!",
                    "Selamat datang!"
                ],
                "priority": 1
            },
            
            # Tasks & Commands
            "task": {
                "patterns": [
                    r"\b(buat|bikin|kerjakan|eksekusi|lakukan)\b",
                    r"\b(tolong|bantu|assist)\b.*\b(tugas|kerjaan)\b"
                ],
                "keywords": ["buat", "bikin", "kerjakan", "eksekusi", "tugas", "kerjaan"]
            },
            
            # File Operations
            "file": {
                "patterns": [
                    r"\b(cari|temukan|open|buka|copy|pindahkan|hapus)\b.*\b(file|folder|berkas|dokumen)\b",
                    r"\b(file|folder|berkas|dokumen)\b.*\b(cari|open|buka)\b"
                ],
                "keywords": ["cari", "buka", "file", "folder", "dokumen", "berkas"],
                "sub_intents": ["search", "open", "copy", "move", "delete"]
            },
            
            # Schedule & Reminders
            "schedule": {
                "patterns": [
                    r"\b(jadwal|agenda|kalender|appointment)\b",
                    r"\b(ingatkan|reminder|notifikasi|alarm)\b",
                    r"\b(nanti|later|besok|hari ini)\b.*\b(ingat|pengingat)\b",
                    r"\b(buat|jadwalkan|set)\b.*\b(jadwal|meeting|appointment)\b"
                ],
                "keywords": ["jadwal", "reminder", "ingatkan", "kalender", "meeting", "appointment"],
                "priority": 2
            },
            
            # Search
            "search": {
                "patterns": [
                    r"\b(cari|temukan|search|google)\b",
                    r"\b(apa itu|who is|dimana|dimana)\b",
                    r"\b?\?$"
                ],
                "keywords": ["cari", "search", "apa", "siapa", "dimana", "kenapa", "mengapa"]
            },
            
            # Settings
            "settings": {
                "patterns": [
                    r"\b(setting|config|konfigurasi|pengaturan)\b",
                    r"\b(ubah|change|ganti|update)\b.*\b(setting|mode|config)\b"
                ],
                "keywords": ["setting", "config", "mode", "pengaturan"]
            },
            
            # System
            "system": {
                "patterns": [
                    r"\b(status|info|sistem|system|info)\b",
                    r"\b(apa|how)\b.*\b(status|kerja|perform)\b"
                ],
                "keywords": ["status", "sistem", "info", "kerja", "perform"]
            },
            
            # Voice
            "voice": {
                "patterns": [
                    r"\b(voice|suara|speech|listen|bicara|ucap)\b",
                    r"\b(matikan|aktifkan|nyalakan)\b.*\b(suara|voice|sound)\b"
                ],
                "keywords": ["voice", "suara", "bicara", "dengar"]
            },
            
            # Memory
            "memory": {
                "patterns": [
                    r"\b(ingat|remember|memory|hapus|forget)\b",
                    r"\b(cek|check)\b.*\b(memory|ingatan|history)\b",
                    r"\b(tidak|don't)\b.*\b(ingat|remember)\b"
                ],
                "keywords": ["ingat", "memory", "hapus", "history"]
            },
            
            # Skills
            "skills": {
                "patterns": [
                    r"\b(skill|kemampuan|bisa|capability)\b",
                    r"\b(ajari|train|belajar|learn)\b.*\b(skill|kemampuan)\b",
                    r"\bapa\b.*\b(bisa|skill)\b"
                ],
                "keywords": ["skill", "kemampuan", "bisa", "ajari"]
            },
            
            # Communication
            "communication": {
                "patterns": [
                    r"\b(telepon|call|chat|message|whatsapp|sms)\b",
                    r"\b(kirim|send|hubungi|contact)\b.*\b(orang|message|wa)\b"
                ],
                "keywords": ["telepon", "chat", "whatsapp", "message", "sms", "hubungi"]
            },
            
            # Money/Finance
            "finance": {
                "patterns": [
                    r"\b(uang|money|finance|transaksi|invoice|bayar)\b",
                    r"\b(berapa|amount|nominal)\b.*\b(duit|uang|money)\b"
                ],
                "keywords": ["uang", "money", "bayar", "invoice", "duit"]
            },
            
            # Company
            "company": {
                "patterns": [
                    r"\b(company|perusahaan|bisnis|maha|lakshmi)\b",
                    r"\b(report|laporan|revenue|pendapatan)\b"
                ],
                "keywords": ["company", "perusahaan", "bisnis", "report", "laporan"]
            },
            
            # Family
            "family": {
                "patterns": [
                    r"\b(bunda|lila|istri|suami|anak|putu|kadek|gaurangga|vishnu|srutakirti)\b"
                ],
                "keywords": ["bunda", "lila", "putu", "kadek", "istri", "anak", "keluarga"]
            },
            
            # Mode
            "mode": {
                "patterns": [
                    r"\b(mode|santai|formal|eksekutif|warm|executive)\b"
                ],
                "keywords": ["mode", "santai", "formal", "eksekutif"]
            },
            
            # Help
            "help": {
                "patterns": [
                    r"\b(help|bantu|tolong|how|caranya)\b",
                    r"\bapa\b.*\b(bisa|dapat)\b.*\b(lakukan|do)\b"
                ],
                "keywords": ["help", "bantu", "tolong", "cara"]
            },
            
            # Shutdown
            "shutdown": {
                "patterns": [
                    r"\b(shutdown|matikan|exit|quit|berhenti|close)\b"
                ],
                "keywords": ["shutdown", "matikan", "exit", "berhenti"]
            }
        }
    
    def classify(self, text: str) -> str:
        """Classify intent from text"""
        text_lower = text.lower()
        
        scores = {}
        
        for intent_name, intent_data in self.intents.items():
            score = 0
            matched = False
            
            # Check patterns
            for pattern in intent_data.get("patterns", []):
                if re.search(pattern, text_lower):
                    score += 2
                    matched = True
            
            # Check keywords
            for keyword in intent_data.get("keywords", []):
                if keyword in text_lower:
                    score += 1
            
            if matched:
                scores[intent_name] = score
        
        if not scores:
            return self.fallback_intent
        
        # Return highest scoring intent
        return max(scores, key=scores.get)
    
    def classify_with_confidence(self, text: str) -> Intent:
        """Classify with confidence score"""
        text_lower = text.lower()
        
        scores = {}
        entities = {}
        
        for intent_name, intent_data in self.intents.items():
            score = 0
            
            # Check patterns
            for pattern in intent_data.get("patterns", []):
                match = re.search(pattern, text_lower)
                if match:
                    score += 2
                    entities[intent_name] = match.group(0)
            
            # Check keywords
            keyword_count = 0
            for keyword in intent_data.get("keywords", []):
                if keyword in text_lower:
                    score += 1
                    keyword_count += 1
            entities[f"{intent_name}_keywords"] = keyword_count
            
            if score > 0:
                scores[intent_name] = score
        
        if not scores:
            return Intent(
                name=self.fallback_intent,
                confidence=0.5,
                entities={},
                original=text
            )
        
        # Calculate confidence
        max_score = max(scores.values())
        confidence = min(max_score / 6, 1.0)  # Normalize to 0-1
        
        top_intent = max(scores, key=scores.get)
        
        return Intent(
            name=top_intent,
            confidence=confidence,
            entities=entities,
            original=text
        )
    
    def get_response(self, intent: str) -> str:
        """Get response template for intent"""
        if intent in self.intents:
            responses = self.intents[intent].get("responses", [])
            if responses:
                return responses[0]
        return ""