"""Property-based tests for outstanding balance enforcement."""

import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings, HealthCheck
from bson import ObjectId
from datetime import datetime
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.staff import Staff
from app.services.appointment_service import AppointmentService
from app.services.balance_service import BalanceService
from app.context import set_tenant_id


@st.composite
def invoice_amounts(draw):
    """Generate valid invoice amounts."""
    amount = draw(st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("50000.00"),
        places=2
    ))
    return amount


class TestBalanceEnforcementProperties:
    """Property-based tests for outstanding balance enforcement."""

    @pytest.fixture(autouse=True)
    def setup(self, clear_db):
        """Set up test fixtures."""
        self.tenant_id = ObjectId()
        set_tenant_id(str(self.tenant_id))
        self.balance_service = BalanceService()

    @given(invoice_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_customer_with_outstanding_balance_cannot_book(self, amount):
        """
        **Validates: Requirements 6.6**
        
        Property: Outstanding Balance Enforcement
        
        For any customer with outstanding balance, the system SHALL prevent new appointment booking.
        
        - Create customer with unpaid invoice
        - Attempt to create appointment
        - Verify appointment creation fails with balance error
        """
        # Create test customer
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
            outstanding_balance=amount,
        )
        customer.save()

        # Create unpaid invoice
        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="issued",
        )
        invoice.save()

        # Create service and staff for appointment
        service = Service(
            tenant_id=self.tenant_id,
            name="Test Service",
            description="Test",
            price=Decimal("1000.00"),
            duration_minutes=60,
        )
        service.save()

        staff = Staff(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Staff",
            email="staff@example.com",
            phone="+234123456789",
        )
        staff.save()

        # Attempt to create appointment
        start_time = datetime.utcnow()
        end_time = start_time.replace(hour=start_time.hour + 1)

        with pytest.raises(ValueError) as exc_info:
            AppointmentService.create_appointment(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                staff_id=staff.id,
                service_id=service.id,
                start_time=start_time,
                end_time=end_time,
            )

        # Verify error message mentions balance
        assert "outstanding balance" in str(exc_info.value).lower()

    @given(invoice_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_customer_with_zero_balance_can_book(self, amount):
        """
        **Validates: Requirements 6.6**
        
        Property: Outstanding Balance Enforcement
        
        For any customer with zero outstanding balance, the system SHALL allow new appointment booking.
        
        - Create customer with no unpaid invoices
        - Create appointment
        - Verify appointment is created successfully
        """
        # Create test customer with zero balance
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
            outstanding_balance=Decimal("0"),
        )
        customer.save()

        # Create service and staff for appointment
        service = Service(
            tenant_id=self.tenant_id,
            name="Test Service",
            description="Test",
            price=Decimal("1000.00"),
            duration_minutes=60,
        )
        service.save()

        staff = Staff(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Staff",
            email="staff@example.com",
            phone="+234123456789",
        )
        staff.save()

        # Create appointment
        start_time = datetime.utcnow()
        end_time = start_time.replace(hour=start_time.hour + 1)

        appointment = AppointmentService.create_appointment(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            staff_id=staff.id,
            service_id=service.id,
            start_time=start_time,
            end_time=end_time,
        )

        # Verify appointment was created
        assert appointment is not None
        assert str(appointment.customer_id) == str(customer.id)
        assert appointment.status == "scheduled"

    @given(invoice_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_balance_calculation_includes_all_unpaid_invoices(self, amount):
        """
        **Validates: Requirements 6.6**
        
        Property: Outstanding Balance Enforcement
        
        For any customer, outstanding balance SHALL equal sum of all unpaid invoices.
        
        - Create multiple unpaid invoices
        - Calculate balance
        - Verify balance equals sum of all unpaid invoices
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

        # Create multiple unpaid invoices
        total_expected_balance = Decimal("0")
        for i in range(3):
            invoice = Invoice(
                tenant_id=self.tenant_id,
                customer_id=customer.id,
                subtotal=amount,
                tax=Decimal("0.00"),
                discount=Decimal("0.00"),
                total=amount,
                status="issued",
            )
            invoice.save()
            total_expected_balance += amount

        # Calculate balance
        calculated_balance = self.balance_service.calculate_customer_balance(str(customer.id))

        # Verify balance equals sum of unpaid invoices
        assert calculated_balance == total_expected_balance

    @given(invoice_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_paid_invoices_not_included_in_balance(self, amount):
        """
        **Validates: Requirements 6.6**
        
        Property: Outstanding Balance Enforcement
        
        For any customer, paid invoices SHALL NOT be included in outstanding balance.
        
        - Create mix of paid and unpaid invoices
        - Calculate balance
        - Verify balance only includes unpaid invoices
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

        # Create paid invoice
        paid_invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="paid",
        )
        paid_invoice.save()

        # Create unpaid invoice
        unpaid_invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="issued",
        )
        unpaid_invoice.save()

        # Calculate balance
        calculated_balance = self.balance_service.calculate_customer_balance(str(customer.id))

        # Verify balance only includes unpaid invoice
        assert calculated_balance == amount

    @given(invoice_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_overdue_invoices_included_in_balance(self, amount):
        """
        **Validates: Requirements 6.6**
        
        Property: Outstanding Balance Enforcement
        
        For any customer, overdue invoices SHALL be included in outstanding balance.
        
        - Create overdue invoice
        - Calculate balance
        - Verify balance includes overdue invoice
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

        # Create overdue invoice
        overdue_invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="overdue",
        )
        overdue_invoice.save()

        # Calculate balance
        calculated_balance = self.balance_service.calculate_customer_balance(str(customer.id))

        # Verify balance includes overdue invoice
        assert calculated_balance == amount

    @given(invoice_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_balance_eligibility_check_returns_correct_status(self, amount):
        """
        **Validates: Requirements 6.6**
        
        Property: Outstanding Balance Enforcement
        
        For any customer, booking eligibility SHALL be based on outstanding balance.
        
        - Create customer with balance
        - Check booking eligibility
        - Verify eligibility status is correct
        """
        # Create test customer with balance
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
            outstanding_balance=amount,
        )
        customer.save()

        # Create unpaid invoice
        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="issued",
        )
        invoice.save()

        # Check booking eligibility
        eligibility = self.balance_service.check_booking_eligibility(str(customer.id))

        # Verify eligibility status
        assert eligibility["is_eligible_to_book"] is False
        assert eligibility["outstanding_balance"] == float(amount)

    @given(invoice_amounts())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_balance_update_reflects_current_unpaid_invoices(self, amount):
        """
        **Validates: Requirements 6.6**
        
        Property: Outstanding Balance Enforcement
        
        For any customer, balance update SHALL reflect current unpaid invoices.
        
        - Create customer with unpaid invoices
        - Update balance
        - Verify balance reflects current state
        """
        # Create test customer
        customer = Customer(
            tenant_id=self.tenant_id,
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="+234123456789",
            outstanding_balance=Decimal("0"),
        )
        customer.save()

        # Create unpaid invoice
        invoice = Invoice(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            subtotal=amount,
            tax=Decimal("0.00"),
            discount=Decimal("0.00"),
            total=amount,
            status="issued",
        )
        invoice.save()

        # Update balance
        updated_balance = self.balance_service.update_customer_balance(str(customer.id))

        # Verify balance was updated
        assert updated_balance == amount

        # Verify customer record was updated
        updated_customer = Customer.objects(id=customer.id).first()
        assert updated_customer.outstanding_balance == amount
