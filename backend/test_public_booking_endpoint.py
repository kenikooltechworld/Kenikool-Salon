#!/usr/bin/env python
"""Test public booking endpoint with subdomain."""

import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import create_app
from app.db import init_db, close_db
from app.models.tenant import Tenant

def main():
    """Test the public booking endpoint."""
    init_db()
    
    try:
        # Create test app
        app = create_app()
        client = TestClient(app)
        
        # Check if kenzola-salon tenant exists
        tenant = Tenant.objects(subdomain="kenzola-salon").first()
        
        if not tenant:
            print("✗ Tenant 'kenzola-salon' not found in database")
            print("  Please create a test tenant first")
            return
        
        print(f"✓ Found tenant: {tenant.name}")
        print(f"  ID: {tenant.id}")
        print(f"  Published: {tenant.is_published}")
        print(f"  Status: {tenant.status}")
        
        # Test the endpoint with subdomain header
        print("\nTesting /api/v1/public/salon-info endpoint...")
        
        # Simulate request from kenzola-salon.localhost
        response = client.get(
            "/api/v1/public/salon-info",
            headers={"Host": "kenzola-salon.localhost:8000"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✓ Public booking endpoint working correctly!")
        else:
            print(f"\n✗ Endpoint returned status {response.status_code}")
            
    finally:
        close_db()

if __name__ == '__main__':
    main()
