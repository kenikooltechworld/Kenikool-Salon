#!/usr/bin/env python
"""Check subscription status."""
from app.db import init_db, close_db
from app.models.subscription import Subscription
from app.models.tenant import Tenant

init_db()

# Get first tenant
tenant = Tenant.objects().first()
if tenant:
    print(f"Tenant: {tenant.id} - {tenant.name}")
    
    # Check subscription
    sub = Subscription.objects(tenant_id=tenant.id).first()
    if sub:
        print(f"✓ Subscription found: {sub.status}")
    else:
        print(f"✗ NO subscription found for tenant {tenant.id}")
        print("Creating subscription...")
        from app.services.subscription_service import SubscriptionService
        sub = SubscriptionService.create_trial_subscription(str(tenant.id), trial_days=30)
        print(f"✓ Subscription created: {sub.status}")
else:
    print("No tenants found")

close_db()
