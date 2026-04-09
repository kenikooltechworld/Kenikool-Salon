#!/usr/bin/env python
"""Simple diagnostic for timeslot issues."""

import sys
from pathlib import Path
from datetime import date

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.db import init_db
from app.models.availability import Availability

init_db()

today = date.today()
day_of_week = today.weekday()

print(f"Today: {today}, Day of week: {day_of_week} (0=Mon, 4=Fri)")

# Get all availability records
all_avail = list(Availability.objects())
print(f"\nTotal availability records: {len(all_avail)}")

# Get recurring for today
recurring = list(Availability.objects(
    is_recurring=True,
    day_of_week=day_of_week,
    is_active=True
))

print(f"Recurring availability for today: {len(recurring)}")
for avail in recurring:
    print(f"  - effective_from: {avail.effective_from}, today: {today}")
    print(f"    effective_from <= today? {avail.effective_from <= today}")
