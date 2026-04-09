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
    """Initialize MongoDB Atlas connection."""
    global _db_connection
    
    if not MONGOENGINE_AVAILABLE:
        logger.warning("Mongoengine not installed - database features will be unavailable")
        return

    try:
        from app.config import settings
        
        if not settings.database_name:
            logger.error("DATABASE_NAME not configured in environment")
            raise ValueError("Missing required database configuration")
        
        if not settings.database_url:
            logger.error("DATABASE_URL not configured in environment")
            raise ValueError("Missing DATABASE_URL configuration")
        
        # Disconnect any existing connections first
        try:
            disconnect()
        except Exception:
            pass
        
        # Connect to MongoDB Atlas
        logger.info(f"Connecting to MongoDB Atlas: {settings.database_name}")
        if _try_connect_to_db(settings.database_url, settings.database_name):
            logger.info("✓ Connected to MongoDB Atlas")
        else:
            logger.error("✗ Failed to connect to MongoDB Atlas")
            raise ConnectionError("Could not establish MongoDB Atlas connection")
        
    except Exception as e:
        logger.error(f"Failed to configure database: {e}", exc_info=True)
        raise


def _try_connect_to_db(connection_url: str, database_name: str) -> bool:
    """Try to connect to a MongoDB instance.
    
    Args:
        connection_url: MongoDB connection string
        database_name: Database name to use
        
    Returns:
        True if connection successful, False otherwise
    """
    global _db_connection
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Remove database name from URL if present, use the database_name parameter instead
            # This ensures we use the DATABASE_NAME env variable, not hardcoded values in the URL
            clean_url = connection_url.split('?')[0]  # Remove query params
            if clean_url.endswith('/'):
                clean_url = clean_url[:-1]
            # Remove database name from path if present (e.g., /Kenikool_Salon)
            if '/' in clean_url.split('@')[-1]:  # Check after the host part
                clean_url = '/'.join(clean_url.split('/')[:-1])
            
            _db_connection = connect(
                db=database_name,
                host=clean_url,
                connect=True,  # Establish connection immediately
                serverSelectionTimeoutMS=10000,  # 10 second timeout for server selection
                connectTimeoutMS=10000,  # 10 second timeout for initial connection
                socketTimeoutMS=None,  # No timeout for socket operations (queries)
                retryWrites=True,
                w="majority",
                maxPoolSize=50,
                minPoolSize=10,
            )
            logger.debug(f"Successfully connected to MongoDB database: {database_name}")
            return True
            
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.debug(f"Connection attempt {retry_count} failed: {str(e)[:100]}. Retrying...")
                import time
                time.sleep(2 ** retry_count)  # Exponential backoff: 2s, 4s, 8s
            else:
                logger.error(f"All {max_retries} connection attempts failed: {str(e)}")
    
    return False


def get_db():
    """Get the raw MongoDB database connection for aggregation queries.
    
    Returns:
        pymongo.database.Database: The MongoDB database instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    if not MONGOENGINE_AVAILABLE:
        raise RuntimeError("Mongoengine not installed - database features unavailable")
    
    if _db_connection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    try:
        from mongoengine import get_db as mongoengine_get_db
        return mongoengine_get_db()
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        raise


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
