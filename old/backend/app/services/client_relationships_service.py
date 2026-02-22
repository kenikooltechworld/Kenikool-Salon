"""
Client Relationships Service

Handles client relationships:
- Client linking (family, friend, referral)
- Referral tracking
- Referral value calculation
- Network visualization

Requirements: REQ-CM-015
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from bson import ObjectId
from decimal import Decimal

from app.database import Database

logger = logging.getLogger(__name__)


class ClientRelationshipsService:
    """Service for managing client relationships"""

    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()

    # Valid relationship types
    RELATIONSHIP_TYPES = ["family", "friend", "referral"]

    def link_clients(
        self,
        tenant_id: str,
        client_id: str,
        related_client_id: str,
        relationship_type: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Link two clients with a relationship
        
        Args:
            tenant_id: Tenant ID
            client_id: Primary client ID
            related_client_id: Related client ID
            relationship_type: Type of relationship (family, friend, referral)
            notes: Optional notes
            
        Returns:
            Created relationship
            
        Requirements: REQ-CM-015
        """
        db = ClientRelationshipsService._get_db()
        # Validate relationship type
        if relationship_type not in self.RELATIONSHIP_TYPES:
            raise ValueError(f"Invalid relationship type: {relationship_type}")

        # Verify both clients exist
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })

        related_client = db.clients.find_one({
            "_id": ObjectId(related_client_id),
            "tenant_id": tenant_id
        })

        if not client or not related_client:
            raise ValueError("One or both clients not found")

        # Check if relationship already exists
        existing = db.client_relationships.find_one({
            "tenant_id": tenant_id,
            "$or": [
                {
                    "client_id": client_id,
                    "related_client_id": related_client_id
                },
                {
                    "client_id": related_client_id,
                    "related_client_id": client_id
                }
            ]
        })

        if existing:
            raise ValueError("Relationship already exists")

        # Create relationship
        relationship = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "related_client_id": related_client_id,
            "relationship_type": relationship_type,
            "notes": notes,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = db.client_relationships.insert_one(relationship)
        relationship["id"] = str(result.inserted_id)

        # Create bidirectional relationship
        reverse_relationship = {
            "tenant_id": tenant_id,
            "client_id": related_client_id,
            "related_client_id": client_id,
            "relationship_type": relationship_type,
            "notes": notes,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        db.client_relationships.insert_one(reverse_relationship)

        return relationship

    def get_client_relationships(
        self,
        tenant_id: str,
        client_id: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all relationships for a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            relationship_type: Filter by relationship type
            
        Returns:
            List of relationships with related client details
            
        Requirements: REQ-CM-015
        """
        db = ClientRelationshipsService._get_db()
        query = {
            "tenant_id": tenant_id,
            "client_id": client_id
        }

        if relationship_type:
            query["relationship_type"] = relationship_type

        relationships = list(db.client_relationships.find(query))

        # Enrich with related client details
        for rel in relationships:
            rel["id"] = str(rel.pop("_id"))

            # Get related client
            related_client = db.clients.find_one({
                "_id": ObjectId(rel["related_client_id"])
            })

            if related_client:
                rel["related_client"] = {
                    "id": str(related_client["_id"]),
                    "name": related_client.get("name"),
                    "phone": related_client.get("phone"),
                    "email": related_client.get("email"),
                    "total_spent": related_client.get("total_spent", 0)
                }

        return relationships

    def unlink_clients(
        self,
        tenant_id: str,
        client_id: str,
        related_client_id: str
    ) -> bool:
        """
        Remove relationship between two clients
        
        Args:
            tenant_id: Tenant ID
            client_id: Primary client ID
            related_client_id: Related client ID
            
        Returns:
            True if successful
            
        Requirements: REQ-CM-015
        """
        db = ClientRelationshipsService._get_db()
        # Delete both directions
        result1 = db.client_relationships.delete_one({
            "tenant_id": tenant_id,
            "client_id": client_id,
            "related_client_id": related_client_id
        })

        result2 = db.client_relationships.delete_one({
            "tenant_id": tenant_id,
            "client_id": related_client_id,
            "related_client_id": client_id
        })

        return result1.deleted_count > 0 or result2.deleted_count > 0

    def track_referral(
        self,
        tenant_id: str,
        referrer_id: str,
        referred_client_id: str,
        referral_source: str = "direct"
    ) -> Dict[str, Any]:
        """
        Track a referral relationship
        
        Args:
            tenant_id: Tenant ID
            referrer_id: Client who referred
            referred_client_id: Client who was referred
            referral_source: Source of referral
            
        Returns:
            Referral record
            
        Requirements: REQ-CM-015
        """
        db = ClientRelationshipsService._get_db()
        # Create referral relationship
        referral = {
            "tenant_id": tenant_id,
            "referrer_id": referrer_id,
            "referred_client_id": referred_client_id,
            "referral_source": referral_source,
            "created_at": datetime.now(),
            "referral_value": 0,  # Will be updated when referred client makes purchase
            "status": "pending"  # pending, converted, inactive
        }

        result = db.referrals.insert_one(referral)
        referral["id"] = str(result.inserted_id)

        # Link clients as referral relationship
        try:
            self.link_clients(
                tenant_id=tenant_id,
                client_id=referrer_id,
                related_client_id=referred_client_id,
                relationship_type="referral",
                notes=f"Referral source: {referral_source}"
            )
        except ValueError:
            # Relationship might already exist
            pass

        return referral

    def get_referrals_by_referrer(
        self,
        tenant_id: str,
        referrer_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all referrals made by a client
        
        Args:
            tenant_id: Tenant ID
            referrer_id: Referrer client ID
            
        Returns:
            List of referrals with details
            
        Requirements: REQ-CM-015
        """
        db = ClientRelationshipsService._get_db()
        referrals = list(db.referrals.find({
            "tenant_id": tenant_id,
            "referrer_id": referrer_id
        }).sort("created_at", -1))

        # Enrich with referred client details
        for ref in referrals:
            ref["id"] = str(ref.pop("_id"))

            # Get referred client
            referred_client = db.clients.find_one({
                "_id": ObjectId(ref["referred_client_id"])
            })

            if referred_client:
                ref["referred_client"] = {
                    "id": str(referred_client["_id"]),
                    "name": referred_client.get("name"),
                    "phone": referred_client.get("phone"),
                    "email": referred_client.get("email"),
                    "total_spent": referred_client.get("total_spent", 0)
                }

        return referrals

    def calculate_referral_value(
        self,
        tenant_id: str,
        referrer_id: str
    ) -> Decimal:
        """
        Calculate total referral value for a client
        
        Sum of all revenue from referred clients
        
        Args:
            tenant_id: Tenant ID
            referrer_id: Referrer client ID
            
        Returns:
            Total referral value
            
        Requirements: REQ-CM-015
        """
        db = ClientRelationshipsService._get_db()
        referrals = list(db.referrals.find({
            "tenant_id": tenant_id,
            "referrer_id": referrer_id,
            "status": "converted"
        }))

        total_value = Decimal(0)

        for ref in referrals:
            # Get referred client's total spent
            referred_client = db.clients.find_one({
                "_id": ObjectId(ref["referred_client_id"])
            })

            if referred_client:
                total_value += Decimal(str(referred_client.get("total_spent", 0)))

        return total_value

    def get_top_referrers(
        self,
        tenant_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top referrers by referral value
        
        Args:
            tenant_id: Tenant ID
            limit: Number of top referrers to return
            
        Returns:
            List of top referrers with their referral value
            
        Requirements: REQ-CM-015
        """
        db = ClientRelationshipsService._get_db()
        # Get all referrers
        referrers = db.referrals.aggregate([
            {"$match": {"tenant_id": tenant_id, "status": "converted"}},
            {"$group": {
                "_id": "$referrer_id",
                "referral_count": {"$sum": 1},
                "total_value": {"$sum": "$referral_value"}
            }},
            {"$sort": {"total_value": -1}},
            {"$limit": limit}
        ])

        top_referrers = []

        for referrer in referrers:
            # Get referrer details
            referrer_client = db.clients.find_one({
                "_id": ObjectId(referrer["_id"])
            })

            if referrer_client:
                top_referrers.append({
                    "id": str(referrer_client["_id"]),
                    "name": referrer_client.get("name"),
                    "phone": referrer_client.get("phone"),
                    "referral_count": referrer["referral_count"],
                    "total_referral_value": referrer["total_value"]
                })

        return top_referrers

    def get_referral_network(
        self,
        tenant_id: str,
        client_id: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        Get referral network for a client (graph data)
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            depth: Depth of network to retrieve
            
        Returns:
            Network graph data (nodes and edges)
            
        Requirements: REQ-CM-015
        """
        db = ClientRelationshipsService._get_db()
        nodes = []
        edges = []
        visited = set()

        def traverse(current_id: str, current_depth: int):
            if current_depth > depth or current_id in visited:
                return

            visited.add(current_id)

            # Get client
            client = db.clients.find_one({
                "_id": ObjectId(current_id)
            })

            if not client:
                return

            # Add node
            nodes.append({
                "id": current_id,
                "name": client.get("name"),
                "total_spent": client.get("total_spent", 0),
                "depth": current_depth
            })

            # Get referrals made by this client
            referrals = list(db.referrals.find({
                "tenant_id": tenant_id,
                "referrer_id": current_id
            }))

            for ref in referrals:
                referred_id = ref["referred_client_id"]

                # Add edge
                edges.append({
                    "source": current_id,
                    "target": referred_id,
                    "type": "referral",
                    "value": ref.get("referral_value", 0)
                })

                # Traverse deeper
                traverse(referred_id, current_depth + 1)

        # Start traversal
        traverse(client_id, 0)

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }

    def update_referral_status(
        self,
        tenant_id: str,
        referral_id: str,
        status: str,
        referral_value: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Update referral status and value
        
        Args:
            tenant_id: Tenant ID
            referral_id: Referral ID
            status: New status (pending, converted, inactive)
            referral_value: Referral value (for converted status)
            
        Returns:
            Updated referral
        """
        db = ClientRelationshipsService._get_db()
        update_data = {
            "status": status,
            "updated_at": datetime.now()
        }

        if referral_value is not None:
            update_data["referral_value"] = referral_value

        result = db.referrals.update_one(
            {
                "_id": ObjectId(referral_id),
                "tenant_id": tenant_id
            },
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise ValueError("Referral not found")

        # Get updated referral
        referral = db.referrals.find_one({
            "_id": ObjectId(referral_id)
        })

        if referral:
            referral["id"] = str(referral.pop("_id"))

        return referral


# Create singleton instance
client_relationships_service = ClientRelationshipsService()
