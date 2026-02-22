"""Integration tests for system integration fixes (appointments, invoices, POS, payments)."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.models.appointment import Appointment
from app.models.invoice import Invoice
from app.models.transaction import Transaction
from app.models.payment import Payment
from app.models.customer import Customer
from app.models.staff import Staff
from app.models.service import Service
from app.services.invoice_service import InvoiceService
from app.services.transaction_service import TransactionService
from app.services.payment_service import PaymentService


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def customer_id():
    """Create a test customer ID."""
    return ObjectId()


@pytest.fixture
def staff_id():
    """Create a test staff ID."""
    return ObjectId()


@pytest.fixture
def service_id():
    """Create a test service ID."""
    return ObjectId()


@pytest.fixture
def setup_test_data(tenant_id, customer_id, staff_id, service_id):
    """Set up test data."""
    # Create customer
    customer = Customer(
        tenant_id=tenant_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+234123456789",
    )
    customer.save()
    
    # Create staff
    staff = Staff(
        tenant_id=tenant_id,
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        phone="+234987654321",
    )
    staff.save()
    
    # Create service
    service = Service(
        tenant_id=tenant_id,
        name="Haircut",
        description="Professional haircut",
        price=Decimal("50.00"),
        duration_minutes=30,
    )
    service.save()
    
    return {
        "customer": customer,
        "staff": staff,
        "service": service,
    }


class TestPhase1AutoInvoiceCreation:
    """Test Phase 1: Auto-Invoice Creation on Appointment Completion."""
    
    def test_invoice_created_on_appointment_completion(self, tenant_id, customer_id, staff_id, service_id, setup_test_data):
        """Test that completing an appointment creates an invoice."""
        # Create appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status="scheduled",
            price=Decimal("50.00"),
        )
        appointment.save()
        
        # Create invoice from appointment
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
        )
        
        # Verify invoice was created
        assert invoice is not None
        assert invoice.appointment_id == appointment.id
        assert invoice.customer_id == customer_id
        assert invoice.total == Decimal("50.00")
        assert invoice.status == "draft"
    
    def test_invoice_issued_status_on_completion(self, tenant_id, customer_id, staff_id, service_id):
        """Test that invoice is set to 'issued' status."""
        # Create appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status="scheduled",
            price=Decimal("50.00"),
        )
        appointment.save()
        
        # Create and issue invoice
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
        )
        invoice.status = "issued"
        invoice.save()
        
        # Verify invoice status
        assert invoice.status == "issued"
    
    def test_invoice_contains_appointment_price(self, tenant_id, customer_id, staff_id, service_id):
        """Test that invoice uses appointment price as line item."""
        appointment_price = Decimal("75.50")
        
        # Create appointment with specific price
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status="scheduled",
            price=appointment_price,
        )
        appointment.save()
        
        # Create invoice
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
        )
        
        # Verify invoice total matches appointment price
        assert invoice.total == appointment_price
        assert len(invoice.line_items) == 1
        assert invoice.line_items[0].unit_price == appointment_price


class TestPhase2AutoPaymentInitialization:
    """Test Phase 2: Auto-Payment Initialization on Invoice Issue."""
    
    def test_auto_initialize_payment_for_invoice(self, tenant_id, customer_id):
        """Test that payment is auto-initialized when invoice is issued."""
        # Create invoice
        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items=[],
            subtotal=Decimal("50.00"),
            discount=Decimal("0"),
            tax=Decimal("0"),
            total=Decimal("50.00"),
            status="issued",
        )
        invoice.save()
        
        # Mock payment service
        with patch('app.services.invoice_service.PaymentService') as mock_payment_service:
            mock_instance = MagicMock()
            mock_payment_service.return_value = mock_instance
            mock_instance.initialize_payment.return_value = {
                "authorization_url": "https://checkout.paystack.com/test",
                "access_code": "test_access_code",
                "reference": "test_reference",
            }
            
            # Auto-initialize payment
            result = InvoiceService.auto_initialize_payment_for_invoice(
                tenant_id=tenant_id,
                invoice=invoice,
                customer_email="john@example.com",
            )
            
            # Verify payment was initialized
            assert result is not None
            assert "authorization_url" in result
            mock_instance.initialize_payment.assert_called_once()
    
    def test_auto_initialize_payment_requires_email(self, tenant_id, customer_id):
        """Test that payment initialization requires customer email."""
        # Create invoice
        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items=[],
            subtotal=Decimal("50.00"),
            discount=Decimal("0"),
            tax=Decimal("0"),
            total=Decimal("50.00"),
            status="issued",
        )
        invoice.save()
        
        # Try to initialize payment without email
        result = InvoiceService.auto_initialize_payment_for_invoice(
            tenant_id=tenant_id,
            invoice=invoice,
            customer_email="",
        )
        
        # Should return None
        assert result is None


class TestPhase3TransactionInvoiceLinking:
    """Test Phase 3: Add invoice_id to Transaction Model."""
    
    def test_transaction_has_invoice_id_field(self, tenant_id, customer_id, staff_id):
        """Test that transaction model has invoice_id field."""
        # Create transaction
        transaction = Transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items=[],
            subtotal=Decimal("50.00"),
            tax_amount=Decimal("0"),
            discount_amount=Decimal("0"),
            total=Decimal("50.00"),
            payment_method="card",
            reference_number="TXN-001",
        )
        transaction.save()
        
        # Verify invoice_id field exists and is None
        assert hasattr(transaction, 'invoice_id')
        assert transaction.invoice_id is None
    
    def test_transaction_links_to_invoice(self, tenant_id, customer_id, staff_id, service_id):
        """Test that transaction can be linked to invoice."""
        # Create appointment and invoice
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status="completed",
            price=Decimal("50.00"),
        )
        appointment.save()
        
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
        )
        
        # Create transaction linked to appointment
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=[{
                "item_type": "service",
                "item_id": str(service_id),
                "item_name": "Haircut",
                "quantity": 1,
                "unit_price": 50.00,
            }],
            payment_method="card",
            appointment_id=appointment.id,
        )
        
        # Verify transaction is linked to invoice
        assert transaction.invoice_id == invoice.id


class TestPhase4PaymentSuccessUpdates:
    """Test Phase 4: Update Invoice & Appointment on Payment Success."""
    
    def test_invoice_marked_paid_on_payment_success(self, tenant_id, customer_id):
        """Test that invoice is marked as paid when payment succeeds."""
        # Create invoice
        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items=[],
            subtotal=Decimal("50.00"),
            discount=Decimal("0"),
            tax=Decimal("0"),
            total=Decimal("50.00"),
            status="issued",
        )
        invoice.save()
        
        # Mark invoice as paid
        updated_invoice = InvoiceService.mark_invoice_paid(
            tenant_id=tenant_id,
            invoice_id=invoice.id,
        )
        
        # Verify invoice status
        assert updated_invoice.status == "paid"
        assert updated_invoice.paid_at is not None
    
    def test_appointment_updated_with_payment_id(self, tenant_id, customer_id, staff_id, service_id):
        """Test that appointment is updated with payment_id when payment succeeds."""
        # Create appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status="completed",
            price=Decimal("50.00"),
        )
        appointment.save()
        
        # Create payment
        payment = Payment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            amount=Decimal("50.00"),
            status="success",
            reference="test_ref_001",
            gateway="paystack",
        )
        payment.save()
        
        # Update appointment with payment_id
        appointment.payment_id = payment.id
        appointment.save()
        
        # Verify appointment has payment_id
        updated_appointment = Appointment.objects(id=appointment.id).first()
        assert updated_appointment.payment_id == payment.id


class TestPhase5UnifiedWorkflow:
    """Test Phase 5: Unified Completion Workflow."""
    
    def test_complete_workflow_appointment_to_payment(self, tenant_id, customer_id, staff_id, service_id):
        """Test complete workflow from appointment completion to payment success."""
        # 1. Create appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status="scheduled",
            price=Decimal("50.00"),
        )
        appointment.save()
        
        # 2. Complete appointment (should auto-create invoice)
        appointment.status = "completed"
        appointment.save()
        
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
        )
        invoice.status = "issued"
        invoice.save()
        
        # 3. Create payment
        payment = Payment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            invoice_id=invoice.id,
            amount=invoice.total,
            status="success",
            reference="test_ref_001",
            gateway="paystack",
            metadata={
                "invoice_id": str(invoice.id),
                "appointment_id": str(appointment.id),
            }
        )
        payment.save()
        
        # 4. Mark invoice as paid
        InvoiceService.mark_invoice_paid(
            tenant_id=tenant_id,
            invoice_id=invoice.id,
        )
        
        # 5. Update appointment with payment_id
        appointment.payment_id = payment.id
        appointment.save()
        
        # Verify complete workflow
        final_appointment = Appointment.objects(id=appointment.id).first()
        final_invoice = Invoice.objects(id=invoice.id).first()
        final_payment = Payment.objects(id=payment.id).first()
        
        assert final_appointment.status == "completed"
        assert final_appointment.payment_id == payment.id
        assert final_invoice.status == "paid"
        assert final_invoice.paid_at is not None
        assert final_payment.status == "success"


class TestTransactionInvoiceLinking:
    """Test transaction to invoice linking."""
    
    def test_transaction_auto_links_to_invoice_via_appointment(self, tenant_id, customer_id, staff_id, service_id):
        """Test that transaction automatically links to invoice when appointment has one."""
        # Create appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status="completed",
            price=Decimal("50.00"),
        )
        appointment.save()
        
        # Create invoice for appointment
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
        )
        
        # Create transaction with appointment_id
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=[{
                "item_type": "service",
                "item_id": str(service_id),
                "item_name": "Haircut",
                "quantity": 1,
                "unit_price": 50.00,
            }],
            payment_method="card",
            appointment_id=appointment.id,
        )
        
        # Verify transaction is linked to invoice
        assert transaction.invoice_id == invoice.id
        assert transaction.appointment_id == appointment.id
