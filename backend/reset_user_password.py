#!/usr/bin/env python
"""Reset user password to a known value."""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.user import User
from app.services.auth_service import AuthenticationService
from app.config import Settings

print("Initializing database...")
init_db()

settings = Settings()
auth_service = AuthenticationService(settings)

# Reset password for both users
users_to_reset = [
    "kenikooltechworld@gmail.com",
    "princechaawa@gmail.com"
]

test_password = "Password123!"

for email in users_to_reset:
    user = User.objects(email=email).first()
    if user:
        hashed = auth_service.hash_password(test_password)
        user.password_hash = hashed
        user.save()
        print(f"✓ Reset password for {email}")
        print(f"  New password: {test_password}")
    else:
        print(f"✗ User not found: {email}")

print("\n✓ All passwords reset successfully!")
print(f"\nYou can now login with:")
print(f"  Email: kenikooltechworld@gmail.com")
print(f"  Password: {test_password}")
