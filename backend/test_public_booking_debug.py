#!/usr/bin/env python
"""Debug script to test public booking endpoints."""

import requests
import json
import sys

def test_endpoint(url, headers=None):
    """Test an endpoint and print response."""
    if headers is None:
        headers = {}
    
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"Headers: {headers}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        try:
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response Body (text): {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# Test with subdomain
headers = {
    'Host': 'kenzola-salon.kenikool.com:8000'
}

test_endpoint('http://localhost:8000/api/v1/public/bookings/salon-info', headers)
test_endpoint('http://localhost:8000/api/v1/public/bookings/testimonials', headers)
test_endpoint('http://localhost:8000/api/v1/public/bookings/statistics', headers)
