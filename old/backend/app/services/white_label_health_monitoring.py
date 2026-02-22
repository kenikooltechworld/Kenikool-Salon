"""
White Label Health Monitoring Service

This service monitors the health of white label configurations including:
- SSL certificate expiration
- DNS configuration validity
- Custom domain accessibility
- Page load times
- Overall uptime tracking
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx

from app.database import Database
from app.services.ssl_manager_service import SSLManagerService
from app.services.dns_verifier_service import DNSVerifierService

logger = logging.getLogger(__name__)


class HealthStatus:
    """Represents health status of a white label configuration"""
    
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class WhiteLabelHealthMonitoring:
    """Service for monitoring white label configuration health"""

    # Health check thresholds
    SSL_EXPIRY_WARNING_DAYS = 7
    SSL_EXPIRY_CRITICAL_DAYS = 1
    DNS_CHECK_TIMEOUT = 10  # seconds
    DOMAIN_ACCESSIBILITY_TIMEOUT = 10  # seconds
    PAGE_LOAD_WARNING_MS = 3000  # milliseconds
    PAGE_LOAD_CRITICAL_MS = 5000  # milliseconds

    def __init__(self):
        """Initialize health monitoring service"""
        self._db = None  # Lazy-loaded database
        self.ssl_manager = SSLManagerService()
        self.dns_verifier = DNSVerifierService()

    @property
    def db(self):
        """Lazy-load database connection"""
        if self._db is None:
            self._db = Database.get_db()
        return self._db

    async def check_all_configurations(self) -> Dict:
        """
        Check health of all white label configurations.

        Returns:
            Dict with health check statistics
        """
        stats = {
            "total_checked": 0,
            "healthy": 0,
            "warning": 0,
            "critical": 0,
            "errors": [],
            "checked_at": datetime.utcnow().isoformat(),
        }

        try:
            # Get all active white label configurations
            configs = list(self.db.white_label_configs.find({"is_active": True}))
            stats["total_checked"] = len(configs)

            logger.info(f"Health Monitoring: Checking {len(configs)} configurations")

            for config in configs:
                try:
                    health = await self.check_configuration_health(config)
                    
                    # Update statistics
                    if health["status"] == HealthStatus.HEALTHY:
                        stats["healthy"] += 1
                    elif health["status"] == HealthStatus.WARNING:
                        stats["warning"] += 1
                    elif health["status"] == HealthStatus.CRITICAL:
                        stats["critical"] += 1

                    # Store health check result
                    await self._store_health_check(config["tenant_id"], health)

                except Exception as e:
                    error_msg = f"Health check error for tenant {config.get('tenant_id')}: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

            logger.info(f"Health Monitoring completed: {stats}")
            return stats

        except Exception as e:
            error_msg = f"Health Monitoring failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            stats["errors"].append(error_msg)
            return stats

    async def check_configuration_health(self, config: Dict) -> Dict:
        """
        Check health of a single white label configuration.

        Args:
            config: White label configuration document

        Returns:
            Dict with health status and details
        """
        tenant_id = config.get("tenant_id")
        domain = config.get("domain", {}).get("custom_domain")

        health = {
            "tenant_id": tenant_id,
            "domain": domain,
            "status": HealthStatus.HEALTHY,
            "checks": {},
            "issues": [],
            "checked_at": datetime.utcnow().isoformat(),
        }

        try:
            # Check SSL certificate
            ssl_check = await self._check_ssl_certificate(tenant_id, domain)
            health["checks"]["ssl"] = ssl_check
            if ssl_check["status"] != HealthStatus.HEALTHY:
                health["issues"].extend(ssl_check.get("issues", []))

            # Check DNS configuration
            dns_check = await self._check_dns_configuration(domain)
            health["checks"]["dns"] = dns_check
            if dns_check["status"] != HealthStatus.HEALTHY:
                health["issues"].extend(dns_check.get("issues", []))

            # Check domain accessibility
            accessibility_check = await self._check_domain_accessibility(domain)
            health["checks"]["accessibility"] = accessibility_check
            if accessibility_check["status"] != HealthStatus.HEALTHY:
                health["issues"].extend(accessibility_check.get("issues", []))

            # Determine overall status
            check_statuses = [
                health["checks"]["ssl"]["status"],
                health["checks"]["dns"]["status"],
                health["checks"]["accessibility"]["status"],
            ]

            if HealthStatus.CRITICAL in check_statuses:
                health["status"] = HealthStatus.CRITICAL
            elif HealthStatus.WARNING in check_statuses:
                health["status"] = HealthStatus.WARNING
            else:
                health["status"] = HealthStatus.HEALTHY

        except Exception as e:
            logger.error(f"Error checking configuration health: {str(e)}")
            health["status"] = HealthStatus.UNKNOWN
            health["issues"].append(f"Health check error: {str(e)}")

        return health

    async def _check_ssl_certificate(self, tenant_id: str, domain: str) -> Dict:
        """
        Check SSL certificate status.

        Args:
            tenant_id: Tenant ID
            domain: Domain to check

        Returns:
            Dict with SSL check status
        """
        check = {
            "status": HealthStatus.HEALTHY,
            "issues": [],
            "details": {},
        }

        try:
            if not domain:
                check["status"] = HealthStatus.WARNING
                check["issues"].append("No custom domain configured")
                return check

            # Get certificate from database
            cert = self.db.ssl_certificates.find_one({
                "domain": domain,
                "tenant_id": tenant_id,
            })

            if not cert:
                check["status"] = HealthStatus.WARNING
                check["issues"].append(f"No SSL certificate found for {domain}")
                check["details"]["certificate_found"] = False
                return check

            check["details"]["certificate_found"] = True
            check["details"]["issued_at"] = cert.get("issued_at").isoformat() if cert.get("issued_at") else None
            check["details"]["expires_at"] = cert.get("expires_at").isoformat() if cert.get("expires_at") else None

            # Check certificate status
            if cert.get("status") != "active":
                check["status"] = HealthStatus.CRITICAL
                check["issues"].append(f"SSL certificate status is {cert.get('status')}")
                return check

            # Check expiration
            expires_at = cert.get("expires_at")
            if not expires_at:
                check["status"] = HealthStatus.WARNING
                check["issues"].append("Certificate expiration date not found")
                return check

            days_until_expiry = (expires_at - datetime.utcnow()).days

            if days_until_expiry <= self.SSL_EXPIRY_CRITICAL_DAYS:
                check["status"] = HealthStatus.CRITICAL
                check["issues"].append(f"SSL certificate expires in {days_until_expiry} day(s)")
            elif days_until_expiry <= self.SSL_EXPIRY_WARNING_DAYS:
                check["status"] = HealthStatus.WARNING
                check["issues"].append(f"SSL certificate expires in {days_until_expiry} day(s)")

            check["details"]["days_until_expiry"] = days_until_expiry

        except Exception as e:
            logger.error(f"Error checking SSL certificate: {str(e)}")
            check["status"] = HealthStatus.UNKNOWN
            check["issues"].append(f"SSL check error: {str(e)}")

        return check

    async def _check_dns_configuration(self, domain: str) -> Dict:
        """
        Check DNS configuration validity.

        Args:
            domain: Domain to check

        Returns:
            Dict with DNS check status
        """
        check = {
            "status": HealthStatus.HEALTHY,
            "issues": [],
            "details": {},
        }

        try:
            if not domain:
                check["status"] = HealthStatus.WARNING
                check["issues"].append("No custom domain configured")
                return check

            # Verify DNS configuration
            result = await self.dns_verifier.verify_domain("", domain)

            check["details"]["verified"] = result.verified
            check["details"]["records_found"] = len(result.records_found)

            if not result.verified:
                check["status"] = HealthStatus.WARNING
                check["issues"].extend(result.issues)
            else:
                check["details"]["records"] = [r.to_dict() for r in result.records_found]

        except Exception as e:
            logger.error(f"Error checking DNS configuration: {str(e)}")
            check["status"] = HealthStatus.WARNING
            check["issues"].append(f"DNS check error: {str(e)}")

        return check

    async def _check_domain_accessibility(self, domain: str) -> Dict:
        """
        Check if custom domain is accessible.

        Args:
            domain: Domain to check

        Returns:
            Dict with accessibility check status
        """
        check = {
            "status": HealthStatus.HEALTHY,
            "issues": [],
            "details": {},
        }

        try:
            if not domain:
                check["status"] = HealthStatus.WARNING
                check["issues"].append("No custom domain configured")
                return check

            # Test domain accessibility
            url = f"https://{domain}"
            
            try:
                async with httpx.AsyncClient(timeout=self.DOMAIN_ACCESSIBILITY_TIMEOUT) as client:
                    response = await client.get(url, follow_redirects=True)
                    
                    check["details"]["status_code"] = response.status_code
                    check["details"]["response_time_ms"] = response.elapsed.total_seconds() * 1000

                    if response.status_code >= 500:
                        check["status"] = HealthStatus.CRITICAL
                        check["issues"].append(f"Domain returned HTTP {response.status_code}")
                    elif response.status_code >= 400:
                        check["status"] = HealthStatus.WARNING
                        check["issues"].append(f"Domain returned HTTP {response.status_code}")

            except httpx.ConnectError:
                check["status"] = HealthStatus.CRITICAL
                check["issues"].append(f"Cannot connect to {domain}")
            except httpx.TimeoutException:
                check["status"] = HealthStatus.WARNING
                check["issues"].append(f"Domain request timed out")
            except Exception as e:
                check["status"] = HealthStatus.WARNING
                check["issues"].append(f"Domain accessibility check failed: {str(e)}")

        except Exception as e:
            logger.error(f"Error checking domain accessibility: {str(e)}")
            check["status"] = HealthStatus.UNKNOWN
            check["issues"].append(f"Accessibility check error: {str(e)}")

        return check

    async def _store_health_check(self, tenant_id: str, health: Dict) -> bool:
        """
        Store health check result in database.

        Args:
            tenant_id: Tenant ID
            health: Health check result

        Returns:
            Success status
        """
        try:
            self.db.white_label_health_checks.insert_one({
                "tenant_id": tenant_id,
                "domain": health.get("domain"),
                "status": health.get("status"),
                "checks": health.get("checks"),
                "issues": health.get("issues"),
                "checked_at": datetime.utcnow(),
            })

            # Keep only last 100 health checks per tenant
            checks = list(self.db.white_label_health_checks.find(
                {"tenant_id": tenant_id}
            ).sort("checked_at", -1).skip(100))

            if checks:
                check_ids = [c["_id"] for c in checks]
                self.db.white_label_health_checks.delete_many({"_id": {"$in": check_ids}})

            return True

        except Exception as e:
            logger.error(f"Error storing health check: {str(e)}")
            return False

    async def get_health_status(self, tenant_id: str) -> Optional[Dict]:
        """
        Get latest health status for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            Latest health check or None
        """
        try:
            health = self.db.white_label_health_checks.find_one(
                {"tenant_id": tenant_id},
                sort=[("checked_at", -1)]
            )
            return health
        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}")
            return None

    async def get_health_history(
        self,
        tenant_id: str,
        limit: int = 30,
        days: int = 7
    ) -> List[Dict]:
        """
        Get health check history for a tenant.

        Args:
            tenant_id: Tenant ID
            limit: Maximum number of records to return
            days: Number of days to look back

        Returns:
            List of health check records
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            history = list(self.db.white_label_health_checks.find({
                "tenant_id": tenant_id,
                "checked_at": {"$gte": start_date}
            }).sort("checked_at", -1).limit(limit))

            return history

        except Exception as e:
            logger.error(f"Error getting health history: {str(e)}")
            return []

    async def get_uptime_metrics(
        self,
        tenant_id: str,
        days: int = 30
    ) -> Dict:
        """
        Calculate uptime metrics for a tenant.

        Args:
            tenant_id: Tenant ID
            days: Number of days to analyze

        Returns:
            Dict with uptime metrics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            checks = list(self.db.white_label_health_checks.find({
                "tenant_id": tenant_id,
                "checked_at": {"$gte": start_date}
            }).sort("checked_at", 1))

            if not checks:
                return {
                    "uptime_percentage": 0,
                    "total_checks": 0,
                    "healthy_checks": 0,
                    "warning_checks": 0,
                    "critical_checks": 0,
                    "period_days": days,
                }

            total = len(checks)
            healthy = sum(1 for c in checks if c.get("status") == HealthStatus.HEALTHY)
            warning = sum(1 for c in checks if c.get("status") == HealthStatus.WARNING)
            critical = sum(1 for c in checks if c.get("status") == HealthStatus.CRITICAL)

            uptime_percentage = (healthy / total * 100) if total > 0 else 0

            return {
                "uptime_percentage": round(uptime_percentage, 2),
                "total_checks": total,
                "healthy_checks": healthy,
                "warning_checks": warning,
                "critical_checks": critical,
                "period_days": days,
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error calculating uptime metrics: {str(e)}")
            return {
                "uptime_percentage": 0,
                "total_checks": 0,
                "healthy_checks": 0,
                "warning_checks": 0,
                "critical_checks": 0,
                "period_days": days,
                "error": str(e),
            }

    async def get_all_tenants_health_summary(self) -> Dict:
        """
        Get health summary for all tenants.

        Returns:
            Dict with health summary for all tenants
        """
        try:
            # Get latest health check for each tenant
            pipeline = [
                {"$sort": {"checked_at": -1}},
                {"$group": {
                    "_id": "$tenant_id",
                    "status": {"$first": "$status"},
                    "domain": {"$first": "$domain"},
                    "issues": {"$first": "$issues"},
                    "checked_at": {"$first": "$checked_at"},
                }},
            ]

            results = list(self.db.white_label_health_checks.aggregate(pipeline))

            # Count by status
            status_counts = {
                HealthStatus.HEALTHY: 0,
                HealthStatus.WARNING: 0,
                HealthStatus.CRITICAL: 0,
                HealthStatus.UNKNOWN: 0,
            }

            for result in results:
                status = result.get("status", HealthStatus.UNKNOWN)
                status_counts[status] = status_counts.get(status, 0) + 1

            return {
                "total_tenants": len(results),
                "status_summary": status_counts,
                "tenants": [
                    {
                        "tenant_id": r["_id"],
                        "status": r.get("status"),
                        "domain": r.get("domain"),
                        "issues_count": len(r.get("issues", [])),
                        "checked_at": r.get("checked_at").isoformat() if r.get("checked_at") else None,
                    }
                    for r in results
                ],
            }

        except Exception as e:
            logger.error(f"Error getting all tenants health summary: {str(e)}")
            return {
                "total_tenants": 0,
                "status_summary": {},
                "tenants": [],
                "error": str(e),
            }
