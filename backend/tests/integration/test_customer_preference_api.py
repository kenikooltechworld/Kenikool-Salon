"""Integration tests for customer preference API endpoints."""

import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from app.main import create_app
from app.models.customer import Customer
from app.models.customer_preference import CustomerPreference
from app.context import set_tenant_id


@pytest.fixture
def app():
    """Create test app."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def customer(tenant_id):
    """Create a test customer."""
    customer = Customer(
        tenant_id=tenant_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890",
        communication_preference="email",
        status="active",
    )
    customer.save()
    return customer


@pytest.fixture
def staff_id():
    """Create a test staff ID."""
    return ObjectId()


@pytest.fixture
def service_id():
    """Create a test service ID."""
    return ObjectId()


class TestCustomerPreferenceAPI:
    """Test customer preference API endpoints."""

    def test_get_customer_preferences_creates_default(self, client, tenant_id, customer):
        """Test getting customer preferences creates default if not exists."""
        # Mock tenant context
        with client:
            response = client.get(
                f"/api/customers/{customer.id}/preferences",
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        # Should return 200 even if preferences don't exist (creates default)
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == str(customer.id)
        assert data["communication_methods"] == ["email"]
        assert data["language"] == "en"
        assert data["preferred_staff_ids"] == []
        assert data["preferred_service_ids"] == []

    def test_get_customer_preferences_not_found(self, client, tenant_id):
        """Test getting preferences for non-existent customer."""
        fake_customer_id = ObjectId()
        
        with client:
            response = client.get(
                f"/api/customers/{fake_customer_id}/preferences",
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 404
        assert "Customer not found" in response.json()["detail"]

    def test_update_customer_preferences(self, client, tenant_id, customer, staff_id, service_id):
        """Test updating customer preferences."""
        update_data = {
            "preferred_staff_ids": [str(staff_id)],
            "preferred_service_ids": [str(service_id)],
            "communication_methods": ["email", "sms"],
            "preferred_time_slots": ["morning", "afternoon"],
            "language": "fr",
            "notes": "Prefers morning appointments",
        }

        with client:
            response = client.put(
                f"/api/customers/{customer.id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["preferred_staff_ids"] == [str(staff_id)]
        assert data["preferred_service_ids"] == [str(service_id)]
        assert data["communication_methods"] == ["email", "sms"]
        assert data["preferred_time_slots"] == ["morning", "afternoon"]
        assert data["language"] == "fr"
        assert data["notes"] == "Prefers morning appointments"

    def test_update_customer_preferences_partial(self, client, tenant_id, customer):
        """Test partial update of customer preferences."""
        # First create preferences
        client.get(
            f"/api/customers/{customer.id}/preferences",
            headers={"X-Tenant-ID": str(tenant_id)},
        )

        # Update only language
        update_data = {"language": "es"}

        with client:
            response = client.put(
                f"/api/customers/{customer.id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "es"
        assert data["communication_methods"] == ["email"]  # Should remain unchanged

    def test_update_customer_preferences_not_found(self, client, tenant_id):
        """Test updating preferences for non-existent customer."""
        fake_customer_id = ObjectId()
        update_data = {"language": "fr"}

        with client:
            response = client.put(
                f"/api/customers/{fake_customer_id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 404
        assert "Customer not found" in response.json()["detail"]

    def test_update_communication_methods(self, client, tenant_id, customer):
        """Test updating communication methods."""
        update_data = {
            "communication_methods": ["sms", "phone"],
        }

        with client:
            response = client.put(
                f"/api/customers/{customer.id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["communication_methods"] == ["sms", "phone"]

    def test_update_preferred_time_slots(self, client, tenant_id, customer):
        """Test updating preferred time slots."""
        update_data = {
            "preferred_time_slots": ["morning", "evening"],
        }

        with client:
            response = client.put(
                f"/api/customers/{customer.id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["preferred_time_slots"] == ["morning", "evening"]

    def test_update_notes(self, client, tenant_id, customer):
        """Test updating preference notes."""
        notes = "Customer has sensitive skin, prefers hypoallergenic products"
        update_data = {"notes": notes}

        with client:
            response = client.put(
                f"/api/customers/{customer.id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == notes

    def test_preferences_response_format(self, client, tenant_id, customer):
        """Test that preferences response has correct format."""
        with client:
            response = client.get(
                f"/api/customers/{customer.id}/preferences",
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()

        # Check all required fields are present
        assert "id" in data
        assert "customer_id" in data
        assert "preferred_staff_ids" in data
        assert "preferred_service_ids" in data
        assert "communication_methods" in data
        assert "preferred_time_slots" in data
        assert "language" in data
        assert "notes" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_multiple_staff_preferences(self, client, tenant_id, customer):
        """Test storing multiple preferred staff members."""
        staff_ids = [str(ObjectId()), str(ObjectId()), str(ObjectId())]
        update_data = {"preferred_staff_ids": staff_ids}

        with client:
            response = client.put(
                f"/api/customers/{customer.id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["preferred_staff_ids"]) == 3
        assert set(data["preferred_staff_ids"]) == set(staff_ids)

    def test_multiple_service_preferences(self, client, tenant_id, customer):
        """Test storing multiple preferred services."""
        service_ids = [str(ObjectId()), str(ObjectId())]
        update_data = {"preferred_service_ids": service_ids}

        with client:
            response = client.put(
                f"/api/customers/{customer.id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["preferred_service_ids"]) == 2
        assert set(data["preferred_service_ids"]) == set(service_ids)

    def test_clear_preferences(self, client, tenant_id, customer, staff_id, service_id):
        """Test clearing preferences by setting empty lists."""
        # First set some preferences
        update_data = {
            "preferred_staff_ids": [str(staff_id)],
            "preferred_service_ids": [str(service_id)],
        }

        with client:
            client.put(
                f"/api/customers/{customer.id}/preferences",
                json=update_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        # Now clear them
        clear_data = {
            "preferred_staff_ids": [],
            "preferred_service_ids": [],
        }

        with client:
            response = client.put(
                f"/api/customers/{customer.id}/preferences",
                json=clear_data,
                headers={"X-Tenant-ID": str(tenant_id)},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["preferred_staff_ids"] == []
        assert data["preferred_service_ids"] == []

    def test_tenant_isolation_in_preferences(self, client):
        """Test that preferences are isolated by tenant."""
        tenant_id_1 = ObjectId()
        tenant_id_2 = ObjectId()

        # Create customers in different tenants
        customer_1 = Customer(
            tenant_id=tenant_id_1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
        )
        customer_1.save()

        customer_2 = Customer(
            tenant_id=tenant_id_2,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+0987654321",
        )
        customer_2.save()

        # Set preferences for customer 1
        update_data_1 = {"language": "en"}
        with client:
            response_1 = client.put(
                f"/api/customers/{customer_1.id}/preferences",
                json=update_data_1,
                headers={"X-Tenant-ID": str(tenant_id_1)},
            )

        # Set preferences for customer 2
        update_data_2 = {"language": "fr"}
        with client:
            response_2 = client.put(
                f"/api/customers/{customer_2.id}/preferences",
                json=update_data_2,
                headers={"X-Tenant-ID": str(tenant_id_2)},
            )

        assert response_1.status_code == 200
        assert response_2.status_code == 200

        # Verify tenant 1 can only see their preferences
        with client:
            response = client.get(
                f"/api/customers/{customer_1.id}/preferences",
                headers={"X-Tenant-ID": str(tenant_id_1)},
            )

        assert response.status_code == 200
        assert response.json()["language"] == "en"

        # Verify tenant 2 can only see their preferences
        with client:
            response = client.get(
                f"/api/customers/{customer_2.id}/preferences",
                headers={"X-Tenant-ID": str(tenant_id_2)},
            )

        assert response.status_code == 200
        assert response.json()["language"] == "fr"

        customer_1.delete()
        customer_2.delete()
