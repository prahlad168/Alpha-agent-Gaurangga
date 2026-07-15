"""
MAHALAKSMI AIOS v1.0 - Volume II: Intelligence Gateway
Dynamic Multi-Model AI Gateway with query routing, context tracking, and fallbacks
PRODUCTION: Real Google GenAI SDK Integration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import deque
import httpx

# Import settings
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import settings

logger = logging.getLogger(__name__)

# Try to import Google GenAI SDK for production use
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
    logger.info("Google GenAI SDK loaded - Production mode enabled")
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenAI SDK not available - Using HTTP fallback")


class AIProvider(Enum):
    """Supported AI providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class AIResponse:
    """Standardized AI response."""
    content: str
    provider: AIProvider
    model: str
    tokens_used: int = 0
    latency_ms: float = 0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Conversation context for tracking."""
    conversation_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    max_tokens: int = 8000
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation."""
        self.messages.append({"role": role, "content": content})
        self.last_updated = datetime.now()
        
        # Trim if exceeds max tokens (rough estimate: 4 chars per token)
        estimated_tokens = len(" ".join(m["content"] for m in self.messages)) // 4
        if estimated_tokens > self.max_tokens:
            # Keep last half of messages
            half = len(self.messages) // 2
            self.messages = self.messages[half:]
    
    def get_context_window(self, max_messages: int = 20) -> List[Dict[str, str]]:
        """Get recent messages within limit."""
        return self.messages[-max_messages:]


