"""
Authentication Service for TaxEase
Handles user registration, login, OTP verification
"""

import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import uuid
import logging

from shared.database import get_db, Database
from shared.models import User, RefreshToken, OTP
from shared.schemas import (
    UserCreate, UserResponse, UserLogin, Token, 
    OTPRequest, OTPVerify, MessageResponse, HealthResponse
)
from shared.auth import JWTManager, create_tokens, get_current_user
from shared.utils import generate_otp, EmailService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TaxEase Auth Service",
    description="Authentication and user management service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await Database.create_tables()
    logger.info("Auth service started successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="auth",
        version="1.0.0"
    )

@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = JWTManager.hash_password(user_data.password)
    
    new_user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        password_hash=hashed_password,
        accept_terms=user_data.accept_terms,
        email_verified=False,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Send welcome email
    await EmailService.send_welcome_email(new_user.email, new_user.first_name)
    
    # Send email verification OTP
    await send_verification_otp(new_user.email, db)
    
    logger.info(f"User registered: {new_user.email}")
    return new_user

@app.post("/api/v1/auth/login", response_model=Token)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens"""
    
    # Get user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not JWTManager.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create tokens
    tokens = create_tokens(str(user.id), user.email)
    
    # Store refresh token in database
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=JWTManager.hash_password(tokens["refresh_token"]),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    
    logger.info(f"User logged in: {user.email}")
    return tokens

@app.post("/api/v1/auth/request-otp", response_model=MessageResponse)
async def request_otp(otp_request: OTPRequest, db: AsyncSession = Depends(get_db)):
    """Request OTP for email verification or password reset"""
    
    if otp_request.purpose == "email_verification":
        await send_verification_otp(otp_request.email, db)
    elif otp_request.purpose == "password_reset":
        await send_password_reset_otp(otp_request.email, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP purpose"
        )
    
    return MessageResponse(message="OTP sent successfully")

@app.post("/api/v1/auth/verify-otp", response_model=MessageResponse)
async def verify_otp(otp_data: OTPVerify, db: AsyncSession = Depends(get_db)):
    """Verify OTP code"""
    
    # Get OTP from database
    result = await db.execute(
        select(OTP).where(
            OTP.email == otp_data.email,
            OTP.code == otp_data.code,
            OTP.purpose == otp_data.purpose,
            OTP.used == False,
            OTP.expires_at > datetime.utcnow()
        )
    )
    otp = result.scalar_one_or_none()
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    otp.used = True
    
    # If email verification, mark user as verified
    if otp_data.purpose == "email_verification":
        user_result = await db.execute(select(User).where(User.email == otp_data.email))
        user = user_result.scalar_one_or_none()
        if user:
            user.email_verified = True
    
    await db.commit()
    
    logger.info(f"OTP verified for {otp_data.email}: {otp_data.purpose}")
    return MessageResponse(message="OTP verified successfully")

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/api/v1/auth/test")
async def test_endpoint():
    """Test endpoint for service health"""
    return {
        "message": "Auth service is running!",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "auth"
    }

# Helper functions
async def send_verification_otp(email: str, db: AsyncSession):
    """Send email verification OTP"""
    
    # Generate OTP
    otp_code = generate_otp()
    
    # Store OTP in database
    otp = OTP(
        email=email,
        code=otp_code,
        purpose="email_verification",
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(otp)
    await db.commit()
    
    # Send email
    await EmailService.send_otp_email(email, otp_code, "email_verification")

async def send_password_reset_otp(email: str, db: AsyncSession):
    """Send password reset OTP"""
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if email exists
        return
    
    # Generate OTP
    otp_code = generate_otp()
    
    # Store OTP in database
    otp = OTP(
        email=email,
        code=otp_code,
        purpose="password_reset",
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(otp)
    await db.commit()
    
    # Send email
    await EmailService.send_otp_email(email, otp_code, "password_reset")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
