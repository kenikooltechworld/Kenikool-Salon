#!/usr/bin/env python
"""Setup availability for the staff member used in booking tests."""

import sys
import os
from datetime import datetime, date, time, timedelta
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.availability import Availability
from bson import ObjectId

def setup_availability_for_staff(staff_id_str: str, tenant_id_str: str):
    """Create availability for a specific staff member."""
    init_db()
    
    staff_id = ObjectId(staff_id_str)
    tenant_id = ObjectId(tenant_id_str)
    
    print(f"Setting up availability for staff: {staff_id}")
    print(f"Tenant: {tenant_id}")
    
    # Create recurring availability for all weekdays (Monday-Friday)
    for day_of_week in range(5):  # 0=Monday, 4=Friday
        avail = Availability(
            tenant_id=tenant_id,
            staff_id=staff_id,
            day_of_week=day_of_week,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=True,
            effective_from=date.today(),
            effective_to=None,  # Ongoing
            is_active=True,
            slot_interval_minutes=30,
            buffer_time_minutes=15,
            concurrent_bookings_allowed=1,
        )
        avail.save()
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        print(f"✓ Created recurring availability for {day_names[day_of_week]}: {avail.id}")
    
    # Create non-recurring availability for the next 7 days
    today = date.today()
    for i in range(7):
        target_date = today + timedelta(days=i)
        avail = Availability(
            tenant_id=tenant_id,
            staff_id=staff_id,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=False,
            effective_from=target_date,
            effective_to=target_date,
            is_active=True,
            slot_interval_minutes=30,
            buffer_time_minutes=15,
            concurrent_bookings_allowed=1,
        )
        avail.save()
        print(f"✓ Created availability for {target_date}: {avail.id}")
    
    print("\n✓ Availability setup complete!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python setup_availability_for_booking.py <staff_id> <tenant_id>")
        print("\nExample:")
        print("  python setup_availability_for_booking.py 6994a43827c33e0380d54428 <your_tenant_id>")
        sys.exit(1)
    
    staff_id = sys.argv[1]
    tenant_id = sys.argv[2]
    
    try:
        setup_availability_for_staff(staff_id, tenant_id)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
