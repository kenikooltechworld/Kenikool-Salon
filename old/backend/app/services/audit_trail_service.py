"""
Audit Trail and Compliance Service

Handles audit logging and compliance reporting including:
- Audit log creation and retrieval
- Change tracking for all entities
- Compliance reporting
- Access logging
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class AuditTrailService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.audit_logs = db.audit_logs
        self.access_logs = db.access_logs

    def log_change(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        user_id: str = "system",
        ip_address: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log a change to an entity"""
        
        log_entry = {
            "tenant_id": self.tenant_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "old_values": old_values or {},
            "new_values": new_values or {},
            "user_id": user_id,
            "ip_address": ip_address,
            "description": description,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        result = self.audit_logs.insert_one(log_entry)
        log_entry["id"] = str(result.inserted_id)
        del log_entry["_id"]
        
        return log_entry

    def get_audit_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if entity_type:
            query["entity_type"] = entity_type
        if entity_id:
            query["entity_id"] = entity_id
        if user_id:
            query["user_id"] = user_id
        if action:
            query["action"] = action
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                date_query["$lte"] = datetime.fromisoformat(end_date)
            if date_query:
                query["timestamp"] = date_query
        
        logs = list(
            self.audit_logs.find(query)
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )
        
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        
        return logs

    def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get complete change history for an entity"""
        
        logs = list(
            self.audit_logs.find({
                "tenant_id": self.tenant_id,
                "entity_type": entity_type,
                "entity_id": entity_id
            })
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        
        return logs

    def log_access(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        access_type: str,
        ip_address: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log access to sensitive data"""
        
        access_log = {
            "tenant_id": self.tenant_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "access_type": access_type,
            "ip_address": ip_address,
            "description": description,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        result = self.access_logs.insert_one(access_log)
        access_log["id"] = str(result.inserted_id)
        del access_log["_id"]
        
        return access_log

    def get_access_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get access logs with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if entity_type:
            query["entity_type"] = entity_type
        if entity_id:
            query["entity_id"] = entity_id
        if user_id:
            query["user_id"] = user_id
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                date_query["$lte"] = datetime.fromisoformat(end_date)
            if date_query:
                query["timestamp"] = date_query
        
        logs = list(
            self.access_logs.find(query)
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )
        
        for log in logs:
            log["id"] = str(log["_id"])
            del log["_id"]
        
        return logs

    def get_user_activity(
        self,
        user_id: str,
        days: int = 30,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get user activity summary"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get audit logs
        audit_logs = list(
            self.audit_logs.find({
                "tenant_id": self.tenant_id,
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            })
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        # Get access logs
        access_logs = list(
            self.access_logs.find({
                "tenant_id": self.tenant_id,
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            })
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        # Count by action
        action_counts = {}
        for log in audit_logs:
            action = log.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Count by entity type
        entity_counts = {}
        for log in audit_logs:
            entity_type = log.get("entity_type", "unknown")
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_changes": len(audit_logs),
            "total_accesses": len(access_logs),
            "action_breakdown": action_counts,
            "entity_breakdown": entity_counts,
            "recent_changes": [
                {
                    "id": str(log["_id"]),
                    "entity_type": log.get("entity_type"),
                    "action": log.get("action"),
                    "timestamp": log.get("timestamp")
                }
                for log in audit_logs[:10]
            ]
        }

    def get_compliance_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Get all changes in period
        all_logs = list(
            self.audit_logs.find({
                "tenant_id": self.tenant_id,
                "timestamp": {
                    "$gte": start_dt,
                    "$lte": end_dt
                }
            })
        )
        
        # Get all access logs in period
        all_access = list(
            self.access_logs.find({
                "tenant_id": self.tenant_id,
                "timestamp": {
                    "$gte": start_dt,
                    "$lte": end_dt
                }
            })
        )
        
        # Analyze changes by entity type
        entity_changes = {}
        for log in all_logs:
            entity_type = log.get("entity_type", "unknown")
            if entity_type not in entity_changes:
                entity_changes[entity_type] = {
                    "total": 0,
                    "creates": 0,
                    "updates": 0,
                    "deletes": 0,
                    "users": set()
                }
            
            entity_changes[entity_type]["total"] += 1
            action = log.get("action", "").lower()
            if "create" in action:
                entity_changes[entity_type]["creates"] += 1
            elif "update" in action:
                entity_changes[entity_type]["updates"] += 1
            elif "delete" in action:
                entity_changes[entity_type]["deletes"] += 1
            
            entity_changes[entity_type]["users"].add(log.get("user_id"))
        
        # Convert sets to lists for JSON serialization
        for entity_type in entity_changes:
            entity_changes[entity_type]["users"] = list(entity_changes[entity_type]["users"])
            entity_changes[entity_type]["user_count"] = len(entity_changes[entity_type]["users"])
        
        # Analyze access patterns
        access_by_user = {}
        for log in all_access:
            user_id = log.get("user_id")
            if user_id not in access_by_user:
                access_by_user[user_id] = 0
            access_by_user[user_id] += 1
        
        # Identify sensitive data access
        sensitive_entities = ["invoice", "payment", "bill", "account"]
        sensitive_access = [
            log for log in all_access
            if any(entity in log.get("entity_type", "").lower() for entity in sensitive_entities)
        ]
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_changes": len(all_logs),
            "total_accesses": len(all_access),
            "entity_changes": entity_changes,
            "access_by_user": access_by_user,
            "sensitive_data_accesses": len(sensitive_access),
            "unique_users": len(set(log.get("user_id") for log in all_logs)),
            "generated_at": datetime.utcnow().isoformat()
        }

    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit trail summary for the tenant"""
        
        total_logs = self.audit_logs.count_documents({"tenant_id": self.tenant_id})
        total_access = self.access_logs.count_documents({"tenant_id": self.tenant_id})
        
        # Get recent activity
        recent_logs = list(
            self.audit_logs.find({"tenant_id": self.tenant_id})
            .sort("timestamp", -1)
            .limit(5)
        )
        
        # Get active users
        pipeline = [
            {"$match": {"tenant_id": self.tenant_id}},
            {"$group": {
                "_id": "$user_id",
                "change_count": {"$sum": 1}
            }},
            {"$sort": {"change_count": -1}},
            {"$limit": 10}
        ]
        
        active_users = list(self.audit_logs.aggregate(pipeline))
        
        return {
            "total_audit_logs": total_logs,
            "total_access_logs": total_access,
            "recent_changes": [
                {
                    "id": str(log["_id"]),
                    "entity_type": log.get("entity_type"),
                    "action": log.get("action"),
                    "user_id": log.get("user_id"),
                    "timestamp": log.get("timestamp")
                }
                for log in recent_logs
            ],
            "active_users": [
                {
                    "user_id": user["_id"],
                    "changes": user["change_count"]
                }
                for user in active_users
            ]
        }
