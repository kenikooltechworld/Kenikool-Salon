"""
Review database indexes for performance optimization
"""
import logging

logger = logging.getLogger(__name__)


def create_review_indexes(db):
    """Create all necessary indexes for review collection"""
    try:
        reviews_collection = db.reviews
        
        # Index 1: Tenant + Status + Created Date (for listing reviews by status)
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("status", 1),
            ("created_at", -1)
        ], name="idx_tenant_status_date")
        logger.info("Created index: idx_tenant_status_date")
        
        # Index 2: Tenant + Service + Status (for service-specific reviews)
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("service_id", 1),
            ("status", 1)
        ], name="idx_tenant_service_status")
        logger.info("Created index: idx_tenant_service_status")
        
        # Index 3: Tenant + Stylist + Status (for stylist-specific reviews)
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("stylist_id", 1),
            ("status", 1)
        ], name="idx_tenant_stylist_status")
        logger.info("Created index: idx_tenant_stylist_status")
        
        # Index 4: Tenant + Rating (for filtering by rating)
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("rating", 1)
        ], name="idx_tenant_rating")
        logger.info("Created index: idx_tenant_rating")
        
        # Index 5: Booking ID (for checking if booking reviewed)
        reviews_collection.create_index([
            ("booking_id", 1)
        ], name="idx_booking_id")
        logger.info("Created index: idx_booking_id")
        
        # Index 6: Tenant + Created Date (for date range queries)
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("created_at", -1)
        ], name="idx_tenant_date")
        logger.info("Created index: idx_tenant_date")
        
        # Index 7: Text index for search (comment and client_name)
        reviews_collection.create_index([
            ("comment", "text"),
            ("client_name", "text"),
            ("service_name", "text"),
            ("stylist_name", "text")
        ], name="idx_text_search")
        logger.info("Created index: idx_text_search")
        
        # Index 8: Tenant + Response exists (for has_response filter)
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("response", 1)
        ], name="idx_tenant_response")
        logger.info("Created index: idx_tenant_response")
        
        # Index 9: Tenant + Photos exists (for has_photos filter)
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("photos", 1)
        ], name="idx_tenant_photos")
        logger.info("Created index: idx_tenant_photos")
        
        # Index 10: Tenant + Flags exists (for is_flagged filter)
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("flags", 1)
        ], name="idx_tenant_flags")
        logger.info("Created index: idx_tenant_flags")
        
        # Index 11: Compound index for common filter combinations
        reviews_collection.create_index([
            ("tenant_id", 1),
            ("status", 1),
            ("rating", 1),
            ("created_at", -1)
        ], name="idx_tenant_status_rating_date")
        logger.info("Created index: idx_tenant_status_rating_date")
        
        logger.info("All review indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating review indexes: {e}")
        raise


def drop_review_indexes(db):
    """Drop all review indexes (for cleanup/reset)"""
    try:
        reviews_collection = db.reviews
        
        # Get all indexes
        indexes = reviews_collection.list_indexes()
        
        # Drop all indexes except _id
        for index in indexes:
            if index["name"] != "_id_":
                reviews_collection.drop_index(index["name"])
                logger.info(f"Dropped index: {index['name']}")
        
        logger.info("All review indexes dropped successfully")
        
    except Exception as e:
        logger.error(f"Error dropping review indexes: {e}")
        raise
