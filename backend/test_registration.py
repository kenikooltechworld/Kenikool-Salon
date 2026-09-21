import requests

url = "http://localhost:8000/api/v1/auth/register"
payload = {
    "salon_name": "Test Salon",
    "owner_name": "Test User",
    "email": "test@example.com",
    "phone": "08012345678",
    "password": "testpass123",
    "address": "123 Test St"
}

try:
    r = requests.post(url, json=payload, timeout=10)
    print("Status:", r.status_code)
    print("Response:", r.text[:500])
except Exception as e:
    print("Error:", e)
