"""FastAPI application initialization and setup."""

import logging
import json
from decimal import Decimal
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .config import settings
from .middleware.tenant_context import TenantContextMiddleware
from .middleware.subdomain_context import SubdomainContextMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
from .middleware.validation import ValidationMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.audit_logging import AuditLoggingMiddleware
from .middleware.public_booking import PublicBookingMiddleware, PublicBookingRateLimitMiddleware
from .middleware.feature_flags import FeatureFlagMiddleware
from .middleware_setup import setup_middleware
from .db import init_db, close_db
from .routes import auth, tenants, registration, audit, services, availability, appointments, time_slots, staff, service_categories, media, roles, shifts, time_off_requests, customers, appointment_history, customer_preferences, invoices, payments, refunds, webhooks, notifications, resources, waiting_room, public_booking, public_booking_management, pos_transactions, pos_discounts, pos_receipts, pos_commissions, pos_reports, pos_carts, pos_refunds, service_commissions, billing, tenant_recovery, staff_settings, owner_dashboard, websocket_notifications, service_addons, customer_auth, customer_portal, public_waitlist, service_packages, public_service_packages, gift_cards, public_gift_cards, recommendations, availability_events, memberships, public_memberships, group_bookings, public_group_bookings, social_proof, email_templates
from .routes import settings as settings_router
# Import celery app to register all tasks
from .tasks import celery_app  # noqa: F401

# Try to import socketio, but make it optional
try:
    from .socketio_handler import setup_socketio
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    # Logger will be configured below, so we'll log this later


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# Configure logging with detailed format
class DetailedFormatter(logging.Formatter):
    """Custom formatter to include extra fields."""
    def format(self, record):
        if hasattr(record, 'extra'):
            extra_str = str(record.extra)
        else:
            extra_str = ""
        
        base_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if extra_str:
            base_format += f" | {extra_str}"
        
        self._style._fmt = base_format
        return super().format(record)

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Update all handlers with detailed formatter
for handler in logging.root.handlers:
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

# Log socketio availability after logger is configured
if not SOCKETIO_AVAILABLE:
    logger.warning("python-socketio not installed. WebSocket features will be disabled.")


