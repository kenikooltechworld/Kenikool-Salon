#!/usr/bin/env python
"""Quick test to verify refund processing on appointment cancellation."""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.tenant import Tenant
from app.models.customer import Customer
from app.models.staff import Staff
from app.models.service import Service
from app.models.user import User
from app.services.appointment_service import AppointmentService
from app.db import connect_db

def test_refund_on_cancel():
    """Test that refund is created when appointment is cancelled."""
    connect_db()
    
    # Create test tenant
    tenant = Tenant(
        name="Test Salon",
        subdomain="test-salon",
        email="test@salon.com",
        phone="1234567890",
    )
    tenant.save()
    tenant_id = tenant.id
    
    # Create test user
    user = User(
        email="staff@test.com",
        first_name="John",
        last_name="Doe",
        password_hash="hashed",
    )
    user.save()
    
    # Create test staff
    staff = Staff(
        tenant_id=tenant_id,
        user_id=user.id,
        specialization="Hair",
    )
    staff.save()
    
    # Create test customer
    customer = Customer(
        tenant_id=tenant_id,
        first_name="Jane",
        last_name="Smith",
        email="customer@test.com",
        phone="9876543210",
    )
    customer.save()
    
    # Create test service
    service = Service(
        tenant_id=tenant_id,
        name="Haircut",
        price=Decimal("50.00"),
        duration_minutes=30,
    )
    service.save()
    
    # Create test payment
    payment = Payment(
        tenant_id=tenant_id,
        customer_id=customer.id,
        amount=Decimal("50.00"),
        status="success",
        reference="test_ref_123",
        gateway="paystack",
        metadata={
            "payment_type": "booking",
            "booking_data": {
                "customerId": str(customer.id),
                "serviceId": str(service.id),
                "staffId": str(staff.id),
                "startTime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "endTime": (datetime.utcnow() + timedelta(days=1, minutes=30)).isoformat(),
                "customerEmail": "customer@test.com",
                "customerName": "Jane Smith",
            }
        }
    )
    payment.save()
    
    # Create appointment with payment_id
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(minutes=30)
    
    appointment = Appointment(
        tenant_id=tenant_id,
        customer_id=customer.id,
        staff_id=staff.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        price=Decimal("50.00"),
        payment_id=payment.id,
        status="confirmed",
    )
    appointment.save()
    
    print(f"✓ Created appointment {appointment.id} with payment {payment.id}")
    
    # Cancel appointment
    try:
        cancelled_appt = AppointmentService.cancel_appointment(
            tenant_id=tenant_id,
            appointment_id=appointment.id,
            reason="Customer requested cancellation"
        )
        print(f"✓ Appointment cancelled: {cancelled_appt.status}")
        
        # Check if refund was created
        from app.models.refund import Refund
        refund = Refund.objects(
            tenant_id=tenant_id,
            payment_id=payment.id
        ).first()
        
        if refund:
            print(f"✓ Refund created: {refund.id}")
            print(f"  - Amount: {refund.amount}")
            print(f"  - Status: {refund.status}")
            print(f"  - Reason: {refund.reason}")
            print("\n✅ Test PASSED: Refund was created on appointment cancellation")
        else:
            print("❌ Test FAILED: No refund found after cancellation")
            
    except Exception as e:
        print(f"❌ Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        Appointment.objects(id=appointment.id).delete()
        Payment.objects(id=payment.id).delete()
        Service.objects(id=service.id).delete()
        Staff.objects(id=staff.id).delete()
        Customer.objects(id=customer.id).delete()
        User.objects(id=user.id).delete()
        Tenant.objects(id=tenant_id).delete()

if __name__ == "__main__":
    test_refund_on_cancel()
