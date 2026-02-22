#!/usr/bin/env python
"""Test schema validation with camelCase input."""

import sys
sys.path.insert(0, '.')

from app.schemas.appointment import AppointmentCreateRequest
from datetime import datetime

# Test with camelCase (what frontend sends)
test_data = {
    "customerId": "507f1f77bcf86cd799439011",
    "staffId": "507f1f77bcf86cd799439012",
    "serviceId": "507f1f77bcf86cd799439013",
    "startTime": "2024-01-20T14:30:00",
    "endTime": "2024-01-20T15:30:00",
    "paymentOption": "now"
}

try:
    request = AppointmentCreateRequest.model_validate(test_data)
    print("✓ Schema validation passed with camelCase input")
    print(f"  customer_id: {request.customer_id}")
    print(f"  staff_id: {request.staff_id}")
    print(f"  service_id: {request.service_id}")
    print(f"  start_time: {request.start_time}")
    print(f"  end_time: {request.end_time}")
    print(f"  payment_option: {request.payment_option}")
except Exception as e:
    print(f"✗ Schema validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
