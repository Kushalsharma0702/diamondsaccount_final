"""
Authentication endpoints for API v2
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
POST /api/v1/auth/otp/request
POST /api/v1/auth/otp/verify
POST /api/v1/auth/password/reset-request
POST /api/v1/auth/password/reset-confirm
"""

import sys
import time
from pathlib import Path
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import get_db
from backend.app.schemas.api_v2 import (
    UserRegister, UserLogin, TokenResponse,
    OTPRequest, OTPVerify, PasswordResetRequest, PasswordResetConfirm,
    SuccessResponse
)
from backend.app.core.auth import (
    create_access_token, create_refresh_token, blacklist_token,
    generate_otp, store_otp, verify_otp, get_current_user, CurrentUser,
    JWT_ACCESS_EXPIRY, JWT_SECRET, redis_client
)
from backend.app.core.errors import (
    AuthenticationError, ValidationError, ResourceConflictError,
    ErrorCodes, invalid_email_error, weak_password_error
)
from backend.app.core.rate_limiter import (
    check_otp_request_rate_limit,
    check_login_rate_limit,
    record_failed_login,
    reset_login_attempts,
    get_client_ip
)
from backend.app.core.audit import (
    log_authentication_failure,
    get_client_ip as audit_get_ip
)
from database.schemas_v2 import User
from backend.app.auth.password import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register new user account"""
    
    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ResourceConflictError(
            error_code=ErrorCodes.RESOURCE_ALREADY_EXISTS,
            message="Email already registered"
        )
    
    # Hash password
    password_hash = hash_password(data.password)
    
    # Create user
    user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        password_hash=password_hash,
        email_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(str(user.id), user.email, "user")
    refresh_token = create_refresh_token(str(user.id))
    
    # Send verification email (TODO)
    otp_code = generate_otp()
    store_otp(user.email, "email_verification", otp_code)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWT_ACCESS_EXPIRY
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login with email and password"""
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # RATE LIMITING - Enforces max 5 login attempts per 10 minutes
    check_login_rate_limit(email=data.email, ip=client_ip)
    
    # Find user
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # Log failed attempt
        log_authentication_failure(
            user_id=None,
            email=data.email,
            reason="User not found",
            ip_address=client_ip,
            endpoint="/api/v1/auth/login"
        )
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_INVALID_CREDENTIALS,
            message="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(data.password, user.password_hash):
        # Record failed login attempt
        count = record_failed_login(data.email)
        
        # Log failed attempt
        log_authentication_failure(
            user_id=str(user.id),
            email=data.email,
            reason="Invalid password",
            ip_address=client_ip,
            endpoint="/api/v1/auth/login"
        )
        # Log failed attempt
        log_authentication_failure(
            user_id=str(user.id),
            email=data.email,
            reason="Invalid password",
            ip_address=client_ip,
            endpoint="/api/v1/auth/login"
        )
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_INVALID_CREDENTIALS,
            message="Invalid email or password"
        )
    
    # Check if account is active
    if not user.is_active:
        log_authentication_failure(
            user_id=str(user.id),
            email=data.email,
            reason="Account inactive",
            ip_address=client_ip,
            endpoint="/api/v1/auth/login"
        )
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_ACCOUNT_INACTIVE,
            message="Account has been deactivated"
        )
    
    # SUCCESS - Reset failed login counter
    reset_login_attempts(data.email)
    
    # Generate tokens
    access_token = create_access_token(str(user.id), user.email, "user")
    refresh_token = create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWT_ACCESS_EXPIRY
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(request: Request, current_user: CurrentUser = Depends(get_current_user)):
    """
    Logout (blacklist current token).
    Enforces INV-A001: Blacklisted tokens MUST be rejected.
    """
    
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_MISSING_TOKEN,
            message="Authorization header missing"
        )
    
    access_token = auth_header.replace("Bearer ", "").strip()
    
    # Decode token to get expiry
    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
        exp = payload.get("exp")
        ttl = max(int(exp - time.time()), 0)
        
        # Blacklist token in Redis
        if redis_client:
            redis_client.setex(f"blacklist:{access_token}", ttl, "1")
    except Exception as e:
        # If decode fails, still return success (idempotent)
        pass
    
    return SuccessResponse(message="Logged out successfully")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    Enforces INV-A002: Refresh endpoint MUST exist.
    """
    
    # Extract refresh token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_TOKEN_INVALID,
            message="Authorization header missing"
        )
    
    refresh_token_str = auth_header.replace("Bearer ", "").strip()
    
    # Check if token blacklisted
    if redis_client and redis_client.exists(f"blacklist:{refresh_token_str}") > 0:
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_TOKEN_BLACKLISTED,
            message="Token has been revoked"
        )
    
    try:
        payload = jwt.decode(refresh_token_str, JWT_SECRET, algorithms=["HS256"])
        
        if payload.get("type") != "refresh":
            raise AuthenticationError(
                error_code=ErrorCodes.AUTH_TOKEN_INVALID,
                message="Invalid token type"
            )
        
        user_id = payload.get("sub")
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise AuthenticationError(
                error_code=ErrorCodes.AUTH_INVALID_CREDENTIALS,
                message="User not found or inactive"
            )
        
        # Generate new access token
        new_access_token = create_access_token(str(user.id), user.email, "user")
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token_str,  # Keep same refresh token
            expires_in=JWT_ACCESS_EXPIRY
        )
        
    except JWTError as e:
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_TOKEN_INVALID,
            message="Invalid or expired refresh token"
        )


@router.post("/otp/request", response_model=SuccessResponse)
async def request_otp(data: OTPRequest, request: Request, db: Session = Depends(get_db)):
    """Request OTP for email verification or password reset"""
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # RATE LIMITING - Enforces OTP-RL-001 and OTP-RL-003
    # Max 3 requests per 10 min per email, Max 10 requests per hour per IP
    check_otp_request_rate_limit(email=data.email, ip=client_ip)
    
    # Check if user exists (for password reset)
    if data.purpose == "password_reset":
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            # Don't reveal if email exists
            return SuccessResponse(
                message="If the email exists, an OTP has been sent"
            )
    
    # Generate and store OTP
    otp_code = generate_otp()
    store_otp(data.email, data.purpose, otp_code, expiry_seconds=600)
    
    # Send email (TODO)
    print(f"OTP for {data.email} ({data.purpose}): {otp_code}")
    
    return SuccessResponse(
        message="OTP sent to email"
    )


@router.post("/otp/verify", response_model=SuccessResponse)
async def verify_otp_endpoint(request: Request, data: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP code"""
    
    # DEBUG: Log request body for troubleshooting
    import logging
    logger = logging.getLogger("auth")
    try:
        body = await request.json()
        logger.info(f"OTP_VERIFY_REQUEST: {body}")
    except:
        pass
    
    # Verify OTP
    is_valid = verify_otp(data.email, data.purpose, data.code)
    
    if not is_valid:
        raise AuthenticationError(
            error_code=ErrorCodes.BUSINESS_OTP_INVALID,
            message="Invalid or expired OTP code"
        )
    
    # If email verification, update user
    if data.purpose == "email_verification":
        user = db.query(User).filter(User.email == data.email).first()
        if user:
            user.email_verified = True
            db.commit()
    
    return SuccessResponse(message="OTP verified successfully")


@router.post("/password/reset-request", response_model=SuccessResponse)
async def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset OTP"""
    
    # Check if user exists
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # Don't reveal if email exists
        return SuccessResponse(
            message="If the email exists, a reset code has been sent"
        )
    
    # Generate and store OTP
    otp_code = generate_otp()
    store_otp(data.email, "password_reset", otp_code)
    
    # Send email (TODO)
    print(f"Password reset OTP for {data.email}: {otp_code}")
    
    return SuccessResponse(
        message="Password reset code sent to email"
    )


@router.post("/password/reset-confirm", response_model=SuccessResponse)
async def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Confirm password reset with OTP"""
    
    # Verify OTP
    is_valid = verify_otp(data.email, "password_reset", data.code)
    
    if not is_valid:
        raise AuthenticationError(
            error_code=ErrorCodes.BUSINESS_OTP_INVALID,
            message="Invalid or expired reset code"
        )
    
    # Find user
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise AuthenticationError(
            error_code=ErrorCodes.AUTH_INVALID_CREDENTIALS,
            message="User not found"
        )
    
    # Update password
    user.password_hash = hash_password(data.new_password)
    db.commit()
    
    return SuccessResponse(message="Password reset successfully")
