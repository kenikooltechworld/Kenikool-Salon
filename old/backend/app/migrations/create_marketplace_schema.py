"""
Migration: Create Marketplace Schema Collections and Indexes

This migration creates all necessary MongoDB collections and indexes for the
marketplace feature, including:
- marketplace_bookings: Marketplace booking records
- guest_accounts: Guest account management
- commission_transactions: Commission tracking
- salon_portfolio: Before/after portfolio images
- referral_tracking: Referral code tracking

It also extends the tenants collection with marketplace-specific fields.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def migrate_up(db):
    """Create marketplace schema collections and indexes"""
    try:
        # 1. Create marketplace_bookings collection
        logger.info("Creating marketplace_bookings collection...")
        if "marketplace_bookings" not in db.list_collection_names():
            db.create_collection("marketplace_bookings")
            
            # Create indexes for marketplace_bookings
            db.marketplace_bookings.create_index([("tenant_id", 1), ("booking_date", -1)])
            db.marketplace_bookings.create_index([("guest_account_id", 1)])
            db.marketplace_bookings.create_index([("booking_reference", 1)], unique=True)
            db.marketplace_bookings.create_index([("status", 1)])
            db.marketplace_bookings.create_index([("payment_status", 1)])
            db.marketplace_bookings.create_index([("created_at", -1)])
            
            logger.info("✓ marketplace_bookings collection created with indexes")
        else:
            logger.info("marketplace_bookings collection already exists")
        
        # 2. Create guest_accounts collection
        logger.info("Creating guest_accounts collection...")
        if "guest_accounts" not in db.list_collection_names():
            db.create_collection("guest_accounts")
            
            # Create indexes for guest_accounts
            db.guest_accounts.create_index([("email", 1)], unique=True)
            db.guest_accounts.create_index([("magic_token", 1)], unique=True, sparse=True)
            db.guest_accounts.create_index([("created_at", -1)])
            db.guest_accounts.create_index([("is_claimed", 1)])
            
            logger.info("✓ guest_accounts collection created with indexes")
        else:
            logger.info("guest_accounts collection already exists")
        
        # 3. Create commission_transactions collection
        logger.info("Creating commission_transactions collection...")
        if "commission_transactions" not in db.list_collection_names():
            db.create_collection("commission_transactions")
            
            # Create indexes for commission_transactions
            db.commission_transactions.create_index([("tenant_id", 1), ("created_at", -1)])
            db.commission_transactions.create_index([("booking_id", 1)])
            db.commission_transactions.create_index([("status", 1)])
            db.commission_transactions.create_index([("transaction_type", 1)])
            db.commission_transactions.create_index([("payout_date", 1)])
            
            logger.info("✓ commission_transactions collection created with indexes")
        else:
            logger.info("commission_transactions collection already exists")
        
        # 4. Create salon_portfolio collection
        logger.info("Creating salon_portfolio collection...")
        if "salon_portfolio" not in db.list_collection_names():
            db.create_collection("salon_portfolio")
            
            # Create indexes for salon_portfolio
            db.salon_portfolio.create_index([("tenant_id", 1), ("display_order", 1)])
            db.salon_portfolio.create_index([("service_type", 1)])
            db.salon_portfolio.create_index([("is_active", 1)])
            db.salon_portfolio.create_index([("created_at", -1)])
            
            logger.info("✓ salon_portfolio collection created with indexes")
        else:
            logger.info("salon_portfolio collection already exists")
        
        # 5. Create referral_tracking collection
        logger.info("Creating referral_tracking collection...")
        if "referral_tracking" not in db.list_collection_names():
            db.create_collection("referral_tracking")
            
            # Create indexes for referral_tracking
            db.referral_tracking.create_index([("referral_code", 1)], unique=True)
            db.referral_tracking.create_index([("tenant_id", 1)])
            db.referral_tracking.create_index([("expires_at", 1)])
            db.referral_tracking.create_index([("clicked_at", -1)])
            db.referral_tracking.create_index([("converted_at", 1)], sparse=True)
            
            logger.info("✓ referral_tracking collection created with indexes")
        else:
            logger.info("referral_tracking collection already exists")
        
        # 6. Extend tenants collection with marketplace fields
        logger.info("Extending tenants collection with marketplace fields...")
        
        # Get all tenants that don't have marketplace fields
        tenants_to_update = db.tenants.find({
            "$or": [
                {"marketplace_enabled": {"$exists": False}},
                {"commission_rate": {"$exists": False}},
                {"referral_commission_rate": {"$exists": False}},
                {"total_marketplace_bookings": {"$exists": False}},
                {"total_commission_paid": {"$exists": False}},
                {"featured_in_marketplace": {"$exists": False}}
            ]
        })
        
        tenant_count = 0
        for tenant in tenants_to_update:
            db.tenants.update_one(
                {"_id": tenant["_id"]},
                {
                    "$set": {
                        "marketplace_enabled": tenant.get("marketplace_enabled", True),
                        "commission_rate": tenant.get("commission_rate", 10.0),
                        "referral_commission_rate": tenant.get("referral_commission_rate", 5.0),
                        "total_marketplace_bookings": tenant.get("total_marketplace_bookings", 0),
                        "total_commission_paid": tenant.get("total_commission_paid", 0),
                        "featured_in_marketplace": tenant.get("featured_in_marketplace", False),
                        "marketplace_updated_at": datetime.utcnow()
                    }
                }
            )
            tenant_count += 1
        
        logger.info(f"✓ Extended {tenant_count} tenants with marketplace fields")
        
        # 7. Log migration completion
        migration_log = {
            "migration_name": "create_marketplace_schema",
            "status": "completed",
            "timestamp": datetime.utcnow(),
            "description": "Created marketplace collections and extended tenants schema",
            "collections_created": [
                "marketplace_bookings",
                "guest_accounts",
                "commission_transactions",
                "salon_portfolio",
                "referral_tracking"
            ],
            "tenants_updated": tenant_count
        }
        
        try:
            db.migrations.insert_one(migration_log)
            logger.info("Migration logged successfully")
        except Exception as e:
            logger.warning(f"Could not log migration: {e}")
        
        logger.info("✓ Marketplace schema migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating marketplace schema: {e}")
        raise


def migrate_down(db):
    """Drop marketplace collections (rollback)"""
    try:
        collections_to_drop = [
            "marketplace_bookings",
            "guest_accounts",
            "commission_transactions",
            "salon_portfolio",
            "referral_tracking"
        ]
        
        for collection_name in collections_to_drop:
            if collection_name in db.list_collection_names():
                db.drop_collection(collection_name)
                logger.info(f"✓ Dropped {collection_name} collection")
            else:
                logger.info(f"{collection_name} collection does not exist")
        
        # Remove marketplace fields from tenants
        logger.info("Removing marketplace fields from tenants...")
        db.tenants.update_many(
            {},
            {
                "$unset": {
                    "marketplace_enabled": "",
                    "commission_rate": "",
                    "referral_commission_rate": "",
                    "total_marketplace_bookings": "",
                    "total_commission_paid": "",
                    "featured_in_marketplace": "",
                    "marketplace_updated_at": ""
                }
            }
        )
        logger.info("✓ Removed marketplace fields from tenants")
        
        # Log migration rollback
        migration_log = {
            "migration_name": "create_marketplace_schema",
            "status": "rolled_back",
            "timestamp": datetime.utcnow(),
            "description": "Dropped marketplace collections and removed tenants schema extensions"
        }
        
        try:
            db.migrations.insert_one(migration_log)
        except Exception as e:
            logger.warning(f"Could not log migration rollback: {e}")
        
        logger.info("✓ Marketplace schema rollback completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error rolling back marketplace schema: {e}")
        raise


def verify_schema(db):
    """Verify that all marketplace collections and indexes exist"""
    try:
        results = {
            "status": "success",
            "collections": {},
            "tenants_with_marketplace_fields": 0,
            "timestamp": datetime.utcnow()
        }
        
        # Check collections
        collections_to_check = [
            "marketplace_bookings",
            "guest_accounts",
            "commission_transactions",
            "salon_portfolio",
            "referral_tracking"
        ]
        
        existing_collections = db.list_collection_names()
        
        for collection_name in collections_to_check:
            if collection_name in existing_collections:
                collection = db[collection_name]
                indexes = list(collection.list_indexes())
                results["collections"][collection_name] = {
                    "exists": True,
                    "document_count": collection.count_documents({}),
                    "index_count": len(indexes),
                    "indexes": [idx["name"] for idx in indexes]
                }
            else:
                results["collections"][collection_name] = {
                    "exists": False,
                    "document_count": 0,
                    "index_count": 0
                }
        
        # Check tenants with marketplace fields
        tenants_with_fields = db.tenants.count_documents({
            "marketplace_enabled": {"$exists": True},
            "commission_rate": {"$exists": True}
        })
        results["tenants_with_marketplace_fields"] = tenants_with_fields
        
        logger.info(f"Schema verification results: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Error verifying schema: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # This allows running the migration directly for testing
    import sys
    from pymongo import MongoClient
    
    # Get MongoDB connection string from environment or use default
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    db = client.salon_db
    
    print("Running migration: create_marketplace_schema")
    print("-" * 50)
    
    try:
        result = migrate_up(db)
        print(f"Migration result: {result}")
        
        print("\nVerifying schema...")
        print("-" * 50)
        verify_result = verify_schema(db)
        print(f"Verification results: {verify_result}")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
