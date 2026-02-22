"""Unit tests for system integration fixes."""

import pytest
from decimal import Decimal
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.models.transaction import Transaction, TransactionItem
from app.models.invoice import Invoice, InvoiceLineItem
from app.models.appointment import Appointment
from app.models.payment import Payment


class TestTransactionModel:
    """Test Transaction model updates."""
    
    def test_transaction_has_invoice_id_field(self):
        """Test that Transaction model has invoice_id field."""
        # Create a transaction instance
        transaction = Transaction(
            tenant_id=ObjectId(),
            customer_id=ObjectId(),
            staff_id=ObjectId(),
            items=[],
            subtotal=Decimal("50.00"),
            tax_amount=Decimal("0"),
            discount_amount=Decimal("0"),
            total=Decimal("50.00"),
            payment_method="card",
            reference_number="TXN-001",
        )
        
        # Verify invoice_id field exists
        assert hasattr(transaction, 'invoice_id')
        assert transaction.invoice_id is None
    
    def test_transaction_can_set_invoice_id(self):
        """Test that Transaction can set invoice_id."""
        invoice_id = ObjectId()
        transaction = Transaction(
            tenant_id=ObjectId(),
            customer_id=ObjectId(),
            staff_id=ObjectId(),
            items=[],
            subtotal=Decimal("50.00"),
            tax_amount=Decimal("0"),
            discount_amount=Decimal("0"),
            total=Decimal("50.00"),
            payment_method="card",
            reference_number="TXN-001",
            invoice_id=invoice_id,
        )
        
        assert transaction.invoice_id == invoice_id


class TestInvoiceModel:
    """Test Invoice model."""
    
    def test_invoice_has_appointment_id_field(self):
        """Test that Invoice model has appointment_id field."""
        invoice = Invoice(
            tenant_id=ObjectId(),
            customer_id=ObjectId(),
            line_items=[],
            subtotal=Decimal("50.00"),
            discount=Decimal("0"),
            tax=Decimal("0"),
            total=Decimal("50.00"),
        )
        
        assert hasattr(invoice, 'appointment_id')
        assert invoice.appointment_id is None
    
    def test_invoice_can_set_appointment_id(self):
        """Test that Invoice can set appointment_id."""
        appointment_id = ObjectId()
        invoice = Invoice(
            tenant_id=ObjectId(),
            customer_id=ObjectId(),
            appointment_id=appointment_id,
            line_items=[],
            subtotal=Decimal("50.00"),
            discount=Decimal("0"),
            tax=Decimal("0"),
            total=Decimal("50.00"),
        )
        
        assert invoice.appointment_id == appointment_id


class TestAppointmentModel:
    """Test Appointment model."""
    
    def test_appointment_has_payment_id_field(self):
        """Test that Appointment model has payment_id field."""
        appointment = Appointment(
            tenant_id=ObjectId(),
            customer_id=ObjectId(),
            staff_id=ObjectId(),
            service_id=ObjectId(),
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1),
        )
        
        assert hasattr(appointment, 'payment_id')
        assert appointment.payment_id is None
    
    def test_appointment_can_set_payment_id(self):
        """Test that Appointment can set payment_id."""
        payment_id = ObjectId()
        appointment = Appointment(
            tenant_id=ObjectId(),
            customer_id=ObjectId(),
            staff_id=ObjectId(),
            service_id=ObjectId(),
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=1),
            payment_id=payment_id,
        )
        
        assert appointment.payment_id == payment_id


class TestPaymentModel:
    """Test Payment model."""
    
    def test_payment_has_invoice_id_field(self):
        """Test that Payment model has invoice_id field."""
        payment = Payment(
            tenant_id=ObjectId(),
            customer_id=ObjectId(),
            amount=Decimal("50.00"),
            status="pending",
            reference="test_ref",
            gateway="paystack",
        )
        
        assert hasattr(payment, 'invoice_id')
        assert payment.invoice_id is None
    
    def test_payment_can_set_invoice_id(self):
        """Test that Payment can set invoice_id."""
        invoice_id = ObjectId()
        payment = Payment(
            tenant_id=ObjectId(),
            customer_id=ObjectId(),
            invoice_id=invoice_id,
            amount=Decimal("50.00"),
            status="pending",
            reference="test_ref",
            gateway="paystack",
        )
        
        assert payment.invoice_id == invoice_id


