"""
Background task for automatic SSL certificate renewal.

This task runs daily to check for expiring SSL certificates and renew them
before they expire. It also sends notifications for certificates that are
about to expire.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict

from app.database import Database
from app.services.ssl_manager_service import SSLManagerService
from app.services.notification_service import NotificationService
from app.services.domain_notification_service import DomainNotificationService

logger = logging.getLogger(__name__)


class SSLRenewalTask:
    """Task for managing SSL certificate renewal"""

    # Days before expiry to start renewal attempts
    RENEWAL_THRESHOLD_DAYS = 30

    # Days before expiry to send urgent notification
    URGENT_NOTIFICATION_THRESHOLD_DAYS = 7

    def __init__(self):
        self.ssl_manager = SSLManagerService()
        self.notification_service = NotificationService()
        self.domain_notification_service = DomainNotificationService()

    async def run(self) -> Dict:
        """
        Check all domains and renew expiring SSL certificates.

        Returns:
            Dict with renewal statistics
        """
        db = Database.get_db()
        stats = {
            "total_checked": 0,
            "renewed": 0,
            "failed": 0,
            "urgent_notifications_sent": 0,
            "errors": []
        }

        try:
            # Find certificates expiring in RENEWAL_THRESHOLD_DAYS
            expiry_threshold = datetime.utcnow() + timedelta(
                days=self.RENEWAL_THRESHOLD_DAYS
            )

            certificates = list(db.ssl_certificates.find({
                "status": "active",
                "expires_at": {"$lte": expiry_threshold}
            }))

            stats["total_checked"] = len(certificates)
            logger.info(f"SSL Renewal Task: Checking {len(certificates)} certificates")

            for cert_doc in certificates:
                domain = cert_doc["domain"]
                tenant_id = cert_doc["tenant_id"]

                try:
                    # Calculate days remaining
                    days_remaining = (
                        cert_doc["expires_at"] - datetime.utcnow()
                    ).days

                    logger.info(
                        f"Checking SSL for {domain}: {days_remaining} days remaining"
                    )

                    # Attempt renewal
                    success, error = await self.ssl_manager.renew_certificate(
                        tenant_id=tenant_id,
                        domain=domain
                    )

                    if success:
                        stats["renewed"] += 1
                        logger.info(f"SSL renewed for {domain}")

                        # Send success notification
                        try:
                            await self.domain_notification_service.send_ssl_renewed(
                                tenant_id,
                                domain,
                                cert_doc["expires_at"]
                            )
                        except Exception as e:
                            logger.error(f"Failed to send renewal notification: {e}")

                        # Send success notification via notification service
                        try:
                            await self.notification_service.send_ssl_renewed(
                                tenant_id,
                                domain,
                                cert_doc["expires_at"]
                            )
                        except Exception as e:
                            logger.error(f"Failed to send renewal notification: {e}")

                    else:
                        stats["failed"] += 1
                        logger.warning(f"SSL renewal failed for {domain}: {error}")

                        # Check if urgent (7 days or less)
                        if days_remaining <= self.URGENT_NOTIFICATION_THRESHOLD_DAYS:
                            stats["urgent_notifications_sent"] += 1

                            try:
                                await self.domain_notification_service.send_urgent_ssl_expiry(
                                    tenant_id,
                                    domain,
                                    days_remaining
                                )
                                logger.info(
                                    f"Urgent SSL expiry notification sent for {domain}"
                                )
                            except Exception as e:
                                logger.error(
                                    f"Failed to send urgent notification: {e}"
                                )

                except Exception as e:
                    stats["failed"] += 1
                    error_msg = f"SSL renewal error for {domain}: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

            logger.info(f"SSL Renewal Task completed: {stats}")
            return stats

        except Exception as e:
            error_msg = f"SSL Renewal Task failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            stats["errors"].append(error_msg)
            return stats


async def check_and_renew_certificates() -> Dict:
    """
    Main entry point for SSL renewal task.

    This function is called by the scheduler/cron job.
    """
    task = SSLRenewalTask()
    return await task.run()


if __name__ == "__main__":
    import asyncio

    # For manual testing
    result = asyncio.run(check_and_renew_certificates())
    print(f"SSL Renewal Task Result: {result}")
