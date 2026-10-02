"""Notification routes."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Optional
from datetime import datetime
from bson import ObjectId
import logging
from app.schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationPreferencesBatchUpdate,
    NotificationTemplateResponse,
    NotificationTemplateCreate,
    InterDepartmentMessageCreate,
    StaffMessageCreate,
    CustomerMessageCreate,
)
from app.services.notification_service import NotificationService
from app.decorators.tenant_isolated import tenant_isolated
from app.context import get_tenant_id
from app.routes.auth import get_current_user_dependency
from app.tasks import run_in_background

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ============================================================================
# SPECIFIC ROUTES (must come before generic /{notification_id} route)
# ============================================================================

@router.get("/unread-count", response_model=dict)
@tenant_isolated
async def get_unread_count(current_user: dict = Depends(get_current_user_dependency)):
    """Get unread notification count for current user."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        logger.info(f"[Notifications] Getting unread count for user_id={user_id}")
        notifications = NotificationService.get_unread_notifications(user_id)
        logger.info(f"[Notifications] Unread count: {len(notifications)}")
        return {"data": {"unread_count": len(notifications)}}
    except Exception as e:
        logger.error(f"[Notifications] Error getting unread count: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get unread count")


@router.get("/messages", response_model=List[NotificationResponse])
@tenant_isolated
async def get_inter_department_messages(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user_dependency),
):
    """Get inter-department messages for current user."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        message_types = ["manager_message", "team_announcement", "custom"]
        notifications = []
        for message_type in message_types:
            batch = NotificationService.get_notifications(
                recipient_id=user_id,
                notification_type=message_type,
                status=status,
                limit=limit,
                skip=skip,
            )
            notifications.extend(batch)

        notifications.sort(key=lambda n: n.created_at, reverse=True)
        return [NotificationResponse.from_orm(n) for n in notifications[:limit]]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Notifications] Error getting messages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get messages")


@router.post("/clear-all")
@tenant_isolated
async def clear_all_notifications(current_user: dict = Depends(get_current_user_dependency)):
    """Clear all notifications for current user."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        notifications = NotificationService.get_notifications(recipient_id=user_id)
        for notification in notifications:
            notification.delete()
        return {"data": {"message": "All notifications cleared"}}
    except Exception as e:
        logger.error(f"Error clearing notifications: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear notifications")


@router.get("/stats", response_model=dict)
@tenant_isolated
async def get_notification_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get notification statistics."""
    stats = NotificationService.get_notification_stats(
        start_date=start_date, end_date=end_date
    )
    return stats


@router.get("/recipient/{recipient_id}/unread", response_model=List[NotificationResponse])
@tenant_isolated
async def get_unread_notifications(recipient_id: str):
    """Get unread notifications for a recipient."""
    notifications = NotificationService.get_unread_notifications(recipient_id)
    return [NotificationResponse.from_orm(n) for n in notifications]


# Notification Preferences - specific routes
@router.post("/preferences", response_model=NotificationPreferenceResponse)
@tenant_isolated
async def set_notification_preference(
    preference: NotificationPreferenceUpdate,
    current_user: dict = Depends(get_current_user_dependency),
):
    """Set notification preference for current user (customer or staff)."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        user_role = current_user.get("role", "customer")
        
        # Determine recipient type and ID
        if user_role == "staff":
            created = NotificationService.set_preference(
                user_id=user_id,
                recipient_type="staff",
                notification_type=preference.notification_type,
                channel=preference.channel,
                enabled=preference.enabled,
            )
        else:
            # For customers, use customer_id if provided, otherwise use user_id
            customer_id = preference.customer_id if hasattr(preference, 'customer_id') and preference.customer_id else user_id
            created = NotificationService.set_preference(
                customer_id=customer_id,
                recipient_type="customer",
                notification_type=preference.notification_type,
                channel=preference.channel,
                enabled=preference.enabled,
            )
        return NotificationPreferenceResponse.from_orm(created)
    except Exception as e:
        logger.error(f"Error setting preference: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/preferences/batch", response_model=dict)
