#!/usr/bin/env python
"""Fix services for public booking."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from app.models.service import Service

init_db()

# Find tenant
tenant = Tenant.objects(subdomain="kenzola-salon").first()
print(f"Tenant: {tenant}")

if tenant:
    # Update existing service
    service = Service.objects(tenant_id=tenant.id, name="Massage").first()
    if service:
        print(f"Found service: {service.name}")
        service.allow_public_booking = True
        service.is_published = True
        service.public_description = "Relaxing massage service"
        service.save()
        print(f"Updated service: {service.name}")
    
    # List all services
    services = Service.objects(tenant_id=tenant.id)
    print(f"Total services: {services.count()}")
    for s in services:
        print(f"  - {s.name}: published={s.is_published}, public={s.allow_public_booking}")
