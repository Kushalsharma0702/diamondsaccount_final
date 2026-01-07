"""Admin authentication endpoints with Redis session management."""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import Admin
from backend.app.database import get_db
from backend.app.auth.password import hash_password, verify_password
from backend.app.auth.jwt import create_access_token, create_refresh_token
from backend.app.utils.redis_session import (
    set_session, get_session, delete_session, refresh_session,
    store_token, revoke_token, is_token_revoked
)

# Load .env from project root
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])
security = HTTPBearer()


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    user: dict
    token: dict
    session_id: str


class AdminRegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = "admin"  # admin or superadmin
    permissions: Optional[list[str]] = None


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login with session management."""
    # Find admin
    admin = db.query(Admin).filter(Admin.email == request.email).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if active
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Verify password
    if not verify_password(request.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    admin.last_login_at = datetime.utcnow()
    db.commit()
    
    # Generate JWT tokens
    payload = {
        "sub": str(admin.id),
        "role": admin.role,
        "email": admin.email,
        "type": "admin"
    }
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    
    # Store token in Redis for revocation tracking
    store_token(access_token, payload, expires_in_seconds=30 * 60)
    
    # Create session in Redis
    session_id = str(uuid4())
    user_data = {
        "user_id": str(admin.id),
        "email": admin.email,
        "name": admin.name,
        "role": admin.role,
        "permissions": admin.permissions or [],
    }
    set_session(session_id, user_data)
    
    return AdminLoginResponse(
        user={
            "id": str(admin.id),
            "email": admin.email,
            "name": admin.name,
            "role": admin.role,
            "permissions": admin.permissions or [],
            "isActive": admin.is_active,
        },
        token={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60,
        },
        session_id=session_id,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def admin_register(request: AdminRegisterRequest, db: Session = Depends(get_db)):
    """Register a new admin (superadmin only)."""
    # Check if email exists
    existing = db.query(Admin).filter(Admin.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create admin
    admin = Admin(
        email=request.email,
        name=request.name,
        password_hash=hash_password(request.password),
        role=request.role,
        permissions=request.permissions or [],
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return {
        "id": str(admin.id),
        "email": admin.email,
        "name": admin.name,
        "role": admin.role,
        "message": "Admin created successfully",
    }


@router.get("/me")
def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Get current admin user."""
    token = credentials.credentials
    
    # Check if token is revoked
    if is_token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    # Decode token to get admin ID
    from backend.app.auth.jwt import verify_token
    payload = verify_token(token)
    if not payload or payload.get("type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    admin_id = payload.get("sub")
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {
        "id": str(admin.id),
        "email": admin.email,
        "name": admin.name,
        "role": admin.role,
        "permissions": admin.permissions or [],
        "isActive": admin.is_active,
        "lastLoginAt": admin.last_login_at.isoformat() if admin.last_login_at else None,
    }


@router.post("/logout")
def admin_logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session_id: Optional[str] = None,
):
    """Logout admin and revoke tokens."""
    token = credentials.credentials
    
    # Revoke token
    revoke_token(token)
    
    # Delete session if provided
    if session_id:
        delete_session(session_id)
    
    return {"message": "Logged out successfully"}


@router.post("/refresh-session")
def refresh_admin_session(session_id: str):
    """Refresh admin session."""
    if refresh_session(session_id):
        return {"message": "Session refreshed"}
    raise HTTPException(status_code=404, detail="Session not found")







