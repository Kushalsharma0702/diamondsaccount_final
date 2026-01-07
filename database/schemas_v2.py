"""
PostgreSQL Schema for Tax-Ease API v2 (Redesigned)

Design Principles:
- Simplified entity model: User → Filing → T1Form
- JSONB for flexible tax form data
- Email-first communication (no chat)
- Role-based authorization
- Audit logging for sensitive operations
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey,
    Index, JSON, Date, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class FilingStatus(str, enum.Enum):
    """Filing status workflow"""
    DOCUMENTS_PENDING = "documents_pending"
    SUBMITTED = "submitted"
    PAYMENT_REQUEST_SENT = "payment_request_sent"
    PAYMENT_COMPLETED = "payment_completed"
    IN_PREPARATION = "in_preparation"
    AWAITING_APPROVAL = "awaiting_approval"
    FILED = "filed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment status (derived)"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"


class DocumentStatus(str, enum.Enum):
    """Document status"""
    PENDING = "pending"
    COMPLETE = "complete"
    MISSING = "missing"
    APPROVED = "approved"
    REUPLOAD_REQUESTED = "reupload_requested"


class T1FormStatus(str, enum.Enum):
    """T1 form status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"


class NotificationType(str, enum.Enum):
    """Notification types"""
    DOCUMENT_REQUEST = "document_request"
    PAYMENT_REQUEST = "payment_request"
    STATUS_UPDATE = "status_update"
    GENERAL = "general"


# ============================================================================
# CORE TABLES
# ============================================================================

class User(Base):
    """User accounts (client users)"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    filings = relationship("Filing", back_populates="user", cascade="all, delete-orphan")


class Admin(Base):
    """Admin users (admin and superadmin)"""
    __tablename__ = "admins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="admin")  # admin, superadmin
    permissions = Column(JSON, nullable=False, default=list)  # Array of permission strings
    avatar = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    assigned_filings = relationship("AdminFilingAssignment", back_populates="admin", cascade="all, delete-orphan")
    created_payments = relationship("Payment", back_populates="created_by_admin", foreign_keys="Payment.created_by_id")
    created_notifications = relationship("Notification", back_populates="created_by_admin", foreign_keys="Notification.created_by_id")
    audit_logs = relationship("AuditLog", back_populates="performed_by", foreign_keys="AuditLog.performed_by_id")


class Filing(Base):
    """Filing records (one per user per tax year)"""
    __tablename__ = "filings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    filing_year = Column(Integer, nullable=False, index=True)
    
    status = Column(String(50), nullable=False, default=FilingStatus.DOCUMENTS_PENDING.value, index=True)
    total_fee = Column(Float, nullable=True)  # Set by admin
    
    # Email thread ID for all communications related to this filing
    email_thread_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="filings")
    admin_assignments = relationship("AdminFilingAssignment", back_populates="filing", cascade="all, delete-orphan")
    t1_forms = relationship("T1Form", back_populates="filing", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="filing", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="filing", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="filing", cascade="all, delete-orphan")
    timeline_events = relationship("FilingTimeline", back_populates="filing", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_filing_user_year', 'user_id', 'filing_year', unique=True),
        Index('idx_filing_status', 'status'),
    )


class AdminFilingAssignment(Base):
    """Admin assignments to filings"""
    __tablename__ = "admin_filing_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=False, index=True)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    admin = relationship("Admin", back_populates="assigned_filings")
    filing = relationship("Filing", back_populates="admin_assignments")
    
    # Unique constraint
    __table_args__ = (
        Index('idx_admin_filing_unique', 'admin_id', 'filing_id', unique=True),
    )


class T1Form(Base):
    """T1 tax form (one per filing, JSONB for flexibility)"""
    __tablename__ = "t1_forms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False, index=True)
    
    status = Column(String(20), nullable=False, default=T1FormStatus.DRAFT.value, index=True)
    
    # JSONB for complete form data (matches Flutter frontend structure)
    form_data = Column(JSONB, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    filing = relationship("Filing", back_populates="t1_forms")
    
    # Indexes
    __table_args__ = (
        Index('idx_t1_form_filing', 'filing_id'),
        Index('idx_t1_form_data', 'form_data', postgresql_using='gin'),
    )


class Document(Base):
    """Documents uploaded by users"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False, index=True)
    
    # Metadata
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)  # Encrypted file path
    
    # Encryption
    encrypted = Column(Boolean, default=True, nullable=False)
    encryption_key_hash = Column(String(255), nullable=True)
    
    # Organization
    section_name = Column(String(100), nullable=True, index=True)
    document_type = Column(String(100), nullable=False)
    
    status = Column(String(20), nullable=False, default=DocumentStatus.PENDING.value, index=True)
    notes = Column(Text, nullable=True)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    filing = relationship("Filing", back_populates="documents")
    
    # Indexes
    __table_args__ = (
        Index('idx_document_filing', 'filing_id'),
        Index('idx_document_status', 'status'),
    )


