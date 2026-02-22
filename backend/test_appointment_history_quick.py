"""Quick test to verify appointment history implementation."""

from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from app.models.appointment_history import AppointmentHistory
from app.models.appointment import Appointment
from app.models.service import Service
from app.services.appointment_history_service import AppointmentHistoryService
from app.db import init_db, close_db

# Initialize database
init_db()

try:
    # Create test data
    tenant_id = ObjectId()
    customer_id = ObjectId()
    staff_id = ObjectId()
    service_id = ObjectId()
    
    print("Testing AppointmentHistory Model...")
    
    # Test 1: Create appointment history
    history = AppointmentHistory(
        tenant_id=tenant_id,
        customer_id=customer_id,
        appointment_id=ObjectId(),
        service_id=service_id,
        staff_id=staff_id,
        appointment_date=datetime.utcnow(),
        duration_minutes=60,
        amount_paid=Decimal("100.00"),
        notes="Test history",
    )
    history.save()
    print(f"✓ Created appointment history: {history.id}")
    
    # Test 2: Retrieve history
    retrieved = AppointmentHistory.objects(id=history.id).first()
    assert retrieved is not None
    assert retrieved.customer_id == customer_id
    print(f"✓ Retrieved appointment history: {retrieved.id}")
    
    # Test 3: Test service - get customer history
    entries, total = AppointmentHistoryService.get_customer_history(
        tenant_id=tenant_id,
        customer_id=customer_id,
        page=1,
        page_size=20,
    )
    assert len(entries) == 1
    assert total == 1
    print(f"✓ Retrieved customer history: {len(entries)} entries")
    
    # Test 4: Test service - get history stats
    stats = AppointmentHistoryService.get_customer_history_stats(
        tenant_id=tenant_id,
        customer_id=customer_id,
    )
    assert stats["total_appointments"] == 1
    assert stats["total_duration_minutes"] == 60
    print(f"✓ Retrieved history stats: {stats['total_appointments']} appointments")
    
    # Test 5: Create completed appointment and history
    start_time = datetime.utcnow() - timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    appointment = Appointment(
        tenant_id=tenant_id,
        customer_id=customer_id,
        staff_id=staff_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status="completed",
        price=Decimal("150.00"),
        notes="Completed appointment",
    )
    appointment.save()
    print(f"✓ Created completed appointment: {appointment.id}")
    
    # Test 6: Create history from appointment
    history_from_appt = AppointmentHistoryService.create_history_from_appointment(
        tenant_id=tenant_id,
        appointment_id=appointment.id,
    )
    assert history_from_appt.id is not None
    assert history_from_appt.appointment_id == appointment.id
    print(f"✓ Created history from appointment: {history_from_appt.id}")
    
    print("\n✅ All tests passed!")
    
finally:
    close_db()
