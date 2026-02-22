#!/usr/bin/env python
"""Test script to check if config can load."""

import sys
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting config import...")
    from app.config import settings
    logger.info(f"Config loaded: {settings.environment}")
    logger.info(f"Database URL: {settings.database_url[:50]}...")
    print("SUCCESS: Config loaded successfully")
    
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    print(f"ERROR: {e}")
    sys.exit(1)
