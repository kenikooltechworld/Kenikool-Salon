"""
Data privacy protection service for analytics
"""
import logging
import hashlib
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DataPrivacyService:
    """Service for managing data privacy and anonymization"""

    def __init__(self):
        """Initialize data privacy service"""
        self.audit_log = []
        self.sensitive_fields = {
            "client": ["email", "phone", "address", "name"],
            "staff": ["email", "phone", "address", "name"],
            "user": ["email", "phone", "address", "name"],
        }

    def anonymize_client_data(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize client data for exports"""
        anonymized = client_data.copy()
        
        # Hash sensitive fields
        if "email" in anonymized:
            anonymized["email"] = self._hash_value(anonymized["email"])
        
        if "phone" in anonymized:
            anonymized["phone"] = self._hash_value(anonymized["phone"])
        
        if "name" in anonymized:
            anonymized["name"] = f"Client_{self._hash_value(anonymized['name'])[:8]}"
        
        if "address" in anonymized:
            anonymized["address"] = "[REDACTED]"
        
        return anonymized

    def anonymize_staff_data(self, staff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize staff data for exports"""
        anonymized = staff_data.copy()
        
        # Hash sensitive fields
        if "email" in anonymized:
            anonymized["email"] = self._hash_value(anonymized["email"])
        
        if "phone" in anonymized:
            anonymized["phone"] = self._hash_value(anonymized["phone"])
        
        if "name" in anonymized:
            anonymized["name"] = f"Staff_{self._hash_value(anonymized['name'])[:8]}"
        
        if "address" in anonymized:
            anonymized["address"] = "[REDACTED]"
        
        return anonymized

    def anonymize_export_data(
        self,
        data: List[Dict[str, Any]],
        entity_type: str = "client"
    ) -> List[Dict[str, Any]]:
        """Anonymize data for export"""
        anonymized_data = []
        
        for item in data:
            if entity_type == "client":
                anonymized_data.append(self.anonymize_client_data(item))
            elif entity_type == "staff":
                anonymized_data.append(self.anonymize_staff_data(item))
            else:
                anonymized_data.append(item)
        
        return anonymized_data

    def add_watermark(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Add watermark to exported data"""
        watermarked = data.copy()
        watermarked["_watermark"] = {
            "exported_by": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "confidential": True,
        }
        return watermarked

    def add_export_tracking(
        self,
        export_id: str,
        user_id: str,
        data_type: str,
        record_count: int,
        includes_pii: bool = False
    ) -> None:
        """Track data exports for audit purposes"""
        audit_entry = {
            "export_id": export_id,
            "user_id": user_id,
            "data_type": data_type,
            "record_count": record_count,
            "includes_pii": includes_pii,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.audit_log.append(audit_entry)
        logger.info(f"Export tracked: {export_id} by user {user_id}")

    def get_audit_log(
        self,
        user_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        filtered_log = self.audit_log
        
        if user_id:
            filtered_log = [entry for entry in filtered_log if entry["user_id"] == user_id]
        
        if start_date:
            filtered_log = [
                entry for entry in filtered_log
                if datetime.fromisoformat(entry["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_log = [
                entry for entry in filtered_log
                if datetime.fromisoformat(entry["timestamp"]) <= end_date
            ]
        
        return filtered_log

    def check_export_limit(
        self,
        user_id: str,
        limit_per_day: int = 10
    ) -> bool:
        """Check if user has exceeded export limit"""
        today = datetime.utcnow().date()
        today_exports = [
            entry for entry in self.audit_log
            if entry["user_id"] == user_id
            and datetime.fromisoformat(entry["timestamp"]).date() == today
        ]
        
        return len(today_exports) < limit_per_day

    def mask_sensitive_fields(
        self,
        data: Dict[str, Any],
        entity_type: str = "client"
    ) -> Dict[str, Any]:
        """Mask sensitive fields in data"""
        masked = data.copy()
        
        sensitive = self.sensitive_fields.get(entity_type, [])
        for field in sensitive:
            if field in masked:
                masked[field] = self._mask_value(masked[field])
        
        return masked

    def redact_pii(self, text: str) -> str:
        """Redact personally identifiable information from text"""
        # Simple redaction - in production, use more sophisticated NLP
        import re
        
        # Redact email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Redact phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        # Redact SSN
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        return text

    def _hash_value(self, value: str) -> str:
        """Hash a value for anonymization"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]

    def _mask_value(self, value: str) -> str:
        """Mask a value"""
        if isinstance(value, str):
            if len(value) <= 2:
                return "*" * len(value)
            return value[:2] + "*" * (len(value) - 2)
        return str(value)

    def get_privacy_policy(self) -> Dict[str, Any]:
        """Get data privacy policy"""
        return {
            "data_retention": "90 days",
            "anonymization": "Enabled for exports",
            "audit_logging": "Enabled",
            "export_limit": "10 per day",
            "pii_protection": "Enabled",
            "encryption": "AES-256",
        }

    def validate_data_access(
        self,
        user_id: str,
        data_type: str,
        user_role: str
    ) -> bool:
        """Validate if user can access specific data type"""
        # Define role-based access
        access_rules = {
            "admin": ["all"],
            "manager": ["aggregated", "anonymized"],
            "staff": ["own_data"],
            "viewer": ["public"],
        }
        
        allowed_types = access_rules.get(user_role, [])
        
        if "all" in allowed_types:
            return True
        
        if data_type in allowed_types:
            return True
        
        return False


# Global data privacy service instance
data_privacy_service = DataPrivacyService()
