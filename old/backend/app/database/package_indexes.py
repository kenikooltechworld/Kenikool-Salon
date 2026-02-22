"""
Database indexes for package system collections
"""
import logging
from pymongo import ASCENDING, DESCENDING
from app.database import db

logger = logging.getLogger(__name__)


def create_package_indexes():
    """Create all necessary indexes for package system collections"""
    try:
        # Package Purchases collection indexes
        db.package_purchases.create_index([
            ("client_id", ASCENDING),
            ("status", ASCENDING)
        ], name="idx_client_status")
        logger.info("Created index: idx_client_status on package_purchases")
        
        db.package_purchases.create_index([
            ("expiration_date", ASCENDING),
            ("status", ASCENDING)
        ], name="idx_expiration_status")
        logger.info("Created index: idx_expiration_status on package_purchases")
        
        db.package_purchases.create_index([
            ("tenant_id", ASCENDING),
            ("purchase_date", DESCENDING)
        ], name="idx_tenant_purchase_date")
        logger.info("Created index: idx_tenant_purchase_date on package_purchases")
        
        # Additional useful indexes for package purchases
        db.package_purchases.create_index([
            ("tenant_id", ASCENDING),
            ("client_id", ASCENDING),
            ("status", ASCENDING)
        ], name="idx_tenant_client_status")
        logger.info("Created index: idx_tenant_client_status on package_purchases")
        
        db.package_purchases.create_index([
            ("package_definition_id", ASCENDING),
            ("status", ASCENDING)
        ], name="idx_package_def_status")
        logger.info("Created index: idx_package_def_status on package_purchases")
        
        logger.info("All package_purchases indexes created successfully")
        
        # Service Credits collection indexes
        db.service_credits.create_index([
            ("purchase_id", ASCENDING),
            ("service_id", ASCENDING)
        ], name="idx_purchase_service")
        logger.info("Created index: idx_purchase_service on service_credits")
        
        db.service_credits.create_index([
            ("purchase_id", ASCENDING),
            ("status", ASCENDING)
        ], name="idx_purchase_status")
        logger.info("Created index: idx_purchase_status on service_credits")
        
        # Additional useful indexes for service credits
        db.service_credits.create_index([
            ("purchase_id", ASCENDING),
            ("remaining_quantity", ASCENDING)
        ], name="idx_purchase_remaining_qty")
        logger.info("Created index: idx_purchase_remaining_qty on service_credits")
        
        logger.info("All service_credits indexes created successfully")
        
        # Redemption Transactions collection indexes
        db.redemption_transactions.create_index([
            ("purchase_id", ASCENDING),
            ("redemption_date", DESCENDING)
        ], name="idx_purchase_redemption_date")
        logger.info("Created index: idx_purchase_redemption_date on redemption_transactions")
        
        db.redemption_transactions.create_index([
            ("client_id", ASCENDING),
            ("redemption_date", DESCENDING)
        ], name="idx_client_redemption_date")
        logger.info("Created index: idx_client_redemption_date on redemption_transactions")
        
        # Additional useful indexes for redemption transactions
        db.redemption_transactions.create_index([
            ("credit_id", ASCENDING)
        ], name="idx_credit_id")
        logger.info("Created index: idx_credit_id on redemption_transactions")
        
        db.redemption_transactions.create_index([
            ("service_id", ASCENDING),
            ("redemption_date", DESCENDING)
        ], name="idx_service_redemption_date")
        logger.info("Created index: idx_service_redemption_date on redemption_transactions")
        
        logger.info("All redemption_transactions indexes created successfully")
        
        # Package Audit Logs collection indexes
        db.package_audit_logs.create_index([
            ("entity_id", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_entity_timestamp")
        logger.info("Created index: idx_entity_timestamp on package_audit_logs")
        
        db.package_audit_logs.create_index([
            ("tenant_id", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_tenant_timestamp")
        logger.info("Created index: idx_tenant_timestamp on package_audit_logs")
        
        # Additional useful indexes for audit logs
        db.package_audit_logs.create_index([
            ("action_type", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_action_timestamp")
        logger.info("Created index: idx_action_timestamp on package_audit_logs")
        
        db.package_audit_logs.create_index([
            ("tenant_id", ASCENDING),
            ("action_type", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_tenant_action_timestamp")
        logger.info("Created index: idx_tenant_action_timestamp on package_audit_logs")
        
        db.package_audit_logs.create_index([
            ("performed_by_user_id", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_user_timestamp")
        logger.info("Created index: idx_user_timestamp on package_audit_logs")
        
        logger.info("All package_audit_logs indexes created successfully")
        
        logger.info("All package system indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating package system indexes: {e}")
        raise


def get_package_index_stats():
    """Get statistics about package system indexes"""
    try:
        collections = [
            "package_purchases",
            "service_credits",
            "redemption_transactions",
            "package_audit_logs"
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
        logger.error(f"Error getting package index stats: {e}")
        raise


def drop_package_indexes(db_instance):
    """Drop all package system indexes (for cleanup/reset)"""
    try:
        collections = [
            "package_purchases",
            "service_credits",
            "redemption_transactions",
            "package_audit_logs"
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
        
        logger.info("All package system indexes dropped successfully")
        
    except Exception as e:
        logger.error(f"Error dropping package system indexes: {e}")
        raise
