"""
Migration script to consolidate booking systems.

This script:
1. Adds new fields to Appointment model for public booking support
2. Migrates existing PublicBooking records to Appointment model
3. Marks existing appointments as internal (is_guest=False)
"""

import os
import sys
from datetime import datetime
from bson import ObjectId

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.appointment import Appointment
from app.models.public_booking import PublicBooking
from app.models.customer import Customer
from app.context import set_tenant_context


def migrate_appointments():
    """Mark all existing appointments as internal bookings."""
    print("Marking existing appointments as internal bookings...")
    
    # Update all appointments without is_guest flag to be internal
    result = Appointment.objects(is_guest__exists=False).update(
        set__is_guest=False
    )
    
    print(f"✓ Updated {result} existing appointments to is_guest=False")


def migrate_public_bookings():
    """Migrate PublicBooking records to Appointment model."""
    print("\nMigrating public bookings to appointments...")
    
    public_bookings = PublicBooking.objects()
    migrated_count = 0
    
    for pb in public_bookings:
        try:
            # Check if appointment already exists for this public booking
            existing_apt = Appointment.objects(
                tenant_id=pb.tenant_id,
                idempotency_key=pb.idempotency_key
            ).first()
            
            if existing_apt:
                print(f"  - Appointment already exists for public booking {pb.id}")
                continue
            
            # Get or create guest customer
            customer = Customer.objects(
                tenant_id=pb.tenant_id,
                email=pb.customer_email
            ).first()
            
            if not customer:
                # Create guest customer
                name_parts = pb.customer_name.split(' ', 1)
                customer = Customer(
                    tenant_id=pb.tenant_id,
                    first_name=name_parts[0],
                    last_name=name_parts[1] if len(name_parts) > 1 else "",
                    email=pb.customer_email,
                    phone=pb.customer_phone,
                    is_guest=True,
                )
                customer.save()
                print(f"  - Created guest customer {customer.id} for {pb.customer_email}")
            
            # Convert booking_date and booking_time to datetime
            from datetime import datetime as dt
            booking_datetime = dt.combine(
                pb.booking_date,
                dt.strptime(pb.booking_time, "%H:%M").time()
            )
            
            # Calculate end time
            from datetime import timedelta
            end_datetime = booking_datetime + timedelta(minutes=pb.duration_minutes)
            
            # Create appointment from public booking
            appointment = Appointment(
                tenant_id=pb.tenant_id,
                customer_id=customer.id,
                staff_id=pb.staff_id,
                service_id=pb.service_id,
                start_time=booking_datetime,
                end_time=end_datetime,
                status=pb.status,
                notes=pb.notes,
                price=None,  # Will be set from service
                payment_id=pb.payment_id,
                payment_option=pb.payment_option,
                payment_status=pb.payment_status,
                idempotency_key=pb.idempotency_key,
                is_guest=True,
                guest_name=pb.customer_name,
                guest_email=pb.customer_email,
                guest_phone=pb.customer_phone,
                reminder_24h_sent=pb.reminder_24h_sent,
                reminder_1h_sent=pb.reminder_1h_sent,
                ip_address=pb.ip_address,
                user_agent=pb.user_agent,
                created_at=pb.created_at,
                updated_at=pb.updated_at,
            )
            
            # Handle cancellation
            if pb.status == "cancelled":
                appointment.cancelled_at = pb.cancelled_at
                appointment.cancellation_reason = pb.cancellation_reason
            
            appointment.save()
            migrated_count += 1
            print(f"  ✓ Migrated public booking {pb.id} to appointment {appointment.id}")
            
        except Exception as e:
            print(f"  ✗ Error migrating public booking {pb.id}: {str(e)}")
    
    print(f"\n✓ Migrated {migrated_count} public bookings to appointments")


def verify_migration():
    """Verify migration was successful."""
    print("\nVerifying migration...")
    
    # Count appointments
    total_appointments = Appointment.objects().count()
    internal_appointments = Appointment.objects(is_guest=False).count()
    guest_appointments = Appointment.objects(is_guest=True).count()
    
    print(f"  Total appointments: {total_appointments}")
    print(f"  Internal appointments: {internal_appointments}")
    print(f"  Guest appointments: {guest_appointments}")
    
    # Count public bookings (should still exist for now)
    total_public_bookings = PublicBooking.objects().count()
    print(f"  Total public bookings (legacy): {total_public_bookings}")
    
    # Count guest customers
    guest_customers = Customer.objects(is_guest=True).count()
    print(f"  Guest customers: {guest_customers}")
    
    print("\n✓ Migration verification complete")


if __name__ == "__main__":
    print("=" * 60)
    print("BOOKING SYSTEM CONSOLIDATION MIGRATION")
    print("=" * 60)
    
    try:
        migrate_appointments()
        migrate_public_bookings()
        verify_migration()
        
        print("\n" + "=" * 60)
        print("✓ MIGRATION COMPLETE")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test public booking creation")
        print("2. Test internal booking creation")
        print("3. Verify both flows work correctly")
        print("4. Once verified, delete PublicBooking model and routes")
        
    except Exception as e:
        print(f"\n✗ MIGRATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
