#!/usr/bin/env python
"""Set password_change_required flag for Staff, Manager, and Customer roles."""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.user import User
from app.models.role import Role

def set_password_change_required():
    """Set password_change_required for users with Staff, Manager, or Customer roles."""
    init_db()
    
    # Get role IDs for Staff, Manager, and Customer
    staff_role = Role.objects(name="Staff").first()
    manager_role = Role.objects(name="Manager").first()
    customer_role = Role.objects(name="Customer").first()
    
    role_ids = []
    if staff_role:
        role_ids.append(staff_role.id)
        print(f"Found Staff role: {staff_role.id}")
    if manager_role:
        role_ids.append(manager_role.id)
        print(f"Found Manager role: {manager_role.id}")
    if customer_role:
        role_ids.append(customer_role.id)
        print(f"Found Customer role: {customer_role.id}")
    
    if not role_ids:
        print("No Staff, Manager, or Customer roles found")
        return
    
    # Find all users with these roles
    users = User.objects(role_ids__in=role_ids)
    
    count = 0
    for user in users:
        # Check if user has any of the target roles
        has_target_role = any(rid in role_ids for rid in user.role_ids)
        if has_target_role and not user.password_change_required:
            user.password_change_required = True
            user.save()
            count += 1
            print(f"✓ Set password_change_required for: {user.email}")
    
    print(f"\n✓ Updated {count} users")

if __name__ == "__main__":
    try:
        set_password_change_required()
        print("\n✓ Migration completed successfully!")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
