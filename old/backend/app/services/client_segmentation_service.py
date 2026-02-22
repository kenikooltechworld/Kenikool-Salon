"""
Client Segmentation Service - Business logic for client segmentation
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ClientSegmentationService:
    """Client segmentation service for automatic client classification"""
    
    # Segment definitions
    SEGMENT_NEW = "new"  # 0-1 visits
    SEGMENT_REGULAR = "regular"  # 2-10 visits
    SEGMENT_VIP = "vip"  # 11+ visits
    SEGMENT_INACTIVE = "inactive"  # No visit in 90 days
    
    @staticmethod
    def calculate_segment(client_id: str, tenant_id: str) -> str:
        """
        Calculate the appropriate segment for a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            
        Returns:
            Segment name (new, regular, vip, inactive)
        """
        db = Database.get_db()
        
        # Get client
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            raise NotFoundException("Client not found")
        
        # Get total visits
        total_visits = client.get("total_visits", 0)
        last_visit_date = client.get("last_visit_date")
        
        # Check if inactive (no visit in 90 days)
        if last_visit_date:
            days_since_last_visit = (datetime.utcnow() - last_visit_date).days
            if days_since_last_visit > 90:
                return ClientSegmentationService.SEGMENT_INACTIVE
        
        # Classify by visit count
        if total_visits == 0 or total_visits == 1:
            return ClientSegmentationService.SEGMENT_NEW
        elif total_visits <= 10:
            return ClientSegmentationService.SEGMENT_REGULAR
        else:
            return ClientSegmentationService.SEGMENT_VIP
    
    @staticmethod
    def update_client_segment(client_id: str, tenant_id: str, segment: Optional[str] = None) -> Dict:
        """
        Update client segment (auto-calculate or manual override)
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            segment: Optional manual segment override
            
        Returns:
            Updated client data
        """
        db = Database.get_db()
        
        # Calculate segment if not provided
        if segment is None:
            segment = ClientSegmentationService.calculate_segment(client_id, tenant_id)
        else:
            # Validate manual segment
            valid_segments = [
                ClientSegmentationService.SEGMENT_NEW,
                ClientSegmentationService.SEGMENT_REGULAR,
                ClientSegmentationService.SEGMENT_VIP,
                ClientSegmentationService.SEGMENT_INACTIVE
            ]
            if segment not in valid_segments:
                raise ValueError(f"Invalid segment. Must be one of: {', '.join(valid_segments)}")
        
        # Update client
        db.clients.update_one(
            {"_id": ObjectId(client_id), "tenant_id": tenant_id},
            {
                "$set": {
                    "segment": segment,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Updated segment for client {client_id} to {segment}")
        
        # Get updated client
        client = db.clients.find_one({"_id": ObjectId(client_id)})
        
        from app.services.client_service import ClientService
        return ClientService._format_client_response(client)
    
    @staticmethod
    def update_all_segments(tenant_id: str) -> Dict:
        """
        Update segments for all clients in a tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Summary of updates
        """
        db = Database.get_db()
        
        # Get all clients
        clients = list(db.clients.find({"tenant_id": tenant_id}))
        
        updated = 0
        errors = 0
        
        for client in clients:
            try:
                client_id = str(client["_id"])
                segment = ClientSegmentationService.calculate_segment(client_id, tenant_id)
                
                # Only update if segment changed
                if client.get("segment") != segment:
                    db.clients.update_one(
                        {"_id": client["_id"]},
                        {
                            "$set": {
                                "segment": segment,
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    updated += 1
                    
            except Exception as e:
                logger.error(f"Failed to update segment for client {client_id}: {e}")
                errors += 1
        
        logger.info(f"Segment update complete: {updated} updated, {errors} errors")
        
        return {
            "total": len(clients),
            "updated": updated,
            "errors": errors
        }
    
    @staticmethod
    def get_segment_distribution(tenant_id: str) -> Dict:
        """
        Get distribution of clients across segments
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dict with segment counts and percentages
        """
        db = Database.get_db()
        
        # Get total clients
        total_clients = db.clients.count_documents({"tenant_id": tenant_id})
        
        if total_clients == 0:
            return {
                "total": 0,
                "segments": {}
            }
        
        # Count by segment
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {
                "_id": "$segment",
                "count": {"$sum": 1}
            }}
        ]
        
        results = list(db.clients.aggregate(pipeline))
        
        segments = {}
        for result in results:
            segment = result["_id"] or "unclassified"
            count = result["count"]
            percentage = (count / total_clients) * 100
            
            segments[segment] = {
                "count": count,
                "percentage": round(percentage, 2)
            }
        
        return {
            "total": total_clients,
            "segments": segments
        }
    
    @staticmethod
    def get_segment_revenue(tenant_id: str) -> Dict:
        """
        Get revenue contribution by segment
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dict with revenue by segment
        """
        db = Database.get_db()
        
        # Get all clients with their segments and spending
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {
                "_id": "$segment",
                "total_revenue": {"$sum": "$total_spent"},
                "client_count": {"$sum": 1},
                "avg_revenue_per_client": {"$avg": "$total_spent"}
            }}
        ]
        
        results = list(db.clients.aggregate(pipeline))
        
        # Calculate total revenue
        total_revenue = sum(r["total_revenue"] for r in results)
        
        segments = {}
        for result in results:
            segment = result["_id"] or "unclassified"
            revenue = result["total_revenue"]
            percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            segments[segment] = {
                "revenue": float(revenue),
                "percentage": round(percentage, 2),
                "client_count": result["client_count"],
                "avg_revenue_per_client": float(result["avg_revenue_per_client"])
            }
        
        return {
            "total_revenue": float(total_revenue),
            "segments": segments
        }


# Singleton instance
client_segmentation_service = ClientSegmentationService()
