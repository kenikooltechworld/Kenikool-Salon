"""Unit tests for payment service."""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from bson import ObjectId
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.tenant import Tenant
from app.models.user import User
from app.services.payment_service import PaymentService
from app.services.auth_service import AuthenticationService
from app.config import settings


@pytest.fixture
def setup_test_data(clear_db):
    """Set up test data for payment service tests."""
    # Create tenant
    tenant = Tenant(
        name="Test Salon",
        subdomain="test-salon",
        subscription_tier="professional",
        status="active",
    )
    tenant.save()

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
        "customer": customer,
        "invoice": invoice,
    }


class TestPaymentService:
    """Test payment service."""

    @patch("app.context.get_tenant_id")
    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_success(
        self, mock_paystack, mock_get_tenant_id, setup_test_data
    ):
        """Test successful payment initialization."""
        # Setup
        tenant = setup_test_data["tenant"]
        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        mock_get_tenant_id.return_value = str(tenant.id)
        mock_paystack.return_value = {
            "reference": "test_ref_123",
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "test_access_code",
        }

        service = PaymentService()

        # Execute
        result = service.initialize_payment(
            amount=Decimal("11000"),
            customer_id=str(customer.id),
            invoice_id=str(invoice.id),
            email="customer@test.com",
            metadata={"order_id": "12345"},
        )

        # Assert
        assert "payment_id" in result
        assert "authorization_url" in result
        assert result["authorization_url"] == "https://checkout.paystack.com/test"
        assert result["reference"] == "test_ref_123"

        # Verify payment record was created
        payment = Payment.objects(
            reference="test_ref_123",
            tenant_id=tenant.id,
        ).first()

        assert payment is not None
        assert payment.status == "pending"
        assert payment.amount == Decimal("11000")
        assert payment.customer_id == customer.id
        assert payment.invoice_id == invoice.id

    @patch("app.context.get_tenant_id")
    def test_initialize_payment_invalid_amount(self, mock_get_tenant_id, setup_test_data):
        """Test payment initialization with invalid amount."""
        tenant = setup_test_data["tenant"]
        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute and assert
        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            service.initialize_payment(
                amount=Decimal("-100"),
                customer_id=str(customer.id),
                invoice_id=str(invoice.id),
                email="customer@test.com",
            )

    @patch("app.context.get_tenant_id")
    def test_initialize_payment_invalid_customer(self, mock_get_tenant_id, setup_test_data):
        """Test payment initialization with invalid customer."""
        tenant = setup_test_data["tenant"]
        invoice = setup_test_data["invoice"]
        invalid_customer_id = str(ObjectId())

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute and assert
        with pytest.raises(ValueError, match="not found"):
            service.initialize_payment(
                amount=Decimal("11000"),
                customer_id=invalid_customer_id,
                invoice_id=str(invoice.id),
                email="customer@test.com",
            )

    @patch("app.context.get_tenant_id")
    def test_initialize_payment_invalid_invoice(self, mock_get_tenant_id, setup_test_data):
        """Test payment initialization with invalid invoice."""
        tenant = setup_test_data["tenant"]
        customer = setup_test_data["customer"]
        invalid_invoice_id = str(ObjectId())

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute and assert
        with pytest.raises(ValueError, match="not found"):
            service.initialize_payment(
                amount=Decimal("11000"),
                customer_id=str(customer.id),
                invoice_id=invalid_invoice_id,
                email="customer@test.com",
            )

    @patch("app.context.get_tenant_id")
    def test_initialize_payment_missing_email(self, mock_get_tenant_id, setup_test_data):
        """Test payment initialization with missing email."""
        tenant = setup_test_data["tenant"]
        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute and assert
        with pytest.raises(ValueError, match="Email is required"):
            service.initialize_payment(
                amount=Decimal("11000"),
                customer_id=str(customer.id),
                invoice_id=str(invoice.id),
                email="",
            )

    @patch("app.context.get_tenant_id")
    @patch("app.services.paystack_service.PaystackService.initialize_transaction")
    def test_initialize_payment_paystack_error(
        self, mock_paystack, mock_get_tenant_id, setup_test_data
    ):
        """Test payment initialization with Paystack error."""
        tenant = setup_test_data["tenant"]
        customer = setup_test_data["customer"]
        invoice = setup_test_data["invoice"]

        mock_get_tenant_id.return_value = str(tenant.id)
        mock_paystack.side_effect = Exception("Paystack API error")

        service = PaymentService()

        # Execute and assert
        with pytest.raises(Exception, match="Failed to initialize payment"):
            service.initialize_payment(
                amount=Decimal("11000"),
                customer_id=str(customer.id),
                invoice_id=str(invoice.id),
                email="customer@test.com",
            )

    @patch("app.context.get_tenant_id")
    def test_get_payment_success(self, mock_get_tenant_id, setup_test_data):
        """Test successful payment retrieval."""
        tenant = setup_test_data["tenant"]

        # Create a payment
        payment = Payment(
            tenant_id=tenant.id,
            customer_id=setup_test_data["customer"].id,
            invoice_id=setup_test_data["invoice"].id,
            amount=Decimal("11000"),
            reference="test_ref",
            status="pending",
        )
        payment.save()

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute
        result = service.get_payment(str(payment.id))

        # Assert
        assert result is not None
        assert result.id == payment.id
        assert result.reference == "test_ref"

    @patch("app.context.get_tenant_id")
    def test_get_payment_not_found(self, mock_get_tenant_id, setup_test_data):
        """Test retrieving non-existent payment."""
        tenant = setup_test_data["tenant"]
        invalid_id = str(ObjectId())

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute
        result = service.get_payment(invalid_id)

        # Assert
        assert result is None

    @patch("app.context.get_tenant_id")
    def test_get_payment_by_reference(self, mock_get_tenant_id, setup_test_data):
        """Test retrieving payment by reference."""
        tenant = setup_test_data["tenant"]

        # Create a payment
        payment = Payment(
            tenant_id=tenant.id,
            customer_id=setup_test_data["customer"].id,
            invoice_id=setup_test_data["invoice"].id,
            amount=Decimal("11000"),
            reference="unique_ref_123",
            status="pending",
        )
        payment.save()

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute
        result = service.get_payment_by_reference("unique_ref_123")

        # Assert
        assert result is not None
        assert result.reference == "unique_ref_123"

    @patch("app.context.get_tenant_id")
    def test_list_payments(self, mock_get_tenant_id, setup_test_data):
        """Test listing payments."""
        tenant = setup_test_data["tenant"]
        customer = setup_test_data["customer"]

        # Create multiple payments
        for i in range(3):
            payment = Payment(
                tenant_id=tenant.id,
                customer_id=customer.id,
                invoice_id=setup_test_data["invoice"].id,
                amount=Decimal("11000"),
                reference=f"ref_{i}",
                status="pending",
            )
            payment.save()

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute
        result = service.list_payments(skip=0, limit=10)

        # Assert
        assert result["total"] >= 3
        assert len(result["payments"]) >= 3

    @patch("app.context.get_tenant_id")
    def test_list_payments_filter_by_customer(self, mock_get_tenant_id, setup_test_data):
        """Test listing payments filtered by customer."""
        tenant = setup_test_data["tenant"]
        customer = setup_test_data["customer"]

        # Create payment
        payment = Payment(
            tenant_id=tenant.id,
            customer_id=customer.id,
            invoice_id=setup_test_data["invoice"].id,
            amount=Decimal("11000"),
            reference="ref_filter",
            status="pending",
        )
        payment.save()

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute
        result = service.list_payments(customer_id=str(customer.id), skip=0, limit=10)

        # Assert
        assert result["total"] >= 1
        assert all(p.customer_id == customer.id for p in result["payments"])

    @patch("app.context.get_tenant_id")
    def test_list_payments_filter_by_status(self, mock_get_tenant_id, setup_test_data):
        """Test listing payments filtered by status."""
        tenant = setup_test_data["tenant"]
        customer = setup_test_data["customer"]

        # Create payment with specific status
        payment = Payment(
            tenant_id=tenant.id,
            customer_id=customer.id,
            invoice_id=setup_test_data["invoice"].id,
            amount=Decimal("11000"),
            reference="ref_status",
            status="success",
        )
        payment.save()

        mock_get_tenant_id.return_value = str(tenant.id)

        service = PaymentService()

        # Execute
        result = service.list_payments(status="success", skip=0, limit=10)

        # Assert
        assert all(p.status == "success" for p in result["payments"])
