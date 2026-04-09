#!/usr/bin/env python
"""Check if registration data exists for the user."""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.db import init_db
from app.models.temp_registration import TempRegistration
from app.models.tenant import Tenant
from app.models.user import User

init_db()

email = "kenikoolsalon@gmail.com"

print("=" * 60)
print(f"CHECKING REGISTRATION DATA FOR: {email}")
print("=" * 60)

# Check temp registration
print("\n[1] Checking temp_registrations collection...")
temp_reg = TempRegistration.objects(email=email).first()
if temp_reg:
    print(f"✓ Found temp registration:")
    print(f"  - Email: {temp_reg.email}")
    print(f"  - Salon Name: {temp_reg.salon_name}")
    print(f"  - Subdomain: {temp_reg.subdomain}")
    print(f"  - Status: Pending verification")
else:
    print(f"✗ No temp registration found")

# Check tenants
print("\n[2] Checking tenants collection...")
tenants = Tenant.objects(name__icontains="kenikool")
if tenants:
    for tenant in tenants:
        print(f"✓ Found tenant:")
        print(f"  - ID: {tenant.id}")
        print(f"  - Name: {tenant.name}")
        print(f"  - Subdomain: {tenant.subdomain}")
        print(f"  - Status: {tenant.status}")
else:
    print(f"✗ No tenants found")

# Check users
print("\n[3] Checking users collection...")
user = User.objects(email=email).first()
if user:
    print(f"✓ Found user:")
    print(f"  - ID: {user.id}")
    print(f"  - Email: {user.email}")
    print(f"  - Name: {user.first_name} {user.last_name}")
    print(f"  - Status: {user.status}")
else:
    print(f"✗ No user found with this email")

print("\n" + "=" * 60)
