"""
Service Notification Service - Monitors service-related events and sends notifications
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)


class ServiceNotificationService:
    """Service for managing service-related notifications"""
    
    def __init__(self, db):
        self.db = db
    
    def check_low_booking_alerts(self, tenant_id: str, days: int = 30) -> List[Dict]:
        """
        Check for services with low booking rates
        
        Sends alerts for services that have fewer than expected bookings.
        
        Requirements: 20.1, 20.2
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all active services
        services = list(self.db.services.find({
            "tenant_id": tenant_id,
            "is_active": True
        }))
        
        low_booking_services = []
        
        for service in services:
            service_id = str(service["_id"])
            
            # Count bookings in the period
            booking_count = self.db.bookings.count_documents({
                "service_id": service_id,
                "tenant_id": tenant_id,
                "created_at": {"$gte": cutoff_date}
            })
            
            # Alert if less than 5 bookings in 30 days (configurable threshold)
            threshold = 5
            if booking_count < threshold:
                low_booking_services.append({
                    "service_id": service_id,
                    "service_name": service.get("name"),
                    "booking_count": booking_count,
                    "threshold": threshold,
                    "period_days": days
                })
                
                # Create notification
                self._create_notification(
                    tenant_id=tenant_id,
                    title="Low Booking Alert",
                    message=f"Service '{service.get('name')}' has only {booking_count} bookings in the last {days} days",
                    notification_type="service_alert",
                    link=f"/dashboard/services/{service_id}"
                )
        
        logger.info(f"Found {len(low_booking_services)} services with low bookings for tenant {tenant_id}")
        return low_booking_services
    
    def send_price_change_notification(
        self,
        tenant_id: str,
        service_id: str,
        service_name: str,
        old_price: float,
        new_price: float,
        user_email: str
    ) -> bool:
        """
        Send notification when service price changes
        
        Requirements: 20.2, 20.3
        """
        price_change_pct = ((new_price - old_price) / old_price) * 100
        
        message = f"Price for '{service_name}' changed from ₦{old_price:,.2f} to ₦{new_price:,.2f} ({price_change_pct:+.1f}%)"
        
        self._create_notification(
            tenant_id=tenant_id,
            title="Service Price Changed",
            message=message,
            notification_type="price_change",
            link=f"/dashboard/services/{service_id}"
        )
        
        logger.info(f"Price change notification sent for service {service_id}")
        return True
    
    def check_inventory_alerts(self, tenant_id: str, service_id: str) -> List[Dict]:
        """
        Check if service has low inventory for required resources
        
        Requirements: 20.4
        """
        # Get service
        service = self.db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            return []
        
        required_resources = service.get("required_resources", [])
        low_stock_resources = []
        
        for resource in required_resources:
            resource_name = resource.get("name")
            required_quantity = resource.get("quantity", 0)
            
            # Check inventory
            inventory_item = self.db.inventory_products.find_one({
                "tenant_id": tenant_id,
                "name": resource_name
            })
            
            if inventory_item:
                current_quantity = inventory_item.get("quantity", 0)
                reorder_level = inventory_item.get("reorder_level", 10)
                
                if current_quantity < reorder_level:
                    low_stock_resources.append({
                        "resource_name": resource_name,
                        "current_quantity": current_quantity,
                        "reorder_level": reorder_level,
                        "required_per_service": required_quantity
                    })
                    
                    # Create notification
                    self._create_notification(
                        tenant_id=tenant_id,
                        title="Low Inventory Alert",
                        message=f"Low stock for '{resource_name}' (required for '{service.get('name')}'): {current_quantity} {inventory_item.get('unit', 'units')} remaining",
                        notification_type="inventory_alert",
                        link=f"/dashboard/inventory"
                    )
        
        return low_stock_resources
    
    def check_negative_review_alerts(self, tenant_id: str, service_id: str) -> List[Dict]:
        """
        Check for negative reviews on a service
        
        Requirements: 20.5
        """
        # Get recent reviews with low ratings (1-2 stars)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        negative_reviews = list(self.db.reviews.find({
            "tenant_id": tenant_id,
            "service_id": service_id,
            "rating": {"$lte": 2},
            "created_at": {"$gte": cutoff_date}
        }))
        
        if negative_reviews:
            service = self.db.services.find_one({"_id": ObjectId(service_id)})
            service_name = service.get("name", "Unknown") if service else "Unknown"
            
            # Create notification
            self._create_notification(
                tenant_id=tenant_id,
                title="Negative Review Alert",
                message=f"Service '{service_name}' received {len(negative_reviews)} negative review(s) in the last 7 days",
                notification_type="review_alert",
                link=f"/dashboard/services/{service_id}"
            )
            
            logger.info(f"Negative review alert sent for service {service_id}")
        
        return negative_reviews
    
    def generate_weekly_performance_summary(self, tenant_id: str) -> Dict:
        """
        Generate weekly performance summary for all services
        
        Requirements: 20.6
        """
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Get all active services
        services = list(self.db.services.find({
            "tenant_id": tenant_id,
            "is_active": True
        }))
        
        summary = {
            "period_start": week_ago,
            "period_end": datetime.utcnow(),
            "services": []
        }
        
        for service in services:
            service_id = str(service["_id"])
            
            # Get bookings for this week
            bookings = list(self.db.bookings.find({
                "service_id": service_id,
                "tenant_id": tenant_id,
                "created_at": {"$gte": week_ago}
            }))
            
            completed_bookings = [b for b in bookings if b.get("status") == "completed"]
            total_revenue = sum(b.get("service_price", 0) for b in completed_bookings)
            
            summary["services"].append({
                "service_id": service_id,
                "service_name": service.get("name"),
                "total_bookings": len(bookings),
                "completed_bookings": len(completed_bookings),
                "total_revenue": total_revenue
            })
        
        # Create summary notification
        total_bookings = sum(s["total_bookings"] for s in summary["services"])
        total_revenue = sum(s["total_revenue"] for s in summary["services"])
        
        self._create_notification(
            tenant_id=tenant_id,
            title="Weekly Performance Summary",
            message=f"This week: {total_bookings} bookings, ₦{total_revenue:,.2f} revenue across all services",
            notification_type="performance_summary",
            link="/dashboard/services"
        )
        
        logger.info(f"Weekly performance summary generated for tenant {tenant_id}")
        return summary
    
    def send_deactivation_notification(
        self,
        tenant_id: str,
        service_id: str,
        service_name: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Send notification when a service is deactivated
        
        Requirements: 20.7
        """
        message = f"Service '{service_name}' has been deactivated"
        if reason:
            message += f": {reason}"
        
        self._create_notification(
            tenant_id=tenant_id,
            title="Service Deactivated",
            message=message,
            notification_type="service_status",
            link=f"/dashboard/services/{service_id}"
        )
        
        logger.info(f"Deactivation notification sent for service {service_id}")
        return True
    
    def get_notification_preferences(self, tenant_id: str) -> Dict:
        """
        Get notification preferences for a tenant
        
        Requirements: 20.2
        """
        preferences = self.db.notification_preferences.find_one({
            "tenant_id": tenant_id
        })
        
        if not preferences:
            # Return default preferences
            return {
                "tenant_id": tenant_id,
                "low_booking_alerts": True,
                "price_change_notifications": True,
                "inventory_alerts": True,
                "negative_review_alerts": True,
                "weekly_summary": True,
                "deactivation_notifications": True,
                "low_booking_threshold": 5,
                "low_booking_period_days": 30
            }
        
        return {
            "tenant_id": preferences["tenant_id"],
            "low_booking_alerts": preferences.get("low_booking_alerts", True),
            "price_change_notifications": preferences.get("price_change_notifications", True),
            "inventory_alerts": preferences.get("inventory_alerts", True),
            "negative_review_alerts": preferences.get("negative_review_alerts", True),
            "weekly_summary": preferences.get("weekly_summary", True),
            "deactivation_notifications": preferences.get("deactivation_notifications", True),
            "low_booking_threshold": preferences.get("low_booking_threshold", 5),
            "low_booking_period_days": preferences.get("low_booking_period_days", 30)
        }
    
    def update_notification_preferences(
        self,
        tenant_id: str,
        preferences: Dict
    ) -> Dict:
        """
        Update notification preferences for a tenant
        
        Requirements: 20.2
        """
        preferences["tenant_id"] = tenant_id
        preferences["updated_at"] = datetime.utcnow()
        
        self.db.notification_preferences.update_one(
            {"tenant_id": tenant_id},
            {"$set": preferences},
            upsert=True
        )
        
        logger.info(f"Notification preferences updated for tenant {tenant_id}")
        return preferences
    
    def _create_notification(
        self,
        tenant_id: str,
        title: str,
        message: str,
        notification_type: str,
        link: Optional[str] = None
    ) -> str:
        """
        Create a notification in the database
        
        Internal helper method
        """
        notification_data = {
            "tenant_id": tenant_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "link": link,
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        
        result = self.db.notifications.insert_one(notification_data)
        notification_id = str(result.inserted_id)
        
        logger.debug(f"Notification created: {notification_id}")
        return notification_id
    
    def run_scheduled_checks(self, tenant_id: str) -> Dict:
        """
        Run all scheduled notification checks
        
        This method should be called periodically (e.g., daily) by a scheduler
        
        Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6
        """
        preferences = self.get_notification_preferences(tenant_id)
        results = {
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow(),
            "checks_run": []
        }
        
        # Check low bookings
        if preferences.get("low_booking_alerts"):
            low_booking_services = self.check_low_booking_alerts(
                tenant_id,
                days=preferences.get("low_booking_period_days", 30)
            )
            results["checks_run"].append({
                "check": "low_booking_alerts",
                "services_flagged": len(low_booking_services)
            })
        
        # Check inventory for all services
        if preferences.get("inventory_alerts"):
            services = list(self.db.services.find({
                "tenant_id": tenant_id,
                "is_active": True
            }))
            
            total_low_stock = 0
            for service in services:
                low_stock = self.check_inventory_alerts(tenant_id, str(service["_id"]))
                total_low_stock += len(low_stock)
            
            results["checks_run"].append({
                "check": "inventory_alerts",
                "resources_flagged": total_low_stock
            })
        
        # Check negative reviews
        if preferences.get("negative_review_alerts"):
            services = list(self.db.services.find({
                "tenant_id": tenant_id,
                "is_active": True
            }))
            
            total_negative_reviews = 0
            for service in services:
                negative_reviews = self.check_negative_review_alerts(tenant_id, str(service["_id"]))
                total_negative_reviews += len(negative_reviews)
            
            results["checks_run"].append({
                "check": "negative_review_alerts",
                "reviews_flagged": total_negative_reviews
            })
        
        logger.info(f"Scheduled notification checks completed for tenant {tenant_id}")
        return results


def get_service_notification_service(db):
    """Factory function to get service notification service instance"""
    return ServiceNotificationService(db)
