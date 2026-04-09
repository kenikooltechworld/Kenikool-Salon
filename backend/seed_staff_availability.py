#!/usr/bin/env python
"""Seed staff availability records for public booking."""

import sys
from pathlib import Path
from datetime import date, time, timedelta

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.db import init_db
from app.models.staff import Staff
from app.models.availability import Availability


def seed_staff_availability():
    """Create default availability records for all active staff members."""
    print("\n" + "=" * 60)
    print("SEEDING STAFF AVAILABILITY")
    print("=" * 60)
    
    # Connect to database
    init_db()
    
    # Get all active staff members
    staff_members = Staff.objects(status="active")
    
    if not staff_members:
        print("No active staff members found. Please create staff first.")
        return False
    
    print(f"\nFound {staff_members.count()} active staff members")
    
    created_count = 0
    skipped_count = 0
    
    for staff in staff_members:
        print(f"\nProcessing staff ID: {staff.id}")
        
        # Check if availability already exists for this staff
        existing = Availability.objects(
            tenant_id=staff.tenant_id,
            staff_id=staff.id,
            is_recurring=True
        ).first()
        
        if existing:
            print(f"  ⊘ Availability already exists, skipping")
            skipped_count += 1
            continue
        
        # Create recurring availability for Monday-Friday (9 AM - 5 PM)
        for day in range(5):  # 0=Monday, 4=Friday
            availability = Availability(
                tenant_id=staff.tenant_id,
                staff_id=staff.id,
                day_of_week=day,
                start_time="09:00:00",
                end_time="17:00:00",
                is_recurring=True,
                effective_from=date.today(),
                effective_to=None,  # Ongoing
                breaks=[
                    {
                        "start_time": "12:00:00",
                        "end_time": "13:00:00",
                    }
                ],
                slot_interval_minutes=30,
                buffer_time_minutes=15,
                concurrent_bookings_allowed=1,
                is_active=True,
                notes="Default availability schedule",
            )
            availability.save()
            created_count += 1
            
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            print(f"  ✓ Created availability for {day_names[day]}")
    
    print("\n" + "=" * 60)
    print(f"AVAILABILITY SEEDING COMPLETE")
    print(f"  Created: {created_count} records")
    print(f"  Skipped: {skipped_count} staff (already had availability)")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = seed_staff_availability()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
