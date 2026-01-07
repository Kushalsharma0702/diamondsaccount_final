"""
User profile endpoints for API v2
GET  /api/v1/users/me
PATCH /api/v1/users/me
"""

import sys
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import get_db
from backend.app.schemas.api_v2 import UserResponse, UserUpdate
from backend.app.core.auth import get_current_user, CurrentUser
from database.schemas_v2 import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    
    user = db.query(User).filter(User.id == current_user.id).first()
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "email_verified": user.email_verified,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    data: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if data.first_name:
        user.first_name = data.first_name
    if data.last_name:
        user.last_name = data.last_name
    if data.phone is not None:
        user.phone = data.phone
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "email_verified": user.email_verified,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
