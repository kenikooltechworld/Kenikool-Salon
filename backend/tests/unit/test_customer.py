"""Unit tests for Customer model and endpoints."""

import pytest
from datetime import date, datetime
from bson import ObjectId
from app.models.customer import Customer
from app.models.tenant import Tenant
from app.context import set_tenant_id, clear_context


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
    tenant.delete()


class TestCustomerCreation:
    """Test customer creation."""

    def test_create_customer_with_valid_data(self, test_tenant):
        """Test creating a customer with valid data."""
        set_tenant_id(test_tenant.id)
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234123456789",
            address="123 Main St, Lagos",
            date_of_birth=date(1990, 5, 15),
            communication_preference="email",
            status="active",
        )
        customer.save()
        clear_context()

        assert customer.id is not None
        assert customer.first_name == "Jane"
        assert customer.last_name == "Smith"
        assert customer.email == "jane@example.com"
        assert customer.phone == "+234123456789"
        assert customer.address == "123 Main St, Lagos"
        assert customer.date_of_birth == date(1990, 5, 15)
        assert customer.communication_preference == "email"
        assert customer.status == "active"

        customer.delete()

    def test_create_customer_with_minimal_data(self, test_tenant):
        """Test creating a customer with minimal required data."""
        set_tenant_id(test_tenant.id)
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+234987654321",
        )
        customer.save()
        clear_context()

        assert customer.id is not None
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.email == "john@example.com"
        assert customer.phone == "+234987654321"
        assert customer.address is None
        assert customer.date_of_birth is None
        assert customer.communication_preference == "email"
        assert customer.status == "active"

        customer.delete()

    def test_create_customer_with_preferred_services(self, test_tenant):
        """Test creating a customer with preferred services."""
        set_tenant_id(test_tenant.id)
        service_ids = [ObjectId(), ObjectId()]
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            phone="+234555555555",
            preferred_services=service_ids,
        )
        customer.save()
        clear_context()

        assert customer.id is not None
        assert customer.preferred_services == service_ids
        assert len(customer.preferred_services) == 2

        customer.delete()

    def test_create_customer_with_preferred_staff(self, test_tenant):
        """Test creating a customer with preferred staff."""
        set_tenant_id(test_tenant.id)
        staff_id = ObjectId()
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Bob",
            last_name="Wilson",
            email="bob@example.com",
            phone="+234666666666",
            preferred_staff_id=staff_id,
        )
        customer.save()
        clear_context()

        assert customer.id is not None
        assert customer.preferred_staff_id == staff_id

        customer.delete()

    def test_create_customer_with_different_communication_preferences(self, test_tenant):
        """Test creating customers with different communication preferences."""
        set_tenant_id(test_tenant.id)
        preferences = ["email", "sms", "phone", "none"]
        
        for pref in preferences:
            customer = Customer(
                tenant_id=test_tenant.id,
                first_name="Test",
                last_name="User",
                email=f"test_{pref}@example.com",
                phone="+234777777777",
                communication_preference=pref,
            )
            customer.save()
            assert customer.communication_preference == pref
            customer.delete()
        
        clear_context()


class TestCustomerUpdate:
    """Test customer updates."""

    def test_update_customer_name(self, test_tenant):
        """Test updating customer name."""
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

        customer.first_name = "Janet"
        customer.last_name = "Smithson"
        customer.save()

        updated = Customer.objects(id=customer.id).first()
        assert updated.first_name == "Janet"
        assert updated.last_name == "Smithson"

        customer.delete()

    def test_update_customer_contact_info(self, test_tenant):
        """Test updating customer contact information."""
        set_tenant_id(test_tenant.id)
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+234123456789",
            address="Old Address",
        )
        customer.save()
        clear_context()

        customer.phone = "+234987654321"
        customer.address = "New Address, Lagos"
        customer.save()

        updated = Customer.objects(id=customer.id).first()
        assert updated.phone == "+234987654321"
        assert updated.address == "New Address, Lagos"

        customer.delete()

    def test_update_customer_preferences(self, test_tenant):
        """Test updating customer preferences."""
        set_tenant_id(test_tenant.id)
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            phone="+234555555555",
            communication_preference="email",
        )
        customer.save()
        clear_context()

        customer.communication_preference = "sms"
        customer.save()

        updated = Customer.objects(id=customer.id).first()
        assert updated.communication_preference == "sms"

        customer.delete()

    def test_update_customer_status(self, test_tenant):
        """Test updating customer status."""
        set_tenant_id(test_tenant.id)
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Bob",
            last_name="Wilson",
            email="bob@example.com",
            phone="+234666666666",
            status="active",
        )
        customer.save()
        clear_context()

        customer.status = "inactive"
        customer.save()

        updated = Customer.objects(id=customer.id).first()
        assert updated.status == "inactive"

        customer.delete()


