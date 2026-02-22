"""
Test authentication endpoints
"""
import pytest
from tests.fixtures.base_fixtures import test_tenant, test_tenant_data, test_user, test_user_data, auth_headers


@pytest.mark.asyncio
async def test_register_success(client, test_db):
    """Test successful registration"""
    response = client.post("/api/auth/register", json={
        "salon_name": "New Test Salon",
        "owner_name": "New Owner",
        "email": "newowner@testsalon.com",
        "phone": "+2348099998888",
        "password": "password123"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newowner@testsalon.com"
    
    # Verify user in database (should be auto-verified in test mode)
    user = test_db.users.find_one({"email": "newowner@testsalon.com"})
    assert user is not None
    assert user["email_verified"] is True  # Auto-verified in test mode


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email"""
    response = client.post("/api/auth/register", json={
        "salon_name": "Another Salon",
        "owner_name": "Another Owner",
        "email": test_user["email"],  # Duplicate email
        "phone": "+2348099997777",
        "password": "password123"
    })
    
    assert response.status_code == 409
    data = response.json()
    assert "already registered" in data["message"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_phone(client, test_user):
    """Test registration with duplicate phone"""
    response = client.post("/api/auth/register", json={
        "salon_name": "Another Salon",
        "owner_name": "Another Owner",
        "email": "different@email.com",
        "phone": test_user["phone"],  # Duplicate phone
        "password": "password123"
    })
    
    assert response.status_code == 409
    data = response.json()
    assert "phone number" in data["message"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_salon_name(client, test_tenant):
    """Test registration with duplicate salon name"""
    response = client.post("/api/auth/register", json={
        "salon_name": test_tenant["salon_name"],  # Duplicate salon name
        "owner_name": "Another Owner",
        "email": "different@email.com",
        "phone": "+2348099996666",
        "password": "password123"
    })
    
    assert response.status_code == 409
    data = response.json()
    assert "salon name" in data["message"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Test registration with invalid email"""
    response = client.post("/api/auth/register", json={
        "salon_name": "Test Salon",
        "owner_name": "Test Owner",
        "email": "invalid-email",  # Invalid email
        "phone": "+2348099995555",
        "password": "password123"
    })
    
    assert response.status_code == 400  # Validation errors return 400


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": "testpassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user["email"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["message"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "password123"
    })
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(client, test_db, test_user):
    """Test login with inactive user"""
    # Deactivate user
    test_db.users.update_one(
        {"_id": test_user["_id"]},
        {"$set": {"is_active": False}}
    )
    
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": "testpassword123"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert "inactive" in data["message"].lower()


@pytest.mark.asyncio
async def test_get_current_user(client, auth_headers):
    """Test getting current user"""
    response = client.get("/api/users/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "full_name" in data


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client):
    """Test getting current user without auth"""
    response = client.get("/api/users/me")
    
    assert response.status_code == 403  # FastAPI returns 403 for missing auth
