"""
Pydantic schemas for notifications and device token registration
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import datetime


class DevicePlatform(str, Enum):
    """Device platform types"""
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    MACOS = "macos"
    WINDOWS = "windows"
    LINUX = "linux"


class DeviceTokenRegister(BaseModel):
    """Request schema for registering device token"""
    token: str = Field(..., description="FCM device token", min_length=10, max_length=500)
    platform: DevicePlatform = Field(..., description="Device platform")
    device_id: Optional[str] = Field(None, description="Optional stable device identifier", max_length=255)
    app_version: Optional[str] = Field(None, description="App version", max_length=50)
    locale: Optional[str] = Field(None, description="Device locale (e.g., en_US)", max_length=10)
    
    @validator('token')
    def validate_token(cls, v):
        """Validate token is not empty after stripping"""
        if not v or not v.strip():
            raise ValueError('Token cannot be empty')
        return v.strip()


class DeviceTokenResponse(BaseModel):
    """Response schema for device token registration"""
    id: str
    user_id: str
    token: str
    platform: str
    device_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_seen_at: datetime
    
    class Config:
        from_attributes = True


class DeviceTokenList(BaseModel):
    """List of device tokens for a user"""
    tokens: list[DeviceTokenResponse]
    total: int
