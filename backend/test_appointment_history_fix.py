#!/usr/bin/env python3
"""Test script to verify appointment history creation for all appointment statuses."""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
sys.path.insert(0, os.path.dirname(__file__))

# Initialize MongoEngine
from mongoengine import connect, disconnect
from app.config import MONGODB_URL

disconnect()
connect(host=MONGODB_URL)

from bson import ObjectId
from app.models.tenant import Tenant
from app.models.customer import Customer
from app.models.staff import Staff
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.appointment_history import AppointmentHistory
from app.services.appointment_service import AppointmentService
from app.services.appointment_history_service import AppointmentHistoryService


def test_appointment_history_creation():
    """Test that history entries are created for all appointment statuses."""
    
    print("\n" + "="*60)
    print("Testing Appointment History Creation")
    print("="*60)
    
    # Create test tenant
    tenant = Tenant(name="Test Tenant", subdomain="test-tenant")
    tenant.save()
    tenant_id = tenant.id
    print(f"\n✓ Created test tenant: {tenant_id}")
    
    # Create test customer
    customer = Customer(
        tenant_id=tenant_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
    )
    customer.save()
    customer_id = customer.id
    print(f"✓ Created test customer: {customer_id}")
    
    # Create test staff
    staff = Staff(
        tenant_id=tenant_id,
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        phone="0987654321",
    )
    staff.save()
    staff_id = staff.id
    print(f"✓ Created test staff: {staff_id}")
    
    # Create test service
    service = Service(
        tenant_id=tenant_id,
        name="Haircut",
        description="Professional haircut",
        price=Decimal("50.00"),
        duration_minutes=30,
    )
    service.save()
    service_id = service.id
    print(f"✓ Created test service: {service_id}")
    
    # Test 1: Create appointment and confirm it
    print("\n--- Test 1: Confirmed Appointment ---")
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(minutes=30)
    
    appt1 = Appointment(
        tenant_id=tenant_id,
        customer_id=customer_id,
        staff_id=staff_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status="scheduled",
        price=Decimal("50.00"),
    )
    appt1.save()
    print(f"✓ Created appointment: {appt1.id} (status: scheduled)")
    
    # Confirm appointment
    appt1.status = "confirmed"
    appt1.confirmed_at = datetime.utcnow()
    appt1.save()
    print(f"✓ Confirmed appointment: {appt1.id}")
    
    # Create history entry
    try:
        history1 = AppointmentHistoryService.create_history_from_appointment(tenant_id, appt1.id)
        print(f"✓ Created history entry: {history1.id}")
    except Exception as e:
        print(f"✗ Failed to create history: {e}")
    
    # Test 2: Create appointment and complete it
    print("\n--- Test 2: Completed Appointment ---")
    start_time = datetime.utcnow() + timedelta(days=2)
    end_time = start_time + timedelta(minutes=30)
    
    appt2 = Appointment(
        tenant_id=tenant_id,
        customer_id=customer_id,
        staff_id=staff_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status="confirmed",
        price=Decimal("50.00"),
    )
    appt2.save()
    print(f"✓ Created appointment: {appt2.id} (status: confirmed)")
    
    # Complete appointment
    appt2.status = "completed"
    appt2.save()
    print(f"✓ Completed appointment: {appt2.id}")
    
    # Create history entry
    try:
        history2 = AppointmentHistoryService.create_history_from_appointment(tenant_id, appt2.id)
        print(f"✓ Created history entry: {history2.id}")
    except Exception as e:
        print(f"✗ Failed to create history: {e}")
    
    # Test 3: Create appointment and cancel it
    print("\n--- Test 3: Cancelled Appointment ---")
    start_time = datetime.utcnow() + timedelta(days=3)
    end_time = start_time + timedelta(minutes=30)
    
    appt3 = Appointment(
        tenant_id=tenant_id,
        customer_id=customer_id,
        staff_id=staff_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status="confirmed",
        price=Decimal("50.00"),
    )
    appt3.save()
    print(f"✓ Created appointment: {appt3.id} (status: confirmed)")
    
    # Cancel appointment
    appt3.status = "cancelled"
    appt3.cancellation_reason = "Customer requested"
    appt3.cancelled_at = datetime.utcnow()
    appt3.save()
    print(f"✓ Cancelled appointment: {appt3.id}")
    
    # Create history entry
    try:
        history3 = AppointmentHistoryService.create_history_from_appointment(tenant_id, appt3.id)
        print(f"✓ Created history entry: {history3.id}")
    except Exception as e:
        print(f"✗ Failed to create history: {e}")
    
    # Test 4: Create appointment and mark as no-show
    print("\n--- Test 4: No-Show Appointment ---")
    start_time = datetime.utcnow() + timedelta(days=4)
    end_time = start_time + timedelta(minutes=30)
    
    appt4 = Appointment(
        tenant_id=tenant_id,
        customer_id=customer_id,
        staff_id=staff_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status="confirmed",
        price=Decimal("50.00"),
    )
    appt4.save()
    print(f"✓ Created appointment: {appt4.id} (status: confirmed)")
    
    # Mark as no-show
    appt4.status = "no_show"
    appt4.no_show_reason = "Customer did not show up"
    appt4.marked_no_show_at = datetime.utcnow()
    appt4.save()
    print(f"✓ Marked appointment as no-show: {appt4.id}")
    
    # Create history entry
    try:
        history4 = AppointmentHistoryService.create_history_from_appointment(tenant_id, appt4.id)
        print(f"✓ Created history entry: {history4.id}")
    except Exception as e:
        print(f"✗ Failed to create history: {e}")
    
    # Verify all history entries were created
    print("\n--- Verification ---")
    history_count = AppointmentHistory.objects(tenant_id=tenant_id, customer_id=customer_id).count()
    print(f"✓ Total history entries for customer: {history_count}")
    
    if history_count == 4:
        print("\n✓ SUCCESS: All 4 appointment history entries were created!")
    else:
        print(f"\n✗ FAILED: Expected 4 history entries, got {history_count}")
    
    # Cleanup
    print("\n--- Cleanup ---")
    Appointment.objects(tenant_id=tenant_id).delete()
    AppointmentHistory.objects(tenant_id=tenant_id).delete()
    Customer.objects(tenant_id=tenant_id).delete()
    Staff.objects(tenant_id=tenant_id).delete()
    Service.objects(tenant_id=tenant_id).delete()
    Tenant.objects(id=tenant_id).delete()
    print("✓ Cleaned up test data")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_appointment_history_creation()
