from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId


class SegmentService:
    """Service for managing client segments"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.segments_collection: Collection = self.db["segments"]
        self.clients_collection: Collection = self.db["clients"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes for efficient querying"""
        self.segments_collection.create_index("tenant_id")
        self.segments_collection.create_index([("tenant_id", 1), ("name", 1)])
        self.clients_collection.create_index("tenant_id")
        self.clients_collection.create_index([("tenant_id", 1), ("last_visit_date", -1)])
        self.clients_collection.create_index([("tenant_id", 1), ("total_spending", -1)])

    def create_segment(self, tenant_id: str, name: str, description: Optional[str],
                      criteria: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new segment"""
        segment = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "name": name,
            "description": description,
            "criteria": criteria,
            "client_count": 0,
            "last_calculated_at": datetime.utcnow(),
            "is_dynamic": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": created_by
        }
        result = self.segments_collection.insert_one(segment)
        segment["_id"] = str(segment["_id"])
        return segment

    def get_segment(self, tenant_id: str, segment_id: str) -> Optional[Dict[str, Any]]:
        """Get a segment by ID"""
        segment = self.segments_collection.find_one({
            "_id": ObjectId(segment_id),
            "tenant_id": tenant_id
        })
        if segment:
            segment["_id"] = str(segment["_id"])
        return segment

    def list_segments(self, tenant_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """List all segments for a tenant"""
        segments = list(self.segments_collection.find(
            {"tenant_id": tenant_id}
        ).skip(skip).limit(limit))
        for seg in segments:
            seg["_id"] = str(seg["_id"])
        return segments

    def update_segment(self, tenant_id: str, segment_id: str, 
                      name: Optional[str] = None, description: Optional[str] = None,
                      criteria: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Update a segment"""
        update_data = {"updated_at": datetime.utcnow()}
        if name:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if criteria:
            update_data["criteria"] = criteria

        result = self.segments_collection.find_one_and_update(
            {"_id": ObjectId(segment_id), "tenant_id": tenant_id},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    def delete_segment(self, tenant_id: str, segment_id: str) -> bool:
        """Delete a segment"""
        result = self.segments_collection.delete_one({
            "_id": ObjectId(segment_id),
            "tenant_id": tenant_id
        })
        return result.deleted_count > 0

    def calculate_segment_size(self, tenant_id: str, criteria: Dict[str, Any]) -> int:
        """Calculate the number of clients matching segment criteria"""
        query = self._build_query(tenant_id, criteria)
        return self.clients_collection.count_documents(query)

    def get_segment_clients(self, tenant_id: str, segment_id: str, 
                           skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get clients matching a segment"""
        segment = self.get_segment(tenant_id, segment_id)
        if not segment:
            return []

        query = self._build_query(tenant_id, segment["criteria"])
        clients = list(self.clients_collection.find(query).skip(skip).limit(limit))
        for client in clients:
            client["_id"] = str(client["_id"])
        return clients

    def preview_segment(self, tenant_id: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Preview segment without saving"""
        client_count = self.calculate_segment_size(tenant_id, criteria)
        sample_clients = list(self.clients_collection.find(
            self._build_query(tenant_id, criteria)
        ).limit(5))
        
        for client in sample_clients:
            client["_id"] = str(client["_id"])

        return {
            "client_count": client_count,
            "sample_clients": sample_clients,
            "criteria": criteria
        }

    def _build_query(self, tenant_id: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Build MongoDB query from segment criteria"""
        query = {"tenant_id": tenant_id}

        if criteria.get("visit_frequency"):
            vf = criteria["visit_frequency"]
            operator = vf.get("operator", "gt")
            value = vf.get("value", 0)
            
            if operator == "gt":
                query["visit_count"] = {"$gt": value}
            elif operator == "lt":
                query["visit_count"] = {"$lt": value}
            elif operator == "eq":
                query["visit_count"] = value
            elif operator == "between":
                min_val, max_val = value
                query["visit_count"] = {"$gte": min_val, "$lte": max_val}

        if criteria.get("last_visit"):
            lv = criteria["last_visit"]
            operator = lv.get("operator", "within")
            days = lv.get("days", 30)
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            if operator == "within":
                query["last_visit"] = {"$gte": cutoff_date}
            elif operator == "before":
                query["last_visit"] = {"$lt": cutoff_date}
            elif operator == "after":
                query["last_visit"] = {"$gte": cutoff_date}

        if criteria.get("total_spending"):
            ts = criteria["total_spending"]
            operator = ts.get("operator", "gt")
            amount = ts.get("amount", 0)
            
            if operator == "gt":
                query["total_spending"] = {"$gt": amount}
            elif operator == "lt":
                query["total_spending"] = {"$lt": amount}
            elif operator == "eq":
                query["total_spending"] = amount
            elif operator == "between":
                min_amt, max_amt = amount
                query["total_spending"] = {"$gte": min_amt, "$lte": max_amt}

        if criteria.get("service_preferences"):
            query["service_preferences"] = {"$in": criteria["service_preferences"]}

        if criteria.get("loyalty_tier"):
            query["loyalty_tier"] = {"$in": criteria["loyalty_tier"]}

        if criteria.get("demographics"):
            demo = criteria["demographics"]
            if demo.get("age_range"):
                min_age, max_age = demo["age_range"]
                query["age"] = {"$gte": min_age, "$lte": max_age}
            if demo.get("gender"):
                query["gender"] = demo["gender"]

        if criteria.get("tags"):
            query["tags"] = {"$in": criteria["tags"]}

        return query
