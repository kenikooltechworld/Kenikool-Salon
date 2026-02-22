"""Integration tests for Customer API endpoints."""

import pytest
from datetime import date
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.customer import Customer
from app.models.tenant import Tenant
from app.models.user import User
from app.context import set_tenant_id, clear_context


client = TestClient(app)


@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
        subscription_tier="professional",
        status="active",
    )
    tenant.save()
    yield tenant
    
    # Clean up customers
    Customer.objects(tenant_id=tenant.id).delete()
    tenant.delete()


@pytest.fixture
def test_user(test_tenant):
    """Create a test user."""
    user = User(
        tenant_id=test_tenant.id,
        email="testuser@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        phone="+234123456789",
        status="active",
    )
    user.save()
    yield user
    user.delete()


@pytest.fixture
def auth_headers(test_tenant, test_user):
    """Create authentication headers."""
    # In a real scenario, this would use actual JWT tokens
    # For testing, we'll set the tenant context
    set_tenant_id(test_tenant.id)
    yield {"X-Tenant-ID": str(test_tenant.id)}
    clear_context()


class TestCustomerListEndpoint:
    """Test customer list endpoint."""

    def test_list_customers_empty(self, test_tenant, auth_headers):
        """Test listing customers when none exist."""
        set_tenant_id(test_tenant.id)
        response = client.get("/v1/customers", headers=auth_headers)
        clear_context()
        
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_customers_with_data(self, test_tenant, auth_headers):
        """Test listing customers with data."""
        set_tenant_id(test_tenant.id)
        
        # Create test customers
        customer1 = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234111111111",
        )
        customer1.save()

        customer2 = Customer(
            tenant_id=test_tenant.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+234222222222",
        )
        customer2.save()
        
        clear_context()
        
        response = client.get("/v1/customers", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["customers"]) >= 2

    def test_list_customers_with_pagination(self, test_tenant, auth_headers):
        """Test listing customers with pagination."""
        set_tenant_id(test_tenant.id)
        
        # Create multiple customers
        for i in range(15):
            customer = Customer(
                tenant_id=test_tenant.id,
                first_name=f"Customer{i}",
                last_name="Test",
                email=f"customer{i}@example.com",
                phone=f"+234{i:09d}",
            )
            customer.save()
        
        clear_context()
        
        # Test first page
        response = client.get("/v1/customers?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) == 10
        assert data["page"] == 1

        # Test second page
        response = client.get("/v1/customers?page=2&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) >= 5

    def test_list_customers_with_status_filter(self, test_tenant, auth_headers):
        """Test listing customers with status filter."""
        set_tenant_id(test_tenant.id)
        
        # Create active customer
        active = Customer(
            tenant_id=test_tenant.id,
            first_name="Active",
            last_name="Customer",
            email="active@example.com",
            phone="+234111111111",
            status="active",
        )
        active.save()

        # Create inactive customer
        inactive = Customer(
            tenant_id=test_tenant.id,
            first_name="Inactive",
            last_name="Customer",
            email="inactive@example.com",
            phone="+234222222222",
            status="inactive",
        )
        inactive.save()
        
        clear_context()
        
        response = client.get("/v1/customers?status=active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(c["status"] == "active" for c in data["customers"])

    def test_list_customers_with_search(self, test_tenant, auth_headers):
        """Test listing customers with search."""
        set_tenant_id(test_tenant.id)
        
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234123456789",
        )
        customer.save()
        
        clear_context()
        
        # Search by name
        response = client.get("/v1/customers?search=Jane", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert any(c["first_name"] == "Jane" for c in data["customers"])

        # Search by phone
        response = client.get("/v1/customers?search=234123456789", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert any(c["phone"] == "+234123456789" for c in data["customers"])


class TestCustomerGetEndpoint:
    """Test customer get endpoint."""

    def test_get_customer_success(self, test_tenant, auth_headers):
        """Test getting a customer successfully."""
        set_tenant_id(test_tenant.id)
        
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234123456789",
        )
        customer.save()
        customer_id = str(customer.id)
        
        clear_context()
        
        response = client.get(f"/v1/customers/{customer_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == customer_id
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"

    def test_get_customer_not_found(self, test_tenant, auth_headers):
        """Test getting a non-existent customer."""
        fake_id = str(ObjectId())
        response = client.get(f"/v1/customers/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404


class TestCustomerCreateEndpoint:
    """Test customer create endpoint."""

    def test_create_customer_success(self, test_tenant, auth_headers):
        """Test creating a customer successfully."""
        set_tenant_id(test_tenant.id)
        
        customer_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone": "+234123456789",
            "address": "123 Main St",
            "communication_preference": "email",
        }
        
        clear_context()
        
        response = client.post("/v1/customers", json=customer_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["email"] == "jane@example.com"
        assert data["phone"] == "+234123456789"

    def test_create_customer_with_preferences(self, test_tenant, auth_headers):
        """Test creating a customer with preferences."""
        set_tenant_id(test_tenant.id)
        
        service_ids = [str(ObjectId()), str(ObjectId())]
        staff_id = str(ObjectId())
        
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "+234987654321",
            "preferred_staff_id": staff_id,
            "preferred_services": service_ids,
            "communication_preference": "sms",
        }
        
        clear_context()
        
        response = client.post("/v1/customers", json=customer_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["preferred_staff_id"] == staff_id
        assert data["preferred_services"] == service_ids

    def test_create_customer_missing_required_field(self, test_tenant, auth_headers):
        """Test creating a customer with missing required field."""
        customer_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            # Missing email and phone
        }
        
        response = client.post("/v1/customers", json=customer_data, headers=auth_headers)
        
        assert response.status_code == 400

    def test_create_customer_duplicate_email(self, test_tenant, auth_headers):
        """Test creating a customer with duplicate email."""
        set_tenant_id(test_tenant.id)
        
        # Create first customer
        customer1 = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234111111111",
        )
        customer1.save()
        
        clear_context()
        
        # Try to create second customer with same email
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "+234222222222",
        }
        
        response = client.post("/v1/customers", json=customer_data, headers=auth_headers)
        
        assert response.status_code == 400


class TestCustomerUpdateEndpoint:
    """Test customer update endpoint."""

    def test_update_customer_success(self, test_tenant, auth_headers):
        """Test updating a customer successfully."""
        set_tenant_id(test_tenant.id)
        
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234123456789",
        )
        customer.save()
        customer_id = str(customer.id)
        
        clear_context()
        
        update_data = {
            "first_name": "Janet",
            "phone": "+234987654321",
        }
        
        response = client.put(f"/v1/customers/{customer_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Janet"
        assert data["phone"] == "+234987654321"

    def test_update_customer_not_found(self, test_tenant, auth_headers):
        """Test updating a non-existent customer."""
        fake_id = str(ObjectId())
        update_data = {"first_name": "Updated"}
        
        response = client.put(f"/v1/customers/{fake_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_customer_status(self, test_tenant, auth_headers):
        """Test updating customer status."""
        set_tenant_id(test_tenant.id)
        
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234123456789",
            status="active",
        )
        customer.save()
        customer_id = str(customer.id)
        
        clear_context()
        
        update_data = {"status": "inactive"}
        
        response = client.put(f"/v1/customers/{customer_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"


class TestCustomerDeleteEndpoint:
    """Test customer delete endpoint."""

    def test_delete_customer_success(self, test_tenant, auth_headers):
        """Test deleting a customer successfully."""
        set_tenant_id(test_tenant.id)
        
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234123456789",
        )
        customer.save()
        customer_id = str(customer.id)
        
        clear_context()
        
        response = client.delete(f"/v1/customers/{customer_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_delete_customer_not_found(self, test_tenant, auth_headers):
        """Test deleting a non-existent customer."""
        fake_id = str(ObjectId())
        
        response = client.delete(f"/v1/customers/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
