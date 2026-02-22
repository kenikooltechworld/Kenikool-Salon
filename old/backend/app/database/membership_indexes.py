"""
Database indexes for membership system collections
"""
import logging
from pymongo import ASCENDING, DESCENDING
from app.database import db

logger = logging.getLogger(__name__)


def create_membership_indexes():
    """Create all necessary indexes for membership system collections"""
    try:
        # Membership Plans collection indexes
        db.membership_plans.create_index([
            ("tenant_id", ASCENDING)
        ], name="idx_tenant_id")
        logger.info("Created index: idx_tenant_id on membership_plans")
        
        db.membership_plans.create_index([
            ("tenant_id", ASCENDING),
            ("name", ASCENDING)
        ], name="idx_tenant_name", unique=True)
        logger.info("Created index: idx_tenant_name on membership_plans (unique)")
        
        db.membership_plans.create_index([
            ("is_active", ASCENDING)
        ], name="idx_is_active")
        logger.info("Created index: idx_is_active on membership_plans")
        
        logger.info("All membership_plans indexes created successfully")
        
        # Membership Subscriptions collection indexes
        db.membership_subscriptions.create_index([
            ("tenant_id", ASCENDING)
        ], name="idx_tenant_id")
        logger.info("Created index: idx_tenant_id on membership_subscriptions")
        
        db.membership_subscriptions.create_index([
            ("client_id", ASCENDING)
        ], name="idx_client_id")
        logger.info("Created index: idx_client_id on membership_subscriptions")
        
        db.membership_subscriptions.create_index([
            ("plan_id", ASCENDING)
        ], name="idx_plan_id")
        logger.info("Created index: idx_plan_id on membership_subscriptions")
        
        db.membership_subscriptions.create_index([
            ("status", ASCENDING)
        ], name="idx_status")
        logger.info("Created index: idx_status on membership_subscriptions")
        
        db.membership_subscriptions.create_index([
            ("end_date", ASCENDING)
        ], name="idx_end_date")
        logger.info("Created index: idx_end_date on membership_subscriptions")
        
        db.membership_subscriptions.create_index([
            ("tenant_id", ASCENDING),
            ("client_id", ASCENDING),
            ("status", ASCENDING)
        ], name="idx_tenant_client_status", unique=True)
        logger.info("Created index: idx_tenant_client_status on membership_subscriptions (unique)")
        
        logger.info("All membership_subscriptions indexes created successfully")
        
        logger.info("All membership system indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating membership system indexes: {e}")
        raise


def get_membership_index_stats():
    """Get statistics about membership system indexes"""
    try:
        collections = [
            "membership_plans",
            "membership_subscriptions"
        ]
        
        stats = {}
        for collection_name in collections:
            collection = db[collection_name]
            index_info = collection.index_information()
            stats[collection_name] = {
                "index_count": len(index_info),
                "indexes": list(index_info.keys())
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting membership index stats: {e}")
        raise


def drop_membership_indexes(db_instance):
    """Drop all membership system indexes (for cleanup/reset)"""
    try:
        collections = [
            "membership_plans",
            "membership_subscriptions"
        ]
        
        for collection_name in collections:
            collection = db_instance[collection_name]
            
            # Get all indexes
            indexes = collection.list_indexes()
            
            # Drop all indexes except _id
            for index in indexes:
                if index["name"] != "_id_":
                    collection.drop_index(index["name"])
                    logger.info(f"Dropped index: {index['name']} from {collection_name}")
        
        logger.info("All membership system indexes dropped successfully")
        
    except Exception as e:
        logger.error(f"Error dropping membership system indexes: {e}")
        raise
