#!/usr/bin/env python
"""Simple test to check app startup."""

import sys
import os

# Set environment to development
os.environ['ENVIRONMENT'] = 'development'

print("Step 1: Importing logging...", flush=True)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Step 2: Importing config...", flush=True)
try:
    from app.config import settings
    print(f"✓ Config loaded: {settings.environment}", flush=True)
except Exception as e:
    print(f"✗ Config error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 3: Importing db...", flush=True)
try:
    from app.db import init_db
    print("✓ DB module imported", flush=True)
except Exception as e:
    print(f"✗ DB error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 4: Importing cache...", flush=True)
try:
    from app.cache import cache
    print("✓ Cache imported", flush=True)
except Exception as e:
    print(f"✗ Cache error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 5: Importing middleware...", flush=True)
try:
    from app.middleware.tenant_context import TenantContextMiddleware
    print("✓ Middleware imported", flush=True)
except Exception as e:
    print(f"✗ Middleware error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 6: Importing routes...", flush=True)
try:
    from app.routes import auth
    print("✓ Routes imported", flush=True)
except Exception as e:
    print(f"✗ Routes error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 7: Creating app...", flush=True)
try:
    from app.main import create_app
    app = create_app()
    print("✓ App created successfully", flush=True)
except Exception as e:
    print(f"✗ App creation error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ SUCCESS: All imports successful!", flush=True)
