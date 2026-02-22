#!/usr/bin/env python
"""Migrate existing confirmed appointments to appointment history."""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.appointment import Appointment
from app.models.appointment_history import AppointmentHistory


def migrate_appointments():
    """Migrate all confirmed appointments to history."""
    print("Starting appointment history migration...")
    
    # Get all confirmed appointments
    confirmed_appointments = list(Appointment.objects(status__in=["confirmed", "completed"]))
    total = len(confirmed_appointments)
    
    print(f"Found {total} confirmed/completed appointments")
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for appointment in confirmed_appointments:
        try:
            # Check if history already exists for this appointment
            existing_history = AppointmentHistory.objects(
                tenant_id=appointment.tenant_id,
                appointment_id=appointment.id
            ).first()
            
            if existing_history:
                skipped += 1
                continue
            
            # Calculate duration in minutes
            duration_minutes = int((appointment.end_time - appointment.start_time).total_seconds() / 60)
            
            # Use appointment price as amount paid (or 0 if not set)
            amount_paid = appointment.price or Decimal("0")
            
            # Create history entry directly
            history = AppointmentHistory(
                tenant_id=appointment.tenant_id,
                customer_id=appointment.customer_id,
                appointment_id=appointment.id,
                service_id=appointment.service_id,
                staff_id=appointment.staff_id,
                appointment_date=appointment.start_time,
                duration_minutes=duration_minutes,
                amount_paid=amount_paid,
                notes=appointment.notes,
            )
            history.save()
            migrated += 1
            print(f"  Migrated appointment {appointment.id}")
                
        except Exception as e:
            errors += 1
            print(f"  Error migrating appointment {appointment.id}: {str(e)}")
    
    print(f"\nMigration complete!")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped (already exists): {skipped}")
    print(f"  Errors: {errors}")


if __name__ == "__main__":
    migrate_appointments()
