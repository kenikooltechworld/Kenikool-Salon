"""
Database index optimization for service-related collections
"""
import logging
from pymongo import ASCENDING, DESCENDING, IndexModel

logger = logging.getLogger(__name__)


async def create_service_indexes(db):
    """
    Create optimized indexes for service-related collections
    
    Requirements: Task 5.7 - Performance Optimization
    """
    try:
        # Services collection indexes
        services_indexes = [
            IndexModel([("tenant_id", ASCENDING), ("is_active", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("category", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("price", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("duration_minutes", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("name", ASCENDING)]),
            IndexModel([("assigned_stylists", ASCENDING)]),
        ]
        await db.services.create_indexes(services_indexes)
        logger.info("Created indexes for services collection")
        
        # Bookings collection indexes (for service queries)
        bookings_indexes = [
            IndexModel([("service_id", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("service_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("service_id", ASCENDING), ("stylist_id", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("service_id", ASCENDING), ("created_at", DESCENDING)]),
        ]
        await db.bookings.create_indexes(bookings_indexes)
        logger.info("Created indexes for bookings collection")
        
        # Service variants collection indexes
        variants_indexes = [
            IndexModel([("service_id", ASCENDING), ("is_active", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("service_id", ASCENDING)]),
        ]
        await db.service_variants.create_indexes(variants_indexes)
        logger.info("Created indexes for service_variants collection")
        
        # Service packages collection indexes
        packages_indexes = [
            IndexModel([("tenant_id", ASCENDING), ("is_active", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("valid_until", ASCENDING)]),
            IndexModel([("services.service_id", ASCENDING)]),
        ]
        await db.service_packages.create_indexes(packages_indexes)
        logger.info("Created indexes for service_packages collection")
        
        # Service templates collection indexes
        templates_indexes = [
            IndexModel([("tenant_id", ASCENDING), ("category", ASCENDING)]),
            IndexModel([("is_default", ASCENDING)]),
        ]
        await db.service_templates.create_indexes(templates_indexes)
        logger.info("Created indexes for service_templates collection")
        
        # Reviews collection indexes (for service reviews)
        reviews_indexes = [
            IndexModel([("service_id", ASCENDING), ("is_approved", ASCENDING)]),
            IndexModel([("service_id", ASCENDING), ("rating", ASCENDING)]),
            IndexModel([("service_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("service_id", ASCENDING)]),
        ]
        await db.reviews.create_indexes(reviews_indexes)
        logger.info("Created indexes for reviews collection")
        
        # Service recommendations collection indexes
        recommendations_indexes = [
            IndexModel([("service_id", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("service_id", ASCENDING)]),
        ]
        await db.service_recommendations.create_indexes(recommendations_indexes)
        logger.info("Created indexes for service_recommendations collection")
        
        # Audit log collection indexes
        audit_indexes = [
            IndexModel([("entity_type", ASCENDING), ("entity_id", ASCENDING), ("timestamp", DESCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("entity_type", ASCENDING), ("timestamp", DESCENDING)]),
        ]
        await db.audit_logs.create_indexes(audit_indexes)
        logger.info("Created indexes for audit_logs collection")
        
        logger.info("All service-related indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        return False


async def create_waitlist_indexes(db):
    """
    Create optimized indexes for waitlist collection
    
    Requirements: Task 1 - Enhance waitlist data model and database schema
    """
    try:
        # Waitlist collection indexes
        waitlist_indexes = [
            IndexModel([("tenant_id", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("priority_score", DESCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("service_id", ASCENDING)]),
            IndexModel([("tenant_id", ASCENDING), ("location_id", ASCENDING)]),
            IndexModel([("access_token", ASCENDING)]),
        ]
        await db.waitlist.create_indexes(waitlist_indexes)
        logger.info("Created indexes for waitlist collection")
        return True
        
    except Exception as e:
        logger.error(f"Error creating waitlist indexes: {e}")
        return False


async def optimize_service_queries(db):
    """
    Additional query optimization utilities
    """
    try:
        # Create text index for service search
        await db.services.create_index([
            ("name", "text"),
            ("description", "text"),
            ("category", "text")
        ])
        logger.info("Created text index for service search")
        
        return True
    except Exception as e:
        logger.error(f"Error optimizing queries: {e}")
        return False
