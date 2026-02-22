from datetime import datetime, timedelta
from typing import Dict, Optional, List
from bson import ObjectId
from app.database import db
import json

class PrivacyGDPRService:
    """Service for managing privacy and GDPR compliance."""
    
    @staticmethod
    def record_consent(tenant_id: str, client_id: str, consent_type: str, 
                      ip_address: str, user_agent: str) -> Dict:
        """Record client consent."""
        consent_record = {
            "client_id": ObjectId(client_id),
            "tenant_id": tenant_id,
            "consent_type": consent_type,
            "granted": True,
            "timestamp": datetime.utcnow(),
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        
        result = db.consent_records.insert_one(consent_record)
        
        db.clients.update_one(
            {"_id": ObjectId(client_id)},
            {"$set": {f"consent.{consent_type}": True}}
        )
        
        return {"status": "recorded", "consent_id": str(result.inserted_id)}
    
    @staticmethod
    def export_client_data(tenant_id: str, client_id: str) -> Dict:
        """Export all client data in machine-readable format."""
        client = db.clients.find_one({"_id": ObjectId(client_id), "tenant_id": tenant_id})
        
        if not client:
            raise ValueError("Client not found")
        
        export_data = {
            "client": {k: str(v) if isinstance(v, ObjectId) else v 
                      for k, v in client.items()},
            "bookings": list(db.bookings.find({"client_id": ObjectId(client_id)})),
            "communications": list(db.communications.find({"client_id": ObjectId(client_id)})),
            "payments": list(db.payments.find({"client_id": ObjectId(client_id)})),
            "consent_records": list(db.consent_records.find({"client_id": ObjectId(client_id)})),
        }
        
        return export_data
    
    @staticmethod
    def anonymize_client(tenant_id: str, client_id: str) -> Dict:
        """Anonymize client PII while preserving analytics."""
        client = db.clients.find_one({"_id": ObjectId(client_id), "tenant_id": tenant_id})
        
        if not client:
            raise ValueError("Client not found")
        
        anonymized_data = {
            "name": f"Anonymous_{client_id[:8]}",
            "email": f"anonymous_{client_id[:8]}@anonymized.local",
            "phone": None,
            "address": None,
            "is_anonymized": True,
            "anonymized_at": datetime.utcnow(),
        }
        
        db.clients.update_one(
            {"_id": ObjectId(client_id)},
            {"$set": anonymized_data}
        )
        
        return {"status": "anonymized", "client_id": str(client_id)}
    
    @staticmethod
    def set_retention_policy(tenant_id: str, policy: Dict) -> Dict:
        """Set data retention policy."""
        retention_policy = {
            "tenant_id": tenant_id,
            "retention_days": policy.get("retention_days", 365),
            "auto_anonymize": policy.get("auto_anonymize", True),
            "anonymize_after_days": policy.get("anonymize_after_days", 180),
            "created_at": datetime.utcnow(),
        }
        
        result = db.retention_policies.update_one(
            {"tenant_id": tenant_id},
            {"$set": retention_policy},
            upsert=True
        )
        
        return {"status": "policy_set", "policy_id": str(result.upserted_id or result.matched_count)}
    
    @staticmethod
    def process_retention_cleanup(tenant_id: str) -> Dict:
        """Process automatic data retention cleanup."""
        policy = db.retention_policies.find_one({"tenant_id": tenant_id})
        
        if not policy:
            return {"status": "no_policy"}
        
        cutoff_date = datetime.utcnow() - timedelta(days=policy["retention_days"])
        anonymize_date = datetime.utcnow() - timedelta(days=policy["anonymize_after_days"])
        
        # Delete old records
        deleted = db.clients.delete_many({
            "tenant_id": tenant_id,
            "created_at": {"$lt": cutoff_date},
            "is_anonymized": True
        })
        
        # Anonymize old clients
        anonymized = db.clients.update_many(
            {
                "tenant_id": tenant_id,
                "created_at": {"$lt": anonymize_date},
                "is_anonymized": False
            },
            {"$set": {"is_anonymized": True, "anonymized_at": datetime.utcnow()}}
        )
        
        return {
            "status": "cleanup_complete",
            "deleted_count": deleted.deleted_count,
            "anonymized_count": anonymized.modified_count
        }
