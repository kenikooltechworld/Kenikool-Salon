#!/usr/bin/env python
"""Check current roles and permissions status."""

import os
import sys
import logging
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def check_status():
    """Check roles and permissions status."""
    try:
        from app.models.tenant import Tenant
        from app.models.role import Role
        from app.models.user import User
        from app.models.role import Permission
        from mongoengine import connect, disconnect
        
        database_url = os.getenv("DATABASE_URL")
        database_name = os.getenv("DATABASE_NAME")
        
        logger.info("Connecting to MongoDB...")
        connect(
            db=database_name,
            host=database_url,
            connect=True,
            serverSelectionTimeoutMS=10000,
            retryWrites=True,
            w="majority",
        )
        logger.info("✓ Connected to MongoDB\n")
        
        # Check tenants
        tenants = Tenant.objects()
        logger.info(f"Total tenants: {tenants.count()}")
        for tenant in tenants:
            logger.info(f"  - {tenant.name} (id: {tenant.id})")
            
            # Check roles for this tenant
            roles = Role.objects(tenant_id=tenant.id)
            logger.info(f"    Roles: {roles.count()}")
            for role in roles:
                logger.info(f"      - {role.name} (id: {role.id}, permissions: {len(role.permissions)})")
            
            # Check users for this tenant
            users = User.objects(tenant_id=tenant.id)
            logger.info(f"    Users: {users.count()}")
            for user in users:
                logger.info(f"      - {user.email} (role_ids: {len(user.role_ids)})")
                for role_id in user.role_ids:
                    role = Role.objects(id=role_id).first()
                    if role:
                        logger.info(f"        - {role.name}")
        
        # Check permissions
        permissions = Permission.objects()
        logger.info(f"\nTotal permissions: {permissions.count()}")
        
        disconnect()
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = check_status()
    sys.exit(0 if success else 1)