class IntelligenceGateway:
    """
    Multi-Model AI Gateway.
    Handles query routing, context tracking, and automatic fallbacks.
    PRODUCTION: Uses Google GenAI SDK for Gemini, with HTTP fallback for others.
    """
    
    def __init__(self):
        # Configure providers
        self.provider_configs: Dict[AIProvider, Dict[str, Any]] = {
            AIProvider.GEMINI: {
                "name": "Google Gemini",
                "model": "gemini-1.5-flash",
                "max_tokens": 8192,
                "enabled": bool(settings.gemini_api_key),
                "api_key": settings.gemini_api_key,
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
                "use_sdk": GENAI_AVAILABLE and bool(settings.gemini_api_key)
            },
            AIProvider.OPENAI: {
                "name": "OpenAI ChatGPT",
                "model": "gpt-3.5-turbo",
                "max_tokens": 4096,
                "enabled": bool(settings.openai_api_key),
                "api_key": settings.openai_api_key,
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "use_sdk": False
            },
            AIProvider.ANTHROPIC: {
                "name": "Anthropic Claude",
                "model": "claude-3-haiku-20240307",
                "max_tokens": 4096,
                "enabled": bool(settings.anthropic_api_key),
                "api_key": settings.anthropic_api_key,
                "endpoint": "https://api.anthropic.com/v1/messages",
                "use_sdk": False
            }
        }
        
        # Initialize GenAI SDK if available
        if GENAI_AVAILABLE and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.genai_model = genai.GenerativeModel(self.provider_configs[AIProvider.GEMINI]["model"])
                logger.info(f"GenAI SDK initialized with model: {self.provider_configs[AIProvider.GEMINI]['model']}")
            except Exception as e:
                logger.error(f"Failed to initialize GenAI SDK: {e}")
                self.genai_model = None
        else:
            self.genai_model = None
        
        self.conversations: Dict[str, ConversationContext] = {}
        self.primary_provider = self._get_primary_provider()
        self.fallback_chain: List[AIProvider] = self._build_fallback_chain()
        
        logger.info(f"Intelligence Gateway initialized with primary: {self.primary_provider}")
        logger.info(f"GenAI SDK Available: {GENAI_AVAILABLE}, Model Loaded: {self.genai_model is not None}")
    
    def _get_primary_provider(self) -> AIProvider:
        """Get primary AI provider based on settings."""
        provider_name = settings.primary_ai_provider.lower()
        for provider in AIProvider:
            if provider.value == provider_name:
                config = self.provider_configs[provider]
                if config["enabled"]:
                    return provider
        return AIProvider.GEMINI
    
    def _build_fallback_chain(self) -> List[AIProvider]:
        """Build fallback chain of providers."""
        chain = [self.primary_provider]
        for provider in AIProvider:
            if provider != self.primary_provider and self.provider_configs[provider]["enabled"]:
                chain.append(provider)
        return chain
    
    def create_conversation(self, conversation_id: Optional[str] = None) -> str:
        """Create new conversation context."""
        if conversation_id is None:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.conversations[conversation_id] = ConversationContext(
            conversation_id=conversation_id
        )
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get conversation by ID."""
        return self.conversations.get(conversation_id)
    
    async def generate(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate AI response with automatic fallback.
        """
        start_time = asyncio.get_event_loop().time()
        
        # Get or create conversation
        if conversation_id:
            conv = self.get_conversation(conversation_id)
            if not conv:
                conversation_id = self.create_conversation(conversation_id)
                conv = self.conversations[conversation_id]
        else:
            conversation_id = self.create_conversation()
            conv = self.conversations[conversation_id]
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(conv.get_context_window())
        messages.append({"role": "user", "content": prompt})
        
        # Try each provider in fallback chain
        last_error = None
        for provider in self.fallback_chain:
            try:
                response = await self._call_provider(
                    provider,
                    messages,
                    temperature,
                    max_tokens
                )
                
                if response.success:
                    # Add to conversation
                    conv.add_message("user", prompt)
                    conv.add_message("assistant", response.content)
                    
                    return response
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Provider {provider.value} failed: {e}")
                continue
        
        # All providers failed
        return AIResponse(
            content="Maaf, terjadi kesalahan pada semua AI services. Silakan coba lagi nanti.",
            provider=self.primary_provider,
            model="none",
            success=False,
            error=last_error or "All providers failed",
            latency_ms=(asyncio.get_event_loop().time() - start_time) * 1000
        )
    
    async def _call_provider(
        self,
        provider: AIProvider,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> AIResponse:
        """Call specific AI provider."""
        config = self.provider_configs[provider]
        start_time = asyncio.get_event_loop().time()
        
        if provider == AIProvider.GEMINI:
            return await self._call_gemini(config, messages, temperature, max_tokens, start_time)
        elif provider == AIProvider.OPENAI:
            return await self._call_openai(config, messages, temperature, max_tokens, start_time)
        elif provider == AIProvider.ANTHROPIC:
            return await self._call_anthropic(config, messages, temperature, max_tokens, start_time)
        
        raise ValueError(f"Unknown provider: {provider}")
    
    async def _call_gemini(
        self,
        config: Dict,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        start_time: float
    ) -> AIResponse:
        """Call Google Gemini API using SDK or HTTP fallback."""
        
        # Try SDK first if available
        if config.get("use_sdk") and self.genai_model:
            return await self._call_gemini_sdk(config, messages, temperature, max_tokens, start_time)
        
        # Fallback to HTTP
        return await self._call_gemini_http(config, messages, temperature, max_tokens, start_time)
    
    async def _call_gemini_sdk(
        self,
        config: Dict,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        start_time: float
    ) -> AIResponse:
        """Call Google Gemini API using official GenAI SDK."""
        try:
            # Build prompt from messages
            system_prompt = ""
            user_prompt = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                elif msg["role"] == "user":
                    user_prompt = msg["content"]
            
            # Build full prompt
            full_prompt = user_prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate response using SDK
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens or config["max_tokens"],
            }
            
            response = self.genai_model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            content = response.text
            
            # Estimate token count (rough: ~4 chars per token)
            tokens_used = len(content) // 4
            
            logger.info(f"GenAI SDK call successful - {len(content)} chars, ~{tokens_used} tokens")
            
            return AIResponse(
                content=content,
                provider=AIProvider.GEMINI,
                model=config["model"],
                tokens_used=tokens_used,
                latency_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                success=True
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"GenAI SDK error: {error_msg}")
            
            # Check for quota limit - fallback to HTTP
            if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                logger.warning("Gemini quota exceeded - falling back to HTTP")
                return await self._call_gemini_http(config, messages, temperature, max_tokens, start_time)
            
            raise ValueError(f"Gemini SDK error: {error_msg}")
    
    async def _call_gemini_http(
        self,
        config: Dict,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        start_time: float
    ) -> AIResponse:
        """Call Google Gemini API via HTTP (fallback)."""
        if not config["api_key"]:
            raise ValueError("Gemini API key not configured")
        
        # Build contents from messages
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                continue  # Gemini handles system differently
            contents.append({
                "role": "model" if msg["role"] == "assistant" else "user",
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens or config["max_tokens"],
            }
        }
        
        async with httpx.AsyncClient() as client:
            url = f"{config['endpoint']}/{config['model']}:generateContent?key={config['api_key']}"
            response = await client.post(url, json=payload, timeout=30.0)
            
            if response.status_code != 200:
                raise ValueError(f"Gemini API error: {response.status_code}")
            
            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            
            return AIResponse(
                content=content,
                provider=AIProvider.GEMINI,
                model=config["model"],
                tokens_used=data.get("usageMetadata", {}).get("totalTokenCount", 0),
                latency_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                success=True
            )
    
    async def _call_openai(
        self,
        config: Dict,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        start_time: float
    ) -> AIResponse:
        """Call OpenAI API."""
        if not config["api_key"]:
            raise ValueError("OpenAI API key not configured")
        
        payload = {
            "model": config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or config["max_tokens"],
        }
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["endpoint"],
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"OpenAI API error: {response.status_code}")
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            return AIResponse(
                content=content,
                provider=AIProvider.OPENAI,
                model=config["model"],
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                latency_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                success=True
            )
    
    async def _call_anthropic(
        self,
        config: Dict,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        start_time: float
    ) -> AIResponse:
        """Call Anthropic Claude API."""
        if not config["api_key"]:
            raise ValueError("Anthropic API key not configured")
        
        # Convert messages format for Claude
        system_msg = ""
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                claude_messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
        
        payload = {
            "model": config["model"],
            "messages": claude_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or config["max_tokens"],
        }
        if system_msg:
            payload["system"] = system_msg
        
        headers = {
            "x-api-key": config["api_key"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["endpoint"],
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"Anthropic API error: {response.status_code}")
            
            data = response.json()
            content = data["content"][0]["text"]
            
            return AIResponse(
                content=content,
                provider=AIProvider.ANTHROPIC,
                model=config["model"],
                tokens_used=data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0),
                latency_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                success=True
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get gateway status."""
        return {
            "primary_provider": self.primary_provider.value,
            "genai_sdk_available": GENAI_AVAILABLE,
            "genai_model_loaded": self.genai_model is not None,
            "providers": {
                provider.value: {
                    "name": config["name"],
                    "model": config["model"],
                    "enabled": config["enabled"],
                    "use_sdk": config.get("use_sdk", False)
                }
                for provider, config in self.provider_configs.items()
            },
            "active_conversations": len(self.conversations)
        }


# Global gateway instance
_gateway: Optional[IntelligenceGateway] = None


def get_gateway() -> IntelligenceGateway:
    """Get or create global gateway instance."""
    global _gateway
    if _gateway is None:
        _gateway = IntelligenceGateway()
    return _gateway
