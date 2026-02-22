"""
Database indexes for settings system collections
"""
import logging
from pymongo import ASCENDING, DESCENDING
from app.database import db

logger = logging.getLogger(__name__)


def create_settings_indexes():
    """Create all necessary indexes for settings system collections"""
    try:
        # Sessions collection indexes
        db.sessions.create_index("user_id")
        db.sessions.create_index("token_hash")
        db.sessions.create_index("expires_at")
        db.sessions.create_index([("user_id", ASCENDING), ("expires_at", ASCENDING)])
        db.sessions.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        logger.info("Created indexes for sessions collection")
        
        # API Keys collection indexes
        db.api_keys.create_index("user_id")
        db.api_keys.create_index("key_hash")
        db.api_keys.create_index([("user_id", ASCENDING), ("is_active", ASCENDING)])
        db.api_keys.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        db.api_keys.create_index("expires_at", sparse=True)
        logger.info("Created indexes for api_keys collection")
        
        # User Preferences collection indexes
        db.user_preferences.create_index("user_id", unique=True)
        db.user_preferences.create_index("tenant_id")
        db.user_preferences.create_index([("tenant_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
        logger.info("Created indexes for user_preferences collection")
        
        # Privacy Settings collection indexes
        db.privacy_settings.create_index("user_id", unique=True)
        db.privacy_settings.create_index("tenant_id")
        db.privacy_settings.create_index([("tenant_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
        logger.info("Created indexes for privacy_settings collection")
        
        # Security Logs collection indexes
        db.security_logs.create_index("user_id")
        db.security_logs.create_index("tenant_id")
        db.security_logs.create_index("timestamp")
        db.security_logs.create_index("event_type")
        db.security_logs.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
        db.security_logs.create_index([("tenant_id", ASCENDING), ("timestamp", DESCENDING)])
        db.security_logs.create_index([("user_id", ASCENDING), ("event_type", ASCENDING)])
        db.security_logs.create_index([("tenant_id", ASCENDING), ("event_type", ASCENDING)])
        db.security_logs.create_index("flagged", sparse=True)
        logger.info("Created indexes for security_logs collection")
        
        # Data Exports collection indexes
        db.data_exports.create_index("user_id")
        db.data_exports.create_index("tenant_id")
        db.data_exports.create_index("status")
        db.data_exports.create_index([("user_id", ASCENDING), ("requested_at", DESCENDING)])
        db.data_exports.create_index([("tenant_id", ASCENDING), ("requested_at", DESCENDING)])
        db.data_exports.create_index("expires_at", sparse=True)
        logger.info("Created indexes for data_exports collection")
        
        # Account Deletions collection indexes
        db.account_deletions.create_index("user_id")
        db.account_deletions.create_index("tenant_id")
        db.account_deletions.create_index("status")
        db.account_deletions.create_index([("user_id", ASCENDING), ("requested_at", DESCENDING)])
        db.account_deletions.create_index([("tenant_id", ASCENDING), ("requested_at", DESCENDING)])
        db.account_deletions.create_index("scheduled_for", sparse=True)
        logger.info("Created indexes for account_deletions collection")
        
        logger.info("All settings system indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating settings system indexes: {e}")
        raise


def get_settings_index_stats():
    """Get statistics about settings system indexes"""
    try:
        collections = [
            "sessions",
            "api_keys",
            "user_preferences",
            "privacy_settings",
            "security_logs",
            "data_exports",
            "account_deletions"
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
        logger.error(f"Error getting settings index stats: {e}")
        raise
