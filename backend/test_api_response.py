"""Test what the API endpoint returns."""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint
API_URL = "http://localhost:8000/api/v1/settings"

# You'll need to get a valid token - for now just check if server is running
try:
    response = requests.get(API_URL, timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'subdomain_url' in data['data']:
            print(f"subdomain_url from API: '{data['data']['subdomain_url']}'")
        else:
            print("Response structure:", data)
    else:
        print(f"Response: {response.text}")
except requests.exceptions.ConnectionError:
    print("Backend server is not running on http://localhost:8000")
except Exception as e:
    print(f"Error: {str(e)}")
