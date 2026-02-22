"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
from app.config import settings
from app.database import Database

# Try to import socketio services, but don't fail if dependencies are missing
try:
    from app.services.socketio_service import socketio_service
    from app.api.socketio_events import register_socketio_handlers
    SOCKETIO_AVAILABLE = True
except ImportError as e:
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(f"SocketIO services not available: {e}")
    SOCKETIO_AVAILABLE = False
    socketio_service = None
    register_socketio_handlers = None

# Try to import voice services, but don't fail if dependencies are missing
# NOTE: Voice services are lazy-loaded to avoid blocking server startup
VOICE_SERVICES_AVAILABLE = False
VoiceAssistantService = None
BackgroundLearningJob = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Always use INFO level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set pymongo to WARNING to reduce noise
logging.getLogger('pymongo').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Global background job
_background_job: BackgroundLearningJob = None
_background_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global _background_job, _background_task
    
    # Startup
    logger.info("=" * 80)
    logger.info("BACKEND SERVER STARTING")
    logger.info("=" * 80)
    
    # Initialize Socket.IO event handlers
    if SOCKETIO_AVAILABLE and register_socketio_handlers:
        try:
            register_socketio_handlers()
            logger.info("✅ Socket.IO event handlers registered")
        except Exception as e:
            logger.warning(f"⚠️  Socket.IO initialization failed: {e}")
    else:
        logger.info("⚠️  Socket.IO handlers not available")
    
    # Skip database connection in test mode (tests handle this separately)
    if not settings.TESTING:
        logger.info("Connecting to database...")
        try:
            Database.connect_db()
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.error("⚠️  Cannot start server without database connection")
            raise
    else:
        logger.info("Test mode: Skipping database connection")
    
    # Initialize background learning job (if voice services are available)
    if VOICE_SERVICES_AVAILABLE:
        try:
            # Initialize voice service with a timeout to prevent blocking server startup
            try:
                voice_service = VoiceAssistantService()
                _background_job = BackgroundLearningJob(
                    pattern_analyzer=voice_service.pattern_analyzer,
                    prediction_engine=voice_service.prediction_engine,
                    suggestion_generator=voice_service.suggestion_generator,
                    insight_generator=voice_service.insight_generator,
                    proactive_alerter=voice_service.proactive_alerter,
                    learning_model=voice_service.learning_model
                )
                # Start background job in a task
                _background_task = asyncio.create_task(_background_job.start(interval_minutes=60))
                logger.info("✅ Background learning job started")
            except Exception as voice_init_error:
                logger.warning(f"⚠️  Voice service initialization failed: {voice_init_error}")
                logger.warning("⚠️  Continuing without background learning job")
        except Exception as e:
            logger.warning(f"⚠️  Failed to start background learning job: {e}")
    else:
        logger.info("⚠️  Voice services not available - skipping background learning job")
    
    logger.info("=" * 80)
    logger.info("✅ SERVER READY ON http://0.0.0.0:8000")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if _background_job:
        await _background_job.stop()
    if _background_task:
        _background_task.cancel()
    if not settings.TESTING:
        try:
            Database.close_db()
        except:
            pass
    logger.info("Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Attach Socket.IO to the app (if available)
if SOCKETIO_AVAILABLE and socketio_service:
    app = socketio_service.attach_to_app(app)
else:
    logger.warning("⚠️  Socket.IO not attached - dependencies not available")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add domain routing middleware
from app.middleware.domain_routing import DomainRoutingMiddleware
app.add_middleware(DomainRoutingMiddleware)

# Add comprehensive request/response logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests and responses with full details"""
    import json
    
    # Skip verbose logging for auth check endpoint during initial auth phase
    is_auth_check = request.url.path == "/api/auth/me"
    
    if not is_auth_check:
        logger.info("=" * 80)
        logger.info(f"=== INCOMING REQUEST ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"URL: {request.url}")
        logger.info(f"Path: {request.url.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Try to read and log request body
        try:
            body = await request.body()
            if body:
                try:
                    body_json = json.loads(body.decode())
                    logger.info(f"Body (JSON): {json.dumps(body_json, indent=2)}")
                except:
                    logger.info(f"Body (raw): {body[:500]}")  # First 500 chars
            else:
                logger.info("Body: (empty)")
        except Exception as e:
            logger.warning(f"Could not read body: {e}")
    
    # Process request
    try:
        response = await call_next(request)
        
        # Only log response if not a 401 on auth check or non-auth endpoints
        if not (response.status_code == 401 and not is_auth_check):
            if not is_auth_check:
                logger.info(f"=== RESPONSE === Status: {response.status_code}")
                logger.info("=" * 80)
        
        return response
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"=== EXCEPTION IN REQUEST PROCESSING ===")
        logger.error(f"Exception Type: {type(e).__name__}")
        logger.error(f"Exception Message: {str(e)}")
        logger.error(f"Full Traceback:", exc_info=True)
        logger.error("=" * 80)
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Kenikool Salon Management SaaS API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if Database._initialized else "disconnected"
    }


# Import exceptions module directly (not through app.api package)
# from app.api import exceptions as exceptions_module
# exceptions_module.register_exception_handlers(app)

# Import API router directly (lazy-loaded)
# from app.api import router as api_router
# app.include_router(api_router, prefix="/api")

# Import other routers directly
# from app.api import webhooks, upload, websocket
# app.include_router(webhooks.router)
# app.include_router(upload.router)
# app.include_router(websocket.router)

# Import auth router
try:
    from app.api import auth
    app.include_router(auth.router)
    logger.info("✅ Auth router registered")
except ImportError as e:
    logger.warning(f"⚠️  Auth router not available: {e}")

# Import search router
try:
    from app.api import search
    app.include_router(search.router)
    logger.info("✅ Search router registered")
except ImportError as e:
    logger.warning(f"⚠️  Search router not available: {e}")

# Import voice assistant router (if available)
try:
    from app.api import voice
    app.include_router(voice.router)
    logger.info("✅ Voice router registered")
except ImportError as e:
    logger.warning(f"⚠️  Voice router not available: {e}")

# Import analytics router
from app.api import analytics
app.include_router(analytics.router)

# Import referral and tenant routers
try:
    from app.api import referrals, tenants
    app.include_router(referrals.router)
    app.include_router(tenants.router)
    logger.info("✅ Referral and tenant routers registered")
except ImportError as e:
    logger.warning(f"⚠️  Referral/tenant routers not available: {e}")

# Import white label routers
try:
    from app.api import white_label, white_label_websocket
    app.include_router(white_label.router)
    app.include_router(white_label_websocket.router)
    logger.info("✅ White label routers registered")
except ImportError as e:
    logger.warning(f"⚠️  White label routers not available: {e}")

# Import campaign routers
from app.api import (
    campaigns, campaign_templates, ab_testing, opt_outs, campaign_integrations,
    campaign_analytics, delivery_tracking, campaign_budget, segments, automation, sms_credits
)
app.include_router(campaigns.router, prefix="/api", tags=["campaigns"])
app.include_router(sms_credits.router, prefix="/api", tags=["sms-credits"])
app.include_router(campaign_templates.router, prefix="/api/campaign-templates", tags=["campaign-templates"])
app.include_router(ab_testing.router, prefix="/api/campaigns", tags=["ab-testing"])
app.include_router(opt_outs.router, prefix="/api/opt-outs", tags=["opt-outs"])
app.include_router(campaign_integrations.router, prefix="/api/campaigns", tags=["integrations"])
app.include_router(campaign_analytics.router, prefix="/api/campaigns", tags=["campaign-analytics"])
app.include_router(delivery_tracking.router, prefix="/api/campaigns", tags=["delivery-tracking"])
app.include_router(campaign_budget.router, prefix="/api/campaigns", tags=["campaign-budget"])
app.include_router(segments.router, prefix="/api/segments", tags=["segments"])
app.include_router(automation.router, prefix="/api/campaign-automation", tags=["automation"])

# Import waitlist routers
try:
    from app.api import waitlist, waitlist_templates, waitlist_client
    app.include_router(waitlist.router)
    app.include_router(waitlist_templates.router)
    app.include_router(waitlist_client.router)
    logger.info("✅ Waitlist routers registered")
except ImportError as e:
    logger.warning(f"⚠️  Waitlist routers not available: {e}")

# Import settings system routers
try:
    from app.api import security, api_keys, privacy_preferences, data_management, profile_settings
    app.include_router(security.router)
    app.include_router(api_keys.router)
    app.include_router(privacy_preferences.router)
    app.include_router(data_management.router)
    app.include_router(profile_settings.router)
    logger.info("✅ Settings system routers registered")
except ImportError as e:
    logger.warning(f"⚠️  Settings system routers not available: {e}")

# Import payment management routers
try:
    from app.api import payments, credits
    app.include_router(payments.router)
    app.include_router(credits.router)
    logger.info("✅ Payment management and credits routers registered")
except ImportError as e:
    logger.warning(f"⚠️  Payment management or credits router not available: {e}")

# Import POS routers
try:
    from app.api import pos
    app.include_router(pos.router)
    logger.info("✅ POS router registered")
except ImportError as e:
    logger.warning(f"⚠️  POS router not available: {e}")

# Import public gift cards routers
try:
    from app.api import public_gift_cards, gift_cards_staff
    app.include_router(public_gift_cards.router)
    app.include_router(gift_cards_staff.router)
    logger.info("✅ Public and staff gift cards routers registered")
except ImportError as e:
    logger.warning(f"⚠️  Public gift cards router not available: {e}")

# Import membership routers
try:
    from app.api import memberships
    app.include_router(memberships.router)
    logger.info("✅ Membership router registered")
except ImportError as e:
    logger.warning(f"⚠️  Membership router not available: {e}")

# Import location routers
try:
    from app.api import locations
    app.include_router(locations.router)
    logger.info("✅ Location router registered")
except ImportError as e:
    logger.warning(f"⚠️  Location router not available: {e}")

# Import clients router
try:
    from app.api import clients
    app.include_router(clients.router)
    logger.info("✅ Clients router registered")
except ImportError as e:
    logger.warning(f"⚠️  Clients router not available: {e}")

# Import bookings router
try:
    from app.api import bookings, group_bookings, availability, no_shows, prerequisites, add_ons, cancellations, booking_templates, variants  # , guest_bookings
    app.include_router(bookings.router)
    app.include_router(group_bookings.router)
    app.include_router(availability.router)
    app.include_router(no_shows.router)
    app.include_router(prerequisites.router)
    app.include_router(add_ons.router)
    app.include_router(cancellations.router)
    app.include_router(booking_templates.router)
    app.include_router(variants.router)
    # app.include_router(guest_bookings.router)
    logger.info("✅ Bookings, group bookings, availability, no-shows, prerequisites, add-ons, cancellations, booking-templates, and variants routers registered")
except ImportError as e:
    logger.warning(f"⚠️  Bookings routers not available: {e}")

# Import guest booking API router (replacement for problematic guest_bookings)
try:
    from app.api import guest_booking_api
    app.include_router(guest_booking_api.router)
    logger.info("✅ Guest booking API router registered")
except ImportError as e:
    logger.warning(f"⚠️  Guest booking API router not available: {e}")

# Import guest dashboard router
try:
    from app.api import guest_dashboard
    app.include_router(guest_dashboard.router)
    logger.info("✅ Guest dashboard router registered")
except ImportError as e:
    logger.warning(f"⚠️  Guest dashboard router not available: {e}")

# Import family accounts router
try:
    from app.api import family_accounts
    app.include_router(family_accounts.router)
    logger.info("✅ Family accounts router registered")
except ImportError as e:
    logger.warning(f"⚠️  Family accounts router not available: {e}")

# Import services router
try:
    from app.api import services, service_inquiries
    app.include_router(services.router)
    app.include_router(service_inquiries.router)
    logger.info("✅ Services and service inquiries routers registered")
except ImportError as e:
    logger.warning(f"⚠️  Services router not available: {e}")

# Import marketplace routers
try:
    from app.api import marketplace, marketplace_bookings, marketplace_payments, marketplace_services
    app.include_router(marketplace.router)
    app.include_router(marketplace_bookings.router)
    app.include_router(marketplace_payments.router)
    app.include_router(marketplace_services.router)
    logger.info("✅ Marketplace routers registered")
except ImportError as e:
    logger.warning(f"⚠️  Marketplace routers not available: {e}")

# Import dashboard router
try:
    from app.api import dashboard
    app.include_router(dashboard.router)
    logger.info("✅ Dashboard router registered")
except ImportError as e:
    logger.warning(f"⚠️  Dashboard router not available: {e}")

# Import staff notifications router
try:
    from app.api import staff_notifications
    app.include_router(staff_notifications.router)
    logger.info("✅ Staff notifications router registered")
except ImportError as e:
    logger.warning(f"⚠️  Staff notifications router not available: {e}")

# Import staff onboarding router
try:
    from app.api import staff_onboarding
    app.include_router(staff_onboarding.router)
    logger.info("✅ Staff onboarding router registered")
except ImportError as e:
    logger.warning(f"⚠️  Staff onboarding router not available: {e}")

# Import notification preferences router
try:
    from app.api import notification_preferences
    app.include_router(notification_preferences.router)
    logger.info("✅ Notification preferences router registered")
except ImportError as e:
    logger.warning(f"⚠️  Notification preferences router not available: {e}")

# Import notifications router
try:
    from app.api import notifications
    app.include_router(notifications.router)
    logger.info("✅ Notifications router registered")
except ImportError as e:
    logger.warning(f"⚠️  Notifications router not available: {e}")

# Import reviews router
try:
    from app.api import reviews
    app.include_router(reviews.router)
    logger.info("✅ Reviews router registered")
except ImportError as e:
    logger.warning(f"⚠️  Reviews router not available: {e}")

# Import stylists router
try:
    from app.api import stylists
    app.include_router(stylists.router)
    logger.info("✅ Stylists router registered")
except ImportError as e:
    logger.warning(f"⚠️  Stylists router not available: {e}")

# Import inventory router
try:
    from app.api import inventory
    app.include_router(inventory.router)
    logger.info("✅ Inventory router registered")
except ImportError as e:
    logger.warning(f"⚠️  Inventory router not available: {e}")

# Import loyalty router
try:
    from app.api import loyalty
    app.include_router(loyalty.router)
    logger.info("✅ Loyalty router registered")
except ImportError as e:
    logger.warning(f"⚠️  Loyalty router not available: {e}")

# Import referrals router (if not already imported)
try:
    from app.api import referrals as referrals_router
    app.include_router(referrals_router.router)
    logger.info("✅ Referrals router registered")
except ImportError as e:
    logger.warning(f"⚠️  Referrals router not available: {e}")

# Import weather router
try:
    from app.api import weather
    app.include_router(weather.router)
    logger.info("✅ Weather router registered")
except ImportError as e:
    logger.warning(f"⚠️  Weather router not available: {e}")

# Import directions router
try:
    from app.api import directions
    app.include_router(directions.router)
    logger.info("✅ Directions router registered")
except ImportError as e:
    logger.warning(f"⚠️  Directions router not available: {e}")

# Import boundaries router
try:
    from app.api import boundaries
    app.include_router(boundaries.router)
    logger.info("✅ Boundaries router registered")
except ImportError as e:
    logger.warning(f"⚠️  Boundaries router not available: {e}")

# Import recommendations router
try:
    from app.api import recommendations
    app.include_router(recommendations.router)
    logger.info("✅ Recommendations router registered")
except ImportError as e:
    logger.warning(f"⚠️  Recommendations router not available: {e}")

# Import settings system routers (integrations, backup, communication, roles)
try:
    from app.api import integrations, backup, data_export, communication_settings, roles
    app.include_router(integrations.router)
    app.include_router(backup.router)
    app.include_router(data_export.router)
    app.include_router(communication_settings.router)
    app.include_router(roles.router)
    logger.info("✅ Settings system routers (integrations, backup, export, communication, roles) registered")
except ImportError as e:
    logger.warning(f"⚠️  Settings system routers not available: {e}")

# Import i18n router
try:
    from app.api import i18n
    app.include_router(i18n.router)
    logger.info("✅ i18n router registered")
except ImportError as e:
    logger.warning(f"⚠️  i18n router not available: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
