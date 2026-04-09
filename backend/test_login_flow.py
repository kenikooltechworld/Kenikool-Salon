"""
Test script to verify login flow and response data
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_flow():
    """Test the complete login flow"""
    
    # Test credentials
    email = "owner@test.com"  # Replace with your test email
    password = "password123"  # Replace with your test password
    
    print("=" * 60)
    print("TESTING LOGIN FLOW")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Testing POST /auth/login")
    print(f"   Email: {email}")
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password,
            "remember_me": False
        }
    )
    
    print(f"   Status Code: {login_response.status_code}")
    print(f"   Response Body: {json.dumps(login_response.json(), indent=2)}")
    print(f"   Cookies Set: {list(login_response.cookies.keys())}")
    
    if login_response.status_code != 200:
        print("\n❌ Login failed!")
        return
    
    # Extract cookies
    cookies = login_response.cookies
    
    # Step 2: Get current user
    print("\n2. Testing GET /auth/me")
    
    me_response = requests.get(
        f"{BASE_URL}/auth/me",
        cookies=cookies
    )
    
    print(f"   Status Code: {me_response.status_code}")
    print(f"   Response Body: {json.dumps(me_response.json(), indent=2)}")
    
    if me_response.status_code == 200:
        user_data = me_response.json()
        
        print("\n" + "=" * 60)
        print("USER DATA ANALYSIS")
        print("=" * 60)
        
        # Check structure
        print(f"\n✓ Response has 'user' key: {'user' in user_data}")
        print(f"✓ Response has 'permissions' key: {'permissions' in user_data}")
        
        if 'user' in user_data:
            user = user_data['user']
            print(f"\n✓ User ID: {user.get('id')}")
            print(f"✓ User Email: {user.get('email')}")
            print(f"✓ User First Name: {user.get('firstName')}")
            print(f"✓ User Last Name: {user.get('lastName')}")
            print(f"✓ User Role: {user.get('role')}")
            print(f"✓ User Role Names: {user.get('roleNames')}")
            print(f"✓ User Tenant ID: {user.get('tenantId')}")
            
            # Check if roleNames contains "Owner"
            role_names = user.get('roleNames', [])
            print(f"\n✓ Has 'Owner' role: {'Owner' in role_names}")
            print(f"✓ All roles: {role_names}")
        
        print("\n" + "=" * 60)
        print("EXPECTED FRONTEND BEHAVIOR")
        print("=" * 60)
        
        if 'user' in user_data and 'roleNames' in user_data['user']:
            role_names = user_data['user']['roleNames']
            if 'Owner' in role_names:
                print("\n✓ Should redirect to: /dashboard (Owner Dashboard)")
            elif 'Manager' in role_names:
                print("\n✓ Should redirect to: /manager (Manager Dashboard)")
            elif 'Staff' in role_names:
                print("\n✓ Should redirect to: /appointments (Staff Dashboard)")
            elif 'Customer' in role_names:
                print("\n✓ Should redirect to: /my-account (Customer Dashboard)")
            else:
                print("\n⚠ No recognized role found!")
        else:
            print("\n❌ Missing user or roleNames in response!")
    
    else:
        print("\n❌ Failed to get user data!")

if __name__ == "__main__":
    test_login_flow()
