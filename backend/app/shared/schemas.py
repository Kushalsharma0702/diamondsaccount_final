"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from uuid import UUID

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    accept_terms: bool = True
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(UserBase):
    id: UUID
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseSchema):
    email: EmailStr
    password: str

# Authentication schemas
class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    id_token: Optional[str] = None  # Cognito ID token

class CognitoToken(BaseSchema):
    """Cognito token response"""
    id_token: str
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int

class TokenRefresh(BaseSchema):
    refresh_token: str

class OTPRequest(BaseSchema):
    email: EmailStr
    purpose: str  # email_verification, password_reset

class OTPVerify(BaseSchema):
    email: EmailStr
    code: str
    purpose: str
    
    @validator('code')
    def normalize_code(cls, v):
        """Normalize OTP code by stripping whitespace"""
        if isinstance(v, str):
            return v.strip()
        return str(v).strip()

# Tax Form schemas
class T1PersonalFormBase(BaseSchema):
    tax_year: int
    sin: Optional[str] = None
    marital_status: Optional[str] = None
    employment_income: Optional[float] = 0.0
    self_employment_income: Optional[float] = 0.0
    investment_income: Optional[float] = 0.0
    other_income: Optional[float] = 0.0
    rrsp_contributions: Optional[float] = 0.0
    charitable_donations: Optional[float] = 0.0

class T1PersonalFormCreate(T1PersonalFormBase):
    pass

class T1PersonalFormUpdate(BaseSchema):
    sin: Optional[str] = None
    marital_status: Optional[str] = None
    employment_income: Optional[float] = None
    self_employment_income: Optional[float] = None
    investment_income: Optional[float] = None
    other_income: Optional[float] = None
    rrsp_contributions: Optional[float] = None
    charitable_donations: Optional[float] = None

class T1PersonalFormResponse(T1PersonalFormBase):
    id: UUID
    user_id: UUID
    status: str
    total_income: float
    federal_tax: float
    provincial_tax: float
    total_tax: float
    refund_or_owing: float
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None

# File schemas
class FileUploadResponse(BaseSchema):
    id: UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    upload_status: str
    created_at: datetime

class FileListResponse(BaseSchema):
    files: List[FileUploadResponse]
    total: int

# Report schemas
class ReportResponse(BaseSchema):
    id: UUID
    report_type: str
    title: str
    status: str
    file_url: Optional[str] = None
    generated_at: Optional[datetime] = None
    created_at: datetime

class ReportRequest(BaseSchema):
    report_type: str
    title: str

# Generic response schemas
class MessageResponse(BaseSchema):
    message: str
    success: bool = True

class HealthResponse(BaseSchema):
    status: str
    timestamp: datetime
    service: str
    version: str

# Error schemas
class ErrorResponse(BaseSchema):
    error: str
    detail: str
    code: Optional[str] = None

# Encrypted File schemas
class EncryptedFileUploadRequest(BaseSchema):
    description: Optional[str] = None

class EncryptedFileUploadResponse(BaseSchema):
    id: UUID
    original_filename: str
    file_type: str
    file_size: int
    is_encrypted: bool
    upload_status: str
    compression_ratio: Optional[float] = None
    encryption_algorithm: Optional[str] = None
    created_at: datetime

class EncryptedFileListResponse(BaseSchema):
    files: List[EncryptedFileUploadResponse]
    total: int

class EncryptedFileDecryptRequest(BaseSchema):
    password: str

class FileDecryptResponse(BaseSchema):
    message: str
    filename: str
    file_size: int
    download_ready: bool = True

class EncryptionSetupRequest(BaseSchema):
    password: str

class EncryptionSetupResponse(BaseSchema):
    message: str
    encryption_enabled: bool
    key_created_at: datetime

class KeyRotationRequest(BaseSchema):
    old_password: str
    new_password: str

class FileStatsResponse(BaseSchema):
    total_files: int
    encrypted_files: int
    total_original_size: int
    total_compressed_size: int
    compression_ratio: float
    encryption_coverage: float