class TestCustomerQuerying:
    """Test customer queries."""

    def test_query_customer_by_email(self, test_tenant):
        """Test querying customer by email."""
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

        found = Customer.objects(email="jane@example.com", tenant_id=test_tenant.id).first()
        assert found is not None
        assert found.first_name == "Jane"

        customer.delete()

    def test_query_customer_by_phone(self, test_tenant):
        """Test querying customer by phone."""
        set_tenant_id(test_tenant.id)
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+234987654321",
        )
        customer.save()
        clear_context()

        found = Customer.objects(phone="+234987654321", tenant_id=test_tenant.id).first()
        assert found is not None
        assert found.first_name == "John"

        customer.delete()

    def test_query_customer_by_status(self, test_tenant):
        """Test querying customers by status."""
        set_tenant_id(test_tenant.id)
        
        # Create active customer
        active_customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            phone="+234555555555",
            status="active",
        )
        active_customer.save()

        # Create inactive customer
        inactive_customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Bob",
            last_name="Wilson",
            email="bob@example.com",
            phone="+234666666666",
            status="inactive",
        )
        inactive_customer.save()
        clear_context()

        active_customers = Customer.objects(status="active", tenant_id=test_tenant.id)
        assert active_customers.count() >= 1

        inactive_customers = Customer.objects(status="inactive", tenant_id=test_tenant.id)
        assert inactive_customers.count() >= 1

        active_customer.delete()
        inactive_customer.delete()

    def test_query_customer_by_name(self, test_tenant):
        """Test querying customers by name."""
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

        # Query by first name
        found = Customer.objects(first_name="Jane", tenant_id=test_tenant.id).first()
        assert found is not None
        assert found.last_name == "Smith"

        # Query by last name
        found = Customer.objects(last_name="Smith", tenant_id=test_tenant.id).first()
        assert found is not None
        assert found.first_name == "Jane"

        customer.delete()

    def test_query_multiple_customers(self, test_tenant):
        """Test querying multiple customers."""
        set_tenant_id(test_tenant.id)
        
        customers_data = [
            ("Jane", "Smith", "jane@example.com", "+234111111111"),
            ("John", "Doe", "john@example.com", "+234222222222"),
            ("Alice", "Johnson", "alice@example.com", "+234333333333"),
        ]
        
        created_customers = []
        for first_name, last_name, email, phone in customers_data:
            customer = Customer(
                tenant_id=test_tenant.id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
            )
            customer.save()
            created_customers.append(customer)
        
        clear_context()

        # Query all customers for tenant
        all_customers = Customer.objects(tenant_id=test_tenant.id)
        assert all_customers.count() >= 3

        # Clean up
        for customer in created_customers:
            customer.delete()


class TestCustomerDeletion:
    """Test customer deletion."""

    def test_delete_customer(self, test_tenant):
        """Test deleting a customer."""
        set_tenant_id(test_tenant.id)
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234123456789",
        )
        customer.save()
        customer_id = customer.id
        clear_context()

        customer.delete()

        found = Customer.objects(id=customer_id).first()
        assert found is None


class TestCustomerValidation:
    """Test customer validation."""

    def test_customer_requires_first_name(self, test_tenant):
        """Test that customer requires first name."""
        set_tenant_id(test_tenant.id)
        
        with pytest.raises(Exception):
            customer = Customer(
                tenant_id=test_tenant.id,
                last_name="Smith",
                email="jane@example.com",
                phone="+234123456789",
            )
            customer.save()
        
        clear_context()

    def test_customer_requires_last_name(self, test_tenant):
        """Test that customer requires last name."""
        set_tenant_id(test_tenant.id)
        
        with pytest.raises(Exception):
            customer = Customer(
                tenant_id=test_tenant.id,
                first_name="Jane",
                email="jane@example.com",
                phone="+234123456789",
            )
            customer.save()
        
        clear_context()

    def test_customer_requires_email(self, test_tenant):
        """Test that customer requires email."""
        set_tenant_id(test_tenant.id)
        
        with pytest.raises(Exception):
            customer = Customer(
                tenant_id=test_tenant.id,
                first_name="Jane",
                last_name="Smith",
                phone="+234123456789",
            )
            customer.save()
        
        clear_context()

    def test_customer_requires_phone(self, test_tenant):
        """Test that customer requires phone."""
        set_tenant_id(test_tenant.id)
        
        with pytest.raises(Exception):
            customer = Customer(
                tenant_id=test_tenant.id,
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
            )
            customer.save()
        
        clear_context()

    def test_customer_status_must_be_valid(self, test_tenant):
        """Test that customer status must be valid."""
        set_tenant_id(test_tenant.id)
        
        with pytest.raises(Exception):
            customer = Customer(
                tenant_id=test_tenant.id,
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                phone="+234123456789",
                status="invalid_status",
            )
            customer.save()
        
        clear_context()

    def test_customer_communication_preference_must_be_valid(self, test_tenant):
        """Test that communication preference must be valid."""
        set_tenant_id(test_tenant.id)
        
        with pytest.raises(Exception):
            customer = Customer(
                tenant_id=test_tenant.id,
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                phone="+234123456789",
                communication_preference="invalid_preference",
            )
            customer.save()
        
        clear_context()
