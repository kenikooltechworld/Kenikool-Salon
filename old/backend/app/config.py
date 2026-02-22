"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os

# Get the backend directory (parent of app directory)
BACKEND_DIR = Path(__file__).parent.parent
ENV_FILE = BACKEND_DIR / ".env"

# Load .env file explicitly if it exists
if ENV_FILE.exists():
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Kenikool Salon Management SaaS"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production-12345678"
    API_VERSION: str = "v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "salon_saas_dev"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT
    JWT_SECRET_KEY: str = "dev-jwt-secret-key-change-in-production-87654321"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Cloudinary (Optional for development)
    CLOUDINARY_CLOUD_NAME: str = "demo"
    CLOUDINARY_API_KEY: str = "123456789012345"
    CLOUDINARY_API_SECRET: str = "demo_secret"
    
    # Termii (SMS & WhatsApp)
    TERMII_API_KEY: str = "demo_termii_api_key"
    TERMII_SENDER_ID: str = "Kenikool"
    TERMII_API_URL: str = "https://api.ng.termii.com/api"
    
    # Paystack (Optional for development)
    PAYSTACK_SECRET_KEY: str = "sk_test_demo_key"
    PAYSTACK_PUBLIC_KEY: str = "pk_test_demo_key"
    PAYSTACK_WEBHOOK_SECRET: str = "demo_webhook_secret"
    
    # Flutterwave (Optional for development)
    FLUTTERWAVE_PUBLIC_KEY_TEST: str = "FLWPUBK_TEST-demo"
    FLUTTERWAVE_SECRET_KEY_TEST: str = "FLWSECK_TEST-demo"
    FLUTTERWAVE_ENCRYPTION_KEY_TEST: str = "FLWSECK_TESTdemo"
    FLUTTERWAVE_SECRET_HASH: str = "demo_webhook_secret"
    
    # MinIO (File Storage)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "salon-saas"
    MINIO_SECURE: bool = False
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Email (Resend)
    RESEND_API_KEY: str = "demo_resend_key"
    EMAIL_FROM: str = "Kenikool Salon <noreply@kenikool.com>"
    
    # OpenStreetMap / Nominatim (Geocoding)
    NOMINATIM_API_URL: str = "https://nominatim.openstreetmap.org"
    NOMINATIM_TIMEOUT: int = 10
    NOMINATIM_CACHE_TTL_DAYS: int = 30
    
    # Mapbox (Geocoding, Maps, Distance Matrix)
    MAPBOX_PUBLIC_KEY: str = ""
    MAPBOX_SECRET_KEY: str = ""
    MAPBOX_API_URL: str = "https://api.mapbox.com"
    MAPBOX_TIMEOUT: int = 10
    MAPBOX_GEOCODING_CACHE_TTL_DAYS: int = 30
    MAPBOX_AUTOCOMPLETE_CACHE_TTL_HOURS: int = 1
    MAPBOX_DISTANCE_CACHE_TTL_HOURS: int = 24
    
    # Testing
    TESTING: bool = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override with environment variable if set
        if os.getenv("TESTING", "").lower() in ("true", "1", "yes"):
            self.TESTING = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()
