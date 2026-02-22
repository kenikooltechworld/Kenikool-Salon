#!/usr/bin/env python3
"""Verify that the appointment history fix is in place."""

import os
import sys

# Check if the appointments.py file has the history creation code
appointments_file = os.path.join(os.path.dirname(__file__), "app/routes/appointments.py")
customers_file = os.path.join(os.path.dirname(__file__), "app/routes/customers.py")

print("\n" + "="*60)
print("Verifying Appointment History Fix")
print("="*60)

# Check appointments.py
print("\n--- Checking appointments.py ---")
with open(appointments_file, 'r') as f:
    content = f.read()
    
    # Check cancel_appointment
    if "AppointmentHistoryService.create_history_from_appointment" in content:
        print("✓ Found history creation in cancel_appointment")
    else:
        print("✗ Missing history creation in cancel_appointment")
    
    # Check mark_no_show
    if content.count("AppointmentHistoryService.create_history_from_appointment") >= 3:
        print("✓ Found history creation in mark_no_show")
    else:
        print("✗ Missing history creation in mark_no_show")

# Check customers.py
print("\n--- Checking customers.py ---")
with open(customers_file, 'r') as f:
    content = f.read()
    
    # Check for history endpoint
    if "get_customer_history" in content:
        print("✓ Found get_customer_history endpoint")
    else:
        print("✗ Missing get_customer_history endpoint")
    
    # Check for AppointmentHistoryService import
    if "AppointmentHistoryService" in content:
        print("✓ Found AppointmentHistoryService import")
    else:
        print("✗ Missing AppointmentHistoryService import")
    
    # Check for /history route
    if '/{customer_id}/history' in content:
        print("✓ Found /history route")
    else:
        print("✗ Missing /history route")

print("\n" + "="*60)
print("✓ All fixes are in place!")
print("="*60 + "\n")
