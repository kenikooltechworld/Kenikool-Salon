#!/usr/bin/env python3
"""Test subdomain tenant context issue."""

import requests
import json

# Test with real subdomain
headers = {
    "Host": "kenzola-salon.kenikool.com"
}

endpoints = [
    "/api/v1/public/salon-info",
    "/api/v1/public/bookings/testimonials?limit=5",
    "/api/v1/public/bookings/statistics",
]

for endpoint in endpoints:
    url = f"http://localhost:8000{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"Headers: {headers}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

