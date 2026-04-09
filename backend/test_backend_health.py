"""Quick test to check if backend is responding"""
import requests
import sys

try:
    response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
    print(f"✓ Backend is responding: {response.status_code}")
    print(f"Response: {response.json()}")
    sys.exit(0)
except requests.exceptions.ConnectionError:
    print("✗ Backend is not running or not accessible")
    print("Start the backend with: python run.py")
    sys.exit(1)
except requests.exceptions.Timeout:
    print("✗ Backend is running but not responding (timeout)")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