class Payment(Base):
    """Payment records (append-only)"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False, index=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    
    # Idempotency
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    filing = relationship("Filing", back_populates="payments")
    created_by_admin = relationship("Admin", back_populates="created_payments", foreign_keys=[created_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_filing', 'filing_id'),
    )


class Notification(Base):
    """In-app notifications (pointers to email)"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=True, index=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Related entity
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    related_entity_type = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    filing = relationship("Filing", back_populates="notifications")
    created_by_admin = relationship("Admin", back_populates="created_notifications", foreign_keys=[created_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_user_read', 'user_id', 'is_read'),
        Index('idx_notification_type', 'type'),
    )


class FilingTimeline(Base):
    """Timeline of events for a filing"""
    __tablename__ = "filing_timeline"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey("filings.id"), nullable=False, index=True)
    
    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    actor_type = Column(String(20), nullable=False)  # user, admin, system
    actor_id = Column(UUID(as_uuid=True), nullable=True)
    actor_name = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    filing = relationship("Filing", back_populates="timeline_events")
    
    # Indexes
    __table_args__ = (
        Index('idx_timeline_filing_created', 'filing_id', 'created_at'),
    )


class AuditLog(Base):
    """Audit trail for sensitive operations"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    performed_by_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    performed_by_name = Column(String(255), nullable=True)
    performed_by_email = Column(String(255), nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    performed_by = relationship("Admin", back_populates="audit_logs", foreign_keys=[performed_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_timestamp', 'timestamp'),
    )


# ============================================================================
# T1 PERSONAL TAX FORM TABLES
# ============================================================================

class T1FormStatus(str, enum.Enum):
    """T1 form status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"