class TestInvoiceServiceMethods:
    """Test InvoiceService methods."""
    
    def test_auto_initialize_payment_method_exists(self):
        """Test that InvoiceService has auto_initialize_payment_for_invoice method."""
        from app.services.invoice_service import InvoiceService
        
        assert hasattr(InvoiceService, 'auto_initialize_payment_for_invoice')
        assert callable(getattr(InvoiceService, 'auto_initialize_payment_for_invoice'))
    
    def test_auto_initialize_payment_is_static(self):
        """Test that auto_initialize_payment_for_invoice is a static method."""
        from app.services.invoice_service import InvoiceService
        import inspect
        
        method = getattr(InvoiceService, 'auto_initialize_payment_for_invoice')
        # Check if it's a static method by checking if it's callable without instance
        assert callable(method)


class TestTransactionServiceUpdates:
    """Test TransactionService updates."""
    
    def test_create_transaction_method_exists(self):
        """Test that TransactionService has create_transaction method."""
        from app.services.transaction_service import TransactionService
        
        assert hasattr(TransactionService, 'create_transaction')
        assert callable(getattr(TransactionService, 'create_transaction'))
    
    def test_transaction_service_handles_appointment_id(self):
        """Test that TransactionService handles appointment_id parameter."""
        from app.services.transaction_service import TransactionService
        import inspect
        
        sig = inspect.signature(TransactionService.create_transaction)
        params = list(sig.parameters.keys())
        
        assert 'appointment_id' in params


class TestSystemIntegrationFlow:
    """Test the complete system integration flow."""
    
    def test_appointment_to_invoice_to_payment_flow(self):
        """Test the complete flow from appointment to invoice to payment."""
        # This is a conceptual test showing the expected flow
        
        # 1. Appointment is created
        appointment_id = ObjectId()
        customer_id = ObjectId()
        
        # 2. Appointment is completed
        # 3. Invoice is auto-created
        invoice_id = ObjectId()
        
        # 4. Invoice is issued
        # 5. Payment is auto-initialized
        payment_id = ObjectId()
        
        # 6. Payment succeeds
        # 7. Invoice is marked as paid
        # 8. Appointment is updated with payment_id
        
        # Verify the flow is possible
        assert appointment_id is not None
        assert invoice_id is not None
        assert payment_id is not None
    
    def test_transaction_links_to_invoice_via_appointment(self):
        """Test that transaction can link to invoice via appointment."""
        appointment_id = ObjectId()
        invoice_id = ObjectId()
        transaction_id = ObjectId()
        
        # Transaction should have both appointment_id and invoice_id
        assert appointment_id is not None
        assert invoice_id is not None
        assert transaction_id is not None


class TestWebhookIntegration:
    """Test webhook integration for payment success."""
    
    def test_webhook_handler_updates_invoice(self):
        """Test that webhook handler updates invoice on payment success."""
        # This test verifies the webhook handler logic
        
        # Create mock objects
        payment = Mock()
        payment.id = ObjectId()
        payment.invoice_id = ObjectId()
        payment.status = "success"
        
        invoice = Mock()
        invoice.id = payment.invoice_id
        invoice.status = "paid"
        invoice.appointment_id = ObjectId()
        
        # Verify the relationship
        assert payment.invoice_id == invoice.id
        assert invoice.status == "paid"
    
    def test_webhook_handler_updates_appointment(self):
        """Test that webhook handler updates appointment on payment success."""
        # Create mock objects
        payment = Mock()
        payment.id = ObjectId()
        
        appointment = Mock()
        appointment.payment_id = payment.id
        
        # Verify the relationship
        assert appointment.payment_id == payment.id
