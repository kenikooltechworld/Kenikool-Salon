"""
White Label Alerting Service

This service handles sending alerts for white label health issues:
- SSL certificate expiration alerts
- DNS configuration break alerts
- Domain accessibility alerts
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from app.database import Database
from app.services.notification_service import NotificationService
from app.services.domain_notification_service import DomainNotificationService

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types"""
    SSL_EXPIRING = "ssl_expiring"
    SSL_EXPIRED = "ssl_expired"
    DNS_BROKEN = "dns_broken"
    DOMAIN_INACCESSIBLE = "domain_inaccessible"
    DOMAIN_SLOW = "domain_slow"
    HEALTH_DEGRADED = "health_degraded"


class WhiteLabelAlertingService:
    """Service for managing white label alerts"""

    # Alert thresholds
    SSL_EXPIRY_ALERT_DAYS = 7
    DNS_CHECK_FAILURE_THRESHOLD = 2  # consecutive failures
    DOMAIN_ACCESSIBILITY_FAILURE_THRESHOLD = 3  # consecutive failures
    PAGE_LOAD_SLOW_THRESHOLD_MS = 3000

    def __init__(self):
        """Initialize alerting service"""
        self._db = None  # Lazy-loaded database
        self.notification_service = NotificationService()
        self.domain_notification_service = DomainNotificationService()

    @property
    def db(self):
        """Lazy-load database connection"""
        if self._db is None:
            self._db = Database.get_db()
        return self._db

    async def process_health_check(self, health: Dict) -> List[Dict]:
        """
        Process health check result and generate alerts if needed.

        Args:
            health: Health check result from WhiteLabelHealthMonitoring

        Returns:
            List of alerts generated
        """
        alerts = []
        tenant_id = health.get("tenant_id")
        domain = health.get("domain")

        try:
            # Check SSL certificate
            ssl_check = health.get("checks", {}).get("ssl", {})
            ssl_alerts = await self._process_ssl_check(tenant_id, domain, ssl_check)
            alerts.extend(ssl_alerts)

            # Check DNS configuration
            dns_check = health.get("checks", {}).get("dns", {})
            dns_alerts = await self._process_dns_check(tenant_id, domain, dns_check)
            alerts.extend(dns_alerts)

            # Check domain accessibility
            accessibility_check = health.get("checks", {}).get("accessibility", {})
            accessibility_alerts = await self._process_accessibility_check(
                tenant_id, domain, accessibility_check
            )
            alerts.extend(accessibility_alerts)

            # Store alerts in database
            for alert in alerts:
                await self._store_alert(alert)

        except Exception as e:
            logger.error(f"Error processing health check: {str(e)}")

        return alerts

    async def _process_ssl_check(
        self,
        tenant_id: str,
        domain: str,
        ssl_check: Dict
    ) -> List[Dict]:
        """
        Process SSL check and generate alerts.

        Args:
            tenant_id: Tenant ID
            domain: Domain
            ssl_check: SSL check result

        Returns:
            List of alerts
        """
        alerts = []

        try:
            status = ssl_check.get("status")
            issues = ssl_check.get("issues", [])
            details = ssl_check.get("details", {})

            # Check for SSL expiration alerts
            days_until_expiry = details.get("days_until_expiry")

            if days_until_expiry is not None:
                if days_until_expiry <= 0:
                    # SSL expired
                    alert = await self._create_alert(
                        tenant_id=tenant_id,
                        domain=domain,
                        alert_type=AlertType.SSL_EXPIRED,
                        severity=AlertSeverity.CRITICAL,
                        message=f"SSL certificate for {domain} has expired",
                        details={
                            "days_until_expiry": days_until_expiry,
                            "expires_at": details.get("expires_at"),
                        }
                    )
                    alerts.append(alert)

                    # Send notification
                    await self._send_ssl_expired_notification(tenant_id, domain)

                elif days_until_expiry <= self.SSL_EXPIRY_ALERT_DAYS:
                    # SSL expiring soon
                    alert = await self._create_alert(
                        tenant_id=tenant_id,
                        domain=domain,
                        alert_type=AlertType.SSL_EXPIRING,
                        severity=AlertSeverity.WARNING,
                        message=f"SSL certificate for {domain} expires in {days_until_expiry} day(s)",
                        details={
                            "days_until_expiry": days_until_expiry,
                            "expires_at": details.get("expires_at"),
                        }
                    )
                    alerts.append(alert)

                    # Send notification
                    await self._send_ssl_expiring_notification(tenant_id, domain, days_until_expiry)

        except Exception as e:
            logger.error(f"Error processing SSL check: {str(e)}")

        return alerts

    async def _process_dns_check(
        self,
        tenant_id: str,
        domain: str,
        dns_check: Dict
    ) -> List[Dict]:
        """
        Process DNS check and generate alerts.

        Args:
            tenant_id: Tenant ID
            domain: Domain
            dns_check: DNS check result

        Returns:
            List of alerts
        """
        alerts = []

        try:
            status = dns_check.get("status")
            issues = dns_check.get("issues", [])

            if status != "healthy" and issues:
                # Check if this is a repeated failure
                consecutive_failures = await self._get_consecutive_failures(
                    tenant_id, domain, AlertType.DNS_BROKEN
                )

                if consecutive_failures >= self.DNS_CHECK_FAILURE_THRESHOLD:
                    alert = await self._create_alert(
                        tenant_id=tenant_id,
                        domain=domain,
                        alert_type=AlertType.DNS_BROKEN,
                        severity=AlertSeverity.CRITICAL,
                        message=f"DNS configuration for {domain} is broken: {'; '.join(issues)}",
                        details={
                            "issues": issues,
                            "consecutive_failures": consecutive_failures,
                        }
                    )
                    alerts.append(alert)

                    # Send notification
                    await self._send_dns_broken_notification(tenant_id, domain, issues)

        except Exception as e:
            logger.error(f"Error processing DNS check: {str(e)}")

        return alerts

    async def _process_accessibility_check(
        self,
        tenant_id: str,
        domain: str,
        accessibility_check: Dict
    ) -> List[Dict]:
        """
        Process domain accessibility check and generate alerts.

        Args:
            tenant_id: Tenant ID
            domain: Domain
            accessibility_check: Accessibility check result

        Returns:
            List of alerts
        """
        alerts = []

        try:
            status = accessibility_check.get("status")
            issues = accessibility_check.get("issues", [])
            details = accessibility_check.get("details", {})

            if status != "healthy":
                # Check if this is a repeated failure
                consecutive_failures = await self._get_consecutive_failures(
                    tenant_id, domain, AlertType.DOMAIN_INACCESSIBLE
                )

                if consecutive_failures >= self.DOMAIN_ACCESSIBILITY_FAILURE_THRESHOLD:
                    alert = await self._create_alert(
                        tenant_id=tenant_id,
                        domain=domain,
                        alert_type=AlertType.DOMAIN_INACCESSIBLE,
                        severity=AlertSeverity.CRITICAL,
                        message=f"Domain {domain} is not accessible: {'; '.join(issues)}",
                        details={
                            "issues": issues,
                            "status_code": details.get("status_code"),
                            "consecutive_failures": consecutive_failures,
                        }
                    )
                    alerts.append(alert)

                    # Send notification
                    await self._send_domain_inaccessible_notification(tenant_id, domain, issues)

            # Check for slow page loads
            response_time_ms = details.get("response_time_ms")
            if response_time_ms and response_time_ms > self.PAGE_LOAD_SLOW_THRESHOLD_MS:
                alert = await self._create_alert(
                    tenant_id=tenant_id,
                    domain=domain,
                    alert_type=AlertType.DOMAIN_SLOW,
                    severity=AlertSeverity.WARNING,
                    message=f"Domain {domain} is responding slowly ({response_time_ms:.0f}ms)",
                    details={
                        "response_time_ms": response_time_ms,
                    }
                )
                alerts.append(alert)

        except Exception as e:
            logger.error(f"Error processing accessibility check: {str(e)}")

        return alerts

    async def _create_alert(
        self,
        tenant_id: str,
        domain: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        details: Dict = None
    ) -> Dict:
        """
        Create an alert record.

        Args:
            tenant_id: Tenant ID
            domain: Domain
            alert_type: Type of alert
            severity: Severity level
            message: Alert message
            details: Additional details

        Returns:
            Alert document
        """
        alert = {
            "tenant_id": tenant_id,
            "domain": domain,
            "alert_type": alert_type.value,
            "severity": severity.value,
            "message": message,
            "details": details or {},
            "acknowledged": False,
            "created_at": datetime.utcnow(),
            "acknowledged_at": None,
            "acknowledged_by": None,
        }

        return alert

    async def _store_alert(self, alert: Dict) -> bool:
        """
        Store alert in database.

        Args:
            alert: Alert document

        Returns:
            Success status
        """
        try:
            self.db.white_label_alerts.insert_one(alert)
            return True
        except Exception as e:
            logger.error(f"Error storing alert: {str(e)}")
            return False

    async def _get_consecutive_failures(
        self,
        tenant_id: str,
        domain: str,
        alert_type: AlertType,
        lookback_hours: int = 24
    ) -> int:
        """
        Get number of consecutive failures for an alert type.

        Args:
            tenant_id: Tenant ID
            domain: Domain
            alert_type: Alert type
            lookback_hours: Hours to look back

        Returns:
            Number of consecutive failures
        """
        try:
            start_date = datetime.utcnow() - timedelta(hours=lookback_hours)

            alerts = list(self.db.white_label_alerts.find({
                "tenant_id": tenant_id,
                "domain": domain,
                "alert_type": alert_type.value,
                "created_at": {"$gte": start_date}
            }).sort("created_at", -1).limit(10))

            # Count consecutive failures (unacknowledged alerts)
            consecutive = 0
            for alert in alerts:
                if not alert.get("acknowledged"):
                    consecutive += 1
                else:
                    break

            return consecutive

        except Exception as e:
            logger.error(f"Error getting consecutive failures: {str(e)}")
            return 0

    async def _send_ssl_expired_notification(self, tenant_id: str, domain: str) -> None:
        """Send SSL expired notification."""
        try:
            await self.domain_notification_service.send_urgent_ssl_expiry(
                tenant_id, domain, 0
            )
        except Exception as e:
            logger.error(f"Error sending SSL expired notification: {str(e)}")

    async def _send_ssl_expiring_notification(
        self,
        tenant_id: str,
        domain: str,
        days_remaining: int
    ) -> None:
        """Send SSL expiring notification."""
        try:
            await self.domain_notification_service.send_urgent_ssl_expiry(
                tenant_id, domain, days_remaining
            )
        except Exception as e:
            logger.error(f"Error sending SSL expiring notification: {str(e)}")

    async def _send_dns_broken_notification(
        self,
        tenant_id: str,
        domain: str,
        issues: List[str]
    ) -> None:
        """Send DNS broken notification."""
        try:
            await self.domain_notification_service.send_domain_health_alert(
                tenant_id, domain, {
                    "dns_broken": True,
                    "issues": issues,
                }
            )
        except Exception as e:
            logger.error(f"Error sending DNS broken notification: {str(e)}")

    async def _send_domain_inaccessible_notification(
        self,
        tenant_id: str,
        domain: str,
        issues: List[str]
    ) -> None:
        """Send domain inaccessible notification."""
        try:
            await self.domain_notification_service.send_domain_health_alert(
                tenant_id, domain, {
                    "domain_inaccessible": True,
                    "issues": issues,
                }
            )
        except Exception as e:
            logger.error(f"Error sending domain inaccessible notification: {str(e)}")

    async def get_alerts(
        self,
        tenant_id: str,
        limit: int = 50,
        skip: int = 0,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None
    ) -> tuple[List[Dict], int]:
        """
        Get alerts for a tenant.

        Args:
            tenant_id: Tenant ID
            limit: Maximum number of alerts to return
            skip: Number of alerts to skip
            severity: Optional severity filter
            acknowledged: Optional acknowledged status filter

        Returns:
            Tuple of (alerts, total_count)
        """
        try:
            query = {"tenant_id": tenant_id}

            if severity:
                query["severity"] = severity

            if acknowledged is not None:
                query["acknowledged"] = acknowledged

            total = self.db.white_label_alerts.count_documents(query)

            alerts = list(self.db.white_label_alerts.find(query)
                         .sort("created_at", -1)
                         .skip(skip)
                         .limit(limit))

            return alerts, total

        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            return [], 0

    async def acknowledge_alert(self, alert_id: str, tenant_id: str, user_id: str) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert ID
            tenant_id: Tenant ID
            user_id: User ID

        Returns:
            Success status
        """
        try:
            from bson import ObjectId

            result = self.db.white_label_alerts.update_one(
                {"_id": ObjectId(alert_id), "tenant_id": tenant_id},
                {"$set": {
                    "acknowledged": True,
                    "acknowledged_at": datetime.utcnow(),
                    "acknowledged_by": user_id,
                }}
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error acknowledging alert: {str(e)}")
            return False

    async def get_alert_summary(self, tenant_id: str) -> Dict:
        """
        Get alert summary for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            Dict with alert summary
        """
        try:
            # Count alerts by severity
            pipeline = [
                {"$match": {"tenant_id": tenant_id}},
                {"$group": {
                    "_id": "$severity",
                    "count": {"$sum": 1}
                }},
            ]

            severity_counts = {}
            for result in self.db.white_label_alerts.aggregate(pipeline):
                severity_counts[result["_id"]] = result["count"]

            # Count unacknowledged alerts
            unacknowledged = self.db.white_label_alerts.count_documents({
                "tenant_id": tenant_id,
                "acknowledged": False
            })

            # Get latest alert
            latest_alert = self.db.white_label_alerts.find_one(
                {"tenant_id": tenant_id},
                sort=[("created_at", -1)]
            )

            return {
                "total_alerts": self.db.white_label_alerts.count_documents({"tenant_id": tenant_id}),
                "unacknowledged_alerts": unacknowledged,
                "severity_breakdown": severity_counts,
                "latest_alert": {
                    "created_at": latest_alert.get("created_at").isoformat() if latest_alert else None,
                    "message": latest_alert.get("message") if latest_alert else None,
                    "severity": latest_alert.get("severity") if latest_alert else None,
                } if latest_alert else None,
            }

        except Exception as e:
            logger.error(f"Error getting alert summary: {str(e)}")
            return {
                "total_alerts": 0,
                "unacknowledged_alerts": 0,
                "severity_breakdown": {},
                "latest_alert": None,
                "error": str(e),
            }
