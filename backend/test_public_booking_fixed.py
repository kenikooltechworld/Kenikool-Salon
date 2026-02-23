#!/usr/bin/env python
"""Test script to verify public booking endpoints are fixed."""

import requests
import json

def test_endpoint(url, headers=None):
    """Test an endpoint and print response."""
    if headers is None:
        headers = {}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} {url.split('/api/v1')[-1]} - {response.status_code}")
        if response.status_code != 200:
            print(f"  Error: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ {url.split('/api/v1')[-1]} - Error: {e}")
        return False

# Test with subdomain header
headers = {
    'Host': 'kenzola-salon.kenikool.com:8000'
}

print("\nTesting Public Booking Endpoints:")
print("=" * 60)

results = []
results.append(test_endpoint('http://localhost:8000/api/v1/public/salon-info', headers))
results.append(test_endpoint('http://localhost:8000/api/v1/public/services', headers))
results.append(test_endpoint('http://localhost:8000/api/v1/public/staff', headers))
results.append(test_endpoint('http://localhost:8000/api/v1/public/bookings/testimonials', headers))
results.append(test_endpoint('http://localhost:8000/api/v1/public/bookings/statistics', headers))

print("=" * 60)
if all(results):
    print("✓ All endpoints working!")
else:
    print("✗ Some endpoints failed")
