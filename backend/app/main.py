"""FastAPI monolith entrypoint for Tax-Ease Backend v2 - Redesigned API."""

# ============================================================================
# STARTUP VALIDATION (FAIL-FAST) - MUST RUN BEFORE APP INITIALIZATION
# ============================================================================
from backend.app.core.startup import run_all_startup_checks

# RUN CHECKS BEFORE STARTING APPLICATION
# Application exits(1) if ANY check fails
run_all_startup_checks()

# Initialize T1 Validation Engine
from backend.app.services.t1_validation_engine import initialize_validation_engine
initialize_validation_engine()

# ============================================================================
# FASTAPI IMPORTS
# ============================================================================
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Import v2 routes
from backend.app.routes_v2 import auth as auth_v2
from backend.app.routes_v2 import users as users_v2
from backend.app.routes_v2 import filings as filings_v2
from backend.app.routes_v2 import documents as documents_v2
from backend.app.routes_v2 import health as health_v2
from backend.app.routes_v2 import t1_forms as t1_forms_v2
from backend.app.routes_v2 import notifications as notifications_v2
from backend.app.routes_v2.admin import t1_admin as t1_admin_v2
from backend.app.routes import admin_auth

# Import v2 exception handlers
from backend.app.core.errors import (
    APIException, api_exception_handler, validation_exception_handler, generic_exception_handler
)

app = FastAPI(
    title="Tax-Ease Backend API v2",
    version="2.0.0",
    description="Redesigned Tax-Ease API with improved architecture and security"
)

# ============================================================================
# MIDDLEWARE - ORDER MATTERS
# ============================================================================

# CORS (first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit logging middleware (logs all requests/responses)
from backend.app.core.audit import audit_middleware
from starlette.middleware.base import BaseHTTPMiddleware

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await audit_middleware(request, call_next)

app.add_middleware(AuditMiddleware)

# Rate limiting middleware (global limits)
from backend.app.core.rate_limiter import rate_limit_middleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await rate_limit_middleware(request, call_next)

app.add_middleware(RateLimitMiddleware)

# Register v2 exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# New v2 routes (redesigned API)
app.include_router(auth_v2.router, prefix="/api/v1")
app.include_router(users_v2.router, prefix="/api/v1")
app.include_router(filings_v2.router, prefix="/api/v1")
app.include_router(documents_v2.router, prefix="/api/v1")
app.include_router(notifications_v2.router, prefix="/api/v1/notifications")
app.include_router(health_v2.router, prefix="/api/v1")
app.include_router(t1_forms_v2.router)  # Already has /api/v1/t1-forms prefix
app.include_router(t1_admin_v2.router)  # Already has /api/v1/admin prefix
app.include_router(admin_auth.router, prefix="/api/v1")  # Admin authentication


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Checks Redis and database connectivity.
    """
    from backend.app.core.startup import check_redis_health, check_database_health
    
    redis_ok = check_redis_health()
    db_ok = check_database_health()
    
    if redis_ok and db_ok:
        return {
            "status": "healthy",
            "redis": "ok",
            "database": "ok"
        }
    else:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "redis": "ok" if redis_ok else "unavailable",
                "database": "ok" if db_ok else "unavailable"
            }
        )
