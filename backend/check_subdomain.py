"""Check what's stored in the subdomain field."""
import os
from dotenv import load_dotenv
from mongoengine import connect
from app.models.tenant import Tenant

# Load environment variables
load_dotenv()

# Connect to MongoDB
DATABASE_URL = os.getenv("DATABASE_URL")
connect(host=DATABASE_URL)

# Find the tenant
tenant = Tenant.objects(name__icontains="kenikool").first()

if tenant:
    print(f"Tenant Name: {tenant.name}")
    print(f"Subdomain stored in DB: '{tenant.subdomain}'")
    print(f"Subdomain length: {len(tenant.subdomain)}")
    print(f"Contains 'localhost': {'localhost' in tenant.subdomain}")
    print(f"Contains ':3000': {':3000' in tenant.subdomain}")
else:
    print("Tenant not found")
