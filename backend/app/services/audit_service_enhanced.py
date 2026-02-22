from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models.audit_log import AuditLog
from app.context import get_tenant_id
from mongoengine import Q


class AuditServiceEnhanced:
    """Enhanced audit logging service for compliance"""

    @staticmethod
    def log_action(
        event_type: str,
        resource: str,
        user_id: Optional[str] = None,
        ip_address: str = "0.0.0.0",
        status_code: int = 200,
        request_body: Optional[Dict[str, Any]] = None,
        response_body: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> AuditLog:
        """Log an action to audit trail"""
        tenant_id = get_tenant_id()
        
        # Redact sensitive data
        request_body = AuditServiceEnhanced._redact_sensitive_data(request_body)
        response_body = AuditServiceEnhanced._redact_sensitive_data(response_body)
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            event_type=event_type,
            resource=resource,
            user_id=user_id,
            ip_address=ip_address,
            status_code=status_code,
            request_body=request_body,
            response_body=response_body,
            user_agent=user_agent,
            error_message=error_message,
            duration_ms=duration_ms,
            tags=tags or [],
        )
        audit_log.save()
        return audit_log

    @staticmethod
    def log_data_access(
        resource_type: str,
        resource_id: str,
        user_id: str,
        ip_address: str,
        action: str = "read",
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log data access for compliance"""
        return AuditServiceEnhanced.log_action(
            event_type="DATA_ACCESS",
            resource=f"{resource_type}/{resource_id}",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            tags=["data_access", resource_type, action],
        )

    @staticmethod
    def log_data_modification(
        resource_type: str,
        resource_id: str,
        user_id: str,
        ip_address: str,
        action: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log data modification for compliance"""
        return AuditServiceEnhanced.log_action(
            event_type="DATA_MODIFICATION",
            resource=f"{resource_type}/{resource_id}",
            user_id=user_id,
            ip_address=ip_address,
            request_body={"action": action, "old_value": old_value},
            response_body={"new_value": new_value},
            user_agent=user_agent,
            tags=["data_modification", resource_type, action],
        )

    @staticmethod
    def log_sensitive_access(
        resource_type: str,
        resource_id: str,
        user_id: str,
        ip_address: str,
        reason: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log access to sensitive data"""
        return AuditServiceEnhanced.log_action(
            event_type="SENSITIVE_DATA_ACCESS",
            resource=f"{resource_type}/{resource_id}",
            user_id=user_id,
            ip_address=ip_address,
            request_body={"reason": reason},
            user_agent=user_agent,
            tags=["sensitive_access", resource_type],
        )

    @staticmethod
    def get_audit_logs(
        event_type: Optional[str] = None,
        resource: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[AuditLog], int]:
        """Get audit logs with filtering"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id)
        
        if event_type:
            query &= Q(event_type=event_type)
        
        if resource:
            query &= Q(resource__icontains=resource)
        
        if user_id:
            query &= Q(user_id=user_id)
        
        if start_date:
            query &= Q(created_at__gte=start_date)
        
        if end_date:
            query &= Q(created_at__lte=end_date)
        
        total = AuditLog.objects(query).count()
        logs = AuditLog.objects(query).order_by('-created_at').skip(skip).limit(limit)
        
        return list(logs), total

    @staticmethod
    def get_user_activity(
        user_id: str,
        days: int = 30,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[AuditLog], int]:
        """Get user activity for specified period"""
        tenant_id = get_tenant_id()
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = Q(tenant_id=tenant_id, user_id=user_id, created_at__gte=start_date)
        
        total = AuditLog.objects(query).count()
        logs = AuditLog.objects(query).order_by('-created_at').skip(skip).limit(limit)
        
        return list(logs), total

    @staticmethod
    def get_sensitive_access_logs(
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[AuditLog], int]:
        """Get sensitive data access logs"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id, event_type="SENSITIVE_DATA_ACCESS")
        
        total = AuditLog.objects(query).count()
        logs = AuditLog.objects(query).order_by('-created_at').skip(skip).limit(limit)
        
        return list(logs), total

    @staticmethod
    def get_failed_access_attempts(
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[AuditLog], int]:
        """Get failed access attempts"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id, status_code__in=[401, 403, 404])
        
        total = AuditLog.objects(query).count()
        logs = AuditLog.objects(query).order_by('-created_at').skip(skip).limit(limit)
        
        return list(logs), total

    @staticmethod
    def get_audit_summary(days: int = 30) -> Dict[str, Any]:
        """Get audit summary for specified period"""
        tenant_id = get_tenant_id()
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = Q(tenant_id=tenant_id, created_at__gte=start_date)
        logs = AuditLog.objects(query)
        
        total_events = logs.count()
        unique_users = len(set(log.user_id for log in logs if log.user_id))
        unique_ips = len(set(log.ip_address for log in logs))
        
        event_types = {}
        for log in logs:
            event_types[log.event_type] = event_types.get(log.event_type, 0) + 1
        
        failed_attempts = AuditLog.objects(query, status_code__in=[401, 403, 404]).count()
        
        return {
            "period_days": days,
            "total_events": total_events,
            "unique_users": unique_users,
            "unique_ips": unique_ips,
            "event_types": event_types,
            "failed_attempts": failed_attempts,
            "start_date": start_date,
            "end_date": datetime.utcnow(),
        }

    @staticmethod
    def _redact_sensitive_data(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Redact sensitive fields from audit logs"""
        if not data:
            return None
        
        sensitive_fields = {
            'password', 'token', 'secret', 'api_key', 'credit_card',
            'ssn', 'phone', 'email', 'address', 'authorization'
        }
        
        redacted = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = AuditServiceEnhanced._redact_sensitive_data(value)
            else:
                redacted[key] = value
        
        return redacted

    @staticmethod
    def export_audit_logs(
        start_date: datetime,
        end_date: datetime,
        format: str = "json",
    ) -> List[Dict[str, Any]]:
        """Export audit logs for compliance"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id, created_at__gte=start_date, created_at__lte=end_date)
        
        logs = AuditLog.objects(query).order_by('-created_at')
        
        result = []
        for log in logs:
            result.append({
                "id": str(log.id),
                "event_type": log.event_type,
                "resource": log.resource,
                "user_id": log.user_id,
                "ip_address": log.ip_address,
                "status_code": log.status_code,
                "user_agent": log.user_agent,
                "error_message": log.error_message,
                "duration_ms": log.duration_ms,
                "tags": log.tags,
                "created_at": log.created_at.isoformat(),
            })
        
        return result
