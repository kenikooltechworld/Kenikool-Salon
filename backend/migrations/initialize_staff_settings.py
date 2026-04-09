"""
Migration script to initialize staff_settings records for existing staff users.
Run this after deploying the staff_settings model and routes.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db, close_db
from app.models.user import User
from app.models.staff_settings import StaffSettings
from bson import ObjectId


def initialize_staff_settings():
    """Initialize staff_settings records for all staff users."""
    init_db()
    
    try:
        # Find all staff users
        staff_users = User.objects(role_names__in=["Staff"]).all()
        
        print(f"Found {len(staff_users)} staff users")
        
        created_count = 0
        skipped_count = 0
        
        for user in staff_users:
            # Check if settings already exist
            existing_settings = StaffSettings.objects(
                tenant_id=user.tenant_id,
                user_id=user.id
            ).first()
            
            if existing_settings:
                print(f"  ✓ Settings already exist for {user.email}")
                skipped_count += 1
                continue
            
            # Create new staff settings
            try:
                settings = StaffSettings(
                    tenant_id=user.tenant_id,
                    user_id=user.id,
                    first_name=user.first_name or "",
                    last_name=user.last_name or "",
                    phone=getattr(user, 'phone', None),
                    email_bookings=True,
                    email_reminders=True,
                    email_messages=True,
                    sms_bookings=False,
                    sms_reminders=False,
                    push_bookings=True,
                    push_reminders=True,
                )
                settings.save()
                print(f"  ✓ Created settings for {user.email}")
                created_count += 1
            except Exception as e:
                print(f"  ✗ Failed to create settings for {user.email}: {str(e)}")
        
        print(f"\nMigration complete:")
        print(f"  Created: {created_count}")
        print(f"  Skipped: {skipped_count}")
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise
    finally:
        close_db()


if __name__ == "__main__":
    initialize_staff_settings()
