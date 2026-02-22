"""
Test expense endpoints
"""
import pytest
from datetime import datetime, date
from tests.fixtures.base_fixtures import test_tenant, test_user, auth_headers


@pytest.mark.asyncio
async def test_create_expense_success(client, auth_headers):
    """Test successful expense creation"""
    response = client.post("/api/expenses", headers=auth_headers, json={
        "category": "Rent",
        "description": "Monthly rent payment",
        "amount": 50000.0,
        "expense_date": date.today().isoformat(),
        "payment_method": "bank_transfer",
        "vendor": "Landlord"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Monthly rent payment"
    assert data["amount"] == 50000.0
    assert data["category"] == "Rent"


@pytest.mark.asyncio
async def test_get_expenses_list(client, auth_headers):
    """Test getting expenses list"""
    response = client.get("/api/expenses", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "expenses" in data
    assert "total" in data
    assert isinstance(data["expenses"], list)


@pytest.mark.asyncio
async def test_get_expenses_filtered(client, auth_headers):
    """Test getting expenses with filters"""
    response = client.get("/api/expenses?category=Rent&limit=10", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "expenses" in data


@pytest.mark.asyncio
async def test_update_expense(client, test_db, auth_headers, test_tenant, test_user):
    """Test updating an expense"""
    expense_data = {
        "category": "Utilities",
        "description": "Old Description",
        "amount": 5000.0,
        "expense_date": date.today(),
        "tenant_id": test_tenant["_id"],
        "created_by": test_user["_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = test_db.expenses.insert_one(expense_data)
    expense_id = str(result.inserted_id)
    
    response = client.patch(f"/api/expenses/{expense_id}", headers=auth_headers, json={
        "description": "Updated Description",
        "amount": 6000.0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated Description"


@pytest.mark.asyncio
async def test_delete_expense(client, test_db, auth_headers, test_tenant, test_user):
    """Test deleting an expense"""
    expense_data = {
        "category": "Supplies",
        "description": "Expense to Delete",
        "amount": 5000.0,
        "expense_date": date.today(),
        "tenant_id": test_tenant["_id"],
        "created_by": test_user["_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = test_db.expenses.insert_one(expense_data)
    expense_id = str(result.inserted_id)
    
    response = client.delete(f"/api/expenses/{expense_id}", headers=auth_headers)
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_expense_invalid_amount(client, auth_headers):
    """Test creating expense with invalid amount"""
    response = client.post("/api/expenses", headers=auth_headers, json={
        "category": "Test",
        "description": "Invalid Expense",
        "amount": -100.0,
        "expense_date": date.today().isoformat()
    })
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_expense_unauthorized(client):
    """Test creating expense without auth"""
    response = client.post("/api/expenses", json={
        "category": "Test",
        "description": "Unauthorized Expense",
        "amount": 5000.0,
        "expense_date": date.today().isoformat()
    })
    
    assert response.status_code == 403
