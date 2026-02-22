"""Property-based tests for refund validation."""

import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings, HealthCheck
from bson import ObjectId
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.services.refund_service import RefundService
from app.context import set_tenant_id


# Strategies for generating test data
@st.composite
def refund_amounts(draw):
    """Generate valid refund amounts."""
    amount = draw(st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("1000000.00"),
        places=2
    ))
    return amount


@st.composite
def refund_reasons(draw):
    """Generate valid refund reasons."""
    reason = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -",
        min_size=5,
        max_size=100
    ))
    return reason


class TestRefundValidationProperties:
    """Property-based tests for refund validation."""

    @pytest.fixture(autouse=True)
    def setup(self, clear_db):
        """Set up test fixtures."""
        self.tenant_id = ObjectId()
        set_tenant_id(str(self.tenant_id))
        self.refund_service = RefundService()

    @given(refund_amounts(), refund_amounts(), refund_reasons())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_refund_amount_not_exceeds_payment_amount(self, payment_amount, refund_amount, reason):
        """
        **Validates: Requirements 6.4**
        
        Property 24: Refund Amount Validation
        
        For any refund request, the refund amount SHALL not exceed the original payment amount.
        
        This property verifies that:
        - Refund amount <= payment amount is accepted
        - Refund amount > payment amount is rejected
        - Refund amount = payment amount is accepted (full refund)
        - Refund amount = 0 is rejected
        """
        # Create test customer
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
        )
        customer.save()

        # Create test invoice
        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            amount=payment_amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=payment_amount,
            status="draft",
        )
        invoice.save()

        # Create test payment with success status
        payment = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice.id,
            amount=payment_amount,
            status="success",
            reference=f"ref_{ObjectId()}",
            gateway="paystack",
        )
        payment.save()

        # Test refund validation
        if refund_amount > payment_amount:
            # Refund amount exceeds payment amount - should fail
            with pytest.raises(ValueError) as exc_info:
                self.refund_service.create_refund(
                    payment_id=str(payment.id),
                    amount=refund_amount,
                    reason=reason,
                )
            assert "exceeds original payment amount" in str(exc_info.value)
        elif refund_amount <= 0:
            # Refund amount is zero or negative - should fail
            with pytest.raises(ValueError) as exc_info:
                self.refund_service.create_refund(
                    payment_id=str(payment.id),
                    amount=refund_amount,
                    reason=reason,
                )
            assert "must be greater than 0" in str(exc_info.value)
        else:
            # Refund amount is valid (0 < refund_amount <= payment_amount)
            # Should succeed
            result = self.refund_service.create_refund(
                payment_id=str(payment.id),
                amount=refund_amount,
                reason=reason,
            )
            
            # Verify refund was created
            assert result["refund_id"] is not None
            assert result["payment_id"] == str(payment.id)
            assert result["amount"] == refund_amount
            assert result["reason"] == reason
            assert result["status"] == "pending"
            
            # Verify refund exists in database
            refund = Refund.objects(
                tenant_id=self.tenant_id,
                id=ObjectId(result["refund_id"])
            ).first()
            assert refund is not None
            assert refund.amount == refund_amount
            assert refund.status == "pending"

    @given(refund_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_refund_requires_success_payment(self, refund_amount):
        """
        **Validates: Requirements 6.4**
        
        Property: Refund can only be created for successful payments.
        
        For any refund request:
        - Payment must be in success status
        - Refund for pending payment should fail
        - Refund for failed payment should fail
        - Refund for cancelled payment should fail
        """
        # Skip if refund amount is invalid
        if refund_amount <= 0 or refund_amount > Decimal("1000000.00"):
            return

        # Create test customer
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
        )
        customer.save()

        # Create test invoice
        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            amount=refund_amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=refund_amount,
            status="draft",
        )
        invoice.save()

        # Test with different payment statuses
        for status in ["pending", "failed", "cancelled"]:
            payment = Payment(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                invoice_id=invoice.id,
                amount=refund_amount,
                status=status,
                reference=f"ref_{ObjectId()}",
                gateway="paystack",
            )
            payment.save()

            # Attempt to create refund - should fail
            with pytest.raises(ValueError) as exc_info:
                self.refund_service.create_refund(
                    payment_id=str(payment.id),
                    amount=refund_amount,
                    reason="Test refund",
                )
            assert "success status" in str(exc_info.value)

    @given(refund_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_no_duplicate_refund_for_same_payment(self, refund_amount):
        """
        **Validates: Requirements 6.4**
        
        Property: Only one active refund per payment.
        
        For any payment:
        - First refund request succeeds
        - Second refund request for same payment fails
        - Prevents duplicate refunds
        """
        # Skip if refund amount is invalid
        if refund_amount <= 0 or refund_amount > Decimal("1000000.00"):
            return

        # Create test customer
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
        )
        customer.save()

        # Create test invoice
        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            amount=refund_amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=refund_amount,
            status="draft",
        )
        invoice.save()

        # Create test payment with success status
        payment = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice.id,
            amount=refund_amount,
            status="success",
            reference=f"ref_{ObjectId()}",
            gateway="paystack",
        )
        payment.save()

        # First refund should succeed
        result1 = self.refund_service.create_refund(
            payment_id=str(payment.id),
            amount=refund_amount,
            reason="First refund",
        )
        assert result1["refund_id"] is not None
        assert result1["status"] == "pending"

        # Second refund should fail
        with pytest.raises(ValueError) as exc_info:
            self.refund_service.create_refund(
                payment_id=str(payment.id),
                amount=refund_amount,
                reason="Second refund",
            )
        assert "already exists" in str(exc_info.value)
