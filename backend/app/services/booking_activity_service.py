"""Service for managing booking activities for social proof."""

from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta

from app.models.booking_activity import BookingActivity


class BookingActivityService:
    """Service for tracking and displaying recent booking activities"""
    
    @staticmethod
    def create_activity(
        tenant_id: ObjectId,
        customer_name: str,
        service_name: str,
        booking_type: str = 'appointment'
    ) -> BookingActivity:
        """
        Create a new booking activity record
        
        Args:
            tenant_id: Tenant ID
            customer_name: Customer name (anonymized - first name only)
            service_name: Service name
            booking_type: Type of booking (appointment, package, membership, group)
            
        Returns:
            Created BookingActivity
        """
        # Anonymize customer name - use first name only
        first_name = customer_name.split()[0] if customer_name else "Someone"
        
        activity = BookingActivity(
            tenant_id=tenant_id,
            customer_name=first_name,
            service_name=service_name,
            booking_type=booking_type,
            is_visible=True
        )
        activity.save()
        
        return activity
    
    @staticmethod
    def get_recent_activities(
        tenant_id: ObjectId,
        limit: int = 10,
        hours: int = 24
    ) -> List[BookingActivity]:
        """
        Get recent booking activities for social proof display
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum number of activities to return
            hours: Number of hours to look back
            
        Returns:
            List of recent BookingActivity records
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        activities = BookingActivity.objects(
            tenant_id=tenant_id,
            is_visible=True,
            created_at__gte=cutoff_time
        ).order_by('-created_at').limit(limit)
        
        return list(activities)
    
    @staticmethod
    def toggle_visibility(
        activity_id: ObjectId,
        is_visible: bool
    ) -> Optional[BookingActivity]:
        """
        Toggle visibility of a booking activity
        
        Args:
            activity_id: Activity ID
            is_visible: New visibility status
            
        Returns:
            Updated BookingActivity or None
        """
        activity = BookingActivity.objects(id=activity_id).first()
        
        if not activity:
            return None
        
        activity.is_visible = is_visible
        activity.save()
        
        return activity
    
    @staticmethod
    def cleanup_old_activities(tenant_id: ObjectId, days: int = 7) -> int:
        """
        Clean up old booking activities
        
        Args:
            tenant_id: Tenant ID
            days: Number of days to keep
            
        Returns:
            Number of deleted activities
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        result = BookingActivity.objects(
            tenant_id=tenant_id,
            created_at__lt=cutoff_time
        ).delete()
        
        return result
