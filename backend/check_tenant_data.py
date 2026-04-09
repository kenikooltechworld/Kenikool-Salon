"""Check what's actually in the tenant data."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from app.config import get_settings

def check_data():
    """Check tenant data."""
    print("=" * 60)
    print("CHECKING TENANT DATA")
    print("=" * 60)
    
    init_db()
    
    config = get_settings()
    print(f"\nPlatform Domain: {config.platform_domain}")
    
    tenants = Tenant.objects(deletion_status="active")
    print(f"\nFound {tenants.count()} active tenants\n")
    
    for tenant in tenants:
        print(f"\n{'=' * 60}")
        print(f"Tenant: {tenant.name}")
        print(f"ID: {tenant.id}")
        print(f"Subdomain: {tenant.subdomain}")
        print(f"Address: {tenant.address}")
        
        settings = tenant.settings or {}
        print(f"\nSettings:")
        print(f"  email: '{settings.get('email', '')}'")
        print(f"  phone: '{settings.get('phone', '')}'")
        print(f"  owner_email: '{settings.get('owner_email', '')}'")
        print(f"  owner_phone: '{settings.get('owner_phone', '')}'")
        
        # Construct subdomain URL
        subdomain_url = f"https://{tenant.subdomain}.{config.platform_domain}" if tenant.subdomain else ""
        print(f"\nConstructed subdomain_url: {subdomain_url}")

if __name__ == "__main__":
    check_data()
