"""
Domain notification service - Sends notifications for domain-related events.

This service handles all notifications related to custom domain management,
including verification status, SSL certificate expiry, and health alerts.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class DomainNotificationService:
    """Service for sending domain-related notifications"""

    def __init__(self):
        self.email_service = email_service

    async def send_domain_verified(
        self,
        tenant_id: str,
        domain: str
    ) -> bool:
        """Send notification when domain is successfully verified."""
        try:
            from app.database import Database
            db = Database.get_db()
            tenant = db.tenants.find_one({"_id": tenant_id})
            
            if not tenant or not tenant.get("email"):
                logger.warning(f"No email found for tenant {tenant_id}")
                return False
            
            recipient_email = tenant["email"]
            subject = f"Domain Verified: {domain}"
            
            html_content = f"""
            <h2>Domain Verified Successfully</h2>
            <p>Your custom domain <strong>{domain}</strong> has been verified and is now active.</p>
            <h3>What's Next?</h3>
            <ul>
                <li>Your domain is now live and ready to use</li>
                <li>SSL certificate has been automatically provisioned</li>
                <li>Your salon is accessible at https://{domain}</li>
            </ul>
            <p>If you have any questions, please contact our support team.</p>
            """

            text_content = f"""Domain Verified Successfully

Your custom domain {domain} has been verified and is now active.

Your domain is now live and ready to use. Your salon is accessible at https://{domain}

If you have any questions, please contact our support team."""

            result = await self.email_service.send_email(
                to=recipient_email,
                subject=subject,
                html=html_content,
                text=text_content
            )

            logger.info(f"Domain verified notification sent for {domain}")
            return result

        except Exception as e:
            logger.error(f"Failed to send domain verified notification: {e}")
            return False

    async def send_verification_failed(
        self,
        tenant_id: str,
        domain: str,
        errors: List[str]
    ) -> bool:
        """Send notification when domain verification fails."""
        try:
            from app.database import Database
            db = Database.get_db()
            tenant = db.tenants.find_one({"_id": tenant_id})
            
            if not tenant or not tenant.get("email"):
                logger.warning(f"No email found for tenant {tenant_id}")
                return False
            
            recipient_email = tenant["email"]
            subject = f"Domain Verification Failed: {domain}"
            
            errors_html = "".join([f"<li>{error}</li>" for error in errors])
            
            html_content = f"""
            <h2>Domain Verification Failed</h2>
            <p>We were unable to verify your custom domain <strong>{domain}</strong>.</p>
            <h3>Issues Found</h3>
            <ul>{errors_html}</ul>
            <h3>How to Fix</h3>
            <ol>
                <li>Log in to your salon dashboard</li>
                <li>Go to Settings → Custom Domains</li>
                <li>Click on your domain to view DNS configuration</li>
                <li>Update your DNS records according to the instructions</li>
                <li>Wait 5-10 minutes for DNS changes to propagate</li>
                <li>Click "Verify Domain" to try again</li>
            </ol>
            <p>If you continue to have issues, please contact our support team.</p>
            """

            text_content = f"""Domain Verification Failed

We were unable to verify your custom domain {domain}.

Issues Found:
{chr(10).join([f"- {error}" for error in errors])}

How to Fix:
1. Log in to your salon dashboard
2. Go to Settings → Custom Domains
3. Click on your domain to view DNS configuration
4. Update your DNS records according to the instructions
5. Wait 5-10 minutes for DNS changes to propagate
6. Click "Verify Domain" to try again

