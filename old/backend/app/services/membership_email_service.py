"""
Email service for membership notifications.
Handles sending emails for subscription events.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.services.email_service import EmailService
from app.config import settings

logger = logging.getLogger(__name__)


class MembershipEmailService:
    """Service for sending membership-related emails"""

    def __init__(self):
        """Initialize the membership email service"""
        self.email_service = EmailService()
        
        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render an email template with context.

        Args:
            template_name: Name of the template file
            context: Dictionary of variables to pass to template

        Returns:
            Rendered HTML string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise

    async def send_welcome_email(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        plan_price: float,
        billing_cycle: str,
        benefits: list,
        discount_percentage: float,
        start_date: datetime,
        next_billing_date: datetime,
        dashboard_url: str,
        salon_name: str,
        currency_symbol: str = "₦",
    ) -> bool:
        """
        Send welcome email for new subscription.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            plan_price: Plan price
            billing_cycle: Billing cycle (monthly, quarterly, yearly)
            benefits: List of plan benefits
            discount_percentage: Discount percentage
            start_date: Subscription start date
            next_billing_date: Next billing date
            dashboard_url: URL to membership dashboard
            salon_name: Salon name
            currency_symbol: Currency symbol

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "plan_price": f"{plan_price:.2f}",
                "billing_cycle": billing_cycle,
                "benefits": benefits,
                "discount_percentage": discount_percentage,
                "start_date": start_date.strftime("%B %d, %Y"),
                "next_billing_date": next_billing_date.strftime("%B %d, %Y"),
                "dashboard_url": dashboard_url,
                "salon_name": salon_name,
                "currency_symbol": currency_symbol,
            }

            html = self._render_template("membership_welcome.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"Welcome to {plan_name} Membership! 🎉",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending welcome email to {client_email}: {str(e)}")
            return False

    async def send_renewal_reminder_7day(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        plan_price: float,
        billing_cycle: str,
        discount_percentage: float,
        renewal_date: datetime,
        manage_url: str,
        pause_url: str,
        salon_name: str,
        currency_symbol: str = "₦",
    ) -> bool:
        """
        Send 7-day renewal reminder email.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            plan_price: Plan price
            billing_cycle: Billing cycle
            discount_percentage: Discount percentage
            renewal_date: Renewal date
            manage_url: URL to manage membership
            pause_url: URL to pause membership
            salon_name: Salon name
            currency_symbol: Currency symbol

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "plan_price": f"{plan_price:.2f}",
                "billing_cycle": billing_cycle,
                "discount_percentage": discount_percentage,
                "renewal_date": renewal_date.strftime("%B %d, %Y"),
                "manage_url": manage_url,
                "pause_url": pause_url,
                "salon_name": salon_name,
                "currency_symbol": currency_symbol,
            }

            html = self._render_template("membership_renewal_reminder_7day.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"Your {plan_name} Membership Renews in 7 Days",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending 7-day reminder to {client_email}: {str(e)}")
            return False

    async def send_renewal_reminder_1day(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        plan_price: float,
        billing_cycle: str,
        discount_percentage: float,
        renewal_date: datetime,
        manage_url: str,
        cancel_url: str,
        salon_name: str,
        currency_symbol: str = "₦",
    ) -> bool:
        """
        Send 1-day renewal reminder email.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            plan_price: Plan price
            billing_cycle: Billing cycle
            discount_percentage: Discount percentage
            renewal_date: Renewal date
            manage_url: URL to manage membership
            cancel_url: URL to cancel membership
            salon_name: Salon name
            currency_symbol: Currency symbol

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "plan_price": f"{plan_price:.2f}",
                "billing_cycle": billing_cycle,
                "discount_percentage": discount_percentage,
                "renewal_date": renewal_date.strftime("%B %d, %Y"),
                "manage_url": manage_url,
                "cancel_url": cancel_url,
                "salon_name": salon_name,
                "currency_symbol": currency_symbol,
            }

            html = self._render_template("membership_renewal_reminder_1day.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"Final Reminder: Your {plan_name} Membership Renews Tomorrow!",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending 1-day reminder to {client_email}: {str(e)}")
            return False

    async def send_renewal_confirmation(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        plan_price: float,
        billing_cycle: str,
        transaction_id: str,
        renewal_date: datetime,
        next_renewal_date: datetime,
        dashboard_url: str,
        salon_name: str,
        currency_symbol: str = "₦",
    ) -> bool:
        """
        Send renewal confirmation email.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            plan_price: Plan price
            billing_cycle: Billing cycle
            transaction_id: Payment transaction ID
            renewal_date: Renewal date
            next_renewal_date: Next renewal date
            dashboard_url: URL to membership dashboard
            salon_name: Salon name
            currency_symbol: Currency symbol

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "plan_price": f"{plan_price:.2f}",
                "billing_cycle": billing_cycle,
                "transaction_id": transaction_id,
                "renewal_date": renewal_date.strftime("%B %d, %Y"),
                "next_renewal_date": next_renewal_date.strftime("%B %d, %Y"),
                "dashboard_url": dashboard_url,
                "salon_name": salon_name,
                "currency_symbol": currency_symbol,
            }

            html = self._render_template("membership_renewal_confirmation.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"Your {plan_name} Membership Has Been Renewed ✓",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending renewal confirmation to {client_email}: {str(e)}")
            return False

    async def send_payment_failure_notification(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        plan_price: float,
        billing_cycle: str,
        failure_reason: str,
        failure_date: datetime,
        grace_period_end_date: datetime,
        update_payment_url: str,
        contact_support_url: str,
        salon_name: str,
        currency_symbol: str = "₦",
    ) -> bool:
        """
        Send payment failure notification email.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            plan_price: Plan price
            billing_cycle: Billing cycle
            failure_reason: Reason for payment failure
            failure_date: Date of failure
            grace_period_end_date: When grace period ends
            update_payment_url: URL to update payment method
            contact_support_url: URL to contact support
            salon_name: Salon name
            currency_symbol: Currency symbol

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "plan_price": f"{plan_price:.2f}",
                "billing_cycle": billing_cycle,
                "failure_reason": failure_reason,
                "failure_date": failure_date.strftime("%B %d, %Y"),
                "grace_period_end_date": grace_period_end_date.strftime("%B %d, %Y"),
                "update_payment_url": update_payment_url,
                "contact_support_url": contact_support_url,
                "salon_name": salon_name,
                "currency_symbol": currency_symbol,
            }

            html = self._render_template("membership_payment_failure.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"Payment Failed - Action Required for Your {plan_name} Membership",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending payment failure notification to {client_email}: {str(e)}")
            return False

    async def send_cancellation_confirmation(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        cancellation_reason: str,
        cancellation_date: datetime,
        access_until_date: Optional[datetime],
        total_paid: Optional[float],
        total_savings: Optional[float],
        rejoin_url: str,
        feedback_url: str,
        salon_name: str,
        currency_symbol: str = "₦",
    ) -> bool:
        """
        Send cancellation confirmation email.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            cancellation_reason: Reason for cancellation
            cancellation_date: Date of cancellation
            access_until_date: Date when access ends (if applicable)
            total_paid: Total amount paid
            total_savings: Total savings from membership
            rejoin_url: URL to rejoin membership
            feedback_url: URL to provide feedback
            salon_name: Salon name
            currency_symbol: Currency symbol

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "cancellation_reason": cancellation_reason,
                "cancellation_date": cancellation_date.strftime("%B %d, %Y"),
                "access_until_date": access_until_date.strftime("%B %d, %Y") if access_until_date else None,
                "total_paid": f"{total_paid:.2f}" if total_paid else None,
                "total_savings": f"{total_savings:.2f}" if total_savings else None,
                "rejoin_url": rejoin_url,
                "feedback_url": feedback_url,
                "salon_name": salon_name,
                "currency_symbol": currency_symbol,
            }

            html = self._render_template("membership_cancellation_confirmation.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"Your {plan_name} Membership Has Been Cancelled",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending cancellation confirmation to {client_email}: {str(e)}")
            return False

    async def send_pause_confirmation(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        pause_date: datetime,
        original_end_date: datetime,
        dashboard_url: str,
        salon_name: str,
    ) -> bool:
        """
        Send pause confirmation email.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            pause_date: Date when paused
            original_end_date: Original end date
            dashboard_url: URL to membership dashboard
            salon_name: Salon name

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "action": "pause",
                "action_date": pause_date.strftime("%B %d, %Y"),
                "original_end_date": original_end_date.strftime("%B %d, %Y"),
                "dashboard_url": dashboard_url,
                "salon_name": salon_name,
            }

            html = self._render_template("membership_pause_resume_confirmation.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"Your {plan_name} Membership Has Been Paused",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending pause confirmation to {client_email}: {str(e)}")
            return False

    async def send_resume_confirmation(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        resume_date: datetime,
        new_end_date: datetime,
        billing_cycle: str,
        dashboard_url: str,
        salon_name: str,
    ) -> bool:
        """
        Send resume confirmation email.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            resume_date: Date when resumed
            new_end_date: New end date
            billing_cycle: Billing cycle
            dashboard_url: URL to membership dashboard
            salon_name: Salon name

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "action": "resume",
                "action_date": resume_date.strftime("%B %d, %Y"),
                "new_end_date": new_end_date.strftime("%B %d, %Y"),
                "billing_cycle": billing_cycle,
                "dashboard_url": dashboard_url,
                "salon_name": salon_name,
            }

            html = self._render_template("membership_pause_resume_confirmation.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"Your {plan_name} Membership Has Been Resumed",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending resume confirmation to {client_email}: {str(e)}")
            return False

    async def send_grace_period_warning(
        self,
        client_email: str,
        client_name: str,
        plan_name: str,
        plan_price: float,
        grace_period_end_date: datetime,
        retry_date_1: datetime,
        retry_date_2: datetime,
        retry_date_3: datetime,
        cancellation_date: datetime,
        update_payment_url: str,
        contact_support_url: str,
        salon_name: str,
        currency_symbol: str = "₦",
    ) -> bool:
        """
        Send grace period warning email.

        Args:
            client_email: Client email address
            client_name: Client name
            plan_name: Membership plan name
            plan_price: Plan price
            grace_period_end_date: When grace period ends
            retry_date_1: First retry date
            retry_date_2: Second retry date
            retry_date_3: Third retry date
            cancellation_date: When membership will be cancelled
            update_payment_url: URL to update payment method
            contact_support_url: URL to contact support
            salon_name: Salon name
            currency_symbol: Currency symbol

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            context = {
                "client_name": client_name,
                "plan_name": plan_name,
                "plan_price": f"{plan_price:.2f}",
                "grace_period_end_date": grace_period_end_date.strftime("%B %d, %Y"),
                "retry_date_1": retry_date_1.strftime("%B %d, %Y"),
                "retry_date_2": retry_date_2.strftime("%B %d, %Y"),
                "retry_date_3": retry_date_3.strftime("%B %d, %Y"),
                "cancellation_date": cancellation_date.strftime("%B %d, %Y"),
                "update_payment_url": update_payment_url,
                "contact_support_url": contact_support_url,
                "salon_name": salon_name,
                "currency_symbol": currency_symbol,
            }

            html = self._render_template("membership_grace_period_warning.html", context)

            return await self.email_service.send_email(
                to=client_email,
                subject=f"⚠️ Urgent: Payment Required to Keep Your {plan_name} Membership",
                html=html,
            )
        except Exception as e:
            logger.error(f"Error sending grace period warning to {client_email}: {str(e)}")
            return False
