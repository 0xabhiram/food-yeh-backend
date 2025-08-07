"""
Configuration settings for the Foodyeh FastAPI backend.
Uses Pydantic settings for type safety and validation.
"""

import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Foodyeh API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "your_super_secret_key_here_make_it_long_and_random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    enforce_https: bool = True
    
    # CORS
    allowed_origins: List[str] = ["https://tablet.foodyeh.io"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # MQTT Configuration
    mqtt_broker: str = "mqtt.foodyeh.io"
    mqtt_port: int = 8883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_client_id: str = "foodyeh_api"
    mqtt_keepalive: int = 60
    
    # Database
    database_url: str = "sqlite:///./foodyeh.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Admin IP Whitelist
    admin_whitelist_ips: List[str] = []
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Health Check
    health_check_timeout: int = 5
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator("allowed_origins")
    def validate_allowed_origins(cls, v):
        if not v:
            raise ValueError("At least one allowed origin must be specified")
        return v
    
    @validator("admin_whitelist_ips")
    def validate_admin_ips(cls, v):
        # Allow empty list for development, but warn
        return v
    
    class Config:
        env_file = "/etc/foodyeh.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.log_level = "DEBUG"
    settings.allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    settings.admin_whitelist_ips = ["127.0.0.1", "::1"] 