"""Property-based tests for payment idempotence."""

import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings, HealthCheck
from bson import ObjectId
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.services.payment_service import PaymentService
from app.context import set_tenant_id


# Strategies for generating test data
@st.composite
def idempotency_key_data(draw):
    """Generate valid idempotency key test data."""
    key_length = draw(st.integers(min_value=10, max_value=50))
    key = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
        min_size=key_length,
        max_size=key_length
    ))
    return {"idempotency_key": key}


@st.composite
def payment_amounts(draw):
    """Generate valid payment amounts."""
    amount = draw(st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("1000000.00"),
        places=2
    ))
    return amount


class TestPaymentIdempotenceProperties:
    """Property-based tests for payment idempotence."""

    @pytest.fixture(autouse=True)
    def setup(self, clear_db):
        """Set up test fixtures."""
        self.tenant_id = ObjectId()
        set_tenant_id(str(self.tenant_id))
        self.payment_service = PaymentService()

    @given(idempotency_key_data(), payment_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_duplicate_payment_returns_existing(self, key_data, amount):
        """
        **Validates: Requirements 6.2**
        
        Property: Duplicate payments with same idempotency_key return existing payment.
        
        For any payment with idempotency_key:
        - First call creates new payment
        - Second call with same idempotency_key returns existing payment
        - Both calls return same payment_id
        - No duplicate payment is created
        """
        # Create test customer and invoice
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
        )
        customer.save()

        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            amount=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="draft",
        )
        invoice.save()

        # First payment initialization
        result1 = self.payment_service.initialize_payment(
            amount=amount,
            customer_id=str(customer.id),
            invoice_id=str(invoice.id),
            email=customer.email,
            idempotency_key=key_data["idempotency_key"],
        )

        # Second payment initialization with same idempotency_key
        result2 = self.payment_service.initialize_payment(
            amount=amount,
            customer_id=str(customer.id),
            invoice_id=str(invoice.id),
            email=customer.email,
            idempotency_key=key_data["idempotency_key"],
        )

        # Verify both calls return same payment_id
        assert result1["payment_id"] == result2["payment_id"]
        assert result1["reference"] == result2["reference"]

        # Verify only one payment was created
        payments = Payment.objects(
            tenant_id=self.tenant_id,
            idempotency_key=key_data["idempotency_key"]
        )
        assert payments.count() == 1

    @given(idempotency_key_data(), payment_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_different_idempotency_keys_create_different_payments(self, key_data, amount):
        """
        **Validates: Requirements 6.2**
        
        Property: Different idempotency_keys create different payments.
        
        For any two payments with different idempotency_keys:
        - Each call creates a new payment
        - Payment IDs are different
        - References are different
        - Both payments exist in database
        """
        # Create test customer and invoice
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
        )
        customer.save()

        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            amount=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="draft",
        )
        invoice.save()

        # First payment with key1
        key1 = key_data["idempotency_key"]
        result1 = self.payment_service.initialize_payment(
            amount=amount,
            customer_id=str(customer.id),
            invoice_id=str(invoice.id),
            email=customer.email,
            idempotency_key=key1,
        )

        # Second payment with key2
        key2 = key1 + "_different"
        result2 = self.payment_service.initialize_payment(
            amount=amount,
            customer_id=str(customer.id),
            invoice_id=str(invoice.id),
            email=customer.email,
            idempotency_key=key2,
        )

        # Verify different payment_ids and references
        assert result1["payment_id"] != result2["payment_id"]
        assert result1["reference"] != result2["reference"]

        # Verify both payments exist
        payment1 = Payment.objects(
            tenant_id=self.tenant_id,
            idempotency_key=key1
        ).first()
        payment2 = Payment.objects(
            tenant_id=self.tenant_id,
            idempotency_key=key2
        ).first()
        assert payment1 is not None
        assert payment2 is not None

    @given(idempotency_key_data())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_payment_without_idempotency_key_always_creates_new(self, key_data):
        """
        **Validates: Requirements 6.2**
        
        Property: Payments without idempotency_key always create new payment.
        
        For any payment without idempotency_key:
        - Each call creates a new payment
        - Payment IDs are different
        - References are different
        """
        # Create test customer and invoice
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
        )
        customer.save()

        amount = Decimal("1000.00")
        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            amount=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="draft",
        )
        invoice.save()

        # First payment without idempotency_key
        result1 = self.payment_service.initialize_payment(
            amount=amount,
            customer_id=str(customer.id),
            invoice_id=str(invoice.id),
            email=customer.email,
            idempotency_key=None,
        )

        # Second payment without idempotency_key
        result2 = self.payment_service.initialize_payment(
            amount=amount,
            customer_id=str(customer.id),
            invoice_id=str(invoice.id),
            email=customer.email,
            idempotency_key=None,
        )

        # Verify different payment_ids and references
        assert result1["payment_id"] != result2["payment_id"]
        assert result1["reference"] != result2["reference"]

    @given(idempotency_key_data(), payment_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_idempotency_key_is_tenant_scoped(self, key_data, amount):
        """
        **Validates: Requirements 6.2**
        
        Property: Idempotency keys are scoped to tenant.
        
        For any idempotency_key:
        - Same key in different tenants creates different payments
        - Payments are isolated by tenant
        """
        # Create first tenant and payment
        tenant1_id = self.tenant_id
        set_tenant_id(str(tenant1_id))

        customer1 = Customer(
            tenant_id=tenant1_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
        )
        customer1.save()

        invoice1 = Invoice(
            tenant_id=tenant1_id,
            customer_id=customer1.id,
            amount=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="draft",
        )
        invoice1.save()

        result1 = self.payment_service.initialize_payment(
            amount=amount,
            customer_id=str(customer1.id),
            invoice_id=str(invoice1.id),
            email=customer1.email,
            idempotency_key=key_data["idempotency_key"],
        )

        # Create second tenant and payment with same idempotency_key
        tenant2_id = ObjectId()
        set_tenant_id(str(tenant2_id))

        customer2 = Customer(
            tenant_id=tenant2_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
        )
        customer2.save()

        invoice2 = Invoice(
            tenant_id=tenant2_id,
            customer_id=customer2.id,
            amount=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="draft",
        )
        invoice2.save()

        result2 = self.payment_service.initialize_payment(
            amount=amount,
            customer_id=str(customer2.id),
            invoice_id=str(invoice2.id),
            email=customer2.email,
            idempotency_key=key_data["idempotency_key"],
        )

        # Verify different payment_ids (different tenants)
        assert result1["payment_id"] != result2["payment_id"]

        # Verify payments are in different tenants
        payment1 = Payment.objects(id=ObjectId(result1["payment_id"])).first()
        payment2 = Payment.objects(id=ObjectId(result2["payment_id"])).first()
        assert payment1.tenant_id != payment2.tenant_id
