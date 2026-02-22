#!/usr/bin/env python
"""Test script to check if the app can start."""

import sys
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting import...")
    from app.config import settings
    logger.info(f"Config loaded: {settings.environment}")
    
    logger.info("Importing main app...")
    from app.main import app
    logger.info("App imported successfully!")
    
    logger.info("App creation successful")
    print("SUCCESS: App started successfully")
    
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    print(f"ERROR: {e}")
    sys.exit(1)
