#!/usr/bin/env python3
"""Debug verification code issue."""

import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.config import Settings
from app.db import init_db
from app.models.temp_registration import TempRegistration

def debug_verification():
    """Debug verification code storage and retrieval."""
    # Initialize database
    init_db()
    
    # Find all temp registrations
    temp_regs = TempRegistration.objects()
    print(f"\nTotal temp registrations: {len(temp_regs)}")
    
    for temp_reg in temp_regs:
        print(f"\n--- Temp Registration ---")
        print(f"Email: {temp_reg.email}")
        print(f"Subdomain: {temp_reg.subdomain}")
        print(f"Verification Code: {temp_reg.verification_code}")
        print(f"Code Expires: {temp_reg.verification_code_expires}")
        print(f"Is Code Expired: {temp_reg.is_code_expired}")
        print(f"Attempt Count: {temp_reg.attempt_count}")
        print(f"Is Locked: {temp_reg.is_locked}")
        print(f"Created At: {temp_reg.created_at}")
        print(f"Expires At: {temp_reg.expires_at}")

if __name__ == "__main__":
    debug_verification()
