#!/usr/bin/env python
"""Check existing appointments in the database."""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
sys.path.insert(0, os.path.dirname(__file__))

# Initialize app
from app.main import app
from app.db import init_db
from app.models.appointment import Appointment
from app.models.staff import Staff

# Initialize database
init_db()

# Get all appointments
print("=" * 80)
print("CHECKING APPOINTMENTS IN DATABASE")
print("=" * 80)

appointments = Appointment.objects()
print(f"\nTotal appointments: {appointments.count()}")

if appointments.count() > 0:
    print("\nAppointments by staff:")
    staff_dict = {}
    for apt in appointments:
        staff_id = str(apt.staff_id)
        if staff_id not in staff_dict:
            staff_dict[staff_id] = []
        staff_dict[staff_id].append(apt)
    
    for staff_id, apts in staff_dict.items():
        print(f"\n  Staff ID: {staff_id}")
        for apt in apts:
            print(f"    - Start: {apt.start_time.isoformat()}")
            print(f"      End:   {apt.end_time.isoformat()}")
            print(f"      Status: {apt.status}")
            print(f"      ID: {apt.id}")
else:
    print("\nNo appointments found in database")

print("\n" + "=" * 80)
