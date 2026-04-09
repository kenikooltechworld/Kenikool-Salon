#!/usr/bin/env python
"""Diagnose timeslot availability issues."""

import sys
from pathlib import Path
from datetime import date, datetime

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.db import init_db
from app.models.staff import Staff
from app.models.service import Service
from app.models.availability import Availability
from app.utils.availability_calculator import AvailabilityCalculator
from bson import ObjectId


def diagnose_timeslot_issue():
    """Diagnose why timeslots are not showing."""
    print("\n" + "=" * 60)
    print("DIAGNOSING TIMESLOT AVAILABILITY ISSUE")
    print("=" * 60)
    
    # Connect to database
    init_db()
    
    # Get today's date
    today = date.today()
    day_of_week = today.weekday()
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    print(f"\nToday: {today} ({day_names[day_of_week]})")
    print(f"Day of week index: {day_of_week}")
    
    # Get first active staff
    staff = Staff.objects(status="active").first()
    if not staff:
        print("\n✗ No active staff found")
        return False
    
    print(f"\nStaff ID: {staff.id}")
    print(f"Tenant ID: {staff.tenant_id}")
    
    # Get first published service
    service = Service.objects(tenant_id=staff.tenant_id, is_published=True).first()
    if not service:
        print("\n✗ No published services found")
        return False
    
    print(f"\nService: {service.name}")
    print(f"Service ID: {service.id}")
    print(f"Duration: {service.duration_minutes} minutes")
    
    # Check availability records
    print(f"\n--- Checking Availability Records ---")
    
    # Check recurring availability for today
    recurring_avail = list(Availability.objects(
        tenant_id=staff.tenant_id,
        staff_id=staff.id,
        is_recurring=True,
        day_of_week=day_of_week,
        is_active=True
    ))
    
    print(f"\nRecurring availability records for {day_names[day_of_week]}: {len(recurring_avail)}")
    for avail in recurring_avail:
        print(f"  - ID: {avail.id}")
        print(f"    Start: {avail.start_time}, End: {avail.end_time}")
        print(f"    Effective from: {avail.effective_from}")
        print(f"    Effective to: {avail.effective_to}")
        print(f"    Is active: {avail.is_active}")
        print(f"    Breaks: {avail.breaks}")
        
        # Check if effective_from is in the future
        if avail.effective_from > today:
            print(f"    ⚠️  WARNING: effective_from ({avail.effective_from}) is AFTER today ({today})")
    
    # Check specific date availability
    specific_avail = list(Availability.objects(
        tenant_id=staff.tenant_id,
        staff_id=staff.id,
        is_recurring=False,
        is_active=True
    ))
    
    print(f"\nSpecific date availability records: {len(specific_avail)}")
    for avail in specific_avail:
        print(f"  - ID: {avail.id}")
        print(f"    Start: {avail.start_time}, End: {avail.end_time}")
        print(f"    Effective from: {avail.effective_from}")
        print(f"    Effective to: {avail.effective_to}")
    
    # Try to get available slots
    print(f"\n--- Testing AvailabilityCalculator ---")
    try:
        slots = AvailabilityCalculator.get_available_slots(
            staff.tenant_id,
            staff.id,
            service.id,
            today
        )
        
        print(f"\nAvailable slots returned: {len(slots)}")
        if slots:
            print("\nFirst 10 slots:")
            for slot in slots[:10]:
                print(f"  - {slot.time} (available: {slot.available})")
        else:
            print("\n✗ No slots returned - this is the problem!")
            
    except Exception as e:
        print(f"\n✗ Error getting slots: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    return True


if __name__ == "__main__":
    try:
        diagnose_timeslot_issue()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