If you continue to have issues, please contact our support team."""

            result = await self.email_service.send_email(
                to=recipient_email,
                subject=subject,
                html=html_content,
                text=text_content
            )

            logger.info(f"Domain verification failed notification sent for {domain}")
            return result

        except Exception as e:
            logger.error(f"Failed to send verification failed notification: {e}")
            return False

    async def send_ssl_expiry_warning(
        self,
        tenant_id: str,
        domain: str,
        days_remaining: int
    ) -> bool:
        """Send notification when SSL certificate is expiring soon."""
        try:
            from app.database import Database
            db = Database.get_db()
            tenant = db.tenants.find_one({"_id": tenant_id})
            
            if not tenant or not tenant.get("email"):
                logger.warning(f"No email found for tenant {tenant_id}")
                return False
            
            recipient_email = tenant["email"]
            subject = f"SSL Certificate Expiring Soon: {domain}"
            
            urgency = "URGENT" if days_remaining <= 7 else "WARNING"
            
            html_content = f"""
            <h2 style="color: {'red' if days_remaining <= 7 else 'orange'};">{urgency}: SSL Certificate Expiring</h2>
            <p>The SSL certificate for <strong>{domain}</strong> will expire in <strong>{days_remaining} days</strong>.</p>
            <h3>What We're Doing</h3>
            <ul>
                <li>We automatically renew SSL certificates before they expire</li>
                <li>Renewal attempts are made 30 days before expiry</li>
                <li>If renewal fails, we'll send you urgent notifications</li>
            </ul>
            <p>If you have any questions, please contact our support team.</p>
            """

            text_content = f"""{urgency}: SSL Certificate Expiring

The SSL certificate for {domain} will expire in {days_remaining} days.

We automatically renew SSL certificates before they expire. If renewal fails, we'll send you urgent notifications.

If you have any questions, please contact our support team."""

            result = await self.email_service.send_email(
                to=recipient_email,
                subject=subject,
                html=html_content,
                text=text_content
            )

            logger.info(f"SSL expiry warning notification sent for {domain}")
            return result

        except Exception as e:
            logger.error(f"Failed to send SSL expiry warning notification: {e}")
            return False

    async def send_urgent_ssl_expiry(
        self,
        tenant_id: str,
        domain: str,
        days_remaining: int
    ) -> bool:
        """Send urgent notification when SSL certificate is expiring very soon."""
        try:
            from app.database import Database
            db = Database.get_db()
            tenant = db.tenants.find_one({"_id": tenant_id})
            
            if not tenant or not tenant.get("email"):
                logger.warning(f"No email found for tenant {tenant_id}")
                return False
            
            recipient_email = tenant["email"]
            subject = f"🚨 URGENT: SSL Certificate Expiring in {days_remaining} Days - {domain}"
            
            html_content = f"""
            <h2 style="color: red;">🚨 URGENT: SSL Certificate Expiring</h2>
            <p>The SSL certificate for <strong>{domain}</strong> will expire in <strong>{days_remaining} days</strong>.</p>
            <h3 style="color: red;">Immediate Action Required</h3>
            <p>Automatic renewal has failed. Your domain will become inaccessible if the certificate is not renewed.</p>
            <h3>What You Need to Do</h3>
            <ol>
                <li><strong>Log in immediately</strong> to your salon dashboard</li>
                <li>Go to Settings → Custom Domains</li>
                <li>Click on <strong>{domain}</strong></li>
                <li>Click <strong>"Renew Certificate"</strong> to manually trigger renewal</li>
            </ol>
            <p>Please contact our support team immediately if you need help!</p>
            """

            text_content = f"""🚨 URGENT: SSL Certificate Expiring

The SSL certificate for {domain} will expire in {days_remaining} days.

Immediate Action Required:
Automatic renewal has failed. Your domain will become inaccessible if the certificate is not renewed.

What You Need to Do:
1. Log in immediately to your salon dashboard
2. Go to Settings → Custom Domains
3. Click on {domain}
4. Click "Renew Certificate" to manually trigger renewal

