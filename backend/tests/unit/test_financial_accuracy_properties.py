"""Property-based tests for financial report accuracy."""

import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings, HealthCheck
from bson import ObjectId
from datetime import datetime, timedelta
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.refund import Refund
from app.models.customer import Customer
from app.services.financial_report_service import FinancialReportService
from app.context import set_tenant_id


@st.composite
def date_range_data(draw):
    """Generate valid date range test data."""
    start_date = draw(st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2024, 12, 1).date()))
    end_date = draw(st.dates(min_value=start_date, max_value=start_date + timedelta(days=90)))
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


@st.composite
def payment_amounts(draw):
    """Generate valid payment amounts."""
    amount = draw(st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("100000.00"),
        places=2
    ))
    return amount


class TestFinancialReportAccuracyProperties:
    """Property-based tests for financial report accuracy."""

    @pytest.fixture(autouse=True)
    def setup(self, clear_db):
        """Set up test fixtures."""
        self.tenant_id = ObjectId()
        set_tenant_id(str(self.tenant_id))
        self.report_service = FinancialReportService()

    @given(date_range_data(), payment_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_revenue_equals_sum_of_payments(self, date_range, amount):
        """
        **Validates: Requirements 6.5, 19.1**
        
        Property: Financial Report Accuracy
        
        For any financial report, total_revenue SHALL equal the sum of all completed appointment payments.
        
        - Create multiple successful payments in date range
        - Generate revenue report
        - Verify total_revenue equals sum of all payment amounts
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

        # Create multiple invoices and payments
        payment_amounts_list = []
        for i in range(3):
            invoice = Invoice(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                subtotal=amount,
                tax=Decimal("0.00"),
                discount=Decimal("0.00"),
                total=amount,
                status="paid",
            )
            invoice.save()

            # Create successful payment
            payment = Payment(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                invoice_id=invoice.id,
                amount=amount,
                reference=f"ref_{i}",
                gateway="paystack",
                status="success",
            )
            payment.save()
            payment_amounts_list.append(amount)

        # Generate revenue report
        report = self.report_service.get_revenue_report(
            date_range["start_date"],
            date_range["end_date"],
            use_cache=False
        )

        # Verify total_revenue equals sum of payments
        expected_revenue = sum(payment_amounts_list)
        assert Decimal(str(report["total_revenue"])) == expected_revenue

    @given(date_range_data(), payment_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_net_revenue_equals_revenue_minus_refunds(self, date_range, amount):
        """
        **Validates: Requirements 6.5, 19.1**
        
        Property: Financial Report Accuracy
        
        For any financial report, net_revenue SHALL equal total_revenue minus total_refunds.
        
        - Create successful payments
        - Create refunds for some payments
        - Generate revenue report
        - Verify net_revenue = total_revenue - total_refunds
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

        # Create invoices and payments
        total_payments = Decimal("0")
        total_refunds = Decimal("0")
        payment_ids = []

        for i in range(3):
            invoice = Invoice(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                subtotal=amount,
                tax=Decimal("0.00"),
                discount=Decimal("0.00"),
                total=amount,
                status="paid",
            )
            invoice.save()

            payment = Payment(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                invoice_id=invoice.id,
                amount=amount,
                reference=f"ref_{i}",
                gateway="paystack",
                status="success",
            )
            payment.save()
            payment_ids.append(payment.id)
            total_payments += amount

        # Create refunds for first payment
        refund_amount = amount / 2
        refund = Refund(
            tenant_id=self.tenant_id,
            payment_id=payment_ids[0],
            amount=refund_amount,
            reason="Partial refund",
            reference="refund_ref_1",
            status="success",
        )
        refund.save()
        total_refunds += refund_amount

        # Generate revenue report
        report = self.report_service.get_revenue_report(
            date_range["start_date"],
            date_range["end_date"],
            use_cache=False
        )

        # Verify net_revenue = total_revenue - total_refunds
        expected_net_revenue = total_payments - total_refunds
        assert Decimal(str(report["net_revenue"])) == expected_net_revenue

    @given(date_range_data())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_payment_count_matches_successful_payments(self, date_range):
        """
        **Validates: Requirements 6.5, 19.1**
        
        Property: Financial Report Accuracy
        
        For any financial report, payment_count SHALL equal the number of successful payments.
        
        - Create multiple payments with different statuses
        - Generate revenue report
        - Verify payment_count equals only successful payments
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

        # Create payments with different statuses
        amount = Decimal("1000.00")
        successful_count = 0

        for i in range(5):
            invoice = Invoice(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                subtotal=amount,
                tax=Decimal("0.00"),
                discount=Decimal("0.00"),
                total=amount,
                status="draft",
            )
            invoice.save()

            # Alternate between successful and failed
            status = "success" if i % 2 == 0 else "failed"
            payment = Payment(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                invoice_id=invoice.id,
                amount=amount,
                reference=f"ref_{i}",
                gateway="paystack",
                status=status,
            )
            payment.save()

            if status == "success":
                successful_count += 1

        # Generate revenue report
        report = self.report_service.get_revenue_report(
            date_range["start_date"],
            date_range["end_date"],
            use_cache=False
        )

        # Verify payment_count equals successful payments
        assert report["payment_count"] == successful_count

    @given(date_range_data())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_refund_count_matches_successful_refunds(self, date_range):
        """
        **Validates: Requirements 6.5, 19.1**
        
        Property: Financial Report Accuracy
        
        For any financial report, refund_count SHALL equal the number of successful refunds.
        
        - Create multiple refunds with different statuses
        - Generate revenue report
        - Verify refund_count equals only successful refunds
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

        # Create payments and refunds
        amount = Decimal("1000.00")
        successful_refund_count = 0

        for i in range(5):
            invoice = Invoice(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                subtotal=amount,
                tax=Decimal("0.00"),
                discount=Decimal("0.00"),
                total=amount,
                status="paid",
            )
            invoice.save()

            payment = Payment(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                invoice_id=invoice.id,
                amount=amount,
                reference=f"ref_{i}",
                gateway="paystack",
                status="success",
            )
            payment.save()

            # Create refund with alternating status
            refund_status = "success" if i % 2 == 0 else "failed"
            refund = Refund(
                tenant_id=self.tenant_id,
                payment_id=payment.id,
                amount=amount / 2,
                reason="Test refund",
                reference=f"refund_ref_{i}",
                status=refund_status,
            )
            refund.save()

            if refund_status == "success":
                successful_refund_count += 1

        # Generate revenue report
        report = self.report_service.get_revenue_report(
            date_range["start_date"],
            date_range["end_date"],
            use_cache=False
        )

        # Verify refund_count equals successful refunds
        assert report["refund_count"] == successful_refund_count

    @given(date_range_data())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_report_excludes_payments_outside_date_range(self, date_range):
        """
        **Validates: Requirements 6.5, 19.1**
        
        Property: Financial Report Accuracy
        
        For any financial report, only payments within the date range SHALL be included.
        
        - Create payments inside and outside date range
        - Generate revenue report
        - Verify only payments within range are included
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

        # Parse date range
        start_date = datetime.fromisoformat(date_range["start_date"])
        end_date = datetime.fromisoformat(date_range["end_date"])

        amount = Decimal("1000.00")
        in_range_count = 0

        # Create payment before range
        invoice_before = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="paid",
        )
        invoice_before.save()

        payment_before = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice_before.id,
            amount=amount,
            reference="ref_before",
            gateway="paystack",
            status="success",
            created_at=start_date - timedelta(days=1),
        )
        payment_before.save()

        # Create payment within range
        invoice_in_range = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="paid",
        )
        invoice_in_range.save()

        payment_in_range = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice_in_range.id,
            amount=amount,
            reference="ref_in_range",
            gateway="paystack",
            status="success",
            created_at=start_date + timedelta(days=1),
        )
        payment_in_range.save()
        in_range_count += 1

        # Create payment after range
        invoice_after = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="paid",
        )
        invoice_after.save()

        payment_after = Payment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            invoice_id=invoice_after.id,
            amount=amount,
            reference="ref_after",
            gateway="paystack",
            status="success",
            created_at=end_date + timedelta(days=1),
        )
        payment_after.save()

        # Generate revenue report
        report = self.report_service.get_revenue_report(
            date_range["start_date"],
            date_range["end_date"],
            use_cache=False
        )

        # Verify only in-range payment is counted
        assert report["payment_count"] == in_range_count
        assert Decimal(str(report["total_revenue"])) == amount * in_range_count
