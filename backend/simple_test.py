#!/usr/bin/env python
"""Simple test to check app startup."""

import sys
import os

# Set environment to development
os.environ['ENVIRONMENT'] = 'development'

print("Step 1: Importing logging...")
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Step 2: Importing config...")
try:
    from app.config import settings
    print(f"✓ Config loaded: {settings.environment}")
except Exception as e:
    print(f"✗ Config error: {e}")
    sys.exit(1)

print("Step 3: Importing db...")
try:
    from app.db import init_db
    print("✓ DB module imported")
except Exception as e:
    print(f"✗ DB error: {e}")
    sys.exit(1)

print("Step 4: Importing middleware...")
try:
    from app.middleware.tenant_context import TenantContextMiddleware
    print("✓ Middleware imported")
except Exception as e:
    print(f"✗ Middleware error: {e}")
    sys.exit(1)

print("Step 5: Importing routes...")
try:
    from app.routes import auth
    print("✓ Routes imported")
except Exception as e:
    print(f"✗ Routes error: {e}")
    sys.exit(1)

print("Step 6: Creating app...")
try:
    from app.main import create_app
    app = create_app()
    print("✓ App created successfully")
except Exception as e:
    print(f"✗ App creation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ SUCCESS: All imports successful!")
