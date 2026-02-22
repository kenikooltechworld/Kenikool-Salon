"""Unit tests for Payment model."""

import pytest
from datetime import datetime
from decimal import Decimal
from bson import ObjectId
from app.models.payment import Payment


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def customer_id():
    """Create a test customer ID."""
    return ObjectId()


@pytest.fixture
def invoice_id():
    """Create a test invoice ID."""
    return ObjectId()


@pytest.fixture
def payment_data(tenant_id, customer_id, invoice_id):
    """Create test payment data."""
    return {
        "tenant_id": tenant_id,
        "customer_id": customer_id,
        "invoice_id": invoice_id,
        "amount": Decimal("50.00"),
        "reference": "PSK_REF_12345",
        "gateway": "paystack",
        "status": "pending",
        "metadata": {"order_id": "ORD_001"},
    }


class TestPaymentModel:
    """Test Payment model."""

    def test_create_payment(self, payment_data):
        """Test creating a payment."""
        payment = Payment(**payment_data)
        payment.save()

        assert payment.id is not None
        assert payment.tenant_id == payment_data["tenant_id"]
        assert payment.customer_id == payment_data["customer_id"]
        assert payment.invoice_id == payment_data["invoice_id"]
        assert payment.amount == Decimal("50.00")
        assert payment.reference == "PSK_REF_12345"
        assert payment.gateway == "paystack"
        assert payment.status == "pending"
        assert payment.metadata == {"order_id": "ORD_001"}

    def test_payment_default_status(self, payment_data):
        """Test payment defaults to pending status."""
        payment_data.pop("status")
        payment = Payment(**payment_data)
        payment.save()

        assert payment.status == "pending"

    def test_payment_default_gateway(self, payment_data):
        """Test payment defaults to paystack gateway."""
        payment_data.pop("gateway")
        payment = Payment(**payment_data)
        payment.save()

        assert payment.gateway == "paystack"

    def test_payment_default_metadata(self, payment_data):
        """Test payment defaults to empty metadata."""
        payment_data.pop("metadata")
        payment = Payment(**payment_data)
        payment.save()

        assert payment.metadata == {}

    def test_payment_timestamps(self, payment_data):
        """Test payment timestamps are set correctly."""
        payment = Payment(**payment_data)
        payment.save()

        assert payment.created_at is not None
        assert payment.updated_at is not None
        assert isinstance(payment.created_at, datetime)
        assert isinstance(payment.updated_at, datetime)

    def test_payment_update_timestamp(self, payment_data):
        """Test updated_at is updated on save."""
        payment = Payment(**payment_data)
        payment.save()

        original_updated_at = payment.updated_at
        payment.status = "success"
        payment.save()

        assert payment.updated_at > original_updated_at

    def test_payment_status_choices(self, payment_data):
        """Test payment status must be one of allowed choices."""
        payment = Payment(**payment_data)
        payment.save()

        # Valid statuses
        for status in ["pending", "success", "failed", "cancelled"]:
            payment.status = status
            payment.save()
            assert payment.status == status

    def test_payment_amount_validation(self, payment_data):
        """Test payment amount must be positive."""
        payment_data["amount"] = Decimal("0")
        with pytest.raises(Exception):
            payment = Payment(**payment_data)
            payment.save()

        payment_data["amount"] = Decimal("-10.00")
        with pytest.raises(Exception):
            payment = Payment(**payment_data)
            payment.save()

    def test_payment_required_fields(self, payment_data):
        """Test payment requires all required fields."""
        required_fields = ["tenant_id", "customer_id", "invoice_id", "amount", "reference"]

        for field in required_fields:
            data = payment_data.copy()
            data.pop(field)
            with pytest.raises(Exception):
                payment = Payment(**data)
                payment.save()

    def test_payment_unique_reference_per_tenant(self, payment_data):
        """Test payment reference is unique per tenant."""
        payment1 = Payment(**payment_data)
        payment1.save()

        # Same reference, same tenant - should fail
        payment2 = Payment(**payment_data)
        with pytest.raises(Exception):
            payment2.save()

    def test_payment_same_reference_different_tenant(self, payment_data):
        """Test same reference can exist in different tenants."""
        payment1 = Payment(**payment_data)
        payment1.save()

        # Create another tenant ID
        tenant2_id = ObjectId()

        # Same reference, different tenant - should succeed
        payment_data["tenant_id"] = tenant2_id
        payment2 = Payment(**payment_data)
        payment2.save()

        assert payment1.reference == payment2.reference
        assert payment1.tenant_id != payment2.tenant_id

    def test_payment_string_representation(self, payment_data):
        """Test payment string representation."""
        payment = Payment(**payment_data)
        payment.save()

        str_repr = str(payment)
        assert "PSK_REF_12345" in str_repr
        assert "50.00" in str_repr
        assert "pending" in str_repr

    def test_payment_repr(self, payment_data):
        """Test payment repr."""
        payment = Payment(**payment_data)
        payment.save()

        repr_str = repr(payment)
        assert "Payment" in repr_str
        assert "PSK_REF_12345" in repr_str
        assert "50.00" in repr_str
        assert "pending" in repr_str

    def test_payment_decimal_precision(self, payment_data):
        """Test payment amount maintains decimal precision."""
        payment_data["amount"] = Decimal("99.99")
        payment = Payment(**payment_data)
        payment.save()

        retrieved = Payment.objects.get(id=payment.id)
        assert retrieved.amount == Decimal("99.99")

    def test_payment_metadata_storage(self, payment_data):
        """Test payment metadata is stored correctly."""
        payment_data["metadata"] = {
            "order_id": "ORD_001",
            "customer_name": "John Doe",
            "service_type": "haircut",
            "nested": {"key": "value"},
        }
        payment = Payment(**payment_data)
        payment.save()

        retrieved = Payment.objects.get(id=payment.id)
        assert retrieved.metadata == payment_data["metadata"]
        assert retrieved.metadata["nested"]["key"] == "value"

    def test_payment_query_by_reference(self, payment_data):
        """Test querying payment by reference."""
        payment = Payment(**payment_data)
        payment.save()

        retrieved = Payment.objects.get(reference="PSK_REF_12345", tenant_id=payment.tenant_id)
        assert retrieved.id == payment.id

    def test_payment_query_by_customer(self, payment_data):
        """Test querying payments by customer."""
        payment1 = Payment(**payment_data)
        payment1.save()

        payment_data["reference"] = "PSK_REF_12346"
        payment2 = Payment(**payment_data)
        payment2.save()

        payments = Payment.objects(
            tenant_id=payment_data["tenant_id"],
            customer_id=payment_data["customer_id"]
        )
        assert len(payments) == 2

    def test_payment_query_by_status(self, payment_data):
        """Test querying payments by status."""
        payment1 = Payment(**payment_data)
        payment1.save()

        payment_data["reference"] = "PSK_REF_12346"
        payment_data["status"] = "success"
        payment2 = Payment(**payment_data)
        payment2.save()

        pending = Payment.objects(
            tenant_id=payment_data["tenant_id"],
            status="pending"
        )
        assert len(pending) == 1

        success = Payment.objects(
            tenant_id=payment_data["tenant_id"],
            status="success"
        )
        assert len(success) == 1

    def test_payment_indexes(self):
        """Test payment indexes are created."""
        indexes = Payment._get_collection().index_information()
        index_names = list(indexes.keys())

        # Check for expected indexes
        assert any("tenant_id" in str(idx) for idx in index_names)
        assert any("reference" in str(idx) for idx in index_names)
        assert any("customer_id" in str(idx) for idx in index_names)
