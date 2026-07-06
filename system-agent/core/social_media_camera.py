"""
GAURANGA Social Media & Camera Integration
Akses Twitter, Kamera, dan Auto-Skill Learning
"""

import os
import sys
import json
import base64
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

class SocialMediaManager:
    """
    Manager untuk Social Media - Twitter/X, Instagram, dll
    Auto-save skills dan insights dari social media
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.owner = self.config.get("agent.owner", "Pak Pur")
        self.logger = logging.getLogger("GAURANGA.Social")
        
        # Storage
        self.data_path = "./data/social_media"
        os.makedirs(self.data_path, exist_ok=True)
        
        # Twitter API credentials (from config)
        self.twitter_api_key = self.config.get("twitter.api_key", "")
        self.twitter_api_secret = self.config.get("twitter.api_secret", "")
        self.twitter_access_token = self.config.get("twitter.access_token", "")
        self.twitter_access_secret = self.config.get("twitter.access_secret", "")
        
        # State
        self.is_connected = False
        self.followers = []
        self.tweets = []
        
        # Auto-save skills from social
        self.learned_from_social = []
        
        self._load_data()
    
    # ══════════════════════════════════════════════════════════════
    # TWITTER/X API
    # ══════════════════════════════════════════════════════════════
    
    def connect_twitter(self, credentials: Dict) -> Dict:
        """Connect to Twitter/X API"""
        self.twitter_api_key = credentials.get("api_key", "")
        self.twitter_api_secret = credentials.get("api_secret", "")
        self.twitter_access_token = credentials.get("access_token", "")
        self.twitter_access_secret = credentials.get("access_secret", "")
        
        if all([self.twitter_api_key, self.twitter_api_secret]):
            self.is_connected = True
            self.logger.info("✅ Twitter connected")
            return {"success": True, "message": "Twitter connected"}
        
        return {"success": False, "message": "Credentials incomplete"}
    
    def get_timeline(self, count: int = 20) -> List[Dict]:
        """Get Twitter timeline"""
        if not self.is_connected:
            return []
        
        # In real implementation, use tweepy or Twitter API v2
        # For demo, return mock data
        return [
            {
                "id": "123456",
                "user": "example_user",
                "text": "Tweet example",
                "created_at": datetime.now().isoformat(),
                "likes": 0,
                "retweets": 0
            }
        ]
    
    def post_tweet(self, content: str, media: List[str] = None) -> Dict:
        """Post tweet"""
        if not self.is_connected:
            return {"success": False, "message": "Twitter not connected"}
        
        # Learn from this post
        self._learn_from_content(content, "twitter")
        
        return {
            "success": True,
            "message": "Tweet posted",
            "tweet_id": f"tweet_{int(time.time())}"
        }
    
    def search_tweets(self, query: str, count: int = 10) -> List[Dict]:
        """Search tweets"""
        if not self.is_connected:
            return []
        
        # Learn from search results
        results = self._mock_search(query, count)
        
        for tweet in results:
            self._learn_from_content(tweet.get("text", ""), "twitter_search")
        
        return results
    
    def _mock_search(self, query: str, count: int) -> List[Dict]:
        """Mock search results"""
        return [
            {
                "id": f"search_{i}",
                "user": f"user_{i}",
                "text": f"Result for '{query}' - {i}",
                "created_at": datetime.now().isoformat()
            }
            for i in range(count)
        ]
    
    def get_trending(self, location: str = "INDONESIA") -> List[Dict]:
        """Get trending topics"""
        return [
            {"topic": "#AI", "tweet_volume": 50000},
            {"topic": "#Tech", "tweet_volume": 30000},
            {"topic": "#Business", "tweet_volume": 20000}
        ]
    
    # ══════════════════════════════════════════════════════════════
    # CAMERA INTEGRATION
    # ══════════════════════════════════════════════════════════════
    
    def capture_photo(self, camera_id: int = 0) -> Dict:
        """
        Ambil foto dari kamera
        In real implementation, use Android Camera2 API or Termux API
        """
        # For demo, return mock
        return {
            "success": True,
            "path": f"{self.data_path}/photo_{int(time.time())}.jpg",
            "timestamp": datetime.now().isoformat(),
            "camera": camera_id
        }
    
    def record_video(self, duration: int = 10) -> Dict:
        """Rekam video"""
        return {
            "success": True,
            "path": f"{self.data_path}/video_{int(time.time())}.mp4",
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
    
    def scan_qr_code(self) -> Dict:
        """Scan QR code from camera"""
        return {
            "success": True,
            "data": "https://example.com",
            "timestamp": datetime.now().isoformat()
        }
    
    def capture_for_analysis(self, purpose: str = "general") -> Dict:
        """Capture and analyze image"""
        photo = self.capture_photo()
        
        # Analyze image
        analysis = self._analyze_image(photo["path"], purpose)
        
        # Learn from analysis
        if purpose == "document":
            self._learn_from_content(analysis.get("text", ""), "document_scan")
        elif purpose == "product":
            self._learn_from_content(analysis.get("description", ""), "product")
        
        return {
            **photo,
            "analysis": analysis
        }
    
    def _analyze_image(self, image_path: str, purpose: str) -> Dict:
        """Analyze image using AI"""
        # In real implementation, use Google Vision, AWS Rekognition, or local ML
        return {
            "success": True,
            "purpose": purpose,
            "labels": ["object", "scene"],
            "text": "Sample extracted text",
            "confidence": 0.95
        }
    
    # ══════════════════════════════════════════════════════════════
    # AUTO-LEARN SKILLS FROM CONTENT
    # ══════════════════════════════════════════════════════════════
    
    def _learn_from_content(self, content: str, source: str):
        """Learn skills/patterns from social media content"""
        if not content:
            return
        
        # Extract keywords and patterns
        keywords = self._extract_keywords(content)
        
        for kw in keywords:
            skill = {
                "keyword": kw,
                "source": source,
                "context": content[:200],
                "learned_at": datetime.now().isoformat(),
                "usage": 0
            }
            
            if skill not in self.learned_from_social:
                self.learned_from_social.append(skill)
                self.logger.info(f"📝 Learned from {source}: {kw}")
        
        self._save_data()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Common business keywords
        keywords = []
        
        business_terms = [
            "marketing", "sales", "revenue", "growth", "strategy",
            "product", "customer", "brand", "digital", "online",
            "content", "engagement", "conversion", "roi", "leads",
            "business", "startup", "investment", "profit", "market"
        ]
        
        text_lower = text.lower()
        for term in business_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords
    
    # ══════════════════════════════════════════════════════════════
    # INSTAGRAM
    # ══════════════════════════════════════════════════════════════
    
    def get_instagram_feed(self) -> List[Dict]:
        """Get Instagram feed"""
        # Using unofficial API or Graph API
        return [
            {
                "id": "123",
                "caption": "Post caption",
                "likes": 100,
                "comments": 10,
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def post_instagram(self, image_path: str, caption: str) -> Dict:
        """Post to Instagram"""
        self._learn_from_content(caption, "instagram")
        
        return {
            "success": True,
            "post_id": f"ig_{int(time.time())}"
        }
    
    # ══════════════════════════════════════════════════════════════
    # DATA PERSISTENCE
    # ══════════════════════════════════════════════════════════════
    
    def _save_data(self):
        """Save learned data"""
        data = {
            "learned": self.learned_from_social[-100:],  # Keep last 100
            "saved_at": datetime.now().isoformat()
        }
        
        filepath = os.path.join(self.data_path, "social_skills.json")
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_data(self):
        """Load saved data"""
        filepath = os.path.join(self.data_path, "social_skills.json")
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.learned_from_social = data.get("learned", [])
    
    def get_learned_skills(self) -> List[Dict]:
        """Get all learned skills from social media"""
        return self.learned_from_social
    
    def get_status(self) -> Dict:
        """Get connection status"""
        return {
            "twitter_connected": self.is_connected,
            "learned_skills": len(self.learned_from_social),
            "sources": list(set(s.get("source") for s in self.learned_from_social))
        }


# ══════════════════════════════════════════════════════════════
# CAMERA SERVICE (Standalone)
# ══════════════════════════════════════════════════════════════

class CameraService:
    """
    Camera Service untuk Alpha Gaurangga
    Akses kamera HP untuk foto, video, QR scan
    """
    
    def __init__(self):
        self.data_path = "./data/camera"
        os.makedirs(self.data_path, exist_ok=True)
        self.logger = logging.getLogger("GAURANGA.Camera")
    
    def take_photo(self) -> Dict:
        """Ambil foto"""
        filename = f"IMG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(self.data_path, filename)
        
        # In real implementation, use Android Camera2 API
        # For demo, create placeholder
        with open(filepath, 'w') as f:
            f.write("PLACEHOLDER")
        
        return {
            "success": True,
            "filename": filename,
            "path": filepath,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_video(self, seconds: int = 30) -> Dict:
        """Rekam video"""
        filename = f"VID_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        filepath = os.path.join(self.data_path, filename)
        
        return {
            "success": True,
            "filename": filename,
            "path": filepath,
            "duration": seconds,
            "timestamp": datetime.now().isoformat()
        }
    
    def scan_qr(self) -> Dict:
        """Scan QR code"""
        return {
            "success": True,
            "data": "QR content placeholder",
            "timestamp": datetime.now().isoformat()
        }
    
    def capture_document(self) -> Dict:
        """Capture document (untuk OCR)"""
        photo = self.take_photo()
        
        return {
            **photo,
            "type": "document",
            "ocr_text": "Extracted text from document"
        }


# ══════════════════════════════════════════════════════════════
# VOICE COMMAND INTERFACE
# ══════════════════════════════════════════════════════════════

class VoiceCommandProcessor:
    """
    Process voice commands untuk social media & camera
    """
    
    COMMANDS = {
        "foto": "take_photo",
        "photo": "take_photo",
        "kamera": "take_photo",
        "gambar": "take_photo",
        "video": "record_video",
        "rekam": "record_video",
        "qr": "scan_qr",
        "scan": "scan_qr",
        "twitter": "twitter",
        "tweet": "post_tweet",
        "posting": "post_tweet",
        "cari": "search",
        "search": "search",
        "trending": "get_trending"
    }
    
    def __init__(self, social: SocialMediaManager, camera: CameraService):
        self.social = social
        self.camera = camera
    
    def process(self, command: str) -> Dict:
        """Process voice command"""
        command_lower = command.lower()
        
        # Find matching command
        for keyword, action in self.COMMANDS.items():
            if keyword in command_lower:
                return self._execute(action, command)
        
        return {
            "success": False,
            "message": f"Command not recognized: {command}"
        }
    
    def _execute(self, action: str, full_command: str) -> Dict:
        """Execute action"""
        if action == "take_photo":
            return self.camera.take_photo()
        elif action == "record_video":
            return self.camera.record_video()
        elif action == "scan_qr":
            return self.camera.scan_qr()
        elif action == "post_tweet":
            # Extract tweet content
            content = full_command.replace("tweet", "").replace("posting", "").strip()
            return self.social.post_tweet(content)
        elif action == "search":
            # Extract search query
            query = full_command.replace("cari", "").replace("search", "").strip()
            return {"results": self.social.search_tweets(query)}
        elif action == "get_trending":
            return {"trending": self.social.get_trending()}
        
        return {"success": False, "message": "Action not found"}


# Global instances
_social_manager = None
_camera_service = None
_voice_processor = None

def get_social_manager(config: Dict = None) -> SocialMediaManager:
    global _social_manager
    if _social_manager is None:
        _social_manager = SocialMediaManager(config)
    return _social_manager

def get_camera_service() -> CameraService:
    global _camera_service
    if _camera_service is None:
        _camera_service = CameraService()
    return _camera_service

def get_voice_processor() -> VoiceCommandProcessor:
    global _voice_processor
    if _voice_processor is None:
        _voice_processor = VoiceCommandProcessor(
            get_social_manager(),
            get_camera_service()
        )
    return _voice_processor
