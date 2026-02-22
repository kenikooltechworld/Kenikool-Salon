#!/usr/bin/env python
"""Diagnose the booking availability issue."""

import sys
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from app.models.staff import Staff
from app.models.availability import Availability
from app.models.appointment import Appointment
from bson import ObjectId

def diagnose():
    """Diagnose the booking issue."""
    init_db()
    
    print("=" * 80)
    print("BOOKING AVAILABILITY DIAGNOSTIC")
    print("=" * 80)
    
    # List all tenants
    tenants = list(Tenant.objects())
    print(f"\n1. TENANTS ({len(tenants)} found)")
    print("-" * 80)
    for tenant in tenants:
        print(f"   ID: {tenant.id}")
        print(f"   Name: {tenant.name}")
        print()
    
    if not tenants:
        print("   ⚠️  No tenants found!")
        return
    
    # Use first tenant
    tenant = tenants[0]
    print(f"\nUsing tenant: {tenant.id} ({tenant.name})")
    
    # List all staff
    staff_list = list(Staff.objects(tenant_id=tenant.id))
    print(f"\n2. STAFF ({len(staff_list)} found)")
    print("-" * 80)
    for staff in staff_list:
        print(f"   ID: {staff.id}")
        print(f"   User ID: {staff.user_id}")
        print(f"   Status: {staff.status}")
        print()
    
    if not staff_list:
        print("   ⚠️  No staff found!")
        return
    
    # Use first staff
    staff = staff_list[0]
    print(f"\nUsing staff: {staff.id} (User: {staff.user_id})")
    
    # Check availability records
    today = date.today()
    print(f"\n3. AVAILABILITY RECORDS for {today}")
    print("-" * 80)
    
    day_of_week = today.weekday()
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    print(f"   Today is: {day_names[day_of_week]}")
    
    # Check recurring availability
    recurring = list(Availability.objects(
        tenant_id=tenant.id,
        staff_id=staff.id,
        is_recurring=True,
        day_of_week=day_of_week,
        is_active=True,
    ))
    print(f"\n   Recurring availability for {day_names[day_of_week]}: {len(recurring)} found")
    for avail in recurring:
        print(f"      - {avail.start_time} to {avail.end_time}")
    
    # Check specific date availability
    specific = list(Availability.objects(
        tenant_id=tenant.id,
        staff_id=staff.id,
        is_recurring=False,
        is_active=True,
        effective_from__lte=today,
    ))
    print(f"\n   Specific date availability: {len(specific)} found")
    for avail in specific:
        print(f"      - {avail.effective_from} to {avail.effective_to}: {avail.start_time} to {avail.end_time}")
    
    # Check all availability records
    all_avail = list(Availability.objects(tenant_id=tenant.id, staff_id=staff.id))
    print(f"\n   Total availability records: {len(all_avail)}")
    
    # Check appointments
    print(f"\n4. APPOINTMENTS for {today}")
    print("-" * 80)
    from datetime import datetime, time
    start_datetime = datetime.combine(today, time.min)
    end_datetime = datetime.combine(today, time.max)
    
    appointments = list(Appointment.objects(
        tenant_id=tenant.id,
        staff_id=staff.id,
        start_time__gte=start_datetime,
        start_time__lt=end_datetime,
    ))
    print(f"   Appointments: {len(appointments)} found")
    for appt in appointments:
        print(f"      - {appt.start_time} to {appt.end_time} (Status: {appt.status})")
    
    # Summary and recommendations
    print(f"\n5. SUMMARY & RECOMMENDATIONS")
    print("-" * 80)
    
    if not recurring and not specific:
        print("   ⚠️  NO AVAILABILITY RECORDS FOUND!")
        print(f"\n   To fix this, run:")
        print(f"   python setup_availability_for_booking.py {staff.id} {tenant.id}")
        print(f"\n   Or use the setup_test_availability.py script")
    else:
        print("   ✓ Availability records exist")
        if not recurring and not specific:
            print("   ⚠️  But none match today's date!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        diagnose()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
