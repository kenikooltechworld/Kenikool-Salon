#!/usr/bin/env python3
"""
Script to check what data is actually being received by the backend
when creating a staff member.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import connect_db
from app.models.staff import Staff
from bson import ObjectId

def check_latest_staff():
    """Check the latest staff member created."""
    connect_db()
    
    # Get the most recent staff member
    latest_staff = Staff.objects().order_by('-created_at').first()
    
    if not latest_staff:
        print("No staff members found in database")
        return
    
    print("=" * 60)
    print("LATEST STAFF MEMBER DATA")
    print("=" * 60)
    print(f"ID: {latest_staff.id}")
    print(f"User ID: {latest_staff.user_id}")
    print(f"Created At: {latest_staff.created_at}")
    print(f"\nSpecialties: {latest_staff.specialties}")
    print(f"  Type: {type(latest_staff.specialties)}")
    print(f"  Length: {len(latest_staff.specialties)}")
    print(f"  Content: {latest_staff.specialties}")
    print(f"\nCertifications: {latest_staff.certifications}")
    print(f"  Type: {type(latest_staff.certifications)}")
    print(f"  Length: {len(latest_staff.certifications)}")
    print(f"  Content: {latest_staff.certifications}")
    print(f"\nCertification Files: {latest_staff.certification_files}")
    print(f"  Type: {type(latest_staff.certification_files)}")
    print(f"  Length: {len(latest_staff.certification_files)}")
    print(f"  Content: {latest_staff.certification_files}")
    print("=" * 60)

if __name__ == "__main__":
    check_latest_staff()
