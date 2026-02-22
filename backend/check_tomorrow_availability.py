#!/usr/bin/env python
"""Check availability for tomorrow."""

import sys
import os
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from app.models.staff import Staff
from app.models.availability import Availability
from bson import ObjectId

def check():
    """Check tomorrow's availability."""
    init_db()
    
    # Get first tenant and staff
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenants found")
        return
    
    staff = Staff.objects(tenant_id=tenant.id).first()
    if not staff:
        print("No staff found")
        return
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    print(f"Today: {today} ({['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][today.weekday()]})")
    print(f"Tomorrow: {tomorrow} ({['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][tomorrow.weekday()]})")
    print()
    
    # Check recurring availability for tomorrow
    day_of_week = tomorrow.weekday()
    recurring = list(Availability.objects(
        tenant_id=tenant.id,
        staff_id=staff.id,
        is_recurring=True,
        day_of_week=day_of_week,
        is_active=True,
    ))
    print(f"Recurring availability for {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week]}: {len(recurring)} found")
    for avail in recurring:
        print(f"  - {avail.start_time} to {avail.end_time}")
    
    # Check specific date availability for tomorrow
    specific = list(Availability.objects(
        tenant_id=tenant.id,
        staff_id=staff.id,
        is_recurring=False,
        is_active=True,
        effective_from__lte=tomorrow,
    ).filter(
        Q(effective_to__gte=tomorrow) | Q(effective_to__exists=False)
    ))
    print(f"\nSpecific date availability for {tomorrow}: {len(specific)} found")
    for avail in specific:
        print(f"  - {avail.effective_from} to {avail.effective_to}: {avail.start_time} to {avail.end_time}")
    
    if not recurring and not specific:
        print(f"\n⚠️  NO AVAILABILITY FOR TOMORROW!")
        print(f"\nTo fix, run:")
        print(f"python setup_availability_for_booking.py {staff.id} {tenant.id}")

if __name__ == "__main__":
    from mongoengine import Q
    try:
        check()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
