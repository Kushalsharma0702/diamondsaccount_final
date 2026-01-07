"""
Authentication middleware for Tax-Ease API v2

JWT validation, token blacklist checking, user context injection
"""

import uuid
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import redis
import os

from backend.app.core.errors import AuthenticationError, ErrorCodes


# ============================================================================
# CONFIGURATION
# ============================================================================

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-min-32-chars-long")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRY = int(os.getenv("JWT_ACCESS_EXPIRY", 3600))  # 1 hour
JWT_REFRESH_EXPIRY = int(os.getenv("JWT_REFRESH_EXPIRY", 2592000))  # 30 days

# Redis for token blacklist
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
    redis_client.ping()
except:
    print("⚠️  Redis not available - token blacklist disabled")
    redis_client = None


# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================

def create_access_token(user_id: str, email: str, role: str = "user") -> str:
    """Create JWT access token"""
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=JWT_ACCESS_EXPIRY)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=JWT_REFRESH_EXPIRY)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_TOKEN_INVALID,
            message=f"Invalid token: {str(e)}"
        )


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    if not redis_client:
        return False
    
    try:
        return redis_client.exists(f"blacklist:{token}") > 0
    except:
        return False


def blacklist_token(token: str, expiry_seconds: int):
    """Add token to blacklist"""
    if not redis_client:
        return
    
    try:
        redis_client.setex(f"blacklist:{token}", expiry_seconds, "1")
    except Exception as e:
        print(f"Failed to blacklist token: {e}")


# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

security = HTTPBearer()


class CurrentUser:
    """Current authenticated user context"""
    
    def __init__(self, user_id: str, email: str, role: str, email_verified: bool = False, permissions: list = None):
        self.id = user_id
        self.user_id = user_id  # Alias for compatibility
        self.email = email
        self.role = role
        self.email_verified = email_verified
        self.permissions = permissions or []
        self.is_admin = role in ["admin", "superadmin"]
        self.is_superadmin = role == "superadmin"


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Extract and validate JWT token, return current user
    
    Raises:
        AuthenticationError: If token is missing, invalid, expired, or revoked
    """
    from sqlalchemy.orm import Session
    from backend.app.database import get_db
    from database.schemas_v2 import User
    
    token = credentials.credentials
    
    # Check if token is blacklisted (INV-A001)
    if is_token_blacklisted(token):
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_TOKEN_REVOKED,
            message="Token has been revoked"
        )
    
    # Decode token
    try:
        payload = decode_token(token)
    except AuthenticationError:
        raise
    
    # Validate token type
    if payload.get("type") != "access":
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_TOKEN_INVALID,
            message="Invalid token type"
        )
    
    # Validate expiry
    exp = payload.get("exp")
    if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_TOKEN_EXPIRED,
            message="Token has expired"
        )
    
    # Extract user info
    user_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role", "user")
    permissions = payload.get("permissions", [])
    
    if not user_id or not email:
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_TOKEN_INVALID,
            message="Invalid token payload"
        )
    
    # Query database to get email_verified status (required for INV-A010)
    # This adds a DB query but ensures email_verified is always current
    email_verified = False
    try:
        # Get DB from request state (set by dependency injection)
        db_gen = get_db()
        db = next(db_gen)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            email_verified = user.email_verified
            role = user.role  # Always use role from DB (not JWT)
        db_gen.close()
    except Exception:
        # If DB query fails, assume email not verified (fail-closed)
        pass
    
    # Create user context
    user = CurrentUser(
        user_id=user_id,
        email=email,
        role=role,
        email_verified=email_verified,
        permissions=permissions
    )
    
    # Attach to request state
    request.state.user = user
    
    return user


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[CurrentUser]:
    """Get current user if token provided, otherwise None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(request, credentials)
    except AuthenticationError:
        return None


# ============================================================================
# ROLE-BASED AUTHENTICATION
# ============================================================================

async def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require admin or superadmin role"""
    if not current_user.is_admin:
        raise AuthenticationError(
            error_code=ErrorCodes.AUTHZ_ROLE_REQUIRED,
            message="This action requires admin role"
        )
    return current_user


async def require_superadmin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require superadmin role"""
    if not current_user.is_superadmin:
        raise AuthenticationError(
            error_code=ErrorCodes.AUTHZ_ROLE_REQUIRED,
            message="This action requires superadmin role"
        )
    return current_user


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

PUBLIC_ENDPOINTS = [
    "/",
    "/health",
    "/health/ready",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/otp/request",
    "/api/v1/auth/otp/verify",
    "/api/v1/auth/password/reset-request",
    "/api/v1/auth/password/reset-confirm",
]


def is_public_endpoint(path: str) -> bool:
    """Check if endpoint is public"""
    return path in PUBLIC_ENDPOINTS


# ============================================================================
# OTP MANAGEMENT (Redis)
# ============================================================================

def generate_otp(length: int = 6) -> str:
    """Generate random numeric OTP"""
    import secrets
    import string
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def store_otp(email: str, purpose: str, code: str, expiry_seconds: int = 600):
    """Store OTP in Redis (10 min expiry)"""
    if not redis_client:
        raise Exception("Redis not available")
    
    key = f"otp:{email}:{purpose}"
    data = {
        "code": code,
        "expires_at": (datetime.utcnow() + timedelta(seconds=expiry_seconds)).isoformat(),
        "attempts": 0
    }
    redis_client.setex(key, expiry_seconds, str(data))


def verify_otp(email: str, purpose: str, code: str) -> bool:
    """Verify OTP code"""
    if not redis_client:
        return False
    
    key = f"otp:{email}:{purpose}"
    stored_data = redis_client.get(key)
    
    if not stored_data:
        return False
    
    import ast
    data = ast.literal_eval(stored_data)
    
    # Check expiry
    expires_at = datetime.fromisoformat(data["expires_at"])
    if datetime.utcnow() > expires_at:
        redis_client.delete(key)
        return False
    
    # Check code
    if data["code"] != code:
        # Increment attempts
        data["attempts"] += 1
        if data["attempts"] >= 5:
            redis_client.delete(key)
        return False
    
    # Valid - delete OTP
    redis_client.delete(key)
    return True
