"""Test script to verify settings endpoint returns tenant_name."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.tenant_settings_service import TenantSettingsService
from app.models.tenant import Tenant
from app.db import init_db

def test_settings_response():
    """Test that settings response includes tenant_name."""
    # Connect to database
    init_db()
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenants found in database")
        return
    
    print(f"Testing with tenant: {tenant.name} (ID: {tenant.id})")
    
    # Get settings
    settings = TenantSettingsService.get_settings(str(tenant.id))
    
    if not settings:
        print("Failed to get settings")
        return
    
    # Check if tenant_name is in response
    if "tenant_name" in settings:
        print(f"✓ tenant_name found in response: {settings['tenant_name']}")
    else:
        print("✗ tenant_name NOT found in response")
    
    # Print all keys
    print("\nAll keys in response:")
    for key in sorted(settings.keys()):
        if key not in ['business_hours', 'system_config', 'integration_config', 'financial_config', 'operational_config']:
            print(f"  - {key}: {settings[key]}")

if __name__ == "__main__":
    test_settings_response()
