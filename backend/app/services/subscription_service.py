"""Subscription service for managing subscription lifecycle."""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId
from dateutil.relativedelta import relativedelta

from app.models.subscription import Subscription
from app.models.pricing_plan import PricingPlan

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing subscriptions."""

    @staticmethod
    def _calculate_period_end(start_date: datetime, billing_cycle: str) -> datetime:
        """
        Calculate period end date using calendar-based calculations.
        
        Args:
            start_date: Start of billing period
            billing_cycle: "monthly" or "yearly"
            
        Returns:
            End date of billing period
        """
        if billing_cycle == "yearly":
            return start_date + relativedelta(years=1)
        else:  # monthly
            return start_date + relativedelta(months=1)

    @staticmethod
    def _calculate_proration(
        current_plan_price: float,
        new_plan_price: float,
        current_period_end: datetime,
        billing_cycle: str,
    ) -> Dict[str, Any]:
        """
        Calculate proration for plan changes.
        
        Args:
            current_plan_price: Current plan price (monthly or yearly)
            new_plan_price: New plan price (monthly or yearly)
            current_period_end: End of current billing period
            billing_cycle: "monthly" or "yearly"
            
        Returns:
            Dict with charge_amount and refund_amount
        """
        now = datetime.utcnow()
        days_remaining = (current_period_end - now).days
        
        if billing_cycle == "yearly":
            total_days = 365
        else:
            total_days = 30
        
        # Calculate daily rates
        current_daily_rate = current_plan_price / total_days
        new_daily_rate = new_plan_price / total_days
        
        # Calculate unused credit from current plan
        unused_credit = current_daily_rate * days_remaining
        
        # Calculate charge for new plan for remaining days
        new_plan_charge = new_daily_rate * days_remaining
        
        # Net charge (positive = charge customer, negative = refund)
        net_charge = new_plan_charge - unused_credit
        
        return {
            "charge_amount": max(0, net_charge),
            "refund_amount": max(0, -net_charge),
            "days_remaining": days_remaining,
        }

    @staticmethod
    def _validate_tier_transition(current_tier: int, new_tier: int, is_upgrade: bool) -> bool:
        """
        Validate that tier transition is valid.
        
        Args:
            current_tier: Current plan tier level
            new_tier: New plan tier level
            is_upgrade: True if upgrading, False if downgrading
            
        Returns:
            True if transition is valid
        """
        if current_tier == new_tier:
            return False  # Cannot change to same tier
        
        if is_upgrade and new_tier <= current_tier:
            return False  # Upgrade must go to higher tier
        
        if not is_upgrade and new_tier >= current_tier:
            return False  # Downgrade must go to lower tier
        
        return True

    @staticmethod
    def create_trial_subscription(tenant_id: str, trial_days: int = 30) -> Subscription:
        """
        Create a trial subscription for a new tenant.

        Args:
            tenant_id: Tenant ID
            trial_days: Number of trial days (default 30)

        Returns:
            Subscription: Created subscription
        """
        try:
            # Get Free plan
            free_plan = PricingPlan.objects(tier_level=0, is_active=True).first()
            if not free_plan:
                logger.error("Free pricing plan not found")
                raise ValueError("Free pricing plan not configured")

            now = datetime.utcnow()
            trial_end = now + timedelta(days=trial_days)

            subscription = Subscription(
                tenant_id=ObjectId(tenant_id),
                pricing_plan_id=free_plan.id,
                billing_cycle="monthly",
                current_period_start=now,
                current_period_end=trial_end,
                next_billing_date=trial_end,
                trial_end=trial_end,
                is_trial=True,
                status="trial",
                auto_renew=True,
            )
            subscription.save()
            logger.info(f"Trial subscription created for tenant {tenant_id}")
            return subscription
        except Exception as e:
            logger.error(f"Error creating trial subscription: {str(e)}")
            raise

    @staticmethod
    def upgrade_subscription(
        tenant_id: str,
        new_plan_id: str,
        billing_cycle: str = "monthly",
        paystack_subscription_id: Optional[str] = None,
    ) -> Subscription:
        """
        Upgrade subscription to a new plan.
        Charges customer for prorated amount of new plan.

        Args:
            tenant_id: Tenant ID
            new_plan_id: New pricing plan ID
            billing_cycle: "monthly" or "yearly"
            paystack_subscription_id: Paystack subscription ID

        Returns:
            Subscription: Updated subscription
        """
        try:
            subscription = Subscription.objects(tenant_id=ObjectId(tenant_id)).first()
            if not subscription:
                raise ValueError(f"Subscription not found for tenant {tenant_id}")

            new_plan = PricingPlan.objects(id=ObjectId(new_plan_id)).first()
            if not new_plan:
                raise ValueError(f"Pricing plan {new_plan_id} not found")

            # Validate tier transition
            current_plan = PricingPlan.objects(id=subscription.pricing_plan_id).first()
            if not current_plan:
                raise ValueError(f"Current pricing plan not found")
            
            if not SubscriptionService._validate_tier_transition(
                current_plan.tier_level, new_plan.tier_level, is_upgrade=True
            ):
                raise ValueError(
                    f"Invalid upgrade: cannot upgrade from tier {current_plan.tier_level} to tier {new_plan.tier_level}"
                )

            # Calculate proration
            current_price = (
                current_plan.monthly_price if billing_cycle == "monthly" else current_plan.yearly_price
            )
            new_price = (
                new_plan.monthly_price if billing_cycle == "monthly" else new_plan.yearly_price
            )
            
            proration = SubscriptionService._calculate_proration(
                current_price,
                new_price,
                subscription.current_period_end,
                billing_cycle,
            )

            # Update subscription
            now = datetime.utcnow()
            subscription.pricing_plan_id = new_plan.id
            subscription.billing_cycle = billing_cycle
            subscription.status = "active"
            subscription.is_trial = False
            subscription.trial_end = None
            subscription.paystack_subscription_id = paystack_subscription_id
            subscription.last_payment_date = now
            # Record the charge amount (prorated)
            subscription.last_payment_amount = proration["charge_amount"]
            subscription.failed_payment_count = 0
            subscription.renewal_reminders_sent = {}
            subscription.save()

            logger.info(
                f"Subscription upgraded for tenant {tenant_id} to plan {new_plan.name}, "
                f"charge: {proration['charge_amount']}, refund: {proration['refund_amount']}"
            )
            return subscription
        except Exception as e:
            logger.error(f"Error upgrading subscription: {str(e)}")
            raise

    @staticmethod
    def downgrade_subscription(
        tenant_id: str,
        new_plan_id: str,
        billing_cycle: str = "monthly",
    ) -> Subscription:
        """
        Downgrade subscription to a lower plan.
        Calculates and issues refund for unused period.
        Changes take effect immediately with proration.

        Args:
            tenant_id: Tenant ID
            new_plan_id: New pricing plan ID
            billing_cycle: "monthly" or "yearly"

        Returns:
            Subscription: Updated subscription
        """
        try:
            subscription = Subscription.objects(tenant_id=ObjectId(tenant_id)).first()
            if not subscription:
                raise ValueError(f"Subscription not found for tenant {tenant_id}")

            new_plan = PricingPlan.objects(id=ObjectId(new_plan_id)).first()
            if not new_plan:
                raise ValueError(f"Pricing plan {new_plan_id} not found")

            # Validate tier transition
            current_plan = PricingPlan.objects(id=subscription.pricing_plan_id).first()
            if not current_plan:
                raise ValueError(f"Current pricing plan not found")
            
            if not SubscriptionService._validate_tier_transition(
                current_plan.tier_level, new_plan.tier_level, is_upgrade=False
            ):
                raise ValueError(
                    f"Invalid downgrade: cannot downgrade from tier {current_plan.tier_level} to tier {new_plan.tier_level}"
                )

            # Calculate proration and refund
            current_price = (
                current_plan.monthly_price if billing_cycle == "monthly" else current_plan.yearly_price
            )
            new_price = (
                new_plan.monthly_price if billing_cycle == "monthly" else new_plan.yearly_price
            )
            
            proration = SubscriptionService._calculate_proration(
                current_price,
                new_price,
                subscription.current_period_end,
                billing_cycle,
            )

            # Update subscription with new plan
            subscription.pricing_plan_id = new_plan.id
            subscription.billing_cycle = billing_cycle
            # Record refund amount (negative indicates refund)
            subscription.last_payment_amount = -proration["refund_amount"]
            subscription.save()

            logger.info(
                f"Subscription downgraded for tenant {tenant_id} to plan {new_plan.name}, "
                f"refund: {proration['refund_amount']}"
            )
            return subscription
        except Exception as e:
            logger.error(f"Error downgrading subscription: {str(e)}")
            raise

    @staticmethod
    def cancel_subscription(tenant_id: str) -> Subscription:
        """
        Cancel subscription.
        Calculates and issues refund for unused billing period.

        Args:
            tenant_id: Tenant ID

        Returns:
            Subscription: Updated subscription
        """
        try:
            subscription = Subscription.objects(tenant_id=ObjectId(tenant_id)).first()
            if not subscription:
                raise ValueError(f"Subscription not found for tenant {tenant_id}")

            # Calculate refund for unused period
            plan = PricingPlan.objects(id=subscription.pricing_plan_id).first()
            if plan:
                plan_price = (
                    plan.monthly_price if subscription.billing_cycle == "monthly" else plan.yearly_price
                )
                
                now = datetime.utcnow()
                days_remaining = (subscription.current_period_end - now).days
                total_days = 365 if subscription.billing_cycle == "yearly" else 30
                
                daily_rate = plan_price / total_days
                refund_amount = daily_rate * days_remaining
            else:
                refund_amount = 0

            subscription.status = "canceled"
            subscription.canceled_at = datetime.utcnow()
            subscription.auto_renew = False
            # Record refund amount (negative indicates refund)
            subscription.last_payment_amount = -refund_amount
            subscription.save()

            logger.info(f"Subscription canceled for tenant {tenant_id}, refund: {refund_amount}")
            return subscription
        except Exception as e:
            logger.error(f"Error canceling subscription: {str(e)}")
            raise

    @staticmethod
    def handle_payment_success(
        tenant_id: str,
        amount: float,
        paystack_subscription_id: str,
    ) -> Subscription:
        """
        Handle successful payment.

        Args:
            tenant_id: Tenant ID
            amount: Payment amount
            paystack_subscription_id: Paystack subscription ID

        Returns:
            Subscription: Updated subscription
        """
        try:
            subscription = Subscription.objects(tenant_id=ObjectId(tenant_id)).first()
            if not subscription:
                raise ValueError(f"Subscription not found for tenant {tenant_id}")

            now = datetime.utcnow()
            subscription.status = "active"
            subscription.last_payment_date = now
            subscription.last_payment_amount = amount
            subscription.failed_payment_count = 0
            subscription.is_in_grace_period = False
            subscription.grace_period_end = None
            subscription.paystack_subscription_id = paystack_subscription_id
            subscription.renewal_reminders_sent = {}  # Reset reminders
            subscription.save()

            logger.info(f"Payment successful for tenant {tenant_id}, amount: {amount}")
            return subscription
        except Exception as e:
            logger.error(f"Error handling payment success: {str(e)}")
            raise

    @staticmethod
    def handle_payment_failure(tenant_id: str, grace_period_days: int = 3) -> Subscription:
        """
        Handle failed payment, enter grace period.

        Args:
            tenant_id: Tenant ID
            grace_period_days: Days to allow before suspension (default 3)

        Returns:
            Subscription: Updated subscription
        """
        try:
            subscription = Subscription.objects(tenant_id=ObjectId(tenant_id)).first()
            if not subscription:
                raise ValueError(f"Subscription not found for tenant {tenant_id}")

            now = datetime.utcnow()
            grace_end = now + timedelta(days=grace_period_days)

            subscription.status = "past_due"
            subscription.is_in_grace_period = True
            subscription.grace_period_end = grace_end
            subscription.failed_payment_count += 1
            subscription.save()

            logger.info(f"Payment failed for tenant {tenant_id}, grace period until {grace_end}")
            return subscription
        except Exception as e:
            logger.error(f"Error handling payment failure: {str(e)}")
            raise

    @staticmethod
    def check_and_expire_subscriptions() -> Dict[str, Any]:
        """
        Check for expired subscriptions and update status.
        Properly handles grace period transitions.
        Should be called by a scheduled task.

        Returns:
            Dict with counts of expired and suspended subscriptions
        """
        try:
            now = datetime.utcnow()
            result = {"expired": 0, "suspended": 0}

            # Find subscriptions that have expired
            expired_subs = Subscription.objects(
                current_period_end__lt=now,
                status__in=["active", "past_due"]
            )

            for sub in expired_subs:
                # Check if in grace period
                if sub.is_in_grace_period and sub.grace_period_end:
                    # Grace period has expired, mark as expired
                    if now > sub.grace_period_end:
                        sub.status = "expired"
                        sub.is_in_grace_period = False
                        sub.save()
                        result["suspended"] += 1
                        logger.info(f"Subscription suspended for tenant {sub.tenant_id} (grace period expired)")
                    # else: still in grace period, don't change status
                else:
                    # Not in grace period, mark as expired
                    sub.status = "expired"
                    sub.save()
                    result["expired"] += 1
                    logger.info(f"Subscription expired for tenant {sub.tenant_id}")

            return result
        except Exception as e:
            logger.error(f"Error checking expired subscriptions: {str(e)}")
            raise

    @staticmethod
    def send_renewal_reminders() -> Dict[str, int]:
        """
        Send renewal reminders for subscriptions expiring soon.
        Should be called by a scheduled task.

        Returns:
            Dict with counts of reminders sent
        """
        try:
            now = datetime.utcnow()
            result = {"7_days": 0, "3_days": 0, "expiry": 0}

            # 7 days before expiry
            seven_days_later = now + timedelta(days=7)
            subs_7_days = Subscription.objects(
                current_period_end__gte=now,
                current_period_end__lte=seven_days_later,
                status="active",
            )

            for sub in subs_7_days:
                if not sub.renewal_reminders_sent.get("7_days"):
                    # TODO: Send email reminder
                    sub.renewal_reminders_sent["7_days"] = True
                    sub.save()
                    result["7_days"] += 1
                    logger.info(f"7-day renewal reminder sent to tenant {sub.tenant_id}")

            # 3 days before expiry
            three_days_later = now + timedelta(days=3)
            subs_3_days = Subscription.objects(
                current_period_end__gte=now,
                current_period_end__lte=three_days_later,
                status="active",
            )

            for sub in subs_3_days:
                if not sub.renewal_reminders_sent.get("3_days"):
                    # TODO: Send email reminder
                    sub.renewal_reminders_sent["3_days"] = True
                    sub.save()
                    result["3_days"] += 1
                    logger.info(f"3-day renewal reminder sent to tenant {sub.tenant_id}")

            # On expiry date
            tomorrow = now + timedelta(days=1)
            subs_expiry = Subscription.objects(
                current_period_end__gte=now,
                current_period_end__lte=tomorrow,
                status="active",
            )

            for sub in subs_expiry:
                if not sub.renewal_reminders_sent.get("expiry"):
                    # TODO: Send email reminder
                    sub.renewal_reminders_sent["expiry"] = True
                    sub.save()
                    result["expiry"] += 1
                    logger.info(f"Expiry reminder sent to tenant {sub.tenant_id}")

            return result
        except Exception as e:
            logger.error(f"Error sending renewal reminders: {str(e)}")
            raise

    @staticmethod
    def get_subscription(tenant_id: str) -> Optional[Subscription]:
        """
        Get subscription for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            Subscription or None
        """
        try:
            return Subscription.objects(tenant_id=ObjectId(tenant_id)).first()
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            return None

    @staticmethod
    def get_plan_features(tenant_id: str) -> Dict[str, Any]:
        """
        Get feature flags for a tenant based on their subscription plan.

        Args:
            tenant_id: Tenant ID

        Returns:
            Dict of feature flags
        """
        try:
            subscription = Subscription.objects(tenant_id=ObjectId(tenant_id)).first()
            if not subscription:
                return {}

            plan = PricingPlan.objects(id=subscription.pricing_plan_id).first()
            if not plan:
                return {}

            return plan.features or {}
        except Exception as e:
            logger.error(f"Error getting plan features: {str(e)}")
            return {}
