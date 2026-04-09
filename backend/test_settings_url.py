"""Test settings URL generation."""
import os
from dotenv import load_dotenv
from mongoengine import connect
from app.models.tenant import Tenant
from app.services.tenant_settings_service import TenantSettingsService

# Load environment variables
load_dotenv()

# Connect to MongoDB
DATABASE_URL = os.getenv("DATABASE_URL")
connect(host=DATABASE_URL)

# Find the tenant
tenant = Tenant.objects(name__icontains="kenikool").first()

if tenant:
    print(f"Tenant Name: {tenant.name}")
    print(f"Tenant ID: {tenant.id}")
    print(f"Subdomain in DB: '{tenant.subdomain}'")
    print("")
    
    # Get settings using the service
    settings = TenantSettingsService.get_settings(str(tenant.id))
    
    if settings:
        print(f"subdomain_url from service: '{settings['subdomain_url']}'")
    else:
        print("Failed to get settings")
else:
    print("Tenant not found")