@tenant_isolated
async def batch_update_notification_preferences(
    payload: NotificationPreferencesBatchUpdate,
    current_user: dict = Depends(get_current_user_dependency),
):
    """Batch update notification preferences for current user."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        user_role = current_user.get("role", "customer")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        results = []
        for preference in payload.preferences:
            # Determine recipient type and ID
            if user_role == "staff":
                created = NotificationService.set_preference(
                    user_id=user_id,
                    recipient_type="staff",
                    notification_type=preference.notification_type,
                    channel=preference.channel,
                    enabled=preference.enabled,
                )
            else:
                customer_id = preference.customer_id if preference.customer_id else user_id
                created = NotificationService.set_preference(
                    customer_id=customer_id,
                    recipient_type="customer",
                    notification_type=preference.notification_type,
                    channel=preference.channel,
                    enabled=preference.enabled,
                )
            results.append(NotificationPreferenceResponse.from_orm(created))
        
        return {"data": results}
    except Exception as e:
        logger.error(f"Error batch updating preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/preferences", response_model=dict)
@tenant_isolated
async def get_all_preferences(current_user: dict = Depends(get_current_user_dependency)):
    """Get all notification preferences for current user."""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        user_role = current_user.get("role", "customer")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get preferences based on user role
        if user_role == "staff":
            preferences = NotificationService.get_preferences(user_id=user_id)
        else:
            preferences = NotificationService.get_preferences(customer_id=user_id)
            
        return {"data": [NotificationPreferenceResponse.from_orm(p) for p in preferences]}
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get preferences")


@router.get("/preferences/{customer_id}/{notification_type}/{channel}", response_model=NotificationPreferenceResponse)
@tenant_isolated
async def get_notification_preference(
    customer_id: str, notification_type: str, channel: str
):
    """Get a specific notification preference."""
    preference = NotificationService.get_preference(
        customer_id, notification_type, channel
    )
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    return NotificationPreferenceResponse.from_orm(preference)


@router.get("/preferences/{customer_id}", response_model=List[NotificationPreferenceResponse])
@tenant_isolated
async def get_customer_preferences(customer_id: str):
    """Get all notification preferences for a customer."""
    preferences = NotificationService.get_preferences(customer_id)
    return [NotificationPreferenceResponse.from_orm(p) for p in preferences]


# Notification Templates - specific routes
@router.post("/templates", response_model=NotificationTemplateResponse)
@tenant_isolated
async def create_template(template: NotificationTemplateCreate):
    """Create a notification template."""
    try:
        created = NotificationService.create_template(
            template_type=template.template_type,
            channel=template.channel,
            body=template.body,
            subject=template.subject,
            variables=template.variables,
            is_default=template.is_default,
        )
        return NotificationTemplateResponse.from_orm(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates", response_model=List[NotificationTemplateResponse])
@tenant_isolated
async def list_templates(
    template_type: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
):
    """List notification templates."""
    templates = NotificationService.get_templates(
        template_type=template_type, channel=channel
    )
    return [NotificationTemplateResponse.from_orm(t) for t in templates]


@router.get("/templates/{template_type}/{channel}", response_model=NotificationTemplateResponse)
@tenant_isolated
async def get_template(template_type: str, channel: str):
    """Get a notification template."""
    template = NotificationService.get_template(template_type, channel)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return NotificationTemplateResponse.from_orm(template)


@router.put("/templates/{template_id}", response_model=NotificationTemplateResponse)
@tenant_isolated
async def update_template(template_id: str, template: NotificationTemplateCreate):
    """Update a notification template."""
    try:
        updated = NotificationService.update_template(
            template_id=template_id,
            body=template.body,
            subject=template.subject,
            variables=template.variables,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Template not found")
        return NotificationTemplateResponse.from_orm(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# INTER-DEPARTMENT COMMUNICATION
# ============================================================================

@router.post("/send-message", response_model=dict)
@tenant_isolated
async def send_inter_department_message(
    payload: InterDepartmentMessageCreate,
    current_user: dict = Depends(get_current_user_dependency),
):
    """Send a message to staff, owners, or a specific role."""
    try:
        from bson import ObjectId
        from app.models.staff import Staff
        from app.models.user import User
        from app.models.role import Role
        from app.tasks import send_email
        from app.services.notification_service import NotificationService

        tenant_id = get_tenant_id()
        sender_id = current_user.get("id") or current_user.get("user_id")
        sender_role = current_user.get("role", "staff")
        sender_role_names = current_user.get("role_names", [])

        if not sender_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # RBAC: Only Owner or Manager can send inter-department messages
        allowed_roles = {"Owner", "Manager"}
        if not any(role in allowed_roles for role in sender_role_names):
            raise HTTPException(
                status_code=403,
                detail="Only Owner or Manager can send inter-department messages",
            )

        recipient_ids = set()

        if payload.recipient_type == "all_staff":
            staff_members = Staff.objects(tenant_id=ObjectId(tenant_id), status="active")
            for staff in staff_members:
                recipient_ids.add(str(staff.user_id))

        elif payload.recipient_type == "role" and payload.role_id:
            role = Role.objects(id=ObjectId(payload.role_id), tenant_id=ObjectId(tenant_id)).first()
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")
            users = User.objects(tenant_id=ObjectId(tenant_id), role_ids__in=[ObjectId(payload.role_id)])
            for user in users:
                recipient_ids.add(str(user.id))

        elif payload.recipient_type == "specific" and payload.recipient_ids:
            recipient_ids = set(payload.recipient_ids)

        else:
            raise HTTPException(status_code=400, detail="Invalid recipient configuration")

        if not recipient_ids:
            raise HTTPException(status_code=400, detail="No recipients found")

        notifications = []
        for recipient_id in recipient_ids:
            notification = NotificationService.create_notification(
                recipient_id=recipient_id,
                recipient_type="staff",
                notification_type=payload.notification_type,
                channel=payload.channel,
                content=payload.content,
                subject=payload.subject,
            )
            notifications.append(notification)

            if payload.send_email:
                try:
                    user = User.objects(id=ObjectId(recipient_id)).first()
                    email = getattr(user, "email", None)
                    if email:
                        context = {
                            "subject": payload.subject or "New Message",
                            "content": payload.content,
                            "sender_role": sender_role,
                        }
                        run_in_background(
                            send_email,
                            to=email,
                            subject=payload.subject or "New Message",
                            template="""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                                <h2 style="color: #333;">{subject}</h2>
                                <p style="color: #555; line-height: 1.6;">{content}</p>
                                <p style="color: #888; font-size: 12px; margin-top: 20px;">
                                    Sent by: {sender_role}
                                </p>
                            </div>""",
                            context=context,
                        )
                except Exception as email_err:
                    logger.warning(f"Failed to send email for inter-department message: {email_err}")

        # Emit real-time Socket.IO event for each recipient
        try:
            from app.socketio_handler import sio
            for recipient_id in recipient_ids:
                await sio.emit(
                    "notification:new",
                    {
                        "type": payload.notification_type,
                        "data": {
                            "subject": payload.subject,
                            "content": payload.content,
                            "sender_role": sender_role,
                            "recipients_count": len(notifications),
                            "recipient_id": recipient_id,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    room=f"user:{tenant_id}:{recipient_id}",
                )
        except Exception as socket_err:
            logger.warning(f"Failed to emit Socket.IO event for new message: {socket_err}")

        return {
            "data": {
                "sent_count": len(notifications),
                "recipient_ids": list(recipient_ids),
                "notification_type": payload.notification_type,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending inter-department message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.post("/staff/send-message", response_model=dict)
@tenant_isolated
async def staff_send_message(
    payload: StaffMessageCreate,
    current_user: dict = Depends(get_current_user_dependency),
):
    """Staff sends a message to owner/manager or other staff members."""
    try:
        from bson import ObjectId
        from app.models.staff import Staff
        from app.models.user import User
        from app.models.role import Role
        from app.tasks import send_email
        from app.services.notification_service import NotificationService

        tenant_id = get_tenant_id()
        sender_id = current_user.get("id") or current_user.get("user_id")
        sender_role = current_user.get("role", "staff")
        sender_role_names = current_user.get("role_names", [])

        if not sender_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # RBAC: Only staff can use this endpoint
        if "Staff" not in sender_role_names and sender_role != "staff":
            raise HTTPException(
                status_code=403,
                detail="Only staff can send messages via this endpoint",
            )

        recipient_ids = set()

        if payload.recipient_type == "owner":
            # Send to all owners/managers
            owners = User.objects(tenant_id=ObjectId(tenant_id), role="owner")
            for owner in owners:
                recipient_ids.add(str(owner.id))

        elif payload.recipient_type == "specific_staff" and payload.recipient_ids:
            recipient_ids = set(payload.recipient_ids)

        elif payload.recipient_type == "role" and payload.role_id:
            role = Role.objects(id=ObjectId(payload.role_id), tenant_id=ObjectId(tenant_id)).first()
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")
            users = User.objects(tenant_id=ObjectId(tenant_id), role_ids__in=[ObjectId(payload.role_id)])
            for user in users:
                recipient_ids.add(str(user.id))

        else:
            raise HTTPException(status_code=400, detail="Invalid recipient configuration")

        # Exclude sender from recipients
        recipient_ids.discard(sender_id)

        if not recipient_ids:
            raise HTTPException(status_code=400, detail="No recipients found")

        notifications = []
        for recipient_id in recipient_ids:
            notification = NotificationService.create_notification(
                recipient_id=recipient_id,
                recipient_type="staff",
                notification_type=payload.notification_type,
                channel=payload.channel,
                content=payload.content,
                subject=payload.subject,
            )
            notifications.append(notification)

            if payload.send_email:
                try:
                    user = User.objects(id=ObjectId(recipient_id)).first()
                    email = getattr(user, "email", None)
                    if email:
                        context = {
                            "subject": payload.subject or "New Message",
                            "content": payload.content,
                            "sender_role": sender_role,
                        }
                        run_in_background(
                            send_email,
                            to=email,
                            subject=payload.subject or "New Message",
                            template="""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                                <h2 style="color: #333;">{subject}</h2>
                                <p style="color: #555; line-height: 1.6;">{content}</p>
                                <p style="color: #888; font-size: 12px; margin-top: 20px;">
                                    Sent by: {sender_role}
                                </p>
                            </div>""",
                            context=context,
                        )
                except Exception as email_err:
                    logger.warning(f"Failed to send email for staff message: {email_err}")

        return {
            "data": {
                "sent_count": len(notifications),
                "recipient_ids": list(recipient_ids),
                "notification_type": payload.notification_type,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending staff message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.post("/customer/send-message", response_model=dict)
@tenant_isolated
async def customer_send_message(
    payload: CustomerMessageCreate,
    current_user: dict = Depends(get_current_user_dependency),
):
    """Customer sends a message to staff or owner."""
    try:
        from bson import ObjectId
        from app.models.staff import Staff
        from app.models.user import User
        from app.tasks import send_email
        from app.services.notification_service import NotificationService

        tenant_id = get_tenant_id()
        sender_id = current_user.get("id") or current_user.get("user_id")
        sender_role = current_user.get("role", "customer")

        if not sender_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # RBAC: Only customers can use this endpoint
        if sender_role != "customer":
            raise HTTPException(
                status_code=403,
                detail="Only customers can send messages via this endpoint",
            )

        recipient_ids = set()

        if payload.recipient_type == "staff":
            # Send to all active staff
            staff_members = Staff.objects(tenant_id=ObjectId(tenant_id), status="active")
            for staff in staff_members:
                recipient_ids.add(str(staff.user_id))

        elif payload.recipient_type == "owner":
            # Send to all owners/managers
            owners = User.objects(tenant_id=ObjectId(tenant_id), role="owner")
            for owner in owners:
                recipient_ids.add(str(owner.id))

        elif payload.recipient_type == "specific" and payload.recipient_ids:
            recipient_ids = set(payload.recipient_ids)

        else:
            raise HTTPException(status_code=400, detail="Invalid recipient configuration")

        # Exclude sender from recipients
        recipient_ids.discard(sender_id)

        if not recipient_ids:
            raise HTTPException(status_code=400, detail="No recipients found")

        notifications = []
        for recipient_id in recipient_ids:
            notification = NotificationService.create_notification(
                recipient_id=recipient_id,
                recipient_type="staff",
                notification_type=payload.notification_type,
                channel=payload.channel,
                content=payload.content,
                subject=payload.subject,
            )
            notifications.append(notification)

            if payload.send_email:
                try:
                    user = User.objects(id=ObjectId(recipient_id)).first()
                    email = getattr(user, "email", None)
                    if email:
                        context = {
                            "subject": payload.subject or "New Customer Message",
                            "content": payload.content,
                            "sender_role": "Customer",
                        }
                        run_in_background(
                            send_email,
                            to=email,
                            subject=payload.subject or "New Customer Message",
                            template="""<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                                <h2 style="color: #333;">{subject}</h2>
                                <p style="color: #555; line-height: 1.6;">{content}</p>
                                <p style="color: #888; font-size: 12px; margin-top: 20px;">
                                    Sent by: Customer
                                </p>
                            </div>""",
                            context=context,
                        )
                except Exception as email_err:
                    logger.warning(f"Failed to send email for customer message: {email_err}")

        return {
            "data": {
                "sent_count": len(notifications),
                "recipient_ids": list(recipient_ids),
                "notification_type": payload.notification_type,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending customer message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send message")


# ============================================================================
# GENERIC ROUTES (must come after specific routes)
# ============================================================================

@router.post("", response_model=NotificationResponse)
@tenant_isolated
async def create_notification(notification: NotificationCreate):
    """Create a new notification."""
    try:
        created = NotificationService.create_notification(
            recipient_id=notification.recipient_id,
            recipient_type=notification.recipient_type,
            notification_type=notification.notification_type,
            channel=notification.channel,
            content=notification.content,
            subject=notification.subject,
            template_id=notification.template_id,
            template_variables=notification.template_variables,
            appointment_id=notification.appointment_id,
            payment_id=notification.payment_id,
            shift_id=notification.shift_id,
            time_off_request_id=notification.time_off_request_id,
            recipient_email=notification.recipient_email,
            recipient_phone=notification.recipient_phone,
        )
        return NotificationResponse.from_orm(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[NotificationResponse])
@tenant_isolated
async def list_notifications(
    recipient_id: Optional[str] = Query(None),
    notification_type: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user_dependency),
):
    """List notifications with optional filtering."""
    try:
        # If no recipient_id specified, use current user's ID
        if not recipient_id:
            recipient_id = current_user.get("id") or current_user.get("user_id")
        
        logger.info(f"[Notifications] Listing notifications for recipient_id={recipient_id}")
        
        notifications = NotificationService.get_notifications(
            recipient_id=recipient_id,
            notification_type=notification_type,
            channel=channel,
            status=status,
            limit=limit,
            skip=skip,
        )
        logger.info(f"[Notifications] Found {len(notifications)} notifications")
        return [NotificationResponse.from_orm(n) for n in notifications]
    except Exception as e:
        logger.error(f"[Notifications] Error listing notifications: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list notifications: {str(e)}")


@router.get("/{notification_id}", response_model=NotificationResponse)
@tenant_isolated
async def get_notification(notification_id: str):
    """Get a notification by ID."""
    try:
        notification = NotificationService.get_notification(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return NotificationResponse.from_orm(notification)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get notification: {str(e)}")


@router.patch("/{notification_id}/mark-read", response_model=NotificationResponse)
@tenant_isolated
async def mark_notification_read(notification_id: str):
    """Mark a notification as read."""
    notification = NotificationService.mark_notification_read(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notification)


@router.delete("/{notification_id}")
@tenant_isolated
async def delete_notification(notification_id: str):
    """Delete a notification."""
    notification = NotificationService.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.delete()
    return {"message": "Notification deleted"}


@router.patch("/{notification_id}/sent", response_model=NotificationResponse)
@tenant_isolated
async def mark_notification_sent(notification_id: str):
    """Mark a notification as sent."""
    notification = NotificationService.mark_notification_sent(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notification)


@router.patch("/{notification_id}/delivered", response_model=NotificationResponse)
@tenant_isolated
async def mark_notification_delivered(notification_id: str):
    """Mark a notification as delivered."""
    notification = NotificationService.mark_notification_delivered(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notification)


@router.patch("/{notification_id}/failed", response_model=NotificationResponse)
@tenant_isolated
async def mark_notification_failed(notification_id: str, reason: Optional[str] = None):
    """Mark a notification as failed."""
    notification = NotificationService.mark_notification_failed(notification_id, reason)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notification)


@router.patch("/{notification_id}/retry", response_model=NotificationResponse)
@tenant_isolated
async def retry_notification(notification_id: str):
    """Retry a failed notification."""
    notification = NotificationService.retry_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notification)


@router.patch("/{notification_id}/unread", response_model=NotificationResponse)
@tenant_isolated
async def mark_notification_unread(notification_id: str):
    """Mark a notification as unread."""
    notification = NotificationService.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = False
    notification.read_at = None
    notification.save()
    return NotificationResponse.from_orm(notification)
