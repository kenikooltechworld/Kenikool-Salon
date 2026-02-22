#!/usr/bin/env python
"""Test response format."""

from datetime import date, time
from app.schemas.public_booking import AvailabilitySlot, AvailabilityResponse

# Create test slots
slots = [
    AvailabilitySlot(time=time(9, 0), available=True),
    AvailabilitySlot(time=time(9, 30), available=True),
    AvailabilitySlot(time=time(10, 0), available=False),
]

# Create response
response = AvailabilityResponse(
    date=date.today(),
    slots=slots,
)

# Print response
print("Response model dump:")
print(response.model_dump())

print("\nResponse model dump with alias:")
print(response.model_dump(by_alias=True))

print("\nResponse JSON:")
print(response.model_dump_json(by_alias=True))