Please contact our support team immediately if you need help!"""

            result = await self.email_service.send_email(
                to=recipient_email,
                subject=subject,
                html=html_content,
                text=text_content
            )

            logger.info(f"Urgent SSL expiry notification sent for {domain}")
            return result

        except Exception as e:
            logger.error(f"Failed to send urgent SSL expiry notification: {e}")
            return False

    async def send_domain_health_alert(
        self,
        tenant_id: str,
        domain: str,
        health_status: Dict[str, bool]
    ) -> bool:
        """Send notification when domain health issues are detected."""
        try:
            from app.database import Database
            db = Database.get_db()
            tenant = db.tenants.find_one({"_id": tenant_id})
            
            if not tenant or not tenant.get("email"):
                logger.warning(f"No email found for tenant {tenant_id}")
                return False
            
            recipient_email = tenant["email"]
            subject = f"Domain Health Alert: {domain}"
            
            # Build list of issues
            issues = []
            if not health_status.get("a_record"):
                issues.append("A record is not pointing to our servers")
            if not health_status.get("txt_record"):
                issues.append("TXT verification record is missing or incorrect")
            if not health_status.get("cname_record"):
                issues.append("CNAME record for www subdomain is missing")
            if not health_status.get("ssl_valid"):
                issues.append("SSL certificate is invalid or expired")
            
            issues_html = "".join([f"<li>{issue}</li>" for issue in issues])
            
            html_content = f"""
            <h2>Domain Health Alert</h2>
            <p>We've detected issues with your custom domain <strong>{domain}</strong>.</p>
            <h3>Issues Detected</h3>
            <ul>{issues_html}</ul>
            <h3>How to Fix</h3>
            <ol>
                <li>Log in to your salon dashboard</li>
                <li>Go to Settings → Custom Domains</li>
                <li>Click on your domain to view current DNS configuration</li>
                <li>Update any DNS records that show as invalid</li>
                <li>Wait 5-10 minutes for DNS changes to propagate</li>
                <li>Click "Check Health" to verify the fixes</li>
            </ol>
            <p>If you're unsure how to fix these issues, please contact our support team.</p>
            """

            text_content = f"""Domain Health Alert

We've detected issues with your custom domain {domain}.

Issues Detected:
{chr(10).join([f"- {issue}" for issue in issues])}

How to Fix:
1. Log in to your salon dashboard
2. Go to Settings → Custom Domains
3. Click on your domain to view current DNS configuration
4. Update any DNS records that show as invalid
5. Wait 5-10 minutes for DNS changes to propagate
6. Click "Check Health" to verify the fixes

If you're unsure how to fix these issues, please contact our support team."""

            result = await self.email_service.send_email(
                to=recipient_email,
                subject=subject,
                html=html_content,
                text=text_content
            )

            logger.info(f"Domain health alert notification sent for {domain}")
            return result

        except Exception as e:
            logger.error(f"Failed to send domain health alert notification: {e}")
            return False

    async def send_ssl_renewed(
        self,
        tenant_id: str,
        domain: str,
        new_expiry: datetime
    ) -> bool:
        """Send notification when SSL certificate is successfully renewed."""
        try:
            from app.database import Database
            db = Database.get_db()
            tenant = db.tenants.find_one({"_id": tenant_id})
            
            if not tenant or not tenant.get("email"):
                logger.warning(f"No email found for tenant {tenant_id}")
                return False
            
            recipient_email = tenant["email"]
            subject = f"SSL Certificate Renewed: {domain}"
            
            expiry_date = new_expiry.strftime("%B %d, %Y")
            
            html_content = f"""
            <h2>SSL Certificate Renewed Successfully</h2>
            <p>The SSL certificate for <strong>{domain}</strong> has been successfully renewed.</p>
            <h3>Certificate Details</h3>
            <ul>
                <li><strong>Domain:</strong> {domain}</li>
                <li><strong>New Expiry Date:</strong> {expiry_date}</li>
                <li><strong>Status:</strong> Active and Valid</li>
            </ul>
            <p>Your domain continues to be secure and accessible. We'll automatically renew the certificate again before it expires.</p>
            """

            text_content = f"""SSL Certificate Renewed Successfully

The SSL certificate for {domain} has been successfully renewed.

Certificate Details:
- Domain: {domain}
- New Expiry Date: {expiry_date}
- Status: Active and Valid

Your domain continues to be secure and accessible. We'll automatically renew the certificate again before it expires."""

            result = await self.email_service.send_email(
                to=recipient_email,
                subject=subject,
                html=html_content,
                text=text_content
            )

            logger.info(f"SSL renewed notification sent for {domain}")
            return result

        except Exception as e:
            logger.error(f"Failed to send SSL renewed notification: {e}")
            return False
