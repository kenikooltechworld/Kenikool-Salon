#!/usr/bin/env python
"""Test database connection."""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.user import User
from app.models.tenant import Tenant

print("Initializing database...")
init_db()

print("Testing database connection...")
try:
    # Try to count users
    user_count = User.objects.count()
    print(f"✓ Database connection OK - Found {user_count} users")
    
    # Try to count tenants
    tenant_count = Tenant.objects.count()
    print(f"✓ Found {tenant_count} tenants")
    
    # List all users
    if user_count > 0:
        print("\nExisting users:")
        for user in User.objects:
            print(f"  - {user.email} ({user.first_name} {user.last_name})")
    else:
        print("\n⚠ No users found in database")
        
except Exception as e:
    print(f"✗ Database error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
