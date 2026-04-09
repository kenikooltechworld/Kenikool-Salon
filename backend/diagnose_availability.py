"""Diagnostic script to identify why no time slots are available."""

import sys
import os
from datetime import date, datetime, time
from bson import ObjectId

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import connect_db
from app.models.availability import Availability
from app.models.service import Service
from app.models.staff import Staff
from app.models.appointment import Appointment
from app.utils.availability_calculator import AvailabilityCalculator

def diagnose_availability(tenant_id_str, staff_id_str, service_id_str, booking_date_str):
    """Diagnose why no time slots are available."""
    
    print(f"\n{'='*80}")
    print(f"AVAILABILITY DIAGNOSTIC TOOL")
    print(f"{'='*80}\n")
    
    # Convert IDs
    try:
        tenant_id = ObjectId(tenant_id_str)
        staff_id = ObjectId(staff_id_str)
        service_id = ObjectId(service_id_str)
        booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
        print(f"✓ IDs converted successfully")
        print(f"  Tenant ID: {tenant_id}")
        print(f"  Staff ID: {staff_id}")
        print(f"  Service ID: {service_id}")
        print(f"  Booking Date: {booking_date} (Day of week: {booking_date.weekday()})\n")
    except Exception as e:
        print(f"✗ Error converting IDs: {e}")
        return
    
    # Check 1: Service exists and allows public booking
    print(f"{'='*80}")
    print(f"CHECK 1: Service Configuration")
    print(f"{'='*80}")
    service = Service.objects(tenant_id=tenant_id, id=service_id).first()
    if not service:
        print(f"✗ Service not found!")
        return
    
    print(f"✓ Service found: {service.name}")
    print(f"  - Duration: {service.duration_minutes} minutes")
    print(f"  - Price: ₦{float(service.price):,.2f}")
    print(f"  - Is Active: {service.is_active}")
    print(f"  - Is Published: {service.is_published}")
    print(f"  - Allow Public Booking: {service.allow_public_booking}")
    
    if not service.allow_public_booking:
        print(f"\n✗ ISSUE FOUND: Service does not allow public booking!")
        print(f"  Fix: Set allow_public_booking=True for this service\n")
        return
    
    # Check 2: Staff exists and is available for public booking
    print(f"\n{'='*80}")
    print(f"CHECK 2: Staff Configuration")
    print(f"{'='*80}")
    staff = Staff.objects(tenant_id=tenant_id, id=staff_id).first()
    if not staff:
        print(f"✗ Staff member not found!")
        return
    
    print(f"✓ Staff found: {staff.user_id.first_name} {staff.user_id.last_name}")
    print(f"  - Status: {staff.status}")
    print(f"  - Is Available for Public Booking: {staff.is_available_for_public_booking}")
    print(f"  - Service IDs: {[str(sid) for sid in staff.service_ids]}")
    
    if not staff.is_available_for_public_booking:
        print(f"\n✗ ISSUE FOUND: Staff is not available for public booking!")
        print(f"  Fix: Set is_available_for_public_booking=True for this staff member\n")
        return
    
    if service_id not in staff.service_ids:
        print(f"\n✗ ISSUE FOUND: Staff does not provide this service!")
        print(f"  Fix: Add service_id {service_id} to staff.service_ids\n")
        return
    
    # Check 3: Availability records exist
    print(f"\n{'='*80}")
    print(f"CHECK 3: Availability Records")
    print(f"{'='*80}")
    
    day_of_week = booking_date.weekday()
    print(f"Looking for availability on day {day_of_week} ({['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week]})")
    
    # Recurring availability
    recurring = list(Availability.objects(
        tenant_id=tenant_id,
        staff_id=staff_id,
        is_recurring=True,
        day_of_week=day_of_week,
        is_active=True,
        effective_from__lte=booking_date,
    ))
    
    print(f"\nRecurring Availability Records: {len(recurring)}")
    for avail in recurring:
        print(f"  - ID: {avail.id}")
        print(f"    Start: {avail.start_time}, End: {avail.end_time}")
        print(f"    Effective From: {avail.effective_from}, To: {avail.effective_to}")
        print(f"    Active: {avail.is_active}")
        print(f"    Slot Interval: {avail.slot_interval_minutes} min")
        print(f"    Buffer Time: {avail.buffer_time_minutes} min")
        print(f"    Concurrent Bookings: {avail.concurrent_bookings_allowed}")
        print(f"    Breaks: {avail.breaks}")
    
    # Specific date availability
    specific = list(Availability.objects(
        tenant_id=tenant_id,
        staff_id=staff_id,
        is_recurring=False,
        is_active=True,
        effective_from__lte=booking_date,
    ))
    
    print(f"\nSpecific Date Availability Records: {len(specific)}")
    for avail in specific:
        print(f"  - ID: {avail.id}")
        print(f"    Start: {avail.start_time}, End: {avail.end_time}")
        print(f"    Effective From: {avail.effective_from}, To: {avail.effective_to}")
        print(f"    Active: {avail.is_active}")
    
    if not recurring and not specific:
        print(f"\n✗ ISSUE FOUND: No availability records found for this staff member on this day!")
        print(f"  Fix: Create an availability record for staff {staff_id} on day {day_of_week}\n")
        return
    
    # Check 4: Generate slots
    print(f"\n{'='*80}")
    print(f"CHECK 4: Slot Generation")
    print(f"{'='*80}")
    
    try:
        slots = AvailabilityCalculator.get_available_slots(
            tenant_id, staff_id, service_id, booking_date
        )
        
        print(f"✓ Generated {len(slots)} available slots:")
        if slots:
            for slot in slots[:10]:  # Show first 10
                print(f"  - {slot.time.strftime('%H:%M')}")
            if len(slots) > 10:
                print(f"  ... and {len(slots) - 10} more")
        else:
            print(f"\n✗ ISSUE FOUND: No slots generated!")
            print(f"  Possible reasons:")
            print(f"  1. All slots are in the past (booking date: {booking_date}, today: {date.today()})")
            print(f"  2. All slots are booked")
            print(f"  3. Service duration doesn't fit in availability window")
            print(f"  4. Slots overlap with break times")
            
            # Check existing appointments
            print(f"\n  Checking existing appointments...")
            start_datetime = datetime.combine(booking_date, time.min)
            end_datetime = datetime.combine(booking_date, time.max)
            
            appointments = Appointment.objects(
                tenant_id=tenant_id,
                staff_id=staff_id,
                status__ne="cancelled",
                start_time__gte=start_datetime,
                start_time__lt=end_datetime
            )
            
            print(f"  Found {appointments.count()} appointments on this date:")
            for appt in appointments:
                print(f"    - {appt.start_time.strftime('%H:%M')} - {appt.end_time.strftime('%H:%M')} ({appt.status})")
    
    except Exception as e:
        print(f"✗ Error generating slots: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*80}")
    print(f"DIAGNOSTIC COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Connect to database
    connect_db()
    
    # Get parameters from command line or use defaults
    if len(sys.argv) >= 5:
        tenant_id = sys.argv[1]
        staff_id = sys.argv[2]
        service_id = sys.argv[3]
        booking_date = sys.argv[4]
    else:
        print("Usage: python diagnose_availability.py <tenant_id> <staff_id> <service_id> <booking_date>")
        print("Example: python diagnose_availability.py 69c430044140ea2e9ce75a02 <staff_id> <service_id> 2026-03-26")
        print("\nPlease provide the IDs from your public booking interface.")
        sys.exit(1)
    
    diagnose_availability(tenant_id, staff_id, service_id, booking_date)
