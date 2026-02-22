#!/usr/bin/env python
"""Test the availability endpoint with debug logging."""

import sys
import os
import logging
from datetime import date, timedelta
from dotenv import load_dotenv

# Setup logging BEFORE importing app modules
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from app.models.staff import Staff
from app.models.service import Service
from app.models.availability import Availability
from app.utils.availability_calculator import AvailabilityCalculator
from bson import ObjectId

def test():
    """Test availability calculation."""
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
    
    service = Service.objects(tenant_id=tenant.id).first()
    if not service:
        print("No services found")
        return
    
    tomorrow = date.today() + timedelta(days=1)
    
    print(f"\n{'='*80}")
    print(f"Tenant ID: {tenant.id}")
    print(f"Staff ID: {staff.id}")
    print(f"Service ID: {service.id}")
    print(f"Service Duration: {service.duration_minutes} minutes")
    print(f"Target Date: {tomorrow}")
    print(f"{'='*80}\n")
    
    # Check what's in the database
    print("Checking database for availability records...")
    day_of_week = tomorrow.weekday()
    all_avail = list(Availability.objects(tenant_id=tenant.id, staff_id=staff.id))
    print(f"Total availability records for this staff: {len(all_avail)}")
    for avail in all_avail:
        print(f"  - ID: {avail.id}")
        print(f"    Recurring: {avail.is_recurring}, Day: {avail.day_of_week}, Active: {avail.is_active}")
        print(f"    From: {avail.effective_from}, To: {avail.effective_to}")
        print(f"    Time: {avail.start_time} to {avail.end_time}")
    
    print(f"\n{'='*80}\n")
    
    # Call the calculator directly
    print("Calling AvailabilityCalculator.get_available_slots()...")
    slots = AvailabilityCalculator.get_available_slots(
        tenant_id=tenant.id,
        staff_id=staff.id,
        service_id=service.id,
        booking_date=tomorrow,
    )
    
    print(f"\nResult: {len(slots)} slots found")
    for slot in slots[:5]:  # Show first 5
        print(f"  - {slot.time}")
    if len(slots) > 5:
        print(f"  ... and {len(slots) - 5} more")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
