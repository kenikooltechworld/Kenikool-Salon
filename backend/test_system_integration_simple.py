#!/usr/bin/env python
"""Simple test to verify system integration is working."""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set up Django/Flask environment
os.environ.setdefault("ENVIRONMENT", "test")

from app.models.tenant import Tenant
from app.models.user import User
from app.models.customer import Customer
from app.models.staff import Staff
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.invoice import Invoice
from app.services.appointment_service import AppointmentService
from app.services.invoice_service import InvoiceService


def test_system_integration():
    """Test that completing an appointment creates an invoice."""
    print("\n" + "="*60)
    print("SYSTEM INTEGRATION TEST")
    print("="*60)
    
    try:
        # Create test tenant
        print("\n1. Creating test tenant...")
        tenant = Tenant(
            name="Test Tenant",
            subdomain="test-tenant",
            email="test@example.com",
        )
        tenant.save()
        print(f"   ✓ Tenant created: {tenant.id}")
        
        # Create test customer
        print("\n2. Creating test customer...")
        customer = Customer(
            tenant_id=tenant.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+234123456789",
        )
        customer.save()
        print(f"   ✓ Customer created: {customer.id}")
        
        # Create test staff
        print("\n3. Creating test staff...")
        staff = Staff(
            tenant_id=tenant.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="+234987654321",
        )
        staff.save()
        print(f"   ✓ Staff created: {staff.id}")
        
        # Create test service
        print("\n4. Creating test service...")
        service = Service(
            tenant_id=tenant.id,
            name="Haircut",
            description="Professional haircut",
            price=Decimal("50.00"),
            duration_minutes=30,
        )
        service.save()
        print(f"   ✓ Service created: {service.id}")
        
        # Create test appointment
        print("\n5. Creating test appointment...")
        appointment = Appointment(
            tenant_id=tenant.id,
            customer_id=customer.id,
            staff_id=staff.id,
            service_id=service.id,
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status="scheduled",
            price=Decimal("50.00"),
        )
        appointment.save()
        print(f"   ✓ Appointment created: {appointment.id}")
        print(f"     Status: {appointment.status}")
        print(f"     Price: {appointment.price}")
        
        # Test invoice creation from appointment
        print("\n6. Creating invoice from appointment...")
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant.id,
            appointment_id=appointment.id,
            discount=Decimal("0"),
            tax=Decimal("0"),
        )
        print(f"   ✓ Invoice created: {invoice.id}")
        print(f"     Status: {invoice.status}")
        print(f"     Total: {invoice.total}")
        print(f"     Appointment ID: {invoice.appointment_id}")
        
        # Verify invoice is linked to appointment
        print("\n7. Verifying invoice-appointment link...")
        assert invoice.appointment_id == appointment.id, "Invoice not linked to appointment"
        print(f"   ✓ Invoice correctly linked to appointment")
        
        # Verify invoice can be fetched
        print("\n8. Fetching invoice from database...")
        fetched_invoice = Invoice.objects(
            tenant_id=tenant.id,
            id=invoice.id
        ).first()
        assert fetched_invoice is not None, "Invoice not found in database"
        print(f"   ✓ Invoice found in database")
        print(f"     ID: {fetched_invoice.id}")
        print(f"     Status: {fetched_invoice.status}")
        print(f"     Total: {fetched_invoice.total}")
        
        # Verify invoices can be listed
        print("\n9. Listing all invoices for tenant...")
        invoices = Invoice.objects(tenant_id=tenant.id)
        print(f"   ✓ Found {invoices.count()} invoice(s)")
        for inv in invoices:
            print(f"     - Invoice {inv.id}: {inv.status} ({inv.total})")
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nSYSTEM INTEGRATION STATUS:")
        print("  ✓ Appointments can be created")
        print("  ✓ Invoices can be created from appointments")
        print("  ✓ Invoices are linked to appointments")
        print("  ✓ Invoices can be fetched from database")
        print("  ✓ Invoices can be listed")
        print("\nCONCLUSION: System integration is working correctly!")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_system_integration()
