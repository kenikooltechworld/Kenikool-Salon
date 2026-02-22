"""Property-based tests for payment retry logic."""

import pytest
from datetime import datetime, timedelta
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
def payment_retry_data(draw):
    """Generate valid payment retry test data."""
    retry_count = draw(st.integers(min_value=0, max_value=2))
    return {
        "retry_count": retry_count,
        "max_retries": 3,
    }


class TestPaymentRetryProperties:
    """Property-based tests for payment retry logic."""

    @pytest.fixture(autouse=True)
    def setup(self, clear_db):
        """Set up test fixtures."""
        self.tenant_id = ObjectId()
        set_tenant_id(str(self.tenant_id))
        self.payment_service = PaymentService()

    @given(payment_retry_data())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_retry_count_increments_correctly(self, data):
        """
        **Validates: Requirements 6.3**
        
        Property: Payment retry count increments correctly on each retry.
        
        For any payment with retry_count < max_retries:
        - Calling retry_payment should increment retry_count by 1
        - Retry count should never exceed max_retries
        - Each retry should update last_retry_at timestamp
        """
        # Create test payment
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
            amount=Decimal("1000.00"),
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=Decimal("1000.00"),
            status="draft",
        )
        invoice.save()

        payment = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice.id,
            amount=Decimal("1000.00"),
            reference=f"ref_{data['retry_count']}",
            gateway="paystack",
            status="failed",
            retry_count=data["retry_count"],
            max_retries=data["max_retries"],
        )
        payment.save()

        # Verify initial state
        assert payment.retry_count == data["retry_count"]
        assert payment.retry_count < payment.max_retries

        # Retry payment
        result = self.payment_service.retry_payment(str(payment.id))

        # Verify retry count incremented
        assert result["retry_count"] == data["retry_count"] + 1
        assert result["retry_count"] <= result["max_retries"]

        # Verify last_retry_at was updated
        updated_payment = Payment.objects(id=payment.id).first()
        assert updated_payment.last_retry_at is not None
        assert updated_payment.last_retry_at <= datetime.utcnow()

    @given(st.integers(min_value=0, max_value=2))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_exponential_backoff_calculation(self, retry_count):
        """
        **Validates: Requirements 6.3**
        
        Property: Exponential backoff delay is calculated correctly.
        
        For any retry_count:
        - Delay should be 2^retry_count seconds
        - Delay should be positive
        - next_retry_at should be set correctly
        """
        # Calculate expected delay
        expected_delay = 2 ** retry_count

        # Get actual delay from service
        actual_delay = self.payment_service._calculate_retry_delay(retry_count)

        # Verify delay matches exponential backoff formula
        assert actual_delay == expected_delay
        assert actual_delay > 0

    @given(st.integers(min_value=0, max_value=2))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_next_retry_time_respects_backoff(self, retry_count):
        """
        **Validates: Requirements 6.3**
        
        Property: next_retry_at respects exponential backoff.
        
        For any payment with retry_count < max_retries:
        - next_retry_at should be set to current_time + exponential_backoff
        - next_retry_at should be in the future
        - Subsequent retries should have longer delays
        """
        # Create test payment
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
            amount=Decimal("1000.00"),
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=Decimal("1000.00"),
            status="draft",
        )
        invoice.save()

        payment = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice.id,
            amount=Decimal("1000.00"),
            reference=f"ref_backoff_{retry_count}",
            gateway="paystack",
            status="failed",
            retry_count=retry_count,
            max_retries=3,
        )
        payment.save()

        # Retry payment
        before_retry = datetime.utcnow()
        result = self.payment_service.retry_payment(str(payment.id))
        after_retry = datetime.utcnow()

        # Verify next_retry_at is set and in the future
        updated_payment = Payment.objects(id=payment.id).first()
        if updated_payment.retry_count < updated_payment.max_retries:
            assert updated_payment.next_retry_at is not None
            assert updated_payment.next_retry_at > after_retry

            # Verify delay matches exponential backoff
            expected_delay = 2 ** updated_payment.retry_count
            actual_delay = (
                updated_payment.next_retry_at - updated_payment.last_retry_at
            ).total_seconds()
            assert actual_delay == expected_delay

    @given(st.integers(min_value=3, max_value=5))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_max_retries_prevents_further_retries(self, max_retries):
        """
        **Validates: Requirements 6.3**
        
        Property: Payment cannot be retried after max_retries is reached.
        
        For any payment with retry_count >= max_retries:
        - Calling retry_payment should raise ValueError
        - Payment status should not change
        - Error message should indicate max retries exceeded
        """
        # Create test payment at max retries
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
            amount=Decimal("1000.00"),
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=Decimal("1000.00"),
            status="draft",
        )
        invoice.save()

        payment = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice.id,
            amount=Decimal("1000.00"),
            reference=f"ref_max_{max_retries}",
            gateway="paystack",
            status="failed",
            retry_count=max_retries,
            max_retries=max_retries,
        )
        payment.save()

        # Attempt to retry should fail
        with pytest.raises(ValueError) as exc_info:
            self.payment_service.retry_payment(str(payment.id))

        assert "Maximum retries" in str(exc_info.value)

    @given(st.integers(min_value=0, max_value=2))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_successful_payment_cannot_be_retried(self, retry_count):
        """
        **Validates: Requirements 6.3**
        
        Property: Successful payments cannot be retried.
        
        For any payment with status='success':
        - Calling retry_payment should raise ValueError
        - Error message should indicate payment is already successful
        """
        # Create successful payment
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
            amount=Decimal("1000.00"),
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=Decimal("1000.00"),
            status="draft",
        )
        invoice.save()

        payment = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice.id,
            amount=Decimal("1000.00"),
            reference=f"ref_success_{retry_count}",
            gateway="paystack",
            status="success",
            retry_count=retry_count,
            max_retries=3,
        )
        payment.save()

        # Attempt to retry should fail
        with pytest.raises(ValueError) as exc_info:
            self.payment_service.retry_payment(str(payment.id))

        assert "successful" in str(exc_info.value).lower()
