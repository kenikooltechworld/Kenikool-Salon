#!/usr/bin/env python
"""Test public availability endpoint."""

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
from app.models.service import Service
from app.models.staff import Staff
from app.models.availability import Availability
from app.services.auth_service import AuthService

# Create test data
print("Creating test data...")
tenant = Tenant(
    name="Test Salon",
    subscription_tier="professional",
    status="active",
    region="us-east-1",
    is_published=True,
)
tenant.save()
print(f"Created tenant: {tenant.id}")

# Create user for staff
user = User(
    tenant_id=tenant.id,
    email="staff@example.com",
    password_hash=AuthService.hash_password("password123"),
    first_name="John",
    last_name="Doe",
    role_id=ObjectId(),
    status="active",
)
user.save()
print(f"Created user: {user.id}")

# Create staff
staff = Staff(
    tenant_id=tenant.id,
    user_id=user.id,
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    phone="+1234567890",
    role="stylist",
    is_active=True,
    is_available_for_public_booking=True,
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
    is_published=True,
    allow_public_booking=True,
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
    slot_interval_minutes=30,
    buffer_time_minutes=15,
    concurrent_bookings_allowed=1,
)
availability.save()
print(f"Created availability: {availability.id}")

# Test the availability calculator
print("\nTesting availability calculator...")
from app.utils.availability_calculator import AvailabilityCalculator

slots = AvailabilityCalculator.get_available_slots(
    tenant_id=tenant.id,
    staff_id=staff.id,
    service_id=service.id,
    booking_date=today,
)

print(f"✓ Got {len(slots)} available slots")
if slots:
    print(f"  First 5 slots:")
    for slot in slots[:5]:
        print(f"    - {slot.time} (available: {slot.available})")
else:
    print("  ✗ No slots returned!")

# Test the response format
print("\nTesting response format...")
from app.schemas.public_booking import AvailabilityResponse, AvailabilitySlot

response_slots = [
    AvailabilitySlot(slot_time=slot.time, available=slot.available) for slot in slots
]

response = AvailabilityResponse(
    availability_date=today,
    slots=response_slots,
)

print(f"Response: {response.model_dump(by_alias=True)}")

# Cleanup
print("\nCleaning up...")
availability.delete()
service.delete()
staff.delete()
user.delete()
tenant.delete()
print("Done!")
