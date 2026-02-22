from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection


class DeliveryTrackingService:
    """Service for real-time delivery tracking"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.sends_collection: Collection = self.db["campaign_sends"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        self.sends_collection.create_index([("campaign_id", 1), ("status", 1)])
        self.sends_collection.create_index([("campaign_id", 1), ("created_at", -1)])

    def get_delivery_status(self, campaign_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get real-time delivery status for a campaign"""
        sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id
        }))

        if not sends:
            return {
                "campaign_id": campaign_id,
                "total_messages": 0,
                "status_breakdown": {
                    "pending": 0,
                    "sending": 0,
                    "delivered": 0,
                    "failed": 0
                },
                "progress_percentage": 0,
                "failures": []
            }

        total = len(sends)
        pending = len([s for s in sends if s.get("status") == "pending"])
        sending = len([s for s in sends if s.get("status") == "sending"])
        delivered = len([s for s in sends if s.get("status") == "delivered"])
        failed = len([s for s in sends if s.get("status") == "failed"])

        failures = [
            {
                "recipient_id": s.get("client_id"),
                "channel": s.get("channel"),
                "error_code": s.get("error_code"),
                "error_message": s.get("error_message"),
                "timestamp": s.get("created_at").isoformat() if s.get("created_at") else None,
                "retryable": s.get("retry_count", 0) < 3
            }
            for s in sends if s.get("status") == "failed"
        ]

        progress = ((delivered + failed) / total * 100) if total > 0 else 0

        return {
            "campaign_id": campaign_id,
            "total_messages": total,
            "status_breakdown": {
                "pending": pending,
                "sending": sending,
                "delivered": delivered,
                "failed": failed
            },
            "progress_percentage": progress,
            "failures": failures
        }

    def get_failure_details(self, campaign_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get detailed failure information"""
        sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id,
            "status": "failed"
        }))

        failures_by_type = {}
        for send in sends:
            error_code = send.get("error_code", "unknown")
            if error_code not in failures_by_type:
                failures_by_type[error_code] = {
                    "count": 0,
                    "message": send.get("error_message", "Unknown error"),
                    "examples": []
                }
            
            failures_by_type[error_code]["count"] += 1
            if len(failures_by_type[error_code]["examples"]) < 3:
                failures_by_type[error_code]["examples"].append({
                    "client_id": send.get("client_id"),
                    "channel": send.get("channel"),
                    "timestamp": send.get("created_at").isoformat() if send.get("created_at") else None
                })

        return {
            "campaign_id": campaign_id,
            "total_failures": len(sends),
            "failures_by_type": failures_by_type
        }

    def retry_failed_messages(self, campaign_id: str, tenant_id: str,
                             max_retries: int = 3) -> Dict[str, Any]:
        """Retry failed messages"""
        failed_sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id,
            "status": "failed",
            "retry_count": {"$lt": max_retries}
        }))

        retry_count = 0
        for send in failed_sends:
            self.sends_collection.update_one(
                {"_id": send["_id"]},
                {
                    "$set": {"status": "pending"},
                    "$inc": {"retry_count": 1}
                }
            )
            retry_count += 1

        return {
            "campaign_id": campaign_id,
            "retried_count": retry_count,
            "total_failed": len(failed_sends)
        }

    def retry_specific_message(self, send_id: str) -> Optional[Dict[str, Any]]:
        """Retry a specific message"""
        result = self.sends_collection.find_one_and_update(
            {"_id": send_id},
            {
                "$set": {"status": "pending"},
                "$inc": {"retry_count": 1}
            },
            return_document=True
        )
        return result

    def categorize_failures(self, campaign_id: str, tenant_id: str) -> Dict[str, Any]:
        """Categorize failures by type"""
        sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id,
            "status": "failed"
        }))

        categories = {
            "invalid_contact": [],
            "network_error": [],
            "provider_error": [],
            "rate_limit": [],
            "other": []
        }

        for send in sends:
            error_code = send.get("error_code", "").lower()
            
            if "invalid" in error_code or "invalid_number" in error_code:
                categories["invalid_contact"].append(send)
            elif "network" in error_code or "timeout" in error_code:
                categories["network_error"].append(send)
            elif "rate" in error_code or "limit" in error_code:
                categories["rate_limit"].append(send)
            elif "provider" in error_code or "api" in error_code:
                categories["provider_error"].append(send)
            else:
                categories["other"].append(send)

        return {
            "campaign_id": campaign_id,
            "total_failures": len(sends),
            "by_category": {
                k: len(v) for k, v in categories.items()
            },
            "details": categories
        }

    def get_estimated_completion(self, campaign_id: str, tenant_id: str) -> Optional[datetime]:
        """Estimate completion time"""
        sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id
        }).sort("created_at", -1).limit(100))

        if not sends:
            return None

        # Calculate average time per message
        completed = [s for s in sends if s.get("status") in ["delivered", "failed"]]
        if not completed:
            return None

        total_time = 0
        for send in completed:
            created = send.get("created_at")
            completed_at = send.get("delivered_at") or send.get("created_at")
            if created and completed_at:
                total_time += (completed_at - created).total_seconds()

        avg_time = total_time / len(completed) if completed else 0
        
        pending = len([s for s in sends if s.get("status") in ["pending", "sending"]])
        estimated_seconds = avg_time * pending

        return datetime.utcnow() + timedelta(seconds=estimated_seconds)
