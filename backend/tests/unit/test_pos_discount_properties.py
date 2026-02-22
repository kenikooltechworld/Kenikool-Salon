"""Property-based tests for POS discount calculations."""

import pytest
from hypothesis import given, strategies as st
from decimal import Decimal
from bson import ObjectId
from app.models.discount import Discount
from app.services.discount_service import DiscountService


class TestDiscountProperties:
    """Property-based tests for discount service."""

    @given(
        discount_value=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("100"), places=2),
        subtotal=st.decimals(min_value=Decimal("1"), max_value=Decimal("10000"), places=2),
    )
    def test_percentage_discount_calculation(self, discount_value, subtotal):
        """
        **Property 6: Discount Calculation Accuracy**
        **Validates: Requirements 77.1**

        For any transaction with applied discount, the discount amount SHALL be
        calculated correctly based on discount type and value.
        """
        tenant_id = ObjectId()

        # Create percentage discount
        discount = Discount(
            tenant_id=tenant_id,
            discount_code="PERCENT-TEST",
            discount_type="percentage",
            discount_value=discount_value,
            applicable_to="transaction",
            active=True,
        )

        # Calculate discount amount
        calculated_amount = DiscountService.calculate_discount_amount(discount, subtotal)

        # Verify calculation
        expected_amount = (subtotal * discount_value) / Decimal("100")
        assert calculated_amount == expected_amount
        assert calculated_amount >= Decimal("0")
        assert calculated_amount <= subtotal

    @given(
        discount_value=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000"), places=2),
        subtotal=st.decimals(min_value=Decimal("1"), max_value=Decimal("10000"), places=2),
    )
    def test_fixed_discount_calculation(self, discount_value, subtotal):
        """
        **Property 6: Discount Calculation Accuracy**
        **Validates: Requirements 77.1**

        For any transaction with applied discount, the discount amount SHALL be
        calculated correctly based on discount type and value.
        """
        tenant_id = ObjectId()

        # Create fixed discount
        discount = Discount(
            tenant_id=tenant_id,
            discount_code="FIXED-TEST",
            discount_type="fixed",
            discount_value=discount_value,
            applicable_to="transaction",
            active=True,
        )

        # Calculate discount amount
        calculated_amount = DiscountService.calculate_discount_amount(discount, subtotal)

        # Verify calculation - fixed discount should not exceed subtotal
        expected_amount = min(discount_value, subtotal)
        assert calculated_amount == expected_amount
        assert calculated_amount >= Decimal("0")
        assert calculated_amount <= subtotal

    @given(
        discount_value=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("100"), places=2),
        max_discount=st.decimals(min_value=Decimal("1"), max_value=Decimal("500"), places=2),
        subtotal=st.decimals(min_value=Decimal("1"), max_value=Decimal("10000"), places=2),
    )
    def test_discount_with_max_limit(self, discount_value, max_discount, subtotal):
        """
        **Property 6: Discount Calculation Accuracy**
        **Validates: Requirements 77.1**

        For any transaction with applied discount, the discount amount SHALL be
        calculated correctly based on discount type and value.
        """
        tenant_id = ObjectId()

        # Create discount with max limit
        discount = Discount(
            tenant_id=tenant_id,
            discount_code="MAX-LIMIT-TEST",
            discount_type="percentage",
            discount_value=discount_value,
            max_discount=max_discount,
            applicable_to="transaction",
            active=True,
        )

        # Calculate discount amount
        calculated_amount = DiscountService.calculate_discount_amount(discount, subtotal)

        # Verify calculation respects max limit
        expected_amount = (subtotal * discount_value) / Decimal("100")
        expected_amount = min(expected_amount, max_discount)
        expected_amount = min(expected_amount, subtotal)

        assert calculated_amount == expected_amount
        assert calculated_amount <= max_discount
        assert calculated_amount <= subtotal
