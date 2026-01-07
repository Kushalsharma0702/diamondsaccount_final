"""
Pydantic schemas for API v2 request/response models
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import re


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class OTPRequest(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    purpose: str = Field(
        ..., 
        pattern='^(email_verification|password_reset)$',
        examples=["email_verification"],
        description="Must be 'email_verification' or 'password_reset'"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "user@example.com",
                "purpose": "email_verification"
            }]
        }
    }


class OTPVerify(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    code: str = Field(
        ..., 
        min_length=6, 
        max_length=6, 
        examples=["123456"],
        description="6-digit OTP code"
    )
    purpose: str = Field(
        ..., 
        pattern='^(email_verification|password_reset)$',
        examples=["email_verification"],
        description="Must be 'email_verification' or 'password_reset'"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "user@example.com",
                "code": "123456",
                "purpose": "email_verification"
            }]
        }
    }


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "user@example.com"
            }]
        }
    }


class PasswordResetConfirm(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    code: str = Field(
        ..., 
        min_length=6, 
        max_length=6,
        examples=["123456"],
        description="6-digit OTP code from email"
    )
    new_password: str = Field(
        ..., 
        min_length=8,
        examples=["NewSecure@123"],
        description="New password (min 8 chars)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "user@example.com",
                "code": "123456",
                "new_password": "NewSecure@123"
            }]
        }
    }


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: str
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None


# ============================================================================
# FILING SCHEMAS
# ============================================================================

class FilingBase(BaseModel):
    filing_year: int = Field(ge=2020, le=2030)


class FilingCreate(FilingBase):
    pass


class FilingResponse(FilingBase):
    id: str
    user_id: str
    status: str
    total_fee: Optional[float] = None
    paid_amount: float = 0.0
    payment_status: str
    email_thread_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    assigned_admin: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class FilingStatusUpdate(BaseModel):
    status: str = Field(
        pattern='^(documents_pending|submitted|payment_request_sent|payment_completed|in_preparation|awaiting_approval|filed|completed|cancelled)$'
    )


class FilingFeeUpdate(BaseModel):
    total_fee: float = Field(ge=0)


class FilingAssignmentUpdate(BaseModel):
    admin_id: str


# ============================================================================
# T1 FORM SCHEMAS
# ============================================================================

class T1FormCreate(BaseModel):
    filing_id: str
    form_data: Dict[str, Any]


class T1FormUpdate(BaseModel):
    form_data: Dict[str, Any]


class T1FormResponse(BaseModel):
    id: str
    filing_id: str
    status: str
    form_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT SCHEMAS
# ============================================================================

class DocumentUploadResponse(BaseModel):
    id: str
    filing_id: str
    name: str
    original_filename: str
    file_type: str
    file_size: int
    section_name: Optional[str] = None
    document_type: str
    status: str
    uploaded_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentResponse(DocumentUploadResponse):
    notes: Optional[str] = None
    updated_at: datetime


class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    notes: Optional[str] = None


class DocumentStatusUpdate(BaseModel):
    status: str = Field(pattern='^(pending|complete|missing|approved|reupload_requested)$')
    notes: Optional[str] = None


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    filing_id: Optional[str] = None
    type: str
    title: str
    message: str
    is_read: bool
    related_entity_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationUnreadCount(BaseModel):
    unread_count: int


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = Field(default="desc", pattern='^(asc|desc)$')


class PaginatedResponse(BaseModel):
    data: List[Any]
    meta: Dict[str, Any]


# ============================================================================
# COMMON RESPONSES
# ============================================================================

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "2.0.0"


class HealthReadyResponse(BaseModel):
    status: str
    checks: Dict[str, str]
