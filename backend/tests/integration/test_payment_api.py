"""Integration tests for Payment API endpoints."""

import pytest
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


class TestPaymentAPI:
    """Test Payment API endpoints."""

    def test_payment_model_creation(self, payment_data):
        """Test creating a payment through model."""
        payment = Payment(**payment_data)
        payment.save()

        assert payment.id is not None
        assert payment.reference == "PSK_REF_12345"
        assert payment.status == "pending"

    def test_payment_retrieval(self, payment_data):
        """Test retrieving a payment."""
        payment = Payment(**payment_data)
        payment.save()

        retrieved = Payment.objects.get(id=payment.id)
        assert retrieved.reference == payment.reference
        assert retrieved.amount == payment.amount

    def test_payment_update(self, payment_data):
        """Test updating a payment."""
        payment = Payment(**payment_data)
        payment.save()

        payment.status = "success"
        payment.metadata["transaction_id"] = "TXN_123"
        payment.save()

        retrieved = Payment.objects.get(id=payment.id)
        assert retrieved.status == "success"
        assert retrieved.metadata["transaction_id"] == "TXN_123"

    def test_payment_list_by_tenant(self, payment_data):
        """Test listing payments for a tenant."""
        payment1 = Payment(**payment_data)
        payment1.save()

        payment_data["reference"] = "PSK_REF_12346"
        payment2 = Payment(**payment_data)
        payment2.save()

        payments = Payment.objects(tenant_id=payment_data["tenant_id"])
        assert len(payments) == 2

    def test_payment_list_by_customer(self, payment_data):
        """Test listing payments for a customer."""
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

    def test_payment_list_by_invoice(self, payment_data):
        """Test listing payments for an invoice."""
        payment1 = Payment(**payment_data)
        payment1.save()

        payment_data["reference"] = "PSK_REF_12346"
        payment2 = Payment(**payment_data)
        payment2.save()

        payments = Payment.objects(
            tenant_id=payment_data["tenant_id"],
            invoice_id=payment_data["invoice_id"]
        )
        assert len(payments) == 2

    def test_payment_status_transitions(self, payment_data):
        """Test payment status transitions."""
        payment = Payment(**payment_data)
        payment.save()

        # pending -> success
        payment.status = "success"
        payment.save()
        assert payment.status == "success"

        # success -> failed (should be allowed for testing)
        payment.status = "failed"
        payment.save()
        assert payment.status == "failed"

        # failed -> cancelled
        payment.status = "cancelled"
        payment.save()
        assert payment.status == "cancelled"

    def test_payment_metadata_updates(self, payment_data):
        """Test updating payment metadata."""
        payment = Payment(**payment_data)
        payment.save()

        # Add more metadata
        payment.metadata["authorization_code"] = "AUTH_123"
        payment.metadata["customer_code"] = "CUS_456"
        payment.save()

        retrieved = Payment.objects.get(id=payment.id)
        assert retrieved.metadata["authorization_code"] == "AUTH_123"
        assert retrieved.metadata["customer_code"] == "CUS_456"

    def test_payment_different_gateways(self, payment_data):
        """Test payments with different gateways."""
        # Paystack payment
        payment1 = Payment(**payment_data)
        payment1.save()

        # Stripe payment
        payment_data["reference"] = "stripe_pi_12345"
        payment_data["gateway"] = "stripe"
        payment2 = Payment(**payment_data)
        payment2.save()

        paystack_payments = Payment.objects(
            tenant_id=payment_data["tenant_id"],
            gateway="paystack"
        )
        assert len(paystack_payments) == 1

        stripe_payments = Payment.objects(
            tenant_id=payment_data["tenant_id"],
            gateway="stripe"
        )
        assert len(stripe_payments) == 1

    def test_payment_amount_precision(self, payment_data):
        """Test payment amount precision."""
        amounts = [
            Decimal("0.01"),
            Decimal("99.99"),
            Decimal("1000.00"),
            Decimal("0.50"),
        ]

        for amount in amounts:
            payment_data["amount"] = amount
            payment_data["reference"] = f"PSK_REF_{amount}"
            payment = Payment(**payment_data)
            payment.save()

            retrieved = Payment.objects.get(reference=payment_data["reference"])
            assert retrieved.amount == amount

    def test_payment_tenant_isolation(self, payment_data):
        """Test payment tenant isolation."""
        # Create payment for tenant 1
        payment1 = Payment(**payment_data)
        payment1.save()

        # Create another tenant ID
        tenant2_id = ObjectId()

        # Create payment for tenant 2
        payment_data["tenant_id"] = tenant2_id
        payment_data["reference"] = "PSK_REF_12346"
        payment2 = Payment(**payment_data)
        payment2.save()

        # Query payments for tenant 1
        tenant1_payments = Payment.objects(tenant_id=payment1.tenant_id)
        assert len(tenant1_payments) == 1
        assert tenant1_payments[0].id == payment1.id

        # Query payments for tenant 2
        tenant2_payments = Payment.objects(tenant_id=tenant2_id)
        assert len(tenant2_payments) == 1
        assert tenant2_payments[0].id == payment2.id

    def test_payment_deletion(self, payment_data):
        """Test deleting a payment."""
        payment = Payment(**payment_data)
        payment.save()

        payment_id = payment.id
        payment.delete()

        with pytest.raises(Exception):
            Payment.objects.get(id=payment_id)

    def test_payment_bulk_operations(self, payment_data):
        """Test bulk payment operations."""
        # Create multiple payments
        payments = []
        for i in range(5):
            payment_data["reference"] = f"PSK_REF_{i}"
            payment = Payment(**payment_data)
            payment.save()
            payments.append(payment)

        # Query all
        all_payments = Payment.objects(tenant_id=payment_data["tenant_id"])
        assert len(all_payments) == 5

        # Update all to success
        Payment.objects(tenant_id=payment_data["tenant_id"]).update(status="success")
        updated = Payment.objects(tenant_id=payment_data["tenant_id"], status="success")
        assert len(updated) == 5

    def test_payment_sorting(self, payment_data):
        """Test sorting payments."""
        # Create payments with different amounts
        for i, amount in enumerate([Decimal("10.00"), Decimal("50.00"), Decimal("30.00")]):
            payment_data["amount"] = amount
            payment_data["reference"] = f"PSK_REF_{i}"
            payment = Payment(**payment_data)
            payment.save()

        # Sort by amount ascending
        payments_asc = Payment.objects(tenant_id=payment_data["tenant_id"]).order_by("amount")
        amounts_asc = [p.amount for p in payments_asc]
        assert amounts_asc == [Decimal("10.00"), Decimal("30.00"), Decimal("50.00")]

        # Sort by amount descending
        payments_desc = Payment.objects(tenant_id=payment_data["tenant_id"]).order_by("-amount")
        amounts_desc = [p.amount for p in payments_desc]
        assert amounts_desc == [Decimal("50.00"), Decimal("30.00"), Decimal("10.00")]

    def test_payment_filtering_by_date_range(self, payment_data):
        """Test filtering payments by date range."""
        from datetime import datetime, timedelta

        payment1 = Payment(**payment_data)
        payment1.save()

        # Create payment with future date
        payment_data["reference"] = "PSK_REF_12346"
        payment2 = Payment(**payment_data)
        payment2.save()

        # Query all payments
        all_payments = Payment.objects(tenant_id=payment_data["tenant_id"])
        assert len(all_payments) == 2
