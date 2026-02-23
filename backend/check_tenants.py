#!/usr/bin/env python3
"""Check existing tenants in database."""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.db import db
from app.models.tenant import Tenant

# Connect to database
db.connect()

# Get all tenants
tenants = Tenant.objects()
print(f"Total tenants: {len(tenants)}")
print()

for tenant in tenants:
    print(f"Tenant ID: {tenant.id}")
    print(f"  Name: {tenant.name}")
    print(f"  Subdomain: {tenant.subdomain}")
    print(f"  Status: {tenant.status}")
    print(f"  Is Published: {tenant.is_published}")
    print()
