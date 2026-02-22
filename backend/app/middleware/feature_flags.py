"""Feature flag middleware to enforce subscription tier limits."""

import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.subscription_service import SubscriptionService
from app.context import get_tenant_id

logger = logging.getLogger(__name__)


class FeatureFlagMiddleware(BaseHTTPMiddleware):
    """Middleware to check feature access based on subscription tier."""

    # Map of feature names to required tier level
    FEATURE_REQUIREMENTS = {
        # POS features
        "/api/v1/pos": 1,  # Starter and above
        "/api/v1/pos/transactions": 1,
        "/api/v1/pos/carts": 1,
        "/api/v1/pos/discounts": 1,
        "/api/v1/pos/receipts": 1,
        "/api/v1/pos/refunds": 1,
        "/api/v1/pos/commissions": 1,
        "/api/v1/pos/reports": 1,
        # API access
        "/api/v1/integrations": 2,  # Professional and above
        # Advanced reports
        "/api/v1/reports/advanced": 2,
        "/api/v1/financial_reports": 2,
        # Multi-location
        "/api/v1/locations": 3,  # Business and above
        # White-label
        "/api/v1/white-label": 4,  # Enterprise and above
    }

    async def dispatch(self, request: Request, call_next):
        """Check feature access before processing request."""
        try:
            # Skip feature checks for public endpoints
            if request.url.path.startswith("/public"):
                return await call_next(request)

            # Skip feature checks for auth endpoints
            if request.url.path.startswith("/api/v1/auth"):
                return await call_next(request)

            # Get tenant ID from context
            tenant_id = request.headers.get("X-Tenant-ID")
            if not tenant_id:
                # Try to get from context
                try:
                    tenant_id = get_tenant_id()
                except:
                    # No tenant context, skip feature check
                    return await call_next(request)

            # Check if this endpoint requires a specific tier
            required_tier = self._get_required_tier(request.url.path)
            if required_tier is None:
                # No tier requirement for this endpoint
                return await call_next(request)

            # Get tenant's subscription
            subscription = SubscriptionService.get_subscription(tenant_id)
            if not subscription:
                # No subscription found, deny access
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No active subscription found",
                )

            # Get pricing plan
            from app.models.pricing_plan import PricingPlan

            plan = PricingPlan.objects(id=subscription.pricing_plan_id).first()
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Pricing plan not found",
                )

            # Check if tenant's tier meets requirement
            if plan.tier_level < required_tier:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This feature requires {self._get_tier_name(required_tier)} plan or higher",
                )

            # Check subscription status
            if subscription.status not in ["trial", "active"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Subscription is not active",
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in feature flag middleware: {str(e)}")
            # Don't block on middleware errors, let request proceed
            pass

        return await call_next(request)

    def _get_required_tier(self, path: str) -> int | None:
        """Get required tier level for a path."""
        for feature_path, tier in self.FEATURE_REQUIREMENTS.items():
            if path.startswith(feature_path):
                return tier
        return None

    def _get_tier_name(self, tier_level: int) -> str:
        """Get tier name from level."""
        tier_names = {
            0: "Free",
            1: "Starter",
            2: "Professional",
            3: "Business",
            4: "Enterprise",
            5: "Premium",
        }
        return tier_names.get(tier_level, "Unknown")
