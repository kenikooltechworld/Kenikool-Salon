#!/usr/bin/env python
"""Quick test to verify availability slots endpoint works."""

import sys
from datetime import datetime, date, time
from bson import ObjectId
from mongoengine import connect, disconnect

# Connect to MongoDB
try:
    disconnect()
    connect('salon_test', host='mongodb://localhost:27017')
except Exception as e:
    print(f"MongoDB connection error: {e}")
    print("Make sure MongoDB is running on localhost:27017")
    sys.exit(1)

from app.models.tenant import Tenant
from app.models.user import User
from app.models.availability import Availability
from app.models.service import Service
from app.models.staff import Staff
from app.services.auth_service import AuthService
from app.context import set_tenant_id

# Create test data
print("Creating test data...")
tenant = Tenant(
    name="Test Salon",
    subscription_tier="professional",
    status="active",
    region="us-east-1",
)
tenant.save()
print(f"Created tenant: {tenant.id}")

# Create staff
staff = Staff(
    tenant_id=tenant.id,
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    phone="+1234567890",
    role="stylist",
    is_active=True,
)
staff.save()
print(f"Created staff: {staff.id}")

# Create service
service = Service(
    tenant_id=tenant.id,
    name="Haircut",
    description="Professional haircut",
    duration_minutes=30,
    price=50.00,
    category="Hair",
    is_active=True,
)
service.save()
print(f"Created service: {service.id}")

# Create availability for today
today = date.today()
availability = Availability(
    tenant_id=tenant.id,
    staff_id=staff.id,
    day_of_week=today.weekday(),
    start_time="09:00:00",
    end_time="17:00:00",
    is_recurring=True,
    effective_from=today,
    is_active=True,
)
availability.save()
print(f"Created availability: {availability.id}")

# Test the availability calculator
print("\nTesting availability calculator...")
from app.utils.availability_calculator import AvailabilityCalculator

set_tenant_id(tenant.id)
calculator = AvailabilityCalculator()

try:
    slots = calculator.get_available_slots(
        tenant_id=tenant.id,
        staff_id=staff.id,
        target_date=today,
        service_duration_minutes=30,
    )
    print(f"✓ Got {len(slots)} available slots")
    if slots:
        print(f"  First slot: {slots[0]}")
except Exception as e:
    print(f"✗ Error getting slots: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
print("\nCleaning up...")
availability.delete()
service.delete()
staff.delete()
tenant.delete()
print("Done!")
