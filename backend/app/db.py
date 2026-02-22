"""Database connection and configuration."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from mongoengine import connect, disconnect
    MONGOENGINE_AVAILABLE = True
except ImportError:
    MONGOENGINE_AVAILABLE = False
    logger.warning("Mongoengine not installed - database features will be unavailable")

_db_connection: Optional[object] = None


def init_db():
    """Initialize database connection."""
    global _db_connection
    
    if not MONGOENGINE_AVAILABLE:
        logger.warning("Mongoengine not installed - database features will be unavailable")
        return

    try:
        from app.config import settings
        
        if not settings.database_url or not settings.database_name:
            logger.error("DATABASE_URL or DATABASE_NAME not configured in environment")
            raise ValueError("Missing required database configuration")
        
        logger.info(f"Attempting to connect to MongoDB with database: {settings.database_name}")
        logger.debug(f"Connection string (masked): {settings.database_url[:50]}...")
        
        # Connect to MongoDB
        _db_connection = connect(
            db=settings.database_name,
            host=settings.database_url,
            connect=False,  # Don't establish connection immediately - lazy connect
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            retryWrites=True,
            w="majority",
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
        logger.info(f"MongoDB connection configured for database: {settings.database_name}")
    except Exception as e:
        logger.error(f"Failed to configure database: {e}", exc_info=True)
        # Don't raise - allow app to start without database for development
        logger.warning("App will continue without database connection")


def close_db():
    """Close database connection."""
    global _db_connection
    
    if not MONGOENGINE_AVAILABLE:
        return

    try:
        disconnect()
        _db_connection = None
        logger.info("Disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Failed to disconnect from MongoDB: {e}")
