#!/usr/bin/env python
"""Initialize staff settings for existing staff members who don't have settings."""

import logging
from app.db import init_db, close_db
from app.models.staff import Staff
from app.models.staff_settings import StaffSettings
from app.models.user import User
from bson import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_staff_settings():
    """Initialize staff settings for all staff members without settings."""
    try:
        init_db()
        logger.info("Database initialized")
        
        # Get all staff members
        all_staff = Staff.objects()
        logger.info(f"Found {all_staff.count()} staff members")
        
        initialized_count = 0
        skipped_count = 0
        
        for staff in all_staff:
            # Check if settings already exist
            existing_settings = StaffSettings.objects(
                tenant_id=staff.tenant_id,
                user_id=staff.user_id
            ).first()
            
            if existing_settings:
                skipped_count += 1
                logger.info(f"Settings already exist for staff {staff.user_id}")
                continue
            
            # Get user info
            user = User.objects(id=staff.user_id).first()
            if not user:
                logger.warning(f"User not found for staff {staff.user_id}")
                continue
            
            # Create default settings
            try:
                staff_settings = StaffSettings(
                    tenant_id=staff.tenant_id,
                    user_id=staff.user_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone=user.phone or "",
                    email_bookings=True,
                    email_reminders=True,
                    email_messages=True,
                    sms_bookings=False,
                    sms_reminders=False,
                    push_bookings=True,
                    push_reminders=True,
                )
                staff_settings.save()
                initialized_count += 1
                logger.info(f"Initialized settings for staff {staff.user_id}")
            except Exception as e:
                logger.error(f"Failed to initialize settings for staff {staff.user_id}: {str(e)}")
        
        logger.info(f"Initialization complete: {initialized_count} initialized, {skipped_count} skipped")
        
    except Exception as e:
        logger.error(f"Failed to initialize staff settings: {str(e)}", exc_info=True)
    finally:
        close_db()


if __name__ == "__main__":
    initialize_staff_settings()
