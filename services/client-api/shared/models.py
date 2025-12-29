"""
Database models for TaxEase application
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    accept_terms = Column(Boolean, default=False)
    
    # Encryption keys for end-to-end encryption
    public_key = Column(Text, nullable=True)  # RSA public key for document encryption
    private_key = Column(Text, nullable=True)  # Encrypted RSA private key
    key_salt = Column(String(255), nullable=True)  # Salt for key derivation
    key_created_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    tax_forms = relationship("T1PersonalForm", back_populates="user")
    t1_forms_main = relationship("T1FormMain", back_populates="user")  # New T1 form structure
    files = relationship("File", back_populates="user")
    reports = relationship("Report", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class RefreshToken(Base):
    """JWT refresh token storage"""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_revoked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

class OTP(Base):
    """One-time password for verification"""
    __tablename__ = "otps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False)  # email_verification, password_reset
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used = Column(Boolean, default=False)

class T1PersonalForm(Base):
    """Enhanced Canadian T1 Personal Tax Form with Encryption Support"""
    __tablename__ = "t1_personal_forms"
    
    id = Column(String(50), primary_key=True)  # Format: T1_{timestamp}
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tax_year = Column(Integer, nullable=False)
    status = Column(String(20), default="draft")  # draft, in_progress, review, submitted, processed
    
    # Encrypted form data (contains all the detailed form information)
    encrypted_form_data = Column(LargeBinary, nullable=True)  # Encrypted + compressed form JSON
    encryption_metadata = Column(Text, nullable=True)  # JSON metadata about encryption
    is_encrypted = Column(Boolean, default=True)
    
    # Basic personal information for indexing/searching (unencrypted)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    sin_encrypted = Column(Boolean, default=True)  # SIN is in encrypted data
    
    # Form completion flags for quick filtering
    has_foreign_property = Column(Boolean, default=False)
    has_medical_expenses = Column(Boolean, default=False)
    has_charitable_donations = Column(Boolean, default=False)
    has_moving_expenses = Column(Boolean, default=False)
    is_self_employed = Column(Boolean, default=False)
    is_first_home_buyer = Column(Boolean, default=False)
    is_first_time_filer = Column(Boolean, default=False)
    
    # Legacy fields for backward compatibility (calculated from encrypted data)
    employment_income = Column(Float, default=0.0)
    self_employment_income = Column(Float, default=0.0)
    investment_income = Column(Float, default=0.0)
    other_income = Column(Float, default=0.0)
    total_income = Column(Float, default=0.0)
    
    # Deductions (calculated from encrypted data)
    rrsp_contributions = Column(Float, default=0.0)
    charitable_donations = Column(Float, default=0.0)
    
    # Tax Calculations (calculated from encrypted data)
    federal_tax = Column(Float, default=0.0)
    provincial_tax = Column(Float, default=0.0)
    total_tax = Column(Float, default=0.0)
    refund_or_owing = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tax_forms")

class File(Base):
    """File storage metadata with end-to-end encryption"""
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Original file size
    
    # Encryption metadata
    encrypted_data = Column(LargeBinary, nullable=True)  # Encrypted + compressed file data
    encrypted_key = Column(Text, nullable=True)  # RSA encrypted AES key
    encryption_metadata = Column(Text, nullable=True)  # JSON metadata about encryption
    is_encrypted = Column(Boolean, default=True)
    
    # Legacy S3 support (for non-encrypted files)
    s3_bucket = Column(String(100), nullable=True)
    s3_key = Column(String(500), nullable=True)
    
    upload_status = Column(String(20), default="pending")  # pending, uploaded, failed, encrypted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="files")

class Report(Base):
    """Generated reports"""
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # tax_summary, t1_form, notice_of_assessment
    title = Column(String(255), nullable=False)
    status = Column(String(20), default="generating")  # generating, ready, failed
    file_url = Column(String(500))
    generated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reports")

class EncryptedDocument(Base):
    """Separate storage for encrypted documents (for large files)"""
    __tablename__ = "encrypted_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)  # Large encrypted data
    checksum = Column(String(64), nullable=False)  # SHA256 checksum
    compression_ratio = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    """Audit trail for user actions"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
