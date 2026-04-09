#!/usr/bin/env python
"""Manually create a user account for testing."""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.db import init_db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.services.auth_service import AuthenticationService
from app.config import Settings

init_db()

settings = Settings()
auth_service = AuthenticationService(settings)

email = "kenikoolsalon@gmail.com"
password = "Wakili@123"
salon_name = "Kenikool Salon"
owner_name = "Kenikool"
subdomain = "kenikool-salon"

print("=" * 60)
print("CREATING USER ACCOUNT")
print("=" * 60)

try:
    # Create tenant
    print(f"\n[1] Creating tenant: {salon_name}")
    tenant = Tenant(
        name=salon_name,
        subdomain=subdomain,
        subscription_tier="trial",
        status="active",
        is_published=True,
        settings={
            "trial_end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "owner_email": email,
            "email": "",
            "phone": "",
            "currency": "NGN",
            "timezone": "Africa/Lagos",
            "language": "en",
            "allow_online_booking": True,
            "auto_confirm_bookings": True,
        },
    )
    tenant.save()
    print(f"✓ Tenant created: {tenant.id}")

    # Create default roles
    print(f"\n[2] Creating roles")
    from app.services.rbac_service import RBACService
    rbac_service = RBACService()
    rbac_service.create_default_roles(str(tenant.id))
    print(f"✓ Roles created")

    # Get Owner role
    role = Role.objects(tenant_id=tenant.id, name="Owner").first()
    if not role:
        role = Role(
            tenant_id=tenant.id,
            name="Owner",
            description="Full platform access",
            permissions=[],
        )
        role.save()
    print(f"✓ Owner role: {role.id}")

    # Create user
    print(f"\n[3] Creating user: {email}")
    hashed_password = auth_service.hash_password(password)
    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash=hashed_password,
        first_name=owner_name,
        last_name="",
        phone="",
        role_ids=[role.id],
        status="active",
        mfa_enabled=False,
    )
    user.save()
    print(f"✓ User created: {user.id}")

    # Create trial subscription
    print(f"\n[4] Creating trial subscription")
    from app.services.subscription_service import SubscriptionService
    SubscriptionService.create_trial_subscription(str(tenant.id), trial_days=30)
    print(f"✓ Trial subscription created")

    print("\n" + "=" * 60)
    print("ACCOUNT CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nLogin credentials:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"  Subdomain: {subdomain}")
    print(f"\nYou should now see these collections in Compass:")
    print(f"  - tenants")
    print(f"  - users")
    print(f"  - roles")
    print(f"  - subscriptions")
    print(f"  - pricing_plans (already exists)")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
