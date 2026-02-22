"""
Migration: Add text search index to reviews collection

This migration creates a MongoDB text index on the reviews collection
to enable full-text search functionality on review comments and client names.

The text index is created on:
- comment: Review text content
- client_name: Client name
- service_name: Service name
- stylist_name: Stylist name

This enables searching reviews by any of these fields using MongoDB's
$text operator with relevance scoring.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def migrate_up(db):
    """Create text index for review search"""
    try:
        reviews_collection = db.reviews
        
        # Check if index already exists
        existing_indexes = reviews_collection.list_indexes()
        index_names = [idx["name"] for idx in existing_indexes]
        
        if "idx_text_search" in index_names:
            logger.info("Text search index already exists, skipping creation")
            return
        
        # Create text index on comment, client_name, service_name, and stylist_name
        reviews_collection.create_index([
            ("comment", "text"),
            ("client_name", "text"),
            ("service_name", "text"),
            ("stylist_name", "text")
        ], name="idx_text_search", default_language="english")
        
        logger.info("Successfully created text search index on reviews collection")
        
        # Log migration completion
        migration_log = {
            "migration_name": "add_review_text_index",
            "status": "completed",
            "timestamp": datetime.utcnow(),
            "description": "Created text index on comment, client_name, service_name, stylist_name"
        }
        
        # Store migration log if migrations collection exists
        try:
            db.migrations.insert_one(migration_log)
        except Exception as e:
            logger.warning(f"Could not log migration: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating text search index: {e}")
        raise


def migrate_down(db):
    """Drop text index (rollback)"""
    try:
        reviews_collection = db.reviews
        
        # Check if index exists
        existing_indexes = reviews_collection.list_indexes()
        index_names = [idx["name"] for idx in existing_indexes]
        
        if "idx_text_search" not in index_names:
            logger.info("Text search index does not exist, skipping removal")
            return
        
        # Drop the text index
        reviews_collection.drop_index("idx_text_search")
        
        logger.info("Successfully dropped text search index from reviews collection")
        
        # Log migration rollback
        migration_log = {
            "migration_name": "add_review_text_index",
            "status": "rolled_back",
            "timestamp": datetime.utcnow(),
            "description": "Dropped text index on comment, client_name, service_name, stylist_name"
        }
        
        # Store migration log if migrations collection exists
        try:
            db.migrations.insert_one(migration_log)
        except Exception as e:
            logger.warning(f"Could not log migration rollback: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error dropping text search index: {e}")
        raise


def test_search_performance(db):
    """Test search performance with the text index"""
    try:
        reviews_collection = db.reviews
        
        # Get sample reviews for testing
        sample_reviews = list(reviews_collection.find().limit(5))
        
        if not sample_reviews:
            logger.info("No reviews found for performance testing")
            return {"status": "no_data", "message": "No reviews in database"}
        
        # Test search queries
        test_queries = [
            "haircut",
            "excellent",
            "color",
            "service",
            "stylist"
        ]
        
        results = {}
        
        for query in test_queries:
            try:
                # Execute text search
                cursor = reviews_collection.find(
                    {"$text": {"$search": query}},
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})])
                
                count = cursor.count()
                results[query] = {
                    "matches": count,
                    "status": "success"
                }
                
                logger.info(f"Text search for '{query}': {count} matches")
                
            except Exception as e:
                results[query] = {
                    "matches": 0,
                    "status": "error",
                    "error": str(e)
                }
                logger.warning(f"Error searching for '{query}': {e}")
        
        return {
            "status": "completed",
            "test_results": results,
            "total_reviews": reviews_collection.count_documents({})
        }
        
    except Exception as e:
        logger.error(f"Error testing search performance: {e}")
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
    
    print("Running migration: add_review_text_index")
    print("-" * 50)
    
    try:
        result = migrate_up(db)
        print(f"Migration result: {result}")
        
        print("\nTesting search performance...")
        print("-" * 50)
        test_result = test_search_performance(db)
        print(f"Test results: {test_result}")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
