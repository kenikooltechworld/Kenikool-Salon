#!/usr/bin/env python3
"""
Test script for booking templates API
"""
import asyncio
import sys
import os
import requests
import json

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_booking_templates_api():
    """Test the booking templates API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Booking Templates API...")
    print("=" * 50)
    
    try:
        # Test GET /api/booking-templates (without auth for now)
        print("1. Testing GET /api/booking-templates")
        response = requests.get(f"{base_url}/api/booking-templates")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response type: {type(data)}")
            if isinstance(data, list):
                print(f"   Templates count: {len(data)}")
                if len(data) > 0:
                    print(f"   First template keys: {list(data[0].keys())}")
            else:
                print(f"   Response: {data}")
        elif response.status_code == 401:
            print("   ✓ Authentication required (expected)")
        else:
            print(f"   Error: {response.text}")
        
        # Test API structure
        print("\n2. Testing API structure")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✓ Server is running")
        else:
            print("   ✗ Server health check failed")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ✗ Cannot connect to server. Is it running on localhost:8000?")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_booking_templates_api()
    sys.exit(0 if success else 1)