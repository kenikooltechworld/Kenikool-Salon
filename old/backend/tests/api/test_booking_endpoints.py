"""
Test booking endpoints
"""
import pytest
from datetime import datetime, timedelta
from tests.fixtures.base_fixtures import test_tenant, test_user, auth_headers
from tests.fixtures.feature_fixtures import test_service, test_stylist, test_client


@pytest.mark.asyncio
async def test_create_booking_success(client, auth_headers, test_service, test_stylist):
    """Test successful booking creation"""
    booking_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    
    response = client.post("/api/bookings", headers=auth_headers, json={
        "client_name": "John Doe",
        "client_phone": "+2348012345678",
        "client_email": "john@example.com",
        "service_id": str(test_service["_id"]),
        "stylist_id": str(test_stylist["_id"]),
        "booking_date": booking_date,
        "notes": "Test booking"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["client_name"] == "John Doe"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_bookings_list(client, auth_headers):
    """Test getting bookings list"""
    response = client.get("/api/bookings", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page_info" in data


@pytest.mark.asyncio
async def test_get_booking_by_id(client, test_db, auth_headers, test_service, test_stylist, test_tenant):
    """Test getting booking by ID"""
    # Create a booking first
    booking_date = datetime.utcnow() + timedelta(days=1)
    booking_data = {
        "client_id": "test_client_id",
        "client_name": "Test Client",
        "client_phone": "+2348012345678",
        "service_id": str(test_service["_id"]),
        "service_name": test_service["name"],
        "service_price": test_service["price"],
        "stylist_id": str(test_stylist["_id"]),
        "stylist_name": test_stylist["name"],
        "booking_date": booking_date,
        "duration_minutes": test_service["duration_minutes"],
        "status": "pending",
        "tenant_id": str(test_tenant["_id"]),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = test_db.bookings.insert_one(booking_data)
    booking_id = str(result.inserted_id)
    
    response = client.get(f"/api/bookings/{booking_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == booking_id


@pytest.mark.asyncio
async def test_update_booking_status(client, test_db, auth_headers, test_service, test_stylist, test_tenant):
    """Test updating booking status"""
    # Create a booking first
    booking_date = datetime.utcnow() + timedelta(days=1)
    booking_data = {
        "client_id": "test_client_id",
        "client_name": "Test Client",
        "client_phone": "+2348012345678",
        "service_id": str(test_service["_id"]),
        "service_name": test_service["name"],
        "service_price": test_service["price"],
        "stylist_id": str(test_stylist["_id"]),
        "stylist_name": test_stylist["name"],
        "booking_date": booking_date,
        "duration_minutes": test_service["duration_minutes"],
        "status": "pending",
        "tenant_id": str(test_tenant["_id"]),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = test_db.bookings.insert_one(booking_data)
    booking_id = str(result.inserted_id)
    
    response = client.patch(f"/api/bookings/{booking_id}/status", headers=auth_headers, json={
        "status": "confirmed"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"


@pytest.mark.asyncio
async def test_create_booking_past_time(client, auth_headers, test_service, test_stylist):
    """Test creating booking with past time fails"""
    past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    
    response = client.post("/api/bookings", headers=auth_headers, json={
        "client_name": "John Doe",
        "client_phone": "+2348012345678",
        "service_id": str(test_service["_id"]),
        "stylist_id": str(test_stylist["_id"]),
        "booking_date": past_time
    })
    
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_create_booking_invalid_phone(client, auth_headers, test_service, test_stylist):
    """Test creating booking with invalid phone"""
    booking_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    
    response = client.post("/api/bookings", headers=auth_headers, json={
        "client_name": "John Doe",
        "client_phone": "123",  # Too short
        "service_id": str(test_service["_id"]),
        "stylist_id": str(test_stylist["_id"]),
        "booking_date": booking_date
    })
    
    assert response.status_code in [400, 422]
