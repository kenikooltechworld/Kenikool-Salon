"""Application configuration management."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "development"
    debug: bool = True

    # API
    api_title: str = "Salon/Spa/Gym SaaS Platform"
    api_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = ""
    database_name: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_session_db: int = 0
    redis_cache_db: int = 1
    redis_lock_db: int = 2

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours
    jwt_refresh_token_expire_days: int = 30

    # CORS - keep as strings in model, parse in validators
    cors_origins_str: str = "http://localhost:3000,http://localhost:8000"
    cors_credentials: bool = True
    cors_methods_str: str = "*"
    cors_headers_str: str = "*"

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # Logging
    log_level: str = "INFO"

    # Optional fields from .env
    app_name: str = "Kenikool Salon"
    secret_key: str = "dev-secret-key"
    platform_domain: str = "localhost:3000"
    termii_api_key: str = ""
    termii_secret_key: str = ""
    termii_sender_id: str = ""
    termii_device_id: str = ""
    termii_api_url: str = ""
    paystack_live_secret_key: str = ""
    paystack_live_public_key: str = ""
    paystack_webhook_secret: str = ""
    resend_api_key: str = ""
    email_from: str = ""
    
    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        json_schema_extra={"env_ignore_empty": True}
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]

    @property
    def cors_methods(self) -> List[str]:
        """Parse CORS methods from comma-separated string or wildcard."""
        if self.cors_methods_str.strip() == "*":
            return ["*"]
        return [method.strip() for method in self.cors_methods_str.split(",") if method.strip()]

    @property
    def cors_headers(self) -> List[str]:
        """Parse CORS headers from comma-separated string or wildcard."""
        if self.cors_headers_str.strip() == "*":
            return ["*"]
        return [header.strip() for header in self.cors_headers_str.split(",") if header.strip()]


def get_settings() -> Settings:
    """Get application settings - returns singleton instance."""
    return settings


# Create singleton instance at module load time
settings = Settings()
