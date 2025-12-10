"""
Main FastAPI application
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_cache import cache
from app.api.v1 import api_router
from app.middleware.cors_middleware import ProductionCORSMiddleware

# Logging
import logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    await init_db()
    await cache.connect()
    yield
    # Shutdown
    await cache.disconnect()
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Tax Hub Dashboard Backend API",
    lifespan=lifespan
)

# CORS Configuration - PRODUCTION READY
# Determine if we're in development mode
is_development = os.getenv("ENVIRONMENT", "development").lower() in ["development", "dev", "local"]

# Build allowed origins from settings
allowed_origins = []
if isinstance(settings.CORS_ORIGINS, str):
    allowed_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
elif isinstance(settings.CORS_ORIGINS, list):
    allowed_origins = list(settings.CORS_ORIGINS)

# Ensure localhost:8080 is always included for admin dashboard
if "http://localhost:8080" not in allowed_origins:
    allowed_origins.append("http://localhost:8080")
if "http://127.0.0.1:8080" not in allowed_origins:
    allowed_origins.append("http://127.0.0.1:8080")

logger.info(f"🌍 Environment: {'DEVELOPMENT' if is_development else 'PRODUCTION'}")
logger.info(f"📍 Allowed CORS origins: {len(allowed_origins)} configured")

# Add ProductionCORSMiddleware - This MUST be added BEFORE any routes
# Using BaseHTTPMiddleware ensures it runs first and handles OPTIONS requests
app.add_middleware(
    ProductionCORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=["content-type", "authorization", "x-requested-with", "accept"],
    allow_credentials=True,
    max_age=3600,
    is_development=is_development,
)

# Include API router (after CORS middleware)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tax Hub Dashboard API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "cors": {
            "development_mode": is_development,
            "allowed_origins_count": len(allowed_origins),
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "redis": "connected" if cache._client else "disconnected"
    }
