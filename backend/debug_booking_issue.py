#!/usr/bin/env python
"""Debug script to check existing appointments and booking issue."""

import os
import sys
from datetime import datetime
from bson import ObjectId

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import db
from app.models.appointment import Appointment
from app.models.staff import Staff

# Connect to DB
db.connect()

# Get all appointments
appointments = Appointment.objects()
print(f'Total appointments: {appointments.count()}')
print()

# Group by staff
staff_appointments = {}
for apt in appointments:
    staff_id = str(apt.staff_id)
    if staff_id not in staff_appointments:
        staff_appointments[staff_id] = []
    staff_appointments[staff_id].append(apt)

# Print appointments by staff
for staff_id, apts in staff_appointments.items():
    print(f'Staff {staff_id}:')
    for apt in apts:
        print(f'  - Start: {apt.start_time.isoformat()}, End: {apt.end_time.isoformat()}, Status: {apt.status}')
    print()

# Check if there are any non-cancelled appointments
non_cancelled = Appointment.objects(status__ne='cancelled')
print(f'Non-cancelled appointments: {non_cancelled.count()}')
