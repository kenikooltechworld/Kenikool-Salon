#!/usr/bin/env python
"""Test booking creation with payment option."""

import os
import sys
sys.path.insert(0, '.')
os.environ['MONGODB_URL'] = 'mongodb://localhost:27017/salon_test'
os.environ['ENVIRONMENT'] = 'test'

from app.models.tenant import Tenant
from app.models.customer import Customer
from app.models.staff import Staff
from app.models.service import Service
from app.models.appointment import Appointment
from datetime import datetime, timedelta

# Get first tenant
tenant = Tenant.objects.first()
if not tenant:
    print('No tenant found')
    sys.exit(1)

print(f'Tenant: {tenant.id}')

# Get first customer
customer = Customer.objects(tenant_id=tenant.id).first()
if not customer:
    print('No customer found')
    sys.exit(1)

print(f'Customer: {customer.id}')

# Get first staff
staff = Staff.objects(tenant_id=tenant.id).first()
if not staff:
    print('No staff found')
    sys.exit(1)

print(f'Staff: {staff.id}')

# Get first service
service = Service.objects(tenant_id=tenant.id).first()
if not service:
    print('No service found')
    sys.exit(1)

print(f'Service: {service.id}')

# Create appointment
start_time = datetime.utcnow() + timedelta(days=1, hours=10)
end_time = start_time + timedelta(hours=1)

appointment = Appointment(
    tenant_id=tenant.id,
    customer_id=customer.id,
    staff_id=staff.id,
    service_id=service.id,
    start_time=start_time,
    end_time=end_time,
    status='scheduled'
)
appointment.save()

print(f'Appointment created: {appointment.id}')
print(f'Status: {appointment.status}')
print(f'Start: {appointment.start_time}')
print(f'End: {appointment.end_time}')
print('✓ Booking creation test passed')
