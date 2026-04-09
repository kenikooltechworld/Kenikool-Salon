#!/usr/bin/env python
"""Check and fix staff availability."""

import sys
from pathlib import Path
from datetime import date

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.db import connect_db
from app.models.staff import Staff
from app.models.availability import Availability

connect_db()

# Get all active staff
staff_members = Staff.objects(status="active")
print(f"Found {staff_members.count()} active staff members\n")

for staff in staff_members:
    print(f"Staff: {staff.user_id.first_name} {staff.user_id.last_name}")
    
    # Check existing availability
    existing = Availability.objects(
        tenant_id=staff.tenant_id,
        staff_id=staff.id
    )
    
    print(f"  Existing availability records: {existing.count()}")
    
    if existing.count() == 0:
        print(f"  Creating default availability (Mon-Fri, 9 AM - 5 PM)...")
        
        for day in range(5):  # Monday-Friday
            availability = Availability(
                tenant_id=staff.tenant_id,
                staff_id=staff.id,
                day_of_week=day,
                start_time="09:00:00",
                end_time="17:00:00",
                is_recurring=True,
                effective_from=date.today(),
                effective_to=None,
                breaks=[{"start_time": "12:00:00", "end_time": "13:00:00"}],
                slot_interval_minutes=30,
                buffer_time_minutes=15,
                concurrent_bookings_allowed=1,
                is_active=True,
                notes="Default availability",
            )
            availability.save()
        
        print(f"  ✓ Created 5 availability records")
    else:
        for avail in existing:
            day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][avail.day_of_week] if avail.day_of_week is not None else "Custom"
            print(f"    - {day_name}: {avail.start_time} - {avail.end_time} (active: {avail.is_active})")
    
    print()

print("Done!")
