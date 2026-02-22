"""
Audit log service - Security event logging and suspicious activity detection
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from bson import ObjectId

from app.database import Database

logger = logging.getLogger(__name__)


class NotFoundException(Exception):
    """Raised when resource is not found"""
    pass


class AuditLogService:
    """Service for security audit logging and event tracking"""

    @staticmethod
    async def log_event(
        user_id: str,
        tenant_id: str,
        event_type: str,
        request_info: Dict,
        success: bool,
        details: Optional[Dict] = None
    ) -> str:
        """
        Log security event
        
        Requirements: 12.1, 12.2, 12.3, 23.1
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            event_type: Type of event (login, password_change, 2fa_enabled, etc.)
            request_info: Request metadata (IP, device, browser, user_agent, location)
            success: Whether event was successful
            details: Additional event-specific data
            
        Returns:
            Log entry ID
        """
        db = Database.get_db()
        
        # Detect suspicious activity
        flagged = await AuditLogService.detect_suspicious_activity(
            user_id, tenant_id, event_type, request_info, success
        )
        
        # Create log entry
        log_entry = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "event_type": event_type,
            "ip_address": request_info.get("ip_address", "unknown"),
            "device": request_info.get("device", "Unknown"),
            "browser": request_info.get("browser", "Unknown"),
            "location": request_info.get("location", "Unknown"),
            "user_agent": request_info.get("user_agent", ""),
            "success": success,
            "details": details or {},
            "flagged": flagged,
            "timestamp": datetime.utcnow()
        }
        
        result = db.security_logs.insert_one(log_entry)
        log_id = str(result.inserted_id)
        
        if flagged:
            logger.warning(f"Suspicious activity detected: {event_type} for user {user_id}")
        else:
            logger.info(f"Security event logged: {event_type} for user {user_id}")
        
        return log_id

    @staticmethod
    async def detect_suspicious_activity(
        user_id: str,
        tenant_id: str,
        event_type: str,
        request_info: Dict,
        success: bool
    ) -> bool:
        """
        Detect suspicious activity patterns
        
        Requirements: 12.2, 12.5, 23.3, 23.4
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            event_type: Type of event
            request_info: Request metadata
            success: Whether event was successful
            
        Returns:
            True if suspicious activity detected
        """
        db = Database.get_db()
        
        # Check for multiple failed logins
        if event_type == "login" and not success:
            failed_count = db.security_logs.count_documents({
                "user_id": user_id,
                "tenant_id": tenant_id,
                "event_type": "login",
                "success": False,
                "timestamp": {"$gt": datetime.utcnow() - timedelta(hours=1)}
            })
            
            if failed_count >= 3:
                return True
        
        # Check for login from new location
        if event_type == "login" and success:
            location = request_info.get("location", "Unknown")
            
            # Check if location has been seen before
            recent_login = db.security_logs.find_one({
                "user_id": user_id,
                "tenant_id": tenant_id,
                "event_type": "login",
                "success": True,
                "location": location,
                "timestamp": {"$gt": datetime.utcnow() - timedelta(days=30)}
            })
            
            if not recent_login:
                return True
        
        return False

    @staticmethod
    async def get_audit_log(
        user_id: str,
        tenant_id: str,
        limit: int = 100,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get audit log entries
        
        Requirements: 12.1, 12.4
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            limit: Number of records to return
            event_type: Filter by event type (optional)
            
        Returns:
            List of audit log entries
        """
        db = Database.get_db()
        
        query = {
            "user_id": user_id,
            "tenant_id": tenant_id
        }
        
        if event_type:
            query["event_type"] = event_type
        
        logs = list(db.security_logs.find(query).sort("timestamp", -1).limit(limit))
        
        # Convert ObjectId to string
        for log in logs:
            log["id"] = str(log.pop("_id"))
        
        return logs

    @staticmethod
    async def export_audit_log(user_id: str, tenant_id: str) -> str:
        """
        Export audit log as CSV
        
        Requirements: 12.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            CSV content as string
        """
        db = Database.get_db()
        
        logs = list(db.security_logs.find({
            "user_id": user_id,
            "tenant_id": tenant_id
        }).sort("timestamp", -1))
        
        if not logs:
            return "No audit log entries found"
        
        # Create CSV header
        csv_lines = [
            "Timestamp,Event Type,IP Address,Device,Browser,Location,Success,Flagged,Details"
        ]
        
        # Add data rows
        for log in logs:
            timestamp = log.get("timestamp", "").isoformat() if log.get("timestamp") else ""
            event_type = log.get("event_type", "")
            ip_address = log.get("ip_address", "")
            device = log.get("device", "")
            browser = log.get("browser", "")
            location = log.get("location", "")
            success = "Yes" if log.get("success") else "No"
            flagged = "Yes" if log.get("flagged") else "No"
            details = str(log.get("details", {})).replace(",", ";")
            
            csv_lines.append(
                f'"{timestamp}","{event_type}","{ip_address}","{device}","{browser}",'
                f'"{location}","{success}","{flagged}","{details}"'
            )
        
        return "\n".join(csv_lines)


# Create singleton instance
audit_log_service = AuditLogService()
