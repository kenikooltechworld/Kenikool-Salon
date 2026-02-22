"""
Migration script to convert review is_approved field to status field
Converts:
  - is_approved: true -> status: "approved"
  - is_approved: false -> status: "pending"
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def migrate_review_status(db):
    """
    Migrate review collection from is_approved boolean to status string
    
    Args:
        db: MongoDB database connection
    """
    try:
        reviews_collection = db.reviews
        
        # Check if migration is needed
        sample = reviews_collection.find_one({"is_approved": {"$exists": True}})
        if not sample:
            logger.info("No reviews with is_approved field found. Migration not needed.")
            return {
                "status": "success",
                "message": "No migration needed",
                "updated_count": 0
            }
        
        # Migrate approved reviews
        approved_result = reviews_collection.update_many(
            {"is_approved": True, "status": {"$exists": False}},
            {
                "$set": {"status": "approved"},
                "$unset": {"is_approved": ""}
            }
        )
        
        # Migrate pending/rejected reviews
        pending_result = reviews_collection.update_many(
            {"is_approved": False, "status": {"$exists": False}},
            {
                "$set": {"status": "pending"},
                "$unset": {"is_approved": ""}
            }
        )
        
        total_updated = approved_result.modified_count + pending_result.modified_count
        
        logger.info(f"Migration completed. Updated {total_updated} reviews")
        logger.info(f"  - Approved: {approved_result.modified_count}")
        logger.info(f"  - Pending: {pending_result.modified_count}")
        
        return {
            "status": "success",
            "message": f"Successfully migrated {total_updated} reviews",
            "updated_count": total_updated,
            "approved_count": approved_result.modified_count,
            "pending_count": pending_result.modified_count
        }
    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return {
            "status": "error",
            "message": f"Migration failed: {str(e)}",
            "updated_count": 0
        }


async def rollback_review_status(db):
    """
    Rollback migration - convert status field back to is_approved
    
    Args:
        db: MongoDB database connection
    """
    try:
        reviews_collection = db.reviews
        
        # Check if rollback is needed
        sample = reviews_collection.find_one({"status": {"$exists": True}})
        if not sample:
            logger.info("No reviews with status field found. Rollback not needed.")
            return {
                "status": "success",
                "message": "No rollback needed",
                "updated_count": 0
            }
        
        # Rollback approved reviews
        approved_result = reviews_collection.update_many(
            {"status": "approved", "is_approved": {"$exists": False}},
            {
                "$set": {"is_approved": True},
                "$unset": {"status": ""}
            }
        )
        
        # Rollback pending/rejected reviews
        pending_result = reviews_collection.update_many(
            {"status": {"$in": ["pending", "rejected"]}, "is_approved": {"$exists": False}},
            {
                "$set": {"is_approved": False},
                "$unset": {"status": ""}
            }
        )
        
        total_updated = approved_result.modified_count + pending_result.modified_count
        
        logger.info(f"Rollback completed. Updated {total_updated} reviews")
        logger.info(f"  - Approved: {approved_result.modified_count}")
        logger.info(f"  - Pending/Rejected: {pending_result.modified_count}")
        
        return {
            "status": "success",
            "message": f"Successfully rolled back {total_updated} reviews",
            "updated_count": total_updated,
            "approved_count": approved_result.modified_count,
            "pending_count": pending_result.modified_count
        }
    
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        return {
            "status": "error",
            "message": f"Rollback failed: {str(e)}",
            "updated_count": 0
        }
