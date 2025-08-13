from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./foodyeh.db"
    
    # JWT
    jwt_secret: str = "your-super-secret-jwt-key-change-this-in-production"
    jwt_algorithm: str = "HS512"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # MQTT
    mqtt_broker_url: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: str = "admin"
    mqtt_password: str = "admin123"
    mqtt_client_id: str = "foodyeh_backend"
    
    # Security
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    rate_limit_auth: int = 5
    rate_limit_window: int = 60
    account_lockout_attempts: int = 5
    account_lockout_duration: int = 600
    
    # File Upload
    upload_dir: str = "./uploads"
    max_file_size: int = 5242880  # 5MB
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
