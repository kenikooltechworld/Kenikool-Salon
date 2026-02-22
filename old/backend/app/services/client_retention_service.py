"""
Client Retention Service

Handles client retention tools:
- At-risk client identification
- Churn probability calculation
- Win-back campaigns
- Retention metrics

Requirements: REQ-CM-013
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
import statistics

from app.database import Database
from app.services.communication_service import CommunicationService

logger = logging.getLogger(__name__)


class ClientRetentionService:
    """Service for client retention analysis and tools"""

    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()

    def identify_at_risk_clients(
        self,
        tenant_id: str,
        days_inactive: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Identify clients who haven't visited in specified days
        
        Args:
            tenant_id: Tenant ID
            days_inactive: Days since last visit to consider at-risk
            
        Returns:
            List of at-risk clients with details
            
        Requirements: REQ-CM-013
        """
        db = ClientRetentionService._get_db()
        cutoff_date = datetime.now() - timedelta(days=days_inactive)

        # Find clients with no recent visits
        at_risk_clients = list(db.clients.find({
            "tenant_id": tenant_id,
            "last_visit_date": {"$lt": cutoff_date},
            "segment": {"$ne": "new"}  # Exclude new clients
        }).sort("last_visit_date", 1))

        # Enrich with analytics
        for client in at_risk_clients:
            client["id"] = str(client.pop("_id"))
            client["days_since_visit"] = (datetime.now() - client.get("last_visit_date", datetime.now())).days
            client["churn_risk_score"] = self._calculate_churn_risk(client)

        return at_risk_clients

    def _calculate_churn_risk(self, client: Dict[str, Any]) -> float:
        """
        Calculate churn risk score (0-1)
        
        Based on:
        - Days since last visit
        - Visit frequency
        - Total spent
        - Attendance rate
        """
        score = 0.0

        # Days since visit (higher = more risk)
        days_since = (datetime.now() - client.get("last_visit_date", datetime.now())).days
        if days_since > 180:
            score += 0.5
        elif days_since > 90:
            score += 0.3
        elif days_since > 30:
            score += 0.1

        # Visit frequency (lower = more risk)
        avg_days_between = client.get("average_days_between_visits")
        if avg_days_between:
            if avg_days_between > 90:
                score += 0.2
            elif avg_days_between > 60:
                score += 0.1

        # Total spent (lower = more risk)
        total_spent = client.get("total_spent", 0)
        if total_spent < 100:
            score += 0.1

        # Attendance rate (lower = more risk)
        no_show_count = client.get("no_show_count", 0)
        total_visits = client.get("total_visits", 0)
        if total_visits > 0:
            no_show_rate = no_show_count / total_visits
            if no_show_rate > 0.2:
                score += 0.2

        return min(score, 1.0)

    def get_retention_metrics(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get retention metrics for the tenant
        
        Returns:
            Retention rate, churn rate, cohort analysis, etc.
            
        Requirements: REQ-CM-013
        """
        db = ClientRetentionService._get_db()
        # Get all clients
        all_clients = list(db.clients.find({"tenant_id": tenant_id}))

        if not all_clients:
            return {
                "total_clients": 0,
                "retention_rate": 0,
                "churn_rate": 0,
                "at_risk_count": 0,
                "cohorts": {}
            }

        # Calculate retention metrics
        total_clients = len(all_clients)

        # At-risk clients (no visit in 90 days)
        cutoff_date = datetime.now() - timedelta(days=90)
        at_risk_count = len([
            c for c in all_clients
            if c.get("last_visit_date", datetime.now()) < cutoff_date
        ])

        # Active clients (visited in last 90 days)
        active_count = total_clients - at_risk_count

        # Retention rate
        retention_rate = (active_count / total_clients * 100) if total_clients > 0 else 0

        # Churn rate
        churn_rate = (at_risk_count / total_clients * 100) if total_clients > 0 else 0

        # Cohort analysis (by segment)
        cohorts = {}
        for segment in ["new", "regular", "vip", "inactive"]:
            segment_clients = [c for c in all_clients if c.get("segment") == segment]
            if segment_clients:
                segment_active = len([
                    c for c in segment_clients
                    if c.get("last_visit_date", datetime.now()) >= cutoff_date
                ])
                cohorts[segment] = {
                    "total": len(segment_clients),
                    "active": segment_active,
                    "retention_rate": (segment_active / len(segment_clients) * 100) if segment_clients else 0
                }

        # Churn rate trends (last 30, 60, 90 days)
        trends = {}
        for days in [30, 60, 90]:
            cutoff = datetime.now() - timedelta(days=days)
            churned = len([
                c for c in all_clients
                if c.get("last_visit_date", datetime.now()) < cutoff
            ])
            trends[f"{days}_days"] = (churned / total_clients * 100) if total_clients > 0 else 0

        return {
            "total_clients": total_clients,
            "active_clients": active_count,
            "at_risk_clients": at_risk_count,
            "retention_rate": round(retention_rate, 2),
            "churn_rate": round(churn_rate, 2),
            "cohorts": cohorts,
            "churn_trends": trends,
            "calculated_at": datetime.now()
        }

    def create_winback_campaign(
        self,
        tenant_id: str,
        client_ids: List[str],
        campaign_name: str,
        message: str,
        channel: str = "sms",
        offer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a win-back campaign for at-risk clients
        
        Args:
            tenant_id: Tenant ID
            client_ids: List of client IDs to target
            campaign_name: Campaign name
            message: Campaign message
            channel: Communication channel
            offer: Special offer details
            
        Returns:
            Campaign details with send results
            
        Requirements: REQ-CM-013
        """
        db = ClientRetentionService._get_db()
        campaign = {
            "tenant_id": tenant_id,
            "campaign_name": campaign_name,
            "campaign_type": "winback",
            "message": message,
            "channel": channel,
            "offer": offer,
            "target_count": len(client_ids),
            "sent_count": 0,
            "failed_count": 0,
            "responses": 0,
            "conversions": 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "active"
        }

        # Insert campaign
        result = db.winback_campaigns.insert_one(campaign)
        campaign["id"] = str(result.inserted_id)

        # Send messages
        send_results = {
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        for client_id in client_ids:
            try:
                # Get client
                client = db.clients.find_one({
                    "_id": ObjectId(client_id),
                    "tenant_id": tenant_id
                })

                if not client:
                    send_results["failed"] += 1
                    send_results["errors"].append({
                        "client_id": client_id,
                        "error": "Client not found"
                    })
                    continue

                # Determine recipient
                if channel == "email":
                    if not client.get("email"):
                        send_results["failed"] += 1
                        continue
                    recipient = client["email"]
                else:
                    recipient = client.get("phone")
                    if not recipient:
                        send_results["failed"] += 1
                        continue

                # Log communication
                communication = CommunicationService.log_communication(
                    client_id=client_id,
                    tenant_id=tenant_id,
                    channel=channel,
                    message_type="winback",
                    content=message,
                    recipient=recipient,
                    direction="outbound",
                    campaign_id=str(campaign["id"])
                )

                # Send message
                try:
                    if channel == "sms":
                        from app.services.termii_service import send_sms
                        success = send_sms(recipient, message)
                    elif channel == "whatsapp":
                        from app.services.termii_service import send_whatsapp
                        success = send_whatsapp(recipient, message)
                    elif channel == "email":
                        from app.services.email_service import email_service
                        success = email_service.send_email(
                            to=recipient,
                            subject="We miss you!",
                            html=f"<p>{message}</p>",
                            text=message
                        )
                    else:
                        success = False

                    if success:
                        send_results["successful"] += 1
                        CommunicationService.update_communication_status(
                            communication_id=str(communication["_id"]),
                            status="sent"
                        )
                    else:
                        send_results["failed"] += 1
                        CommunicationService.update_communication_status(
                            communication_id=str(communication["_id"]),
                            status="failed"
                        )

                except Exception as e:
                    logger.error(f"Error sending winback message: {e}")
                    send_results["failed"] += 1
                    CommunicationService.update_communication_status(
                        communication_id=str(communication["_id"]),
                        status="failed",
                        error_message=str(e)
                    )

            except Exception as e:
                logger.error(f"Error processing client {client_id}: {e}")
                send_results["failed"] += 1
                send_results["errors"].append({
                    "client_id": client_id,
                    "error": str(e)
                })

        # Update campaign with send results
        db.winback_campaigns.update_one(
            {"_id": ObjectId(campaign["id"])},
            {
                "$set": {
                    "sent_count": send_results["successful"],
                    "failed_count": send_results["failed"],
                    "updated_at": datetime.now()
                }
            }
        )

        campaign.update(send_results)
        return campaign

    def track_winback_conversion(
        self,
        tenant_id: str,
        client_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """
        Track when a client returns after win-back campaign
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            campaign_id: Campaign ID
            
        Returns:
            Updated campaign data
        """
        db = ClientRetentionService._get_db()
        # Update campaign conversion count
        db.winback_campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$inc": {"conversions": 1},
                "$set": {"updated_at": datetime.now()}
            }
        )

        # Log activity
        db.client_activities.insert_one({
            "client_id": client_id,
            "tenant_id": tenant_id,
            "activity_type": "winback_conversion",
            "description": f"Client returned after win-back campaign {campaign_id}",
            "campaign_id": campaign_id,
            "created_at": datetime.now()
        })

        # Get updated campaign
        campaign = db.winback_campaigns.find_one({"_id": ObjectId(campaign_id)})
        if campaign:
            campaign["id"] = str(campaign.pop("_id"))

        return campaign

    def get_winback_campaign_results(
        self,
        tenant_id: str,
        campaign_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get results for a specific win-back campaign
        
        Args:
            tenant_id: Tenant ID
            campaign_id: Campaign ID
            
        Returns:
            Campaign results or None
        """
        db = ClientRetentionService._get_db()
        campaign = db.winback_campaigns.find_one({
            "_id": ObjectId(campaign_id),
            "tenant_id": tenant_id
        })

        if campaign:
            campaign["id"] = str(campaign.pop("_id"))
            
            # Calculate success rate
            if campaign.get("sent_count", 0) > 0:
                campaign["success_rate"] = (
                    campaign.get("conversions", 0) / campaign["sent_count"] * 100
                )
            else:
                campaign["success_rate"] = 0

        return campaign


# Create singleton instance
client_retention_service = ClientRetentionService()
