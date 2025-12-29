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
from sqlalchemy import text
from datetime import datetime
from sqlalchemy import select
from app.models.admin_user import AdminUser
from app.core.auth import get_password_hash
from app.core.database import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    await init_db()

    # Seed a default superadmin if none exists (dev convenience)
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(AdminUser).limit(1))
            existing = result.scalar_one_or_none()
            if not existing:
                default_email = os.getenv("ADMIN_EMAIL", "admin@taxease.com")
                default_password = os.getenv("ADMIN_PASSWORD", "Admin123!")
                admin = AdminUser(
                    name="Super Admin",
                    email=default_email.lower(),
                    password_hash=get_password_hash(default_password),
                    role="superadmin",
                    permissions=[],  # superadmin bypasses permissions
                    is_active=True,
                )
                session.add(admin)
                await session.commit()
                logger.info("✅ Seeded default superadmin for admin dashboard")
                logger.info(f"   Email: {default_email}")
                logger.info(f"   Password: {default_password}")
    except Exception as e:
        logger.warning(f"⚠️ Could not seed default superadmin: {e}")

    # Ensure real client records exist for ALL registered users (same Postgres as client-api)
    try:
        from app.core.database import engine
        current_year = datetime.utcnow().year
        async with engine.begin() as conn:
            # Upsert-like insert (id aligns to users.id so filters match files/forms)
            await conn.execute(
                text(
                    """
                    INSERT INTO clients (
                        id, name, email, phone, filing_year, status, payment_status,
                        total_amount, paid_amount, created_at, updated_at
                    )
                    SELECT
                        u.id,
                        TRIM(CONCAT(u.first_name, ' ', u.last_name)) AS name,
                        LOWER(u.email) AS email,
                        u.phone,
                        :year AS filing_year,
                        'documents_pending' AS status,
                        'pending' AS payment_status,
                        0.0 AS total_amount,
                        0.0 AS paid_amount,
                        NOW() AS created_at,
                        NOW() AS updated_at
                    FROM users u
                    LEFT JOIN clients c
                        ON LOWER(c.email) = LOWER(u.email) AND c.filing_year = :year
                    WHERE c.id IS NULL
                    """
                ),
                {"year": current_year},
            )
        logger.info("✅ Admin sync: ensured clients exist for users")
    except Exception as e:
        logger.warning(f"⚠️ Admin sync: could not auto-create clients from users: {e}")
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
