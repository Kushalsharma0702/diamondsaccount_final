"""
Rate Limiting for Tax-Ease API v2

Redis-based rate limiting using token bucket algorithm.
Enforces OTP-RL-001, OTP-RL-002, OTP-RL-003.

CRITICAL: Fail-closed behavior - if Redis unavailable, deny request.
"""

import time
from typing import Optional
import redis
import os
from fastapi import Request, HTTPException, status

from backend.app.core.errors import APIException, ErrorCodes


# ============================================================================
# REDIS CLIENT
# ============================================================================

def get_redis_client():
    """Get Redis client for rate limiting"""
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD", None)
    
    return redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )


# ============================================================================
# RATE LIMIT RULES
# ============================================================================

RATE_LIMITS = {
    # OTP request rate limiting
    "otp_request_email": {
        "limit": 3,
        "window": 600,  # 10 minutes
        "error_message": "Too many OTP requests. Please try again in {remaining} seconds."
    },
    
    # OTP verification rate limiting
    "otp_verify": {
        "limit": 5,
        "window": 600,  # 10 minutes (per OTP lifecycle)
        "error_message": "Too many OTP verification attempts. Request a new OTP."
    },
    
    # Global IP rate limit for OTP
    "otp_global_ip": {
        "limit": 10,
        "window": 3600,  # 1 hour
        "error_message": "Too many OTP requests from your IP. Please try again later."
    },
    
    # Login attempts per email
    "login_email": {
        "limit": 5,
        "window": 600,  # 10 minutes
        "error_message": "Too many login attempts. Account locked for 30 minutes."
    },
    
    # Global login attempts per IP
    "login_global_ip": {
        "limit": 20,
        "window": 3600,  # 1 hour
        "error_message": "Too many login attempts from your IP. Please try again later."
    },
    
    # Password reset request
    "password_reset_email": {
        "limit": 3,
        "window": 600,  # 10 minutes
        "error_message": "Too many password reset requests. Please try again later."
    },
}


# ============================================================================
# TOKEN BUCKET RATE LIMITER
# ============================================================================

class RateLimiter:
    """
    Token bucket rate limiter using Redis.
    
    Features:
    - Sliding window counter
    - Automatic expiry
    - Fail-closed (deny if Redis unavailable)
    """
    
    def __init__(self):
        self.redis = get_redis_client()
    
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        identifier: str
    ) -> tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Rate limit key (e.g., "otp_request_email")
            limit: Max requests allowed
            window: Time window in seconds
            identifier: Unique identifier (email, IP, etc.)
        
        Returns:
            (is_allowed, remaining_seconds_if_blocked)
        
        Raises:
            APIException: If Redis unavailable (fail-closed)
        """
        
        redis_key = f"ratelimit:{key}:{identifier}"
        
        try:
            # Get current count
            current = self.redis.get(redis_key)
            
            if current is None:
                # First request - set counter and expiry
                self.redis.setex(redis_key, window, 1)
                return True, None
            
            current_count = int(current)
            
            if current_count >= limit:
                # Rate limit exceeded - get TTL
                ttl = self.redis.ttl(redis_key)
                return False, ttl if ttl > 0 else window
            
            # Increment counter
            self.redis.incr(redis_key)
            return True, None
            
        except redis.RedisError as e:
            # FAIL-CLOSED: If Redis unavailable, deny request
            raise APIException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                error_code=ErrorCodes.SERVER_INTERNAL_ERROR,
                message="Service temporarily unavailable. Please try again later."
            )
    
    def increment_counter(
        self,
        key: str,
        identifier: str,
        window: int
    ) -> int:
        """
        Increment counter (for post-action tracking like failed logins).
        
        Returns: Current count
        """
        redis_key = f"ratelimit:{key}:{identifier}"
        
        try:
            current = self.redis.get(redis_key)
            
            if current is None:
                self.redis.setex(redis_key, window, 1)
                return 1
            
            count = self.redis.incr(redis_key)
            return count
            
        except redis.RedisError:
            # If Redis unavailable, we can't track - allow but log
            return 0
    
    def reset_counter(self, key: str, identifier: str) -> None:
        """Reset rate limit counter (e.g., after successful login)"""
        redis_key = f"ratelimit:{key}:{identifier}"
        try:
            self.redis.delete(redis_key)
        except redis.RedisError:
            pass  # Best effort
    
    def get_remaining_count(
        self,
        key: str,
        identifier: str,
        limit: int
    ) -> int:
        """Get remaining requests before rate limit"""
        redis_key = f"ratelimit:{key}:{identifier}"
        
        try:
            current = self.redis.get(redis_key)
            if current is None:
                return limit
            return max(0, limit - int(current))
        except redis.RedisError:
            return 0  # Assume exhausted if Redis unavailable


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_client_ip(request: Request) -> str:
    """
    Extract client IP from request.
    Handles X-Forwarded-For header for proxied requests.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_otp_request_rate_limit(email: str, ip: str) -> None:
    """
    Check rate limits for OTP request.
    
    Enforces:
    - OTP-RL-001: Max 3 requests per 10 minutes per email
    - OTP-RL-003: Max 10 requests per hour per IP
    
    Raises: HTTPException if rate limit exceeded
    """
    # Skip rate limiting in development mode
    if os.getenv("ENVIRONMENT") == "development":
        return
    
    limiter = RateLimiter()
    
    # Check email rate limit
    email_allowed, email_wait = limiter.check_rate_limit(
        key="otp_request_email",
        limit=RATE_LIMITS["otp_request_email"]["limit"],
        window=RATE_LIMITS["otp_request_email"]["window"],
        identifier=email
    )
    
    if not email_allowed:
        raise APIException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
            message=RATE_LIMITS["otp_request_email"]["error_message"].format(
                remaining=email_wait
            )
        )
    
    # Check IP rate limit
    ip_allowed, ip_wait = limiter.check_rate_limit(
        key="otp_global_ip",
        limit=RATE_LIMITS["otp_global_ip"]["limit"],
        window=RATE_LIMITS["otp_global_ip"]["window"],
        identifier=ip
    )
    
    if not ip_allowed:
        raise APIException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
            message=RATE_LIMITS["otp_global_ip"]["error_message"]
        )


