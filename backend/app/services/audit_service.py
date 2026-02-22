"""Audit service for logging and compliance."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.models.audit_log import AuditLog
from app.context import get_tenant_id

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging and compliance reporting."""

    async def log_event(
        self,
        event_type: str,
        resource: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        ip_address: str = "unknown",
        status_code: int = 200,
        request_body: Optional[Dict[str, Any]] = None,
        response_body: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[AuditLog]:
        """Log an audit event."""
        try:
            if not tenant_id:
                tenant_id = get_tenant_id()

            if not tenant_id:
                logger.warning("Cannot log audit event without tenant_id")
                return None

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
            logger.debug(f"Audit event logged: {event_type} {resource}")
            return audit_log

        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return None

    def get_audit_logs(
        self,
        tenant_id: str,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        resource: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[AuditLog]:
        """Get audit logs with filtering."""
        try:
            query = AuditLog.objects(tenant_id=tenant_id)

            if user_id:
                query = query(user_id=user_id)

            if event_type:
                query = query(event_type=event_type)

            if resource:
                query = query(resource__contains=resource)

            if start_date:
                query = query(created_at__gte=start_date)

            if end_date:
                query = query(created_at__lte=end_date)

            return query.order_by("-created_at").skip(skip).limit(limit)

        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []

    def get_audit_log_by_id(self, tenant_id: str, log_id: str) -> Optional[AuditLog]:
        """Get a specific audit log."""
        try:
            return AuditLog.objects(tenant_id=tenant_id, id=log_id).first()
        except Exception as e:
            logger.error(f"Error retrieving audit log: {e}")
            return None

    def get_user_activity(
        self,
        tenant_id: str,
        user_id: str,
        days: int = 30,
    ) -> List[AuditLog]:
        """Get user activity for a period."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            return self.get_audit_logs(
                tenant_id=tenant_id,
                user_id=user_id,
                start_date=start_date,
                limit=1000,
            )
        except Exception as e:
            logger.error(f"Error retrieving user activity: {e}")
            return []

    def get_failed_logins(
        self,
        tenant_id: str,
        days: int = 7,
    ) -> List[AuditLog]:
        """Get failed login attempts."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            return self.get_audit_logs(
                tenant_id=tenant_id,
                event_type="POST",
                resource="/auth/login",
                start_date=start_date,
                limit=1000,
            )
        except Exception as e:
            logger.error(f"Error retrieving failed logins: {e}")
            return []

    def get_suspicious_activity(
        self,
        tenant_id: str,
        days: int = 7,
    ) -> List[AuditLog]:
        """Get suspicious activity (failed logins, errors, etc.)."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = AuditLog.objects(
                tenant_id=tenant_id,
                created_at__gte=start_date,
            )

            # Filter for suspicious patterns
            suspicious = []
            for log in query.order_by("-created_at"):
                # Failed login attempts
                if log.event_type == "POST" and "/auth/login" in log.resource:
                    if log.status_code in [401, 403]:
                        suspicious.append(log)

                # Multiple failed attempts from same IP
                if log.status_code >= 400:
                    suspicious.append(log)

            return suspicious[:1000]

        except Exception as e:
            logger.error(f"Error retrieving suspicious activity: {e}")
            return []

    def generate_compliance_report(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Generate compliance report."""
        try:
            logs = self.get_audit_logs(
                tenant_id=tenant_id,
                start_date=start_date,
                end_date=end_date,
                limit=10000,
            )

            report = {
                "tenant_id": tenant_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "total_events": len(logs),
                "events_by_type": {},
                "events_by_resource": {},
                "failed_operations": 0,
                "unique_users": set(),
                "unique_ips": set(),
            }

            for log in logs:
                # Count by event type
                event_type = log.event_type
                report["events_by_type"][event_type] = (
                    report["events_by_type"].get(event_type, 0) + 1
                )

                # Count by resource
                resource = log.resource
                report["events_by_resource"][resource] = (
                    report["events_by_resource"].get(resource, 0) + 1
                )

                # Count failures
                if log.status_code >= 400:
                    report["failed_operations"] += 1

                # Track unique users and IPs
                if log.user_id:
                    report["unique_users"].add(log.user_id)
                report["unique_ips"].add(log.ip_address)

            # Convert sets to counts
            report["unique_users"] = len(report["unique_users"])
            report["unique_ips"] = len(report["unique_ips"])

            return report

        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {}

    def cleanup_old_logs(self, tenant_id: str, days: int = 90) -> int:
        """Delete audit logs older than specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = AuditLog.objects(
                tenant_id=tenant_id,
                created_at__lt=cutoff_date,
            ).delete()

            logger.info(f"Deleted {result} old audit logs for tenant {tenant_id}")
            return result

        except Exception as e:
            logger.error(f"Error cleaning up audit logs: {e}")
            return 0
