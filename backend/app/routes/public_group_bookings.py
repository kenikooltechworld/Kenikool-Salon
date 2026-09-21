from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
import logging

from app.schemas.group_booking import PublicGroupBookingCreate, GroupBookingResponse
from app.services.group_booking_service import GroupBookingService
from app.middleware.tenant_context import get_tenant_id
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/public/group-bookings", tags=["Public Group Bookings"])


@router.post("", response_model=GroupBookingResponse)
async def create_public_group_booking(
    request: Request,
    booking_data: PublicGroupBookingCreate
):
    """Create a new group booking from public booking page"""
    tenant_id = get_tenant_id()

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    if len(booking_data.participants) < 2:
        raise HTTPException(
            status_code=400,
            detail="Group bookings require at least 2 participants"
        )
    if len(booking_data.participants) > 20:
        raise HTTPException(
            status_code=400,
            detail="Group bookings are limited to 20 participants."
        )

    group_booking = GroupBookingService.create_group_booking(
        tenant_id=tenant_id,
        booking_data=booking_data,
        ip_address=ip_address,
        user_agent=user_agent
    )

    try:
        from app.tasks import send_email
        from app.services.email_template_service import EmailTemplateService
        from app.models.tenant import Tenant
        from app.models.staff import Staff

        organizer_staff_id = booking_data.staff_ids[0] if booking_data.staff_ids else None
        staff = None
        if organizer_staff_id:
            staff = Staff.objects(tenant_id=tenant_id, id=ObjectId(organizer_staff_id)).first()

        tenant = Tenant.objects(id=tenant_id).first()
        business_email = tenant.settings.get("email", tenant.email) if tenant.settings else tenant.email

        email_context = {
            "customer_email": booking_data.organizer_email,
            "business_email": business_email,
        }
        rendered = EmailTemplateService.render_customer_welcome_email(
            str(tenant_id), email_context
        )
        run_in_background(send_email,
            to=booking_data.organizer_email,
            subject="Your group booking has been received",
            template=rendered or "<p>Your group booking has been received.</p>",
            context=email_context,
        )
    except Exception as notif_err:
        logger.warning(f"Group booking email notification failed: {notif_err}")

    return GroupBookingResponse(
        id=str(group_booking.id),
        tenant_id=str(group_booking.tenant_id),
        **group_booking.to_mongo().to_dict()
    )


@router.get("/{booking_id}", response_model=GroupBookingResponse)
async def get_public_group_booking(
    request: Request,
    booking_id: str,
    email: str = None
):
    """Get group booking details (email optional for confirmation page)"""
    tenant_id = get_tenant_id()

    booking = GroupBookingService.get_group_booking(ObjectId(booking_id))

    if not booking:
        raise HTTPException(status_code=404, detail="Group booking not found")

    if email and booking.organizer_email != email:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if booking.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Group booking not found")

    return GroupBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        **booking.to_mongo().to_dict()
    )


@router.post("/{booking_id}/cancel")
async def cancel_public_group_booking(
    request: Request,
    booking_id: str,
    email: str,
    cancellation_reason: str = None
):
    """Cancel a group booking (requires organizer email for verification)"""
    tenant_id = get_tenant_id()

    booking = GroupBookingService.get_group_booking(ObjectId(booking_id))

    if not booking:
        raise HTTPException(status_code=404, detail="Group booking not found")

    if booking.organizer_email != email:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if booking.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Group booking not found")

    if booking.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel booking with status: {booking.status}"
        )

    booking = GroupBookingService.cancel_group_booking(
        ObjectId(booking_id),
        cancellation_reason
    )

    try:
        from app.tasks import send_email
        from app.services.email_template_service import EmailTemplateService
        from app.models.tenant import Tenant

        tenant = Tenant.objects(id=tenant_id).first()
        business_email = tenant.settings.get("email", tenant.email) if tenant.settings else tenant.email
        organizer_email = booking.organizer_email or email

        email_context = {
            "customer_email": organizer_email,
            "business_email": business_email,
        }
        rendered = EmailTemplateService.render_customer_welcome_email(
            str(tenant_id), email_context
        )
        run_in_background(send_email,
            to=organizer_email,
            subject="Your group booking has been cancelled",
            template=rendered or "<p>Your group booking has been cancelled.</p>",
            context=email_context,
        )
    except Exception as notif_err:
        logger.warning(f"Group booking cancellation notification failed: {notif_err}")

    return {"message": "Group booking cancelled successfully"}


