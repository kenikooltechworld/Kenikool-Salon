"""Check config values."""
import os
from dotenv import load_dotenv
from app.config import get_settings

# Load environment variables
load_dotenv()

# Get settings
config = get_settings()

print(f"ENVIRONMENT from .env: {os.getenv('ENVIRONMENT')}")
print(f"PLATFORM_DOMAIN from .env: {os.getenv('PLATFORM_DOMAIN')}")
print(f"")
print(f"config.environment: {config.environment}")
print(f"config.platform_domain: {config.platform_domain}")
