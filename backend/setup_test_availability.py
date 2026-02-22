#!/usr/bin/env python
"""Setup test availability for staff."""

import sys
import os
from datetime import datetime, date, time, timedelta
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.availability import Availability
from app.models.staff import Staff
from app.models.tenant import Tenant
from bson import ObjectId

def setup_availability():
    """Create test availability."""
    init_db()
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenants found")
        return
    
    print(f"Tenant: {tenant.id}")
    
    # Get first staff
    staff = Staff.objects(tenant_id=tenant.id).first()
    if not staff:
        print("No staff found")
        return
    
    print(f"Staff: {staff.id}")
    
    # Create recurring availability for all weekdays (Monday-Friday)
    for day_of_week in range(5):  # 0=Monday, 4=Friday
        avail = Availability(
            tenant_id=tenant.id,
            staff_id=staff.id,
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
    
    # Create non-recurring availability for today
    today = date.today()
    avail_today = Availability(
        tenant_id=tenant.id,
        staff_id=staff.id,
        start_time="09:00:00",
        end_time="17:00:00",
        is_recurring=False,
        effective_from=today,
        effective_to=today,
        is_active=True,
        slot_interval_minutes=30,
        buffer_time_minutes=15,
        concurrent_bookings_allowed=1,
    )
    avail_today.save()
    print(f"✓ Created non-recurring availability for today: {avail_today.id}")
    
    # Create non-recurring availability for tomorrow
    tomorrow = today + timedelta(days=1)
    avail_tomorrow = Availability(
        tenant_id=tenant.id,
        staff_id=staff.id,
        start_time="09:00:00",
        end_time="17:00:00",
        is_recurring=False,
        effective_from=tomorrow,
        effective_to=tomorrow,
        is_active=True,
        slot_interval_minutes=30,
        buffer_time_minutes=15,
        concurrent_bookings_allowed=1,
    )
    avail_tomorrow.save()
    print(f"✓ Created non-recurring availability for tomorrow: {avail_tomorrow.id}")
    
    print("\n✓ Test availability setup complete!")

if __name__ == "__main__":
    try:
        setup_availability()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
