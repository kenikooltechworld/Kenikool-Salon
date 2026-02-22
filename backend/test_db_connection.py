#!/usr/bin/env python
"""Test MongoDB connection from Docker container."""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test MongoDB connection."""
    database_url = os.getenv("DATABASE_URL")
    database_name = os.getenv("DATABASE_NAME")
    
    logger.info(f"DATABASE_URL: {database_url[:50] if database_url else 'NOT SET'}...")
    logger.info(f"DATABASE_NAME: {database_name}")
    
    if not database_url or not database_name:
        logger.error("Missing DATABASE_URL or DATABASE_NAME")
        return False
    
    try:
        from mongoengine import connect, disconnect
        
        logger.info("Attempting to connect to MongoDB...")
        connection = connect(
            db=database_name,
            host=database_url,
            connect=True,
            serverSelectionTimeoutMS=10000,
            retryWrites=True,
            w="majority",
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        logger.info("✓ Successfully connected to MongoDB!")
        
        # Try to access the database
        from mongoengine import Document, StringField
        
        class TestDoc(Document):
            test_field = StringField()
            meta = {'db_alias': 'default'}
        
        # Try to create a test document
        test_doc = TestDoc(test_field="test")
        test_doc.save()
        logger.info("✓ Successfully created test document!")
        
        # Clean up
        test_doc.delete()
        logger.info("✓ Successfully deleted test document!")
        
        disconnect()
        logger.info("✓ Connection test passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Connection test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
