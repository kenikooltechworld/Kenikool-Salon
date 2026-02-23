#!/usr/bin/env python3
"""Find real tenant and test endpoints."""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from bson import ObjectId

# Connect to database
init_db()

# Get the tenant from the logs
tenant_id = ObjectId("699b3d144563ae82e761dcb0")
tenant = Tenant.objects(id=tenant_id).first()

if tenant:
    print(f"Found tenant:")
    print(f"  ID: {tenant.id}")
    print(f"  Name: {tenant.name}")
    print(f"  Subdomain: {tenant.subdomain}")
    print(f"  Status: {tenant.status}")
    print(f"  Is Published: {tenant.is_published}")
else:
    print("Tenant not found")
    print("\nAll tenants:")
    for t in Tenant.objects():
        print(f"  {t.id} - {t.name} - subdomain: {t.subdomain} - published: {t.is_published}")