class T1Form(Base):
    """
    T1 Personal Tax Form - one per filing
    Stores state machine, locking mechanism, and completion tracking
    """
    __tablename__ = "t1_forms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filing_id = Column(UUID(as_uuid=True), ForeignKey('filings.id', ondelete='CASCADE'), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(20), nullable=False, default='draft')
    is_locked = Column(Boolean, nullable=False, default=False)
    completion_percentage = Column(Integer, nullable=False, default=0)
    last_saved_step_id = Column(String(50), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('admins.id'), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    filing = relationship("Filing", backref="t1_form")
    answers = relationship("T1Answer", back_populates="t1_form", cascade="all, delete-orphan")
    sections_progress = relationship("T1SectionProgress", back_populates="t1_form", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_t1_forms_filing_id', 'filing_id'),
        Index('idx_t1_forms_user_id', 'user_id'),
        Index('idx_t1_forms_status', 'status'),
        {'extend_existing': True}
    )


class T1Answer(Base):
    """
    T1 Answers - normalized key-value storage with polymorphic values
    Field keys match T1Structure.json exactly (e.g., "personalInfo.firstName")
    """
    __tablename__ = "t1_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    t1_form_id = Column(UUID(as_uuid=True), ForeignKey('t1_forms.id', ondelete='CASCADE'), nullable=False)
    field_key = Column(String(200), nullable=False)
    value_boolean = Column(Boolean, nullable=True)
    value_text = Column(Text, nullable=True)
    value_numeric = Column(Float, nullable=True)
    value_date = Column(Date, nullable=True)
    value_array = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    t1_form = relationship("T1Form", back_populates="answers")

    __table_args__ = (
        Index('idx_t1_answers_form_id', 't1_form_id'),
        Index('idx_t1_answers_field_key', 'field_key'),
        Index('idx_t1_answers_array_gin', 'value_array', postgresql_using='gin'),
        {'extend_existing': True}
    )


class T1SectionProgress(Base):
    """
    T1 Sections Progress - tracks completion and review status per step/section
    Used for admin dashboard progress tracking
    """
    __tablename__ = "t1_sections_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    t1_form_id = Column(UUID(as_uuid=True), ForeignKey('t1_forms.id', ondelete='CASCADE'), nullable=False)
    step_id = Column(String(50), nullable=False)
    section_id = Column(String(100), nullable=False)
    is_reviewed = Column(Boolean, nullable=False, default=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('admins.id'), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    t1_form = relationship("T1Form", back_populates="sections_progress")

    __table_args__ = (
        Index('idx_t1_sections_progress_t1_form_id', 't1_form_id'),
        Index('idx_t1_sections_progress_reviewed_by', 'reviewed_by'),
        {'extend_existing': True}
    )

    __table_args__ = (
        Index('idx_t1_sections_progress_form_id', 't1_form_id'),
        Index('idx_t1_sections_progress_reviewed', 'is_reviewed'),
        {'extend_existing': True}
    )


class EmailThreadStatus(str, enum.Enum):
    """Email thread status"""
    OPEN = "open"
    CLOSED = "closed"


class EmailThread(Base):
    """
    Email Threads - thread-based email communication between users and admins
    """
    __tablename__ = "email_threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(String(100), nullable=False, unique=True)
    t1_form_id = Column(UUID(as_uuid=True), ForeignKey('t1_forms.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subject = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default='open')
    context_field_key = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    messages = relationship("EmailMessage", back_populates="thread", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_email_threads_thread_id', 'thread_id'),
        Index('idx_email_threads_t1_form_id', 't1_form_id'),
        Index('idx_email_threads_user_id', 'user_id'),
        Index('idx_email_threads_last_message_at', 'last_message_at'),
        {'extend_existing': True}
    )


class SenderType(str, enum.Enum):
    """Email sender type"""
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"


class MessageType(str, enum.Enum):
    """Email message type"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    SYSTEM = "system"


class EmailMessage(Base):
    """
    Email Messages - individual messages within a thread
    """
    __tablename__ = "email_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(String(100), ForeignKey('email_threads.thread_id', ondelete='CASCADE'), nullable=False)
    sender_type = Column(String(10), nullable=False)
    sender_id = Column(UUID(as_uuid=True), nullable=False)
    sender_name = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False)
    message_type = Column(String(20), nullable=False, default='message')
    message_body = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    thread = relationship("EmailThread", back_populates="messages")

    __table_args__ = (
        Index('idx_email_messages_thread_id', 'thread_id'),
        Index('idx_email_messages_sender_id', 'sender_id'),
        Index('idx_email_messages_created_at', 'created_at'),
        Index('idx_email_messages_is_read', 'is_read'),
        {'extend_existing': True}
    )


# ============================================================================
# MIGRATION NOTES
# ============================================================================
"""
DEPRECATED TABLES (to be removed after migration):
- clients → filings (renamed)
- tax_returns → t1_forms (renamed, simplified)
- tax_sections → removed (stored in t1_forms.form_data JSONB)
- chat_messages → removed (email-first model)
- refresh_tokens → removed (use Redis)
- otps → removed (use Redis)
- admin_client_map → admin_filing_assignments (renamed)

MIGRATION SCRIPTS:
See API_REDESIGN_PHASE5.md Section 4.3 for migration SQL
"""


if __name__ == "__main__":
    """Create database schema"""
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    from pathlib import Path
    import os

    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path)

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "taxease")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print(f"🔗 Connecting to: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    try:
        engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(engine)
        print("✅ Schema v2 created successfully!")
        print("\n📋 Tables:")
        for table in Base.metadata.tables:
            print(f"  - {table}")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
