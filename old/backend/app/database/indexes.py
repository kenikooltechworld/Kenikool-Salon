"""
Database indexes for analytics collections
"""
import logging
from pymongo import ASCENDING, DESCENDING, TEXT
from app.database import db

logger = logging.getLogger(__name__)


async def create_analytics_indexes():
    """Create all necessary indexes for analytics collections"""
    try:
        # Analytics aggregations indexes
        await db.analytics_aggregations.create_index([("tenant_id", ASCENDING)])
        await db.analytics_aggregations.create_index([("tenant_id", ASCENDING), ("date", DESCENDING)])
        await db.analytics_aggregations.create_index([("tenant_id", ASCENDING), ("metric_type", ASCENDING)])
        await db.analytics_aggregations.create_index([("tenant_id", ASCENDING), ("location_id", ASCENDING)])
        await db.analytics_aggregations.create_index([("date", DESCENDING)])
        
        logger.info("Created indexes for analytics_aggregations")
        
        # Client analytics indexes
        await db.client_analytics.create_index([("tenant_id", ASCENDING)])
        await db.client_analytics.create_index([("tenant_id", ASCENDING), ("client_id", ASCENDING)])
        await db.client_analytics.create_index([("tenant_id", ASCENDING), ("segment", ASCENDING)])
        await db.client_analytics.create_index([("tenant_id", ASCENDING), ("ltv", DESCENDING)])
        await db.client_analytics.create_index([("churn_probability", DESCENDING)])
        
        logger.info("Created indexes for client_analytics")
        
        # Inventory analytics indexes
        await db.inventory_analytics.create_index([("tenant_id", ASCENDING)])
        await db.inventory_analytics.create_index([("tenant_id", ASCENDING), ("product_id", ASCENDING)])
        await db.inventory_analytics.create_index([("tenant_id", ASCENDING), ("turnover_rate", DESCENDING)])
        await db.inventory_analytics.create_index([("tenant_id", ASCENDING), ("profit_margin", DESCENDING)])
        await db.inventory_analytics.create_index([("date", DESCENDING)])
        
        logger.info("Created indexes for inventory_analytics")
        
        # Campaign analytics indexes
        await db.campaign_analytics.create_index([("tenant_id", ASCENDING)])
        await db.campaign_analytics.create_index([("tenant_id", ASCENDING), ("campaign_id", ASCENDING)])
        await db.campaign_analytics.create_index([("tenant_id", ASCENDING), ("roi", DESCENDING)])
        await db.campaign_analytics.create_index([("date", DESCENDING)])
        
        logger.info("Created indexes for campaign_analytics")
        
        # Custom reports indexes
        await db.custom_reports.create_index([("tenant_id", ASCENDING)])
        await db.custom_reports.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
        await db.custom_reports.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
        
        logger.info("Created indexes for custom_reports")
        
        # Goals tracking indexes
        await db.goals_tracking.create_index([("tenant_id", ASCENDING)])
        await db.goals_tracking.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
        await db.goals_tracking.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
        
        logger.info("Created indexes for goals_tracking")
        
        # Predictive models indexes
        await db.predictive_models.create_index([("tenant_id", ASCENDING)])
        await db.predictive_models.create_index([("tenant_id", ASCENDING), ("model_type", ASCENDING)])
        await db.predictive_models.create_index([("tenant_id", ASCENDING), ("updated_at", DESCENDING)])
        
        logger.info("Created indexes for predictive_models")
        
        # Scheduled exports indexes
        await db.scheduled_exports.create_index([("tenant_id", ASCENDING)])
        await db.scheduled_exports.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
        await db.scheduled_exports.create_index([("next_run", ASCENDING)])
        
        logger.info("Created indexes for scheduled_exports")
        
        logger.info("All analytics indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating analytics indexes: {e}")
        raise


async def create_text_indexes():
    """Create text indexes for search functionality"""
    try:
        # Text search indexes
        await db.custom_reports.create_index([("name", TEXT), ("description", TEXT)])
        await db.goals_tracking.create_index([("name", TEXT)])
        
        logger.info("Text indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating text indexes: {e}")
        raise


async def optimize_aggregation_pipeline():
    """Optimize aggregation pipeline with indexes"""
    try:
        # Create compound indexes for common aggregation patterns
        
        # Revenue aggregation by date and location
        await db.analytics_aggregations.create_index([
            ("tenant_id", ASCENDING),
            ("date", DESCENDING),
            ("location_id", ASCENDING),
            ("metric_type", ASCENDING)
        ])
        
        # Client segmentation aggregation
        await db.client_analytics.create_index([
            ("tenant_id", ASCENDING),
            ("segment", ASCENDING),
            ("ltv", DESCENDING)
        ])
        
        # Inventory profitability aggregation
        await db.inventory_analytics.create_index([
            ("tenant_id", ASCENDING),
            ("profit_margin", DESCENDING),
            ("turnover_rate", DESCENDING)
        ])
        
        logger.info("Aggregation pipeline indexes optimized")
        
    except Exception as e:
        logger.error(f"Error optimizing aggregation pipeline: {e}")
        raise


async def get_index_stats():
    """Get statistics about indexes"""
    try:
        collections = [
            "analytics_aggregations",
            "client_analytics",
            "inventory_analytics",
            "campaign_analytics",
            "custom_reports",
            "goals_tracking",
            "predictive_models",
            "scheduled_exports"
        ]
        
        stats = {}
        for collection_name in collections:
            collection = db[collection_name]
            index_info = await collection.index_information()
            stats[collection_name] = {
                "index_count": len(index_info),
                "indexes": list(index_info.keys())
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting index stats: {e}")
        raise
