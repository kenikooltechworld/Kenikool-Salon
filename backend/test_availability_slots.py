#!/usr/bin/env python3
"""Test script for availability slots endpoint."""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
}

def test_available_slots():
    """Test the available slots endpoint."""
    
    # Use today's date
    target_date = datetime.now().strftime("%Y-%m-%d")
    
    # Example IDs (replace with actual IDs from your database)
    staff_id = "6994a43827c33e0380d54428"
    service_id = "699360b499372847efc1be54"
    
    # Build the URL
    url = f"{BASE_URL}/availability/slots/available"
    params = {
        "staff_id": staff_id,
        "service_id": service_id,
        "target_date": target_date,
    }
    
    print(f"Testing endpoint: {url}")
    print(f"Parameters: {params}")
    print()
    
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("Success! Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_available_slots()