def _seed_pricing_plans():
    """Seed pricing plans into the database."""
    from .models.pricing_plan import PricingPlan
    
    plans = [
        {
            "name": "Free",
            "tier_level": 0,
            "description": "Perfect for getting started",
            "monthly_price": 0.0,
            "yearly_price": 0.0,
            "trial_days": 30,
            "is_trial_plan": True,
            "is_featured": False,
            "features": {
                "max_staff_count": 1,
                "has_pos": False,
                "has_api_access": False,
                "has_advanced_reports": False,
                "has_multi_location": False,
                "has_white_label": False,
                "support_level": "email",
            },
        },
        {
            "name": "Starter",
            "tier_level": 1,
            "description": "For small salons",
            "monthly_price": 5000.0,
            "yearly_price": 50000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": False,
            "features": {
                "max_staff_count": 5,
                "has_pos": True,
                "has_api_access": False,
                "has_advanced_reports": False,
                "has_multi_location": False,
                "has_white_label": False,
                "support_level": "email",
            },
        },
        {
            "name": "Professional",
            "tier_level": 2,
            "description": "For growing businesses",
            "monthly_price": 15000.0,
            "yearly_price": 150000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": True,
            "features": {
                "max_staff_count": 15,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": False,
                "has_white_label": False,
                "support_level": "priority",
            },
        },
        {
            "name": "Business",
            "tier_level": 3,
            "description": "For established businesses",
            "monthly_price": 35000.0,
            "yearly_price": 350000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": False,
            "features": {
                "max_staff_count": 50,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": True,
                "has_white_label": False,
                "support_level": "priority",
            },
        },
        {
            "name": "Enterprise",
            "tier_level": 4,
            "description": "For large operations",
            "monthly_price": 75000.0,
            "yearly_price": 750000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": False,
            "features": {
                "max_staff_count": 200,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": True,
                "has_white_label": True,
                "support_level": "dedicated",
            },
        },
        {
            "name": "Premium",
            "tier_level": 5,
            "description": "Top tier with all features",
            "monthly_price": 150000.0,
            "yearly_price": 1500000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": False,
            "features": {
                "max_staff_count": 500,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": True,
                "has_white_label": True,
                "support_level": "dedicated",
            },
        },
    ]
    
    for plan_data in plans:
        existing = PricingPlan.objects(tier_level=plan_data["tier_level"]).first()
        if not existing:
            plan = PricingPlan(**plan_data)
            plan.save()
            logger.info(f"Created pricing plan: {plan_data['name']}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        debug=settings.debug,
    )
    
    # Set custom JSON encoder for Decimal handling
    app.json_encoder = DecimalEncoder

    # Setup middleware
    setup_middleware(app)

    # Add security headers middleware (first to apply to all responses)
    app.add_middleware(SecurityHeadersMiddleware)

    # Add audit logging middleware
    app.add_middleware(AuditLoggingMiddleware)

    # Add validation middleware
    app.add_middleware(ValidationMiddleware)

    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    # Add feature flags middleware to enforce subscription tier limits
    app.add_middleware(FeatureFlagMiddleware)

    # Add public booking middleware (registered before subdomain so it executes after)
    app.add_middleware(PublicBookingMiddleware)

    # Add public booking rate limiting middleware
    app.add_middleware(PublicBookingRateLimitMiddleware)

    # Add tenant context middleware
    app.add_middleware(TenantContextMiddleware)

    # Add subdomain context middleware (registered last so it executes first)
    app.add_middleware(SubdomainContextMiddleware)

    # Register routes
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(registration.router, prefix=settings.api_prefix)
    app.include_router(tenants.router, prefix=settings.api_prefix)
    app.include_router(tenant_recovery.router, prefix=settings.api_prefix)
    app.include_router(audit.router, prefix=settings.api_prefix)
    app.include_router(media.router, prefix=settings.api_prefix)
    app.include_router(roles.router, prefix=settings.api_prefix)
    app.include_router(service_categories.router, prefix=settings.api_prefix)
    app.include_router(services.router, prefix=settings.api_prefix)
    app.include_router(availability.router, prefix=settings.api_prefix)
    app.include_router(appointments.router, prefix=settings.api_prefix)
    app.include_router(time_slots.router, prefix=settings.api_prefix)
    app.include_router(staff.router, prefix=settings.api_prefix)
    app.include_router(shifts.router, prefix=settings.api_prefix)
    app.include_router(time_off_requests.router, prefix=settings.api_prefix)
    app.include_router(customers.router, prefix=settings.api_prefix)
    app.include_router(customer_preferences.router, prefix=settings.api_prefix)
    app.include_router(appointment_history.router, prefix=settings.api_prefix)
    app.include_router(invoices.router, prefix=settings.api_prefix)
    app.include_router(payments.router, prefix=settings.api_prefix)
    app.include_router(refunds.router, prefix=settings.api_prefix)
    app.include_router(webhooks.router, prefix=settings.api_prefix)
    app.include_router(notifications.router, prefix=settings.api_prefix)
    app.include_router(resources.router, prefix=settings.api_prefix)
    app.include_router(waiting_room.router, prefix=settings.api_prefix)
    app.include_router(public_booking.router, prefix=settings.api_prefix)
    app.include_router(public_booking_management.router, prefix=settings.api_prefix)
    app.include_router(pos_transactions.router, prefix=settings.api_prefix)
    app.include_router(pos_carts.router, prefix=settings.api_prefix)
    app.include_router(pos_refunds.router, prefix=settings.api_prefix)
    app.include_router(pos_discounts.router, prefix=settings.api_prefix)
    app.include_router(pos_receipts.router, prefix=settings.api_prefix)
    app.include_router(pos_commissions.router, prefix=settings.api_prefix)
    app.include_router(pos_reports.router, prefix=settings.api_prefix)
    app.include_router(service_commissions.router, prefix=settings.api_prefix)
    app.include_router(billing.router, prefix=settings.api_prefix)
    app.include_router(staff_settings.router, prefix=settings.api_prefix)
    app.include_router(owner_dashboard.router, prefix=settings.api_prefix)
    app.include_router(settings_router.router, prefix=settings.api_prefix)
    app.include_router(email_templates.router, prefix=settings.api_prefix)
    app.include_router(websocket_notifications.router)
    # Service packages routes (both public and admin)
    app.include_router(service_packages.router, prefix=settings.api_prefix)
    app.include_router(public_service_packages.router, prefix=settings.api_prefix)
    # Service addons routes (both public and admin)
    app.include_router(service_addons.public_router, prefix=settings.api_prefix)
    app.include_router(service_addons.admin_router, prefix=settings.api_prefix)
    # Gift cards routes (both public and admin)
    app.include_router(gift_cards.router, prefix=settings.api_prefix)
    app.include_router(public_gift_cards.router, prefix=settings.api_prefix)
    
    # Customer authentication and portal routes
    app.include_router(customer_auth.router, prefix=settings.api_prefix)
    app.include_router(customer_portal.router, prefix=settings.api_prefix)
    
    # Public waitlist routes
    app.include_router(public_waitlist.router, prefix=settings.api_prefix)
    
    # Recommendations routes
    app.include_router(recommendations.router, prefix=settings.api_prefix)
    
    # Availability events routes (real-time updates)
    app.include_router(availability_events.router, prefix=settings.api_prefix)
    
    # Membership routes (both public and admin)
    app.include_router(memberships.router, prefix=settings.api_prefix)
    app.include_router(public_memberships.router, prefix=settings.api_prefix)
    
    # Group booking routes (both public and admin)
    app.include_router(group_bookings.router, prefix=settings.api_prefix)
    app.include_router(public_group_bookings.router, prefix=settings.api_prefix)
    
    # Social proof routes
    app.include_router(social_proof.router, prefix=settings.api_prefix)

    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize database on startup."""
        try:
            init_db()
            logger.info("Database initialized successfully")
            
            # Seed pricing plans if they don't exist
            from .models.pricing_plan import PricingPlan
            existing_plans = PricingPlan.objects().count()
            if existing_plans == 0:
                logger.info("Seeding pricing plans...")
                _seed_pricing_plans()
                logger.info("Pricing plans seeded successfully")
            
            # Log all registered routes
            logger.info("=" * 60)
            logger.info("Registered API Routes:")
            logger.info("=" * 60)
            for route in app.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    methods = ', '.join(sorted(route.methods)) if route.methods else 'N/A'
                    logger.info(f"  {methods:20} {route.path}")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            # Don't raise - allow app to start

    # Close database on shutdown
    @app.on_event("shutdown")
    async def shutdown_event():
        """Close database on shutdown."""
        try:
            close_db()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "environment": settings.environment}

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Salon/Spa/Gym SaaS Platform API",
            "version": settings.api_version,
            "docs": "/docs",
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred",
                },
            },
        )

    logger.info(f"FastAPI application created - Environment: {settings.environment}")

    # Wrap FastAPI app with Socket.IO ASGI app if available
    if SOCKETIO_AVAILABLE:
        asgi_app = setup_socketio(app)
        return asgi_app
    else:
        return app


# Create application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