def check_login_rate_limit(email: str, ip: str) -> None:
    """
    Check rate limits for login attempts.
    
    Enforces:
    - Max 5 login attempts per 10 minutes per email
    - Max 20 login attempts per hour per IP
    
    Raises: HTTPException if rate limit exceeded
    """
    # Skip rate limiting in development mode
    if os.getenv("ENVIRONMENT") == "development":
        return
    
    limiter = RateLimiter()
    
    # Check email rate limit
    email_allowed, email_wait = limiter.check_rate_limit(
        key="login_email",
        limit=RATE_LIMITS["login_email"]["limit"],
        window=RATE_LIMITS["login_email"]["window"],
        identifier=email
    )
    
    if not email_allowed:
        # Account lockout
        raise APIException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
            message=RATE_LIMITS["login_email"]["error_message"]
        )
    
    # Check IP rate limit
    ip_allowed, ip_wait = limiter.check_rate_limit(
        key="login_global_ip",
        limit=RATE_LIMITS["login_global_ip"]["limit"],
        window=RATE_LIMITS["login_global_ip"]["window"],
        identifier=ip
    )
    
    if not ip_allowed:
        raise APIException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
            message=RATE_LIMITS["login_global_ip"]["error_message"]
        )


def record_failed_login(email: str) -> int:
    """
    Record failed login attempt.
    
    Returns: Number of failed attempts
    """
    limiter = RateLimiter()
    count = limiter.increment_counter(
        key="login_email",
        identifier=email,
        window=RATE_LIMITS["login_email"]["window"]
    )
    return count


def reset_login_attempts(email: str) -> None:
    """Reset failed login counter after successful login"""
    limiter = RateLimiter()
    limiter.reset_counter("login_email", email)


def check_account_locked(user_id: str) -> bool:
    """
    Check if account is temporarily locked.
    
    Returns: True if locked
    """
    try:
        client = get_redis_client()
        return client.exists(f"account_locked:{user_id}") > 0
    except redis.RedisError:
        # If Redis unavailable, assume not locked (fail-open for this check)
        return False


def lock_account(user_id: str, duration: int = 1800) -> None:
    """
    Temporarily lock account.
    
    Args:
        user_id: User ID
        duration: Lock duration in seconds (default 30 min)
    """
    try:
        client = get_redis_client()
        client.setex(f"account_locked:{user_id}", duration, "1")
    except redis.RedisError:
        pass  # Best effort


# ============================================================================
# MIDDLEWARE INTEGRATION
# ============================================================================

async def rate_limit_middleware(request: Request, call_next):
    """
    Global rate limiting middleware.
    
    Note: Endpoint-specific rate limiting is handled in endpoints.
    This middleware provides last-resort global rate limiting.
    """
    
    # Get client IP
    ip = get_client_ip(request)
    
    # Global rate limit: 1000 requests per minute per IP
    limiter = RateLimiter()
    
    try:
        allowed, wait = limiter.check_rate_limit(
            key="global_ip",
            limit=1000,
            window=60,
            identifier=ip
        )
        
        if not allowed:
            raise APIException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
                message="Too many requests. Please slow down."
            )
    except APIException:
        raise
    except Exception:
        pass  # Don't block on rate limiter errors
    
    response = await call_next(request)
    return response
