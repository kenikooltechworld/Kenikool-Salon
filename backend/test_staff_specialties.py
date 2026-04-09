"""Test script to verify staff specialties and certifications are saved correctly."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db import connect_db
from app.models.staff import Staff
from app.models.user import User
from bson import ObjectId

def test_staff_specialties():
    """Test that staff specialties and certifications are saved and retrieved correctly."""
    connect_db()
    
    print("\n=== Testing Staff Specialties and Certifications ===\n")
    
    # Find a staff member
    staff = Staff.objects().first()
    
    if not staff:
        print("❌ No staff members found in database")
        return
    
    print(f"Staff ID: {staff.id}")
    print(f"User ID: {staff.user_id}")
    
    # Get user details
    user = User.objects(id=staff.user_id).first()
    if user:
        print(f"Name: {user.first_name} {user.last_name}")
        print(f"Email: {user.email}")
    
    print(f"\nSpecialties ({len(staff.specialties)}):")
    if staff.specialties:
        for i, specialty in enumerate(staff.specialties, 1):
            print(f"  {i}. {specialty}")
    else:
        print("  (none)")
    
    print(f"\nCertifications ({len(staff.certifications)}):")
    if staff.certifications:
        for i, cert in enumerate(staff.certifications, 1):
            print(f"  {i}. {cert}")
    else:
        print("  (none)")
    
    print(f"\nCertificate Files ({len(staff.certification_files)}):")
    if staff.certification_files:
        for i, file_url in enumerate(staff.certification_files, 1):
            print(f"  {i}. {file_url}")
    else:
        print("  (none)")
    
    print("\n=== Test Complete ===\n")

if __name__ == "__main__":
    test_staff_specialties()
