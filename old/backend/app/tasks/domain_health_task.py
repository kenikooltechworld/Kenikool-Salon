"""
Background task for domain health monitoring.

This task runs daily to check the health of all verified custom domains,
including DNS configuration and SSL certificate validity. It updates domain
status and sends notifications for unhealthy domains.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from app.database import Database
from app.services.domain_service import DomainService
from app.services.ssl_service import SSLService
from app.services.notification_service import NotificationService
from app.services.domain_notification_service import DomainNotificationService

logger = logging.getLogger(__name__)


class DomainHealthTask:
    """Task for monitoring domain health"""

    # Days of warning status before sending alert
    WARNING_DURATION_THRESHOLD_DAYS = 7

    def __init__(self):
        self.domain_service = DomainService()
        self.ssl_service = SSLService()
        self.notification_service = NotificationService()
        self.domain_notification_service = DomainNotificationService()

    async def run(self) -> Dict:
        """
        Check health of all verified domains.

        Returns:
            Dict with health check statistics
        """
        db = Database.get_db()
        stats = {
            "total_checked": 0,
            "healthy": 0,
            "warning": 0,
            "failed": 0,
            "alerts_sent": 0,
            "errors": []
        }

        try:
            # Find all verified domains
            domains = list(db.domains.find({"status": "verified"}))

            stats["total_checked"] = len(domains)
            logger.info(f"Domain Health Task: Checking {len(domains)} domains")

            for domain_doc in domains:
                domain = domain_doc["domain"]
                tenant_id = domain_doc["tenant_id"]

                try:
                    health_status = {
                        "a_record": False,
                        "txt_record": False,
                        "cname_record": False,
                        "ssl_valid": False
                    }

                    # Check DNS records
                    health_status["a_record"] = await DomainService._verify_a_record(
                        domain
                    )
                    health_status["txt_record"] = await DomainService._verify_txt_record(
                        domain,
                        domain_doc.get("verification_token", "")
                    )
                    health_status["cname_record"] = await self._verify_cname_record(
                        domain
                    )

                    # Check SSL certificate
                    health_status["ssl_valid"] = await self.ssl_service.check_certificate_valid(
                        domain
                    )

                    # Determine overall status
                    all_healthy = all(health_status.values())

                    if all_healthy:
                        stats["healthy"] += 1
                        logger.info(f"Domain {domain} is healthy")

                        # If was in warning, update back to verified
                        if domain_doc.get("status") == "warning":
                            db.domains.update_one(
                                {"_id": domain_doc["_id"]},
                                {"$set": {
                                    "status": "verified",
                                    "health_check_at": datetime.utcnow(),
                                    "health_issues": []
                                }}
                            )
                            logger.info(f"Domain {domain} recovered to verified status")

                    else:
                        # Domain has issues
                        health_issues = [
                            k for k, v in health_status.items() if not v
                        ]

                        stats["warning"] += 1
                        logger.warning(
                            f"Domain {domain} has health issues: {health_issues}"
                        )

                        # Update to warning status
                        db.domains.update_one(
                            {"_id": domain_doc["_id"]},
                            {"$set": {
                                "status": "warning",
                                "health_check_at": datetime.utcnow(),
                                "health_issues": health_issues
                            }}
                        )

                        # Check if warning duration exceeds threshold
                        if domain_doc.get("status") == "warning":
                            warning_start = domain_doc.get(
                                "health_check_at",
                                datetime.utcnow()
                            )
                            warning_duration = datetime.utcnow() - warning_start

                            if warning_duration.days >= self.WARNING_DURATION_THRESHOLD_DAYS:
                                stats["alerts_sent"] += 1

                                try:
                                    await self.domain_notification_service.send_domain_health_alert(
                                        tenant_id,
                                        domain,
                                        health_status
                                    )
                                    logger.info(
                                        f"Health alert sent for {domain}"
                                    )
                                except Exception as e:
                                    logger.error(
                                        f"Failed to send health alert: {e}"
                                    )

                except Exception as e:
                    stats["failed"] += 1
                    error_msg = f"Health check error for {domain}: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

            logger.info(f"Domain Health Task completed: {stats}")
            return stats

        except Exception as e:
            error_msg = f"Domain Health Task failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            stats["errors"].append(error_msg)
            return stats

    @staticmethod
    async def _verify_cname_record(domain: str) -> bool:
        """Verify CNAME record for www subdomain"""
        try:
            import dns.resolver

            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5

            answers = resolver.resolve(f"www.{domain}", 'CNAME')

            for rdata in answers:
                if str(rdata).rstrip('.') == domain:
                    return True
            return False
        except Exception as e:
            logger.warning(f"CNAME verification failed for {domain}: {e}")
            return False


async def check_domain_health() -> Dict:
    """
    Main entry point for domain health monitoring task.

    This function is called by the scheduler/cron job.
    """
    task = DomainHealthTask()
    return await task.run()


if __name__ == "__main__":
    import asyncio

    # For manual testing
    result = asyncio.run(check_domain_health())
    print(f"Domain Health Task Result: {result}")
