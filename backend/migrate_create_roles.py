#!/usr/bin/env python
"""Migration script to create missing roles for existing tenants."""

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

def migrate_roles():
    """Create fresh roles for all tenants."""
    try:
        from app.models.tenant import Tenant
        from app.models.role import Role
        from app.services.rbac_service import RBACService
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
        
        # Get all tenants
        tenants = Tenant.objects()
        logger.info(f"Found {tenants.count()} tenants\n")
        
        rbac_service = RBACService()
        created_count = 0
        
        for tenant in tenants:
            logger.info(f"Processing tenant {tenant.id} ({tenant.name})...")
            
            # Delete existing roles for this tenant
            deleted_roles = Role.objects(tenant_id=tenant.id).delete()
            logger.info(f"  Deleted {deleted_roles} roles")
            
            # Create fresh default roles
            logger.info(f"  Creating fresh default roles...")
            try:
                rbac_service.create_default_roles(str(tenant.id))
                logger.info(f"  ✓ Successfully created fresh roles for {tenant.name}\n")
                created_count += 1
            except Exception as e:
                logger.error(f"  ✗ Failed to create roles for {tenant.name}: {e}\n")
        
        logger.info(f"\n✓ Fresh roles creation complete!")
        logger.info(f"  - Total tenants: {tenants.count()}")
        logger.info(f"  - Created: {created_count}")
        
        disconnect()
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = migrate_roles()
    sys.exit(0 if success else 1)
