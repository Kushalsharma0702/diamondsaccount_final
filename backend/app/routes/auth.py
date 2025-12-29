"""Dummy auth + static OTP endpoints backed by existing users/otps tables."""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import User, Client
from backend.app.database import get_db
from backend.app.auth.password import hash_password, verify_password
from backend.app.auth.jwt import create_access_token, create_refresh_token
from backend.app.auth.otp import create_otp_record, verify_otp_code

# Load .env from project root
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

router = APIRouter(prefix="/auth", tags=["auth"])

STATIC_OTP = os.getenv("STATIC_OTP", os.getenv("DEVELOPER_OTP", "123456"))


class RegisterRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    password: str
    confirm_password: Optional[str] = None  # Optional - validate if provided
    accept_terms: Optional[bool] = False  # Optional - for frontend compatibility


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class OTPRequest(BaseModel):
    email: EmailStr
    purpose: str


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    code: str
    purpose: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new client user account.
    
    Fields match signup form:
    - first_name, last_name, email, phone, password, confirm_password (optional)
    """
    # Validate password match if confirm_password is provided
    if request.confirm_password and request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Validate password strength (min 6 characters)
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Check if email already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    user = User(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
        password_hash=hash_password(request.password),
        email_verified=False,
        is_active=True,
    )
    db.add(user)
    db.flush()  # Flush to get user.id before creating client

    # Automatically create client record for new user
    year = datetime.utcnow().year
    name = f"{request.first_name} {request.last_name}".strip()
    client = Client(
        user_id=user.id,
        name=name,
        email=request.email,
        phone=request.phone,
        filing_year=year,
        status="documents_pending",
        payment_status="pending",
        total_amount=0.0,
        paid_amount=0.0,
    )
    db.add(client)
    db.commit()
    db.refresh(user)
    db.refresh(client)

    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "client_id": str(client.id),  # Include client ID in response
        "message": "Account created successfully",
    }


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Sign in with email and password.
    
    Fields match signin form:
    - email, password
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    # Ensure client record exists (auto-create if missing)
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        year = datetime.utcnow().year
        name = f"{user.first_name} {user.last_name}".strip()
        if not name:
            name = user.email.split('@')[0]  # Fallback to email username
        
        client = Client(
            user_id=user.id,
            name=name,
            email=user.email,
            phone=user.phone,
            filing_year=year,
            status="documents_pending",
            payment_status="pending",
            total_amount=0.0,
            paid_amount=0.0,
        )
        db.add(client)
        db.commit()

    # Generate JWT tokens
    payload = {"sub": str(user.id), "role": "client", "email": user.email}
    access = create_access_token(payload)
    refresh = create_refresh_token(payload)
    
    return TokenResponse(
        access_token=access, 
        refresh_token=refresh, 
        expires_in=30 * 60
    )


@router.post("/request-otp")
def request_otp(request: OTPRequest, db: Session = Depends(get_db)):
    """Issue a static OTP (123456) and record it in DB for auditing."""
    # create a record but ignore generated code; always use STATIC_OTP
    otp = create_otp_record(db=db, email=request.email, purpose=request.purpose, user_id=None)
    # overwrite stored code to match static OTP so verify_otp_code works
    otp.code = STATIC_OTP
    db.commit()

    return {"message": "OTP sent (static)", "success": True}


@router.post("/verify-otp")
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify static OTP 123456 (universal for all users) and mark user email as verified."""
    # Verify with static OTP support
    ok = verify_otp_code(
        db=db, 
        email=request.email, 
        code=request.code, 
        purpose=request.purpose,
        static_otp=STATIC_OTP
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.email == request.email).first()
    if user:
        user.email_verified = True
        db.commit()

    return {"message": "OTP verified", "success": True}
