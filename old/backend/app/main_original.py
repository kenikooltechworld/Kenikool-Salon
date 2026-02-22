"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Always use INFO level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set pymongo to WARNING to reduce noise
logging.getLogger('pymongo').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("=" * 80)
    logger.info("BACKEND SERVER STARTING")
    logger.info("=" * 80)
    
    # Skip database connection in test mode (tests handle this separately)
    if not settings.TESTING:
        logger.info("Attempting database connection in background...")
        # Don't block startup on database connection
        import threading
        def connect_db_async():
            try:
                Database.connect_db()
                logger.info("✅ Database connected successfully")
            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                logger.warning("⚠️  Server running in LIMITED MODE")
        
        thread = threading.Thread(target=connect_db_async, daemon=True)
        thread.start()
        logger.info("✅ Application started (database connecting in background)")
    else:
        logger.info("Test mode: Skipping database connection")
    
    logger.info("=" * 80)
    logger.info("✅ SERVER READY ON http://0.0.0.0:8000")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add comprehensive request/response logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests and responses with full details"""
    import json
    
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
from app.api import exceptions as exceptions_module
exceptions_module.register_exception_handlers(app)

# Import API router directly (lazy-loaded)
from app.api import router as api_router
app.include_router(api_router, prefix="/api")

# Import other routers directly
from app.api import webhooks, upload, websocket
app.include_router(webhooks.router)
app.include_router(upload.router)
app.include_router(websocket.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
