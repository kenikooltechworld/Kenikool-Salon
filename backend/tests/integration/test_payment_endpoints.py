"""Integration tests for payment endpoints."""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.tenant import Tenant
from app.models.user import User
from app.services.auth_service import AuthenticationService
from app.config import settings

client = TestClient(app)


@pytest.fixture
def setup_test_data(clear_db):
    """Set up test data for payment tests."""
    # Create tenant
    tenant = Tenant(
        name="Test Salon",
        subdomain="test-salon",
        subscription_tier="professional",
        status="active",
    )
    tenant.save()

    # Create user
    auth_service = AuthenticationService(settings)
    user = User(
        tenant_id=tenant.id,
        email="owner@test.com",
        password_hash=auth_service.hash_password("password123"),
        first_name="Test",
        last_name="Owner",
        role_ids=[ObjectId()],
        status="active",
    )
    user.save()

    # Create customer
    customer = Customer(
        tenant_id=tenant.id,
        first_name="John",
        last_name="Doe",
        email="customer@test.com",
        phone="+234123456789",
    )
    customer.save()

    # Create invoice
    invoice = Invoice(
        tenant_id=tenant.id,
        customer_id=customer.id,
        subtotal=Decimal("10000"),
        discount=Decimal("0"),
        tax=Decimal("1000"),
        total=Decimal("11000"),
        status="issued",
    )
    invoice.save()

    return {
        "tenant": tenant,
        "user": user,
        "customer": customer,
        "invoice": invoice,
    }


@pytest.fixture
def auth_headers(setup_test_data):
    """Get authentication headers."""
    user = setup_test_data["user"]
    tenant = setup_test_data["tenant"]
    
    # Create JWT token
    auth_service = AuthenticationService(settings)
    token = auth_service.create_access_token(
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        email=user.email,
        role_ids=user.role_ids,
    )
    
    return {"Authorization": f"Bearer {token}"}


class TestPaymentInitialization:
    """Test payment initialization endpoint."""

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_success(self, mock_paystack, setup_test_data, auth_headers):
        """Test successful payment initialization."""
        # Mock Paystack response
        mock_paystack.return_value = {
            "reference": "test_ref_123",
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "test_access_code",
        }

        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
            "metadata": {"order_id": "12345"},
        }

        response = client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "payment_id" in data
        assert "authorization_url" in data
        assert data["authorization_url"] == "https://checkout.paystack.com/test"
        assert data["reference"] == "test_ref_123"

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_invalid_amount(self, mock_paystack, setup_test_data, auth_headers):
        """Test payment initialization with invalid amount."""
        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        payload = {
            "amount": -100,  # Invalid negative amount
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
        }

        response = client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_invalid_customer(self, mock_paystack, setup_test_data, auth_headers):
        """Test payment initialization with invalid customer."""
        invoice = setup_test_data["invoice"]
        invalid_customer_id = str(ObjectId())

        payload = {
            "amount": 11000,
            "customer_id": invalid_customer_id,
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
        }

        response = client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_invalid_invoice(self, mock_paystack, setup_test_data, auth_headers):
        """Test payment initialization with invalid invoice."""
        customer = setup_test_data["customer"]
        invalid_invoice_id = str(ObjectId())

        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": invalid_invoice_id,
            "email": "customer@test.com",
        }

        response = client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_missing_email(self, mock_paystack, setup_test_data, auth_headers):
        """Test payment initialization with missing email."""
        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            # Missing email
        }

        response = client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_paystack_error(self, mock_paystack, setup_test_data, auth_headers):
        """Test payment initialization with Paystack error."""
        mock_paystack.side_effect = Exception("Paystack API error")

        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
        }

        response = client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 500

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_creates_record(self, mock_paystack, setup_test_data, auth_headers):
        """Test that payment initialization creates a payment record."""
        mock_paystack.return_value = {
            "reference": "test_ref_456",
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "test_access_code",
        }

        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]
        tenant = setup_test_data["tenant"]

        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
        }

        response = client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Verify payment record was created
        payment = Payment.objects(
            reference="test_ref_456",
            tenant_id=tenant.id,
        ).first()

        assert payment is not None
        assert payment.status == "pending"
        assert payment.amount == Decimal("11000")
        assert payment.customer_id == customer.id
        assert payment.invoice_id == invoice.id


class TestPaymentRetrieval:
    """Test payment retrieval endpoints."""

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_get_payment_success(self, mock_paystack, setup_test_data, auth_headers):
        """Test successful payment retrieval."""
        mock_paystack.return_value = {
            "reference": "test_ref_789",
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "test_access_code",
        }

        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        # Create payment
        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
        }

        init_response = client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        payment_id = init_response.json()["payment_id"]

        # Retrieve payment
        response = client.get(
            f"/v1/payments/{payment_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment_id
        assert data["status"] == "pending"
        assert data["reference"] == "test_ref_789"

    def test_get_payment_not_found(self, auth_headers):
        """Test retrieving non-existent payment."""
        invalid_id = str(ObjectId())

        response = client.get(
            f"/v1/payments/{invalid_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_list_payments_success(self, mock_paystack, setup_test_data, auth_headers):
        """Test successful payment listing."""
        mock_paystack.return_value = {
            "reference": "test_ref_list",
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "test_access_code",
        }

        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        # Create payment
        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
        }

        client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        # List payments
        response = client.get(
            "/v1/payments",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "payments" in data
        assert data["total"] >= 1

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_list_payments_filter_by_customer(self, mock_paystack, setup_test_data, auth_headers):
        """Test listing payments filtered by customer."""
        mock_paystack.return_value = {
            "reference": "test_ref_filter",
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "test_access_code",
        }

        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        # Create payment
        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
        }

        client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        # List payments filtered by customer
        response = client.get(
            f"/v1/payments?customer_id={customer.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert all(p["customer_id"] == str(customer.id) for p in data["payments"])

    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_list_payments_filter_by_status(self, mock_paystack, setup_test_data, auth_headers):
        """Test listing payments filtered by status."""
        mock_paystack.return_value = {
            "reference": "test_ref_status",
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "test_access_code",
        }

        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        # Create payment
        payload = {
            "amount": 11000,
            "customer_id": str(customer.id),
            "invoice_id": str(invoice.id),
            "email": "customer@test.com",
        }

        client.post(
            "/v1/payments/initialize",
            json=payload,
            headers=auth_headers,
        )

        # List payments filtered by status
        response = client.get(
            "/v1/payments?status=pending",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert all(p["status"] == "pending" for p in data["payments"])
