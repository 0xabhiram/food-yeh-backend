from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./foodyeh.db"
    
    # JWT - Updated to match .env field names
    jwt_secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS512"
    access_token_expire_days: int = 200
    
    # MQTT Settings - Updated for cloud deployment
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_keepalive: int = 60  # 1 minute keepalive to match Mosquitto
    refresh_token_expire_days: int = 700
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # MQTT Broker Configuration
    # For cloud deployment, you need to set these in .env file
    # or use a cloud MQTT service like HiveMQ, AWS IoT, etc.
    mqtt_broker_url: str = "localhost"  # Change to your MQTT broker IP
    mqtt_broker_port: int = 1883
    mqtt_username: str = ""  # Empty for anonymous access
    mqtt_password: str = ""  # Empty for anonymous access
    mqtt_client_id: str = "foodyeh_backend"
    
    # Security - Handle CORS_ORIGINS as comma-separated string
    cors_origins: str = "*"  # Allow all origins for development
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
    
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file

    # Property to maintain backward compatibility
    @property
    def jwt_secret(self) -> str:
        return self.jwt_secret_key
    
    @property
    def jwt_algorithm(self) -> str:
        return self.algorithm
    
    @property
    def access_token_expire_minutes(self) -> int:
        return self.access_token_expire_days * 24 * 60  # Convert days to minutes
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins string to list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
