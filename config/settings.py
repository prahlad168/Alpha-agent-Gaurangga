"""
MAHALAKSMI AIOS v1.0 - Configuration Settings
Enterprise-grade settings management with Pydantic BaseSettings
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Main application settings loaded from environment variables."""
    
    # Application Identity
    app_name: str = "MAHALAKSMI AIOS"
    app_version: str = "1.0.0"
    app_description: str = "Enterprise AI Operating System"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Security Keys (REQUIRED for production)
    secret_key: str = "change-me-in-production-use-strong-random-key"
    jwt_secret: str = "jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # AI/ML Configuration
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Primary AI Provider
    primary_ai_provider: str = "gemini"  # openai, gemini, anthropic
    
    # Revenue & Finance Endpoints
    flip_api_key: Optional[str] = None
    midtrans_server_key: Optional[str] = None
    payment_webhook_secret: Optional[str] = None
    
    # CEO Bank Details
    ceo_bank_code: str = "014"  # BCA
    ceo_account_number: str = "6485086645"
    ceo_account_holder: str = "I Made Purna Ananda"
    
    # Bitcoin Wallet (Alternative)
    bitcoin_wallet_address: str = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    bitcoin_enabled: bool = False
    
    # Database (Placeholder for future)
    database_url: Optional[str] = None
    
    # Redis (Placeholder for future)
    redis_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Revenue Allocation
    ceo_share_percentage: float = 60.0
    operational_reserve_percentage: float = 40.0
    
    # RBAC Roles
    admin_role: str = "executive"
    developer_role: str = "developer"
    operations_role: str = "operations"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
