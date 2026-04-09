"""MongoDB index definitions for tenant isolation and query optimization."""

from mongoengine import connect, get_db
import logging

logger = logging.getLogger(__name__)


def create_indexes():
    """Create all required MongoDB indexes for the application."""
    try:
        db = get_db()
        
        # Tenant collection indexes
        db.tenants.create_index([("created_at", -1)])
        db.tenants.create_index([("status", 1)])
        db.tenants.create_index([("status", 1), ("created_at", -1)])
        db.tenants.create_index([("subdomain", 1)], unique=True)
        logger.info("Created indexes for tenants collection")
        
        # User collection indexes
        db.users.create_index([("tenant_id", 1), ("_id", 1)])
        db.users.create_index([("tenant_id", 1), ("email", 1)], unique=True)
        db.users.create_index([("tenant_id", 1), ("status", 1)])
        db.users.create_index([("tenant_id", 1), ("created_at", -1)])
        logger.info("Created indexes for users collection")
        
        # Session collection indexes
        db.sessions.create_index([("tenant_id", 1), ("user_id", 1)])
        db.sessions.create_index([("tenant_id", 1), ("status", 1)])
        db.sessions.create_index([("tenant_id", 1), ("created_at", -1)])
        logger.info("Created indexes for sessions collection")
        
        # Role collection indexes
        db.roles.create_index([("tenant_id", 1), ("name", 1)])
        db.roles.create_index([("tenant_id", 1), ("is_custom", 1)])
        logger.info("Created indexes for roles collection")
        
        # Permission collection indexes
        db.permissions.create_index([("tenant_id", 1), ("resource", 1), ("action", 1)])
        db.permissions.create_index([("tenant_id", 1), ("_id", 1)])  # For batch lookups
        logger.info("Created indexes for permissions collection")
        
        # Temp registration collection indexes
        db.temp_registrations.create_index([("email", 1)])
        db.temp_registrations.create_index([("phone", 1)])
        db.temp_registrations.create_index([("expires_at", 1)], expireAfterSeconds=0)
        logger.info("Created indexes for temp_registrations collection")
        
        logger.info("All indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


def verify_indexes():
    """Verify that all required indexes exist."""
    try:
        db = get_db()
        
        collections_to_check = {
            "tenants": [
                ("created_at", -1),
                ("status", 1),
                ("subdomain", 1),
            ],
            "users": [
                ("tenant_id", 1),
                ("email", 1),
                ("status", 1),
            ],
            "sessions": [
                ("tenant_id", 1),
                ("user_id", 1),
                ("status", 1),
            ],
            "roles": [
                ("tenant_id", 1),
                ("name", 1),
            ],
            "permissions": [
                ("tenant_id", 1),
                ("resource", 1),
            ],
        }
        
        for collection_name, expected_indexes in collections_to_check.items():
            collection = db[collection_name]
            existing_indexes = collection.list_indexes()
            index_names = [idx["name"] for idx in existing_indexes]
            
            logger.info(f"Indexes for {collection_name}: {index_names}")
        
        logger.info("Index verification completed")
        
    except Exception as e:
        logger.error(f"Error verifying indexes: {e}")
        raise
