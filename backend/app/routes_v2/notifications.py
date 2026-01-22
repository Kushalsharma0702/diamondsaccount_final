"""
Notifications API endpoints
POST /api/v1/notifications/device-tokens - Register FCM device token
GET /api/v1/notifications/device-tokens - List user's device tokens
DELETE /api/v1/notifications/device-tokens/{token_id} - Remove device token
"""
import sys
from pathlib import Path
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import get_db
from backend.app.schemas.notifications import (
    DeviceTokenRegister,
    DeviceTokenResponse,
    DeviceTokenList
)
from backend.app.core.auth import get_current_user, CurrentUser
from database.schemas_v2 import NotificationDeviceToken, DevicePlatform

router = APIRouter(tags=["notifications"])


@router.post(
    "/device-tokens",
    response_model=DeviceTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Register FCM device token",
    description="Register or update an FCM device token for push notifications"
)
async def register_device_token(
    token_data: DeviceTokenRegister,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register or update an FCM device token for the authenticated user.
    
    - If the token already exists, updates it and sets is_active = true
    - If the token is new, creates a new record
    - Always updates last_seen_at to current timestamp
    
    The token is used by the backend to send push notifications via FCM.
    """
    user_id = uuid.UUID(current_user.id)
    
    # Check if token already exists (for any user)
    stmt = select(NotificationDeviceToken).where(
        NotificationDeviceToken.token == token_data.token
    )
    existing_token = db.execute(stmt).scalar_one_or_none()
    
    if existing_token:
        # Update existing token
        existing_token.user_id = user_id  # Reassign to current user if needed
        existing_token.platform = DevicePlatform[token_data.platform.value.upper()]
        existing_token.device_id = token_data.device_id
        existing_token.app_version = token_data.app_version
        existing_token.locale = token_data.locale
        existing_token.is_active = True
        existing_token.last_seen_at = datetime.utcnow()
        existing_token.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_token)
        
        return DeviceTokenResponse(
            id=str(existing_token.id),
            user_id=str(existing_token.user_id),
            token=existing_token.token,
            platform=existing_token.platform.value,
            device_id=existing_token.device_id,
            is_active=existing_token.is_active,
            created_at=existing_token.created_at,
            updated_at=existing_token.updated_at,
            last_seen_at=existing_token.last_seen_at
        )
    else:
        # Create new token
        new_token = NotificationDeviceToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token=token_data.token,
            platform=DevicePlatform[token_data.platform.value.upper()],
            device_id=token_data.device_id,
            app_version=token_data.app_version,
            locale=token_data.locale,
            is_active=True,
            last_seen_at=datetime.utcnow()
        )
        
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        
        return DeviceTokenResponse(
            id=str(new_token.id),
            user_id=str(new_token.user_id),
            token=new_token.token,
            platform=new_token.platform.value,
            device_id=new_token.device_id,
            is_active=new_token.is_active,
            created_at=new_token.created_at,
            updated_at=new_token.updated_at,
            last_seen_at=new_token.last_seen_at
        )


@router.get(
    "/device-tokens",
    response_model=DeviceTokenList,
    status_code=status.HTTP_200_OK,
    summary="List user's device tokens",
    description="Get all registered device tokens for the authenticated user"
)
async def list_device_tokens(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all device tokens registered for the authenticated user.
    """
    user_id = uuid.UUID(current_user.id)
    
    stmt = select(NotificationDeviceToken).where(
        and_(
            NotificationDeviceToken.user_id == user_id,
            NotificationDeviceToken.is_active == True
        )
    ).order_by(NotificationDeviceToken.last_seen_at.desc())
    
    tokens = db.execute(stmt).scalars().all()
    
    token_responses = [
        DeviceTokenResponse(
            id=str(token.id),
            user_id=str(token.user_id),
            token=token.token,
            platform=token.platform.value,
            device_id=token.device_id,
            is_active=token.is_active,
            created_at=token.created_at,
            updated_at=token.updated_at,
            last_seen_at=token.last_seen_at
        )
        for token in tokens
    ]
    
    return DeviceTokenList(
        tokens=token_responses,
        total=len(token_responses)
    )


@router.delete(
    "/device-tokens/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove device token",
    description="Deactivate a device token (soft delete)"
)
async def remove_device_token(
    token_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a device token for the authenticated user.
    This is a soft delete - sets is_active = false.
    """
    user_id = uuid.UUID(current_user.id)
    token_uuid = uuid.UUID(token_id)
    
    stmt = select(NotificationDeviceToken).where(
        and_(
            NotificationDeviceToken.id == token_uuid,
            NotificationDeviceToken.user_id == user_id
        )
    )
    
    token = db.execute(stmt).scalar_one_or_none()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    
    token.is_active = False
    token.updated_at = datetime.utcnow()
    
    db.commit()
    
    return None
