"""
Notifications API endpoints - for fetching and managing user notifications
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List, Dict
from datetime import datetime
import logging
from bson import ObjectId

from app.api.dependencies import get_current_user, get_current_tenant_id
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
async def get_notifications(
    is_read: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get user notifications
    
    Args:
        is_read: Filter by read status (True/False/None for all)
        limit: Number of notifications to return
        offset: Pagination offset
        current_user: Current authenticated user
    
    Returns:
        List of notifications with unread count
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        # Build query filter
        query_filter = {
            "user_id": user_id,
            "tenant_id": tenant_id
        }
        
        if is_read is not None:
            query_filter["is_read"] = is_read
        
        # Get total count
        total_count = db.notifications.count_documents(query_filter)
        
        # Get unread count
        unread_count = db.notifications.count_documents({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "is_read": False
        })
        
        # Fetch notifications with pagination
        notifications = list(
            db.notifications.find(query_filter)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Convert ObjectId to string for JSON serialization
        for notif in notifications:
            notif["id"] = str(notif.get("_id", ""))
            if "_id" in notif:
                del notif["_id"]
        
        return {
            "notifications": notifications,
            "unread_count": unread_count,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


@router.patch("/{notification_id}")
async def update_notification(
    notification_id: str,
    is_read: Optional[bool] = None,
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update a notification (mark as read/unread)
    
    Args:
        notification_id: ID of notification to update
        is_read: Mark as read (True) or unread (False)
        current_user: Current authenticated user
    
    Returns:
        Updated notification
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        # Validate notification_id format
        try:
            notif_obj_id = ObjectId(notification_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification ID format"
            )
        
        # Find and update notification
        notification = db.notifications.find_one_and_update(
            {
                "_id": notif_obj_id,
                "user_id": user_id,
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "is_read": is_read if is_read is not None else True,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Convert ObjectId to string
        notification["id"] = str(notification.get("_id", ""))
        if "_id" in notification:
            del notification["_id"]
        
        return notification
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification"
        )


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Mark all notifications as read for the current user
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Success message with count of updated notifications
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        # Update all unread notifications
        result = db.notifications.update_many(
            {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "is_read": False
            },
            {
                "$set": {
                    "is_read": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": f"Marked {result.modified_count} notifications as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notifications as read: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notifications as read"
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a notification
    
    Args:
        notification_id: ID of notification to delete
        current_user: Current authenticated user
    
    Returns:
        Success message
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        # Validate notification_id format
        try:
            notif_obj_id = ObjectId(notification_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification ID format"
            )
        
        # Delete notification
        result = db.notifications.delete_one({
            "_id": notif_obj_id,
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {
            "success": True,
            "message": "Notification deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )


@router.get("/preferences")
async def get_notification_preferences(
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current notification preferences for user"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        prefs = db.notification_preferences.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if not prefs:
            # Return default preferences
            return {
                "booking_confirmation": True,
                "booking_reminder_24h": True,
                "booking_reminder_1h": True,
                "cancellation_notification": True,
                "rescheduling_notification": True,
                "credit_expiration_warning": True,
                "email_enabled": True,
                "sms_enabled": True,
                "push_enabled": True
            }
        
        prefs["id"] = str(prefs.get("_id", ""))
        if "_id" in prefs:
            del prefs["_id"]
        
        return prefs
    except Exception as e:
        logger.error(f"Error fetching preferences: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch preferences"
        )


@router.patch("/preferences")
async def update_notification_preferences(
    preferences: Dict,
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update notification preferences for user"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        # Update or create preferences
        result = db.notification_preferences.find_one_and_update(
            {
                "user_id": user_id,
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    **preferences,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True,
            return_document=True
        )
        
        result["id"] = str(result.get("_id", ""))
        if "_id" in result:
            del result["_id"]
        
        return result
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


@router.get("/logs")
async def get_notification_logs(
    status_filter: Optional[str] = Query(None),
    type_filter: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get notification logs with filtering"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        # Build query filter
        query_filter = {
            "user_id": user_id,
            "tenant_id": tenant_id
        }
        
        if status_filter:
            query_filter["status"] = status_filter
        
        if type_filter:
            query_filter["type"] = type_filter
        
        # Get total count
        total_count = db.notification_logs.count_documents(query_filter)
        
        # Fetch logs with pagination
        logs = list(
            db.notification_logs.find(query_filter)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for log in logs:
            log["id"] = str(log.get("_id", ""))
            if "_id" in log:
                del log["_id"]
        
        return {
            "logs": logs,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching notification logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification logs"
        )


@router.post("/retry")
async def retry_notification(
    notification_id: str = Query(...),
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Retry sending a failed notification"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        # Validate notification_id format
        try:
            notif_obj_id = ObjectId(notification_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification ID format"
            )
        
        # Find the notification log
        log = db.notification_logs.find_one({
            "_id": notif_obj_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "status": "failed"
        })
        
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed notification not found"
            )
        
        # Update status to pending for retry
        result = db.notification_logs.find_one_and_update(
            {"_id": notif_obj_id},
            {
                "$set": {
                    "status": "pending",
                    "retry_count": log.get("retry_count", 0) + 1,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        result["id"] = str(result.get("_id", ""))
        if "_id" in result:
            del result["_id"]
        
        return {
            "success": True,
            "message": "Notification queued for retry",
            "notification": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry notification"
        )
