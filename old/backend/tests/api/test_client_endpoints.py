"""
Test client endpoints
"""
import pytest
from tests.fixtures.base_fixtures import test_tenant, test_user, auth_headers


@pytest.mark.asyncio
async def test_create_client_success(client, auth_headers):
    """Test successful client creation"""
    response = client.post("/api/clients", headers=auth_headers, json={
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+2348012345678"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_clients_list(client, auth_headers):
    """Test getting clients list"""
    response = client.get("/api/clients", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page_info" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_client_by_id(client, test_db, auth_headers, test_tenant):
    """Test getting client by ID"""
    # Create a client first
    from datetime import datetime
    client_data = {
        "name": "Test Client",
        "email": "testclient@example.com",
        "phone": "+2348011111111",
        "tenant_id": str(test_tenant["_id"]),
        "total_visits": 0,
        "total_spent": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = test_db.clients.insert_one(client_data)
    client_id = str(result.inserted_id)
    
    response = client.get(f"/api/clients/{client_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id
    assert data["name"] == "Test Client"


@pytest.mark.asyncio
async def test_update_client(client, test_db, auth_headers, test_tenant):
    """Test updating a client"""
    # Create a client first
    from datetime import datetime
    client_data = {
        "name": "Old Name",
        "email": "old@example.com",
        "phone": "+2348011111111",
        "tenant_id": str(test_tenant["_id"]),
        "total_visits": 0,
        "total_spent": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = test_db.clients.insert_one(client_data)
    client_id = str(result.inserted_id)
    
    response = client.patch(f"/api/clients/{client_id}", headers=auth_headers, json={
        "name": "Updated Name",
        "email": "updated@example.com"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_create_client_duplicate_email(client, auth_headers, test_db, test_tenant):
    """Test creating client with duplicate email"""
    # Create first client
    from datetime import datetime
    client_data = {
        "name": "First Client",
        "email": "duplicate@example.com",
        "phone": "+2348011111111",
        "tenant_id": str(test_tenant["_id"]),
        "total_visits": 0,
        "total_spent": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    test_db.clients.insert_one(client_data)
    
    # Try to create second client with same email
    response = client.post("/api/clients", headers=auth_headers, json={
        "name": "Second Client",
        "email": "duplicate@example.com",
        "phone": "+2348022222222"
    })
    
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_client_unauthorized(client):
    """Test creating client without auth"""
    response = client.post("/api/clients", json={
        "name": "Unauthorized Client",
        "email": "unauth@example.com",
        "phone": "+2348011111111"
    })
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_client_invalid_phone(client, auth_headers):
    """Test creating client with invalid phone"""
    response = client.post("/api/clients", headers=auth_headers, json={
        "name": "Test Client",
        "phone": "123",  # Too short
        "email": "test@example.com"
    })
    
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_search_clients(client, auth_headers, test_db, test_tenant):
    """Test searching clients"""
    # Create test clients
    from datetime import datetime
    clients = [
        {
            "name": "Alice Smith",
            "phone": "+2348011111111",
            "email": "alice@example.com",
            "tenant_id": str(test_tenant["_id"]),
            "total_visits": 0,
            "total_spent": 0.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Bob Jones",
            "phone": "+2348022222222",
            "email": "bob@example.com",
            "tenant_id": str(test_tenant["_id"]),
            "total_visits": 0,
            "total_spent": 0.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    test_db.clients.insert_many(clients)
    
    response = client.get("/api/clients?search=Alice", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
