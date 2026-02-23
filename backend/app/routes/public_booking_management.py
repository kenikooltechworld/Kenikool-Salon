"""Public booking management routes for cancellation and rescheduling."""

from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from pydantic import BaseModel

from app.models.public_booking import PublicBooking, PublicBookingStatus
from app.models.tenant import Tenant
from app.schemas.public_booking import PublicBookingResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/public", tags=["public_booking_management"])


class CancellationRequest(BaseModel):
    """Cancellation request model."""
    cancellation_reason: str | None = None


class RescheduleRequest(BaseModel):
    """Reschedule request model."""
    new_date: str  # YYYY-MM-DD format
    new_time: str  # HH:MM format


@router.post("/bookings/{booking_id}/cancel", response_model=PublicBookingResponse)
async def cancel_public_booking(
    request: Request,
    booking_id: str,
    cancellation_data: CancellationRequest,
):
    """
    Cancel a public booking.

    Args:
        booking_id: Public booking ID
        cancellation_data: Cancellation details

    Returns:
        Updated booking details
    """
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        booking_id_obj = ObjectId(booking_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Get booking
    booking = PublicBooking.objects(
        tenant_id=tenant_id_obj, id=booking_id_obj
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check if cancellation is allowed (not within 2 hours of appointment)
    booking_datetime = datetime.combine(booking.booking_date, booking.booking_time)
    time_until_appointment = booking_datetime - datetime.now()

    if time_until_appointment < timedelta(hours=2):
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel bookings within 2 hours of appointment time",
        )

    # Update booking status
    booking.status = PublicBookingStatus.CANCELLED
    booking.cancellation_reason = cancellation_data.cancellation_reason
    booking.cancelled_at = datetime.now()
    booking.updated_at = datetime.now()
    booking.save()

    logger.info(
        f"Booking {booking_id} cancelled by customer. Reason: {cancellation_data.cancellation_reason}"
    )

    return PublicBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        service_id=str(booking.service_id),
        staff_id=str(booking.staff_id),
        appointment_id=str(booking.appointment_id) if booking.appointment_id else None,
        customer_name=booking.customer_name,
        customer_email=booking.customer_email,
        customer_phone=booking.customer_phone,
        booking_date=booking.booking_date,
        booking_time=booking.booking_time,
        duration_minutes=booking.duration_minutes,
        status=booking.status,
        notes=booking.notes,
        created_at=booking.created_at.isoformat(),
        updated_at=booking.updated_at.isoformat(),
    )


@router.post("/bookings/{booking_id}/reschedule", response_model=PublicBookingResponse)
async def reschedule_public_booking(
    request: Request,
    booking_id: str,
    reschedule_data: RescheduleRequest,
):
    """
    Reschedule a public booking to a new date/time.

    Args:
        booking_id: Public booking ID
        reschedule_data: New date and time

    Returns:
        Updated booking details
    """
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        booking_id_obj = ObjectId(booking_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Get booking
    booking = PublicBooking.objects(
        tenant_id=tenant_id_obj, id=booking_id_obj
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check if rescheduling is allowed (at least 24 hours before appointment)
    booking_datetime = datetime.combine(booking.booking_date, booking.booking_time)
    time_until_appointment = booking_datetime - datetime.now()

    if time_until_appointment < timedelta(hours=24):
        raise HTTPException(
            status_code=400,
            detail="Cannot reschedule bookings within 24 hours of appointment time",
        )

    # Parse new date and time
    try:
        new_date = datetime.strptime(reschedule_data.new_date, "%Y-%m-%d").date()
        new_time = datetime.strptime(reschedule_data.new_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date or time format. Use YYYY-MM-DD and HH:MM",
        )

    # Update booking
    booking.booking_date = new_date
    booking.booking_time = new_time
    booking.updated_at = datetime.now()
    booking.save()

    logger.info(
        f"Booking {booking_id} rescheduled to {new_date} at {new_time}"
    )

    return PublicBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        service_id=str(booking.service_id),
        staff_id=str(booking.staff_id),
        appointment_id=str(booking.appointment_id) if booking.appointment_id else None,
        customer_name=booking.customer_name,
        customer_email=booking.customer_email,
        customer_phone=booking.customer_phone,
        booking_date=booking.booking_date,
        booking_time=booking.booking_time,
        duration_minutes=booking.duration_minutes,
        status=booking.status,
        notes=booking.notes,
        created_at=booking.created_at.isoformat(),
        updated_at=booking.updated_at.isoformat(),
    )



class NotificationPreferencesRequest(BaseModel):
    """Notification preferences request model."""
    send_confirmation_email: bool = True
    send_24h_reminder_email: bool = True
    send_1h_reminder_email: bool = True
    send_sms_reminders: bool = False


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response model."""
    send_confirmation_email: bool
    send_24h_reminder_email: bool
    send_1h_reminder_email: bool
    send_sms_reminders: bool


@router.get("/bookings/{booking_id}/notification-preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    request: Request,
    booking_id: str,
):
    """
    Get notification preferences for a public booking.

    Args:
        booking_id: Public booking ID

    Returns:
        Notification preferences
    """
    from app.models.public_booking import PublicBookingNotificationPreference
    
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        booking_id_obj = ObjectId(booking_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Get booking
    booking = PublicBooking.objects(
        tenant_id=tenant_id_obj, id=booking_id_obj
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Get or create preferences
    prefs = PublicBookingNotificationPreference.objects(
        tenant_id=tenant_id_obj, booking_id=booking_id_obj
    ).first()

    if not prefs:
        # Return defaults
        return NotificationPreferencesResponse(
            send_confirmation_email=True,
            send_24h_reminder_email=True,
            send_1h_reminder_email=True,
            send_sms_reminders=False,
        )

    return NotificationPreferencesResponse(
        send_confirmation_email=prefs.send_confirmation_email,
        send_24h_reminder_email=prefs.send_24h_reminder_email,
        send_1h_reminder_email=prefs.send_1h_reminder_email,
        send_sms_reminders=prefs.send_sms_reminders,
    )


@router.post("/bookings/{booking_id}/notification-preferences", response_model=dict)
async def update_notification_preferences(
    request: Request,
    booking_id: str,
    preferences_data: NotificationPreferencesRequest,
):
    """
    Update notification preferences for a public booking.

    Args:
        booking_id: Public booking ID
        preferences_data: Notification preferences

    Returns:
        Success response
    """
    from app.models.public_booking import PublicBookingNotificationPreference
    
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        booking_id_obj = ObjectId(booking_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Get booking
    booking = PublicBooking.objects(
        tenant_id=tenant_id_obj, id=booking_id_obj
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Get or create preferences
    prefs = PublicBookingNotificationPreference.objects(
        tenant_id=tenant_id_obj, booking_id=booking_id_obj
    ).first()

    if not prefs:
        prefs = PublicBookingNotificationPreference(
            tenant_id=tenant_id_obj,
            booking_id=booking_id_obj,
            customer_email=booking.customer_email,
            customer_phone=booking.customer_phone,
        )

    # Update preferences
    prefs.send_confirmation_email = preferences_data.send_confirmation_email
    prefs.send_24h_reminder_email = preferences_data.send_24h_reminder_email
    prefs.send_1h_reminder_email = preferences_data.send_1h_reminder_email
    prefs.send_sms_reminders = preferences_data.send_sms_reminders
    prefs.updated_at = datetime.now()
    prefs.save()

    logger.info(f"Notification preferences updated for booking {booking_id}")

    return {"message": "Preferences updated successfully"}
