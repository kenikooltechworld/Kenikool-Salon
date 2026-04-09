"""Notification routes."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
import logging
from app.schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationTemplateResponse,
    NotificationTemplateCreate,
)
from app.services.notification_service import NotificationService
from app.decorators.tenant_isolated import tenant_isolated
from app.context import get_tenant_id
from app.routes.auth import get_current_user_dependency

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
        notifications = NotificationService.get_unread_notifications(user_id)
        return {"data": {"unread_count": len(notifications)}}
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get unread count")


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
@router.get("")
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
        
        notifications = NotificationService.get_notifications(
            recipient_id=recipient_id,
            notification_type=notification_type,
            channel=channel,
            status=status,
            limit=limit,
            skip=skip,
        )
        return [NotificationResponse.from_orm(n) for n in notifications]
    except Exception as e:
        logger.error(f"Error listing notifications: {str(e)}", exc_info=True)
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


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
@tenant_isolated
async def mark_notification_read(notification_id: str):
    """Mark a notification as read."""
    notification = NotificationService.mark_notification_read(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_orm(notification)


@router.patch("/{notification_id}/mark-read", response_model=NotificationResponse)
@tenant_isolated
async def mark_notification_read_alt(notification_id: str):
    """Mark a notification as read (alternative endpoint)."""
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
