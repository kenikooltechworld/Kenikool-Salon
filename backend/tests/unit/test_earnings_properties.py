"""Property-based tests for staff earnings calculations.

This module tests the core properties of staff earnings:
- Property 4: Earnings Calculation Accuracy - Verify total equals sum of individual commissions

Validates: Requirements 5.2, 5.3, 5.4
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta, date
from decimal import Decimal
from bson import ObjectId

from app.models.staff_commission import StaffCommission
from app.models.transaction import Transaction, TransactionItem
from app.services.commission_service import CommissionService


# Strategy generators for property-based testing
@st.composite
def commission_amounts(draw):
    """Generate valid commission amounts."""
    return draw(st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("1000.00"),
        places=2
    ))


@st.composite
def commission_rates(draw):
    """Generate valid commission rates for percentage calculations."""
    return draw(st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("50.00"),
        places=2
    ))


@st.composite
def transaction_amounts(draw):
    """Generate valid transaction amounts."""
    return draw(st.decimals(
        min_value=Decimal("1.00"),
        max_value=Decimal("5000.00"),
        places=2
    ))


@st.composite
def commission_data_list(draw):
    """Generate a list of commission data for testing."""
    num_commissions = draw(st.integers(min_value=1, max_value=10))
    commissions = []
    
    for _ in range(num_commissions):
        commission_type = draw(st.sampled_from(["percentage", "fixed"]))
        
        if commission_type == "percentage":
            transaction_amount = draw(transaction_amounts())
            commission_rate = draw(commission_rates())
            commission_amount = (transaction_amount * commission_rate) / Decimal("100")
        else:
            transaction_amount = draw(transaction_amounts())
            commission_amount = draw(commission_amounts())
            commission_rate = commission_amount  # For fixed type, rate equals amount
        
        commissions.append({
            "transaction_id": ObjectId(),
            "transaction_amount": transaction_amount,
            "commission_amount": commission_amount,
            "commission_rate": commission_rate,
            "commission_type": commission_type,
            "calculated_at": datetime.utcnow() - timedelta(days=draw(st.integers(0, 30))),
        })
    
    return commissions


@st.composite
def date_ranges(draw):
    """Generate valid date ranges for filtering."""
    start_date = draw(st.dates(
        min_value=date(2024, 1, 1),
        max_value=date(2024, 12, 31)
    ))
    end_date = draw(st.dates(
        min_value=start_date,
        max_value=start_date + timedelta(days=90)
    ))
    return start_date, end_date


class TestEarningsCalculationAccuracy:
    """Property-based tests for earnings calculation accuracy.
    
    **Property 4: Earnings Calculation Accuracy**
    Verify total earnings equals sum of individual commission amounts
    
    Validates: Requirements 5.2, 5.3, 5.4
    """

    @given(
        commissions_data=commission_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_total_earnings_equals_sum_of_commissions(
        self,
        commissions_data,
    ):
        """
        **Property 4: Earnings Calculation Accuracy - Total Calculation**
        
        For any staff member, the total earnings displayed SHALL equal the sum
        of all individual commission amounts for that staff member in the
        specified period.
        
        Validates: Requirements 5.2, 5.3, 5.4
        """
        tenant_id = ObjectId()
        staff_id = ObjectId()
        
        # Create commission records
        created_commissions = []
        expected_total = Decimal("0")
        
        for comm_data in commissions_data:
            commission = StaffCommission(
                tenant_id=tenant_id,
                staff_id=staff_id,
                transaction_id=comm_data["transaction_id"],
                commission_amount=comm_data["commission_amount"],
                commission_rate=comm_data["commission_rate"],
                commission_type=comm_data["commission_type"],
                calculated_at=comm_data["calculated_at"],
            )
            commission.save()
            created_commissions.append(commission)
            expected_total += comm_data["commission_amount"]
        
        # Calculate total using service method
        calculated_total = CommissionService.calculate_total_commission(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        # Verify total equals sum of individual commissions
        assert calculated_total == expected_total, \
            f"Total earnings {calculated_total} should equal sum of commissions {expected_total}"
        
        # Verify individual commission amounts are preserved
        fetched_commissions = StaffCommission.objects(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        fetched_total = sum(c.commission_amount for c in fetched_commissions)
        assert fetched_total == expected_total, \
            f"Fetched total {fetched_total} should equal expected total {expected_total}"
        
        # Cleanup
        for commission in created_commissions:
            commission.delete()

    @given(
        commissions_data=commission_data_list(),
        date_range=date_ranges(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=15,
        deadline=2000
    )
    def test_date_range_filtering_maintains_accuracy(
        self,
        commissions_data,
        date_range,
    ):
        """
        **Property 4: Earnings Calculation Accuracy - Date Range Filtering**
        
        For any date range filter applied to earnings, the total SHALL equal
        the sum of individual commissions within that date range, and no
        commissions outside the range SHALL be included.
        
        Validates: Requirements 5.4
        """
        tenant_id = ObjectId()
        staff_id = ObjectId()
        
        start_date, end_date = date_range
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Create commission records with varying dates
        created_commissions = []
        expected_total_in_range = Decimal("0")
        expected_total_outside_range = Decimal("0")
        
        for i, comm_data in enumerate(commissions_data):
            # Alternate between in-range and out-of-range dates
            if i % 2 == 0:
                # In range
                calc_date = start_datetime + timedelta(
                    days=(end_datetime - start_datetime).days // 2
                )
                expected_total_in_range += comm_data["commission_amount"]
            else:
                # Out of range (before start)
                calc_date = start_datetime - timedelta(days=10)
                expected_total_outside_range += comm_data["commission_amount"]
            
            commission = StaffCommission(
                tenant_id=tenant_id,
                staff_id=staff_id,
                transaction_id=comm_data["transaction_id"],
                commission_amount=comm_data["commission_amount"],
                commission_rate=comm_data["commission_rate"],
                commission_type=comm_data["commission_type"],
                calculated_at=calc_date,
            )
            commission.save()
            created_commissions.append(commission)
        
        # Calculate total with date range filter
        calculated_total = CommissionService.calculate_total_commission(
            tenant_id=tenant_id,
            staff_id=staff_id,
            start_date=start_datetime,
            end_date=end_datetime,
        )
        
        # Verify filtered total equals sum of commissions in range
        assert calculated_total == expected_total_in_range, \
            f"Filtered total {calculated_total} should equal in-range sum {expected_total_in_range}"
        
        # Verify total without filter includes all commissions
        total_without_filter = CommissionService.calculate_total_commission(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        expected_total_all = expected_total_in_range + expected_total_outside_range
        assert total_without_filter == expected_total_all, \
            f"Unfiltered total {total_without_filter} should equal all commissions {expected_total_all}"
        
        # Cleanup
        for commission in created_commissions:
            commission.delete()

    @given(
        percentage_commissions=st.lists(
            st.tuples(transaction_amounts(), commission_rates()),
            min_size=1,
            max_size=5
        ),
        fixed_commissions=st.lists(
            st.tuples(transaction_amounts(), commission_amounts()),
            min_size=1,
            max_size=5
        ),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=10,
        deadline=2000
    )
    def test_commission_breakdown_calculations_are_correct(
        self,
        percentage_commissions,
        fixed_commissions,
    ):
        """
        **Property 4: Earnings Calculation Accuracy - Commission Breakdown**
        
        For any mix of percentage and fixed commissions, the breakdown
        calculations SHALL be mathematically correct, and the sum of
        breakdown totals SHALL equal the overall total.
        
        Validates: Requirements 5.3
        """
        tenant_id = ObjectId()
        staff_id = ObjectId()
        
        created_commissions = []
        expected_percentage_total = Decimal("0")
        expected_fixed_total = Decimal("0")
        
        # Create percentage commissions
        for transaction_amount, commission_rate in percentage_commissions:
            commission_amount = (transaction_amount * commission_rate) / Decimal("100")
            
            commission = StaffCommission(
                tenant_id=tenant_id,
                staff_id=staff_id,
                transaction_id=ObjectId(),
                commission_amount=commission_amount,
                commission_rate=commission_rate,
                commission_type="percentage",
                calculated_at=datetime.utcnow(),
            )
            commission.save()
            created_commissions.append(commission)
            expected_percentage_total += commission_amount
        
        # Create fixed commissions
        for transaction_amount, commission_amount in fixed_commissions:
            commission = StaffCommission(
                tenant_id=tenant_id,
                staff_id=staff_id,
                transaction_id=ObjectId(),
                commission_amount=commission_amount,
                commission_rate=commission_amount,  # For fixed, rate equals amount
                commission_type="fixed",
                calculated_at=datetime.utcnow(),
            )
            commission.save()
            created_commissions.append(commission)
            expected_fixed_total += commission_amount
        
        # Fetch and calculate breakdown
        all_commissions = StaffCommission.objects(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        percentage_total = sum(
            c.commission_amount for c in all_commissions
            if c.commission_type == "percentage"
        )
        
        fixed_total = sum(
            c.commission_amount for c in all_commissions
            if c.commission_type == "fixed"
        )
        
        # Verify breakdown calculations
        assert percentage_total == expected_percentage_total, \
            f"Percentage total {percentage_total} should equal expected {expected_percentage_total}"
        
        assert fixed_total == expected_fixed_total, \
            f"Fixed total {fixed_total} should equal expected {expected_fixed_total}"
        
        # Verify breakdown sum equals overall total
        breakdown_sum = percentage_total + fixed_total
        overall_total = CommissionService.calculate_total_commission(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        assert breakdown_sum == overall_total, \
            f"Breakdown sum {breakdown_sum} should equal overall total {overall_total}"
        
        # Cleanup
        for commission in created_commissions:
            commission.delete()

    @given(
        commission_amount=commission_amounts(),
        commission_rate=commission_rates(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=1000
    )
    def test_single_commission_calculation_accuracy(
        self,
        commission_amount,
        commission_rate,
    ):
        """
        **Property 4: Earnings Calculation Accuracy - Single Commission**
        
        For any single commission calculation, the commission amount SHALL
        be calculated correctly based on the commission type and rate.
        
        Validates: Requirements 5.2
        """
        tenant_id = ObjectId()
        staff_id = ObjectId()
        customer_id = ObjectId()
        
        # Test percentage commission
        transaction_amount = Decimal("100.00")
        
        # Create transaction
        transaction = Transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items=[
                TransactionItem(
                    item_type="service",
                    item_id=str(ObjectId()),
                    item_name="Test Service",
                    quantity=1,
                    unit_price=transaction_amount,
                    tax_rate=Decimal("0"),
                    discount_rate=Decimal("0"),
                )
            ],
            subtotal=transaction_amount,
            tax_amount=Decimal("0"),
            discount_amount=Decimal("0"),
            total=transaction_amount,
            payment_method="cash",
            status="completed",
        )
        transaction.save()
        
        # Calculate percentage commission
        percentage_commission = CommissionService.calculate_commission(
            tenant_id=tenant_id,
            transaction_id=transaction.id,
            staff_id=staff_id,
            commission_rate=commission_rate,
            commission_type="percentage",
        )
        
        expected_percentage_amount = (transaction_amount * commission_rate) / Decimal("100")
        assert percentage_commission.commission_amount == expected_percentage_amount, \
            f"Percentage commission {percentage_commission.commission_amount} should equal {expected_percentage_amount}"
        
        # Calculate fixed commission
        fixed_commission = CommissionService.calculate_commission(
            tenant_id=tenant_id,
            transaction_id=transaction.id,
            staff_id=staff_id,
            commission_rate=commission_amount,
            commission_type="fixed",
        )
        
        assert fixed_commission.commission_amount == commission_amount, \
            f"Fixed commission {fixed_commission.commission_amount} should equal {commission_amount}"
        
        # Cleanup
        percentage_commission.delete()
        fixed_commission.delete()
        transaction.delete()

    def test_zero_commissions_total_is_zero(self):
        """
        **Property 4: Earnings Calculation Accuracy - Zero Case**
        
        For any staff member with no commissions, the total earnings SHALL
        be zero, and breakdown calculations SHALL handle empty data correctly.
        
        Validates: Requirements 5.2
        """
        tenant_id = ObjectId()
        staff_id = ObjectId()
        
        # Calculate total for staff with no commissions
        total = CommissionService.calculate_total_commission(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        assert total == Decimal("0"), f"Total for staff with no commissions should be 0, got {total}"
        
        # Verify list is empty
        commissions, count = CommissionService.list_staff_commissions(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        assert len(commissions) == 0, "Should have no commissions"
        assert count == 0, "Count should be 0"

    @given(
        num_commissions=st.integers(min_value=1, max_value=5),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=10,
        deadline=2000
    )
    def test_commission_persistence_maintains_accuracy(
        self,
        num_commissions,
    ):
        """
        **Property 4: Earnings Calculation Accuracy - Persistence**
        
        For any set of commissions, after saving and retrieving from the
        database, the commission amounts SHALL remain accurate and the
        total SHALL be preserved.
        
        Validates: Requirements 5.2
        """
        tenant_id = ObjectId()
        staff_id = ObjectId()
        
        # Create commissions with known amounts
        created_commissions = []
        expected_total = Decimal("0")
        
        for i in range(num_commissions):
            amount = Decimal(f"{(i + 1) * 10}.50")  # 10.50, 20.50, 30.50, etc.
            
            commission = StaffCommission(
                tenant_id=tenant_id,
                staff_id=staff_id,
                transaction_id=ObjectId(),
                commission_amount=amount,
                commission_rate=Decimal("10.00"),
                commission_type="percentage",
                calculated_at=datetime.utcnow(),
            )
            commission.save()
            created_commissions.append(commission)
            expected_total += amount
        
        # Retrieve and verify persistence
        fetched_commissions = StaffCommission.objects(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        # Verify count
        assert fetched_commissions.count() == num_commissions, \
            f"Should have {num_commissions} commissions, got {fetched_commissions.count()}"
        
        # Verify individual amounts are preserved
        fetched_amounts = [c.commission_amount for c in fetched_commissions]
        created_amounts = [c.commission_amount for c in created_commissions]
        
        assert sorted(fetched_amounts) == sorted(created_amounts), \
            "Fetched amounts should match created amounts"
        
        # Verify total is preserved
        fetched_total = sum(fetched_amounts)
        assert fetched_total == expected_total, \
            f"Fetched total {fetched_total} should equal expected {expected_total}"
        
        # Cleanup
        for commission in created_commissions:
            commission.delete()


class TestEarningsEdgeCases:
    """Test edge cases for earnings calculations."""

    def test_very_small_commission_amounts(self):
        """Test handling of very small commission amounts (precision)."""
        tenant_id = ObjectId()
        staff_id = ObjectId()
        
        # Create commission with very small amount
        small_amount = Decimal("0.01")
        
        commission = StaffCommission(
            tenant_id=tenant_id,
            staff_id=staff_id,
            transaction_id=ObjectId(),
            commission_amount=small_amount,
            commission_rate=Decimal("0.01"),
            commission_type="percentage",
            calculated_at=datetime.utcnow(),
        )
        commission.save()
        
        # Verify precision is maintained
        total = CommissionService.calculate_total_commission(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        assert total == small_amount, f"Small amount precision should be maintained: {total} vs {small_amount}"
        
        # Cleanup
        commission.delete()

    def test_large_commission_amounts(self):
        """Test handling of large commission amounts."""
        tenant_id = ObjectId()
        staff_id = ObjectId()
        
        # Create commission with large amount
        large_amount = Decimal("9999.99")
        
        commission = StaffCommission(
            tenant_id=tenant_id,
            staff_id=staff_id,
            transaction_id=ObjectId(),
            commission_amount=large_amount,
            commission_rate=Decimal("50.00"),
            commission_type="percentage",
            calculated_at=datetime.utcnow(),
        )
        commission.save()
        
        # Verify large amounts are handled correctly
        total = CommissionService.calculate_total_commission(
            tenant_id=tenant_id,
            staff_id=staff_id,
        )
        
        assert total == large_amount, f"Large amount should be handled correctly: {total} vs {large_amount}"
        
        # Cleanup
        commission.delete()