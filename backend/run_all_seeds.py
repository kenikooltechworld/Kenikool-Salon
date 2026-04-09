#!/usr/bin/env python
"""Run all seed scripts in the correct order."""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

print("=" * 60)
print("RUNNING ALL SEED SCRIPTS")
print("=" * 60)

# 1. Seed pricing plans
print("\n[1/4] Seeding pricing plans...")
try:
    from seed_pricing_plans import seed_pricing_plans
    seed_pricing_plans()
    print("✓ Pricing plans seeded successfully!")
except Exception as e:
    print(f"✗ Error seeding pricing plans: {e}")
    import traceback
    traceback.print_exc()

# 2. Seed test user
print("\n[2/4] Seeding test user...")
try:
    from seed_test_user import seed_test_user
    seed_test_user()
    print("✓ Test user seeded successfully!")
except Exception as e:
    print(f"✗ Error seeding test user: {e}")
    import traceback
    traceback.print_exc()

# 3. Populate tenant settings
print("\n[3/4] Populating tenant settings...")
try:
    from populate_tenant_settings import populate_settings
    if populate_settings():
        print("✓ Tenant settings populated successfully!")
    else:
        print("✗ Failed to populate tenant settings")
except Exception as e:
    print(f"✗ Error populating tenant settings: {e}")
    import traceback
    traceback.print_exc()

# 4. Seed staff availability
print("\n[4/4] Seeding staff availability...")
try:
    from seed_staff_availability import seed_staff_availability
    if seed_staff_availability():
        print("✓ Staff availability seeded successfully!")
    else:
        print("✗ Failed to seed staff availability")
except Exception as e:
    print(f"✗ Error seeding staff availability: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("ALL SEED SCRIPTS COMPLETED")
print("=" * 60)
print("\nYou should now see all collections in MongoDB Compass:")
print("  - pricing_plans")
print("  - tenants")
print("  - users")
print("  - roles")
print("  - And other collections with data")
