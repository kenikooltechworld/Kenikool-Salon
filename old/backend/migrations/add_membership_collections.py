"""
Migration script to create membership collections and indexes.
Run this migration to set up the database schema for the membership system.
"""

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import OperationFailure
import logging

logger = logging.getLogger(__name__)


async def migrate_up(db):
    """
    Create membership collections and indexes.
    
    Args:
        db: MongoDB database instance
    """
    try:
        # Create membership_plans collection
        logger.info("Creating membership_plans collection...")
        try:
            db.create_collection("membership_plans")
        except OperationFailure as e:
            if "already exists" in str(e):
                logger.info("membership_plans collection already exists")
            else:
                raise

        # Create indexes for membership_plans
        plans_collection = db["membership_plans"]
        
        # Index on tenant_id
        logger.info("Creating index on tenant_id for membership_plans...")
        plans_collection.create_index([("tenant_id", ASCENDING)])
        
        # Unique compound index on tenant_id + name
        logger.info("Creating unique index on tenant_id + name for membership_plans...")
        plans_collection.create_index(
            [("tenant_id", ASCENDING), ("name", ASCENDING)],
            unique=True
        )
        
        # Index on is_active
        logger.info("Creating index on is_active for membership_plans...")
        plans_collection.create_index([("is_active", ASCENDING)])
        
        # Create membership_subscriptions collection
        logger.info("Creating membership_subscriptions collection...")
        try:
            db.create_collection("membership_subscriptions")
        except OperationFailure as e:
            if "already exists" in str(e):
                logger.info("membership_subscriptions collection already exists")
            else:
                raise

        # Create indexes for membership_subscriptions
        subscriptions_collection = db["membership_subscriptions"]
        
        # Index on tenant_id
        logger.info("Creating index on tenant_id for membership_subscriptions...")
        subscriptions_collection.create_index([("tenant_id", ASCENDING)])
        
        # Index on client_id
        logger.info("Creating index on client_id for membership_subscriptions...")
        subscriptions_collection.create_index([("client_id", ASCENDING)])
        
        # Index on plan_id
        logger.info("Creating index on plan_id for membership_subscriptions...")
        subscriptions_collection.create_index([("plan_id", ASCENDING)])
        
        # Index on status
        logger.info("Creating index on status for membership_subscriptions...")
        subscriptions_collection.create_index([("status", ASCENDING)])
        
        # Index on end_date (for renewal queries)
        logger.info("Creating index on end_date for membership_subscriptions...")
        subscriptions_collection.create_index([("end_date", ASCENDING)])
        
        # Compound index to prevent duplicate active subscriptions
        logger.info("Creating compound index on tenant_id + client_id + status...")
        subscriptions_collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("client_id", ASCENDING),
                ("status", ASCENDING)
            ]
        )
        
        logger.info("Migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise


async def migrate_down(db):
    """
    Drop membership collections (for rollback).
    
    Args:
        db: MongoDB database instance
    """
    try:
        logger.info("Dropping membership_plans collection...")
        db["membership_plans"].drop()
        
        logger.info("Dropping membership_subscriptions collection...")
        db["membership_subscriptions"].drop()
        
        logger.info("Rollback completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        raise


# Migration metadata
MIGRATION_ID = "add_membership_collections"
DESCRIPTION = "Create membership_plans and membership_subscriptions collections with indexes"
VERSION = "1.0"
