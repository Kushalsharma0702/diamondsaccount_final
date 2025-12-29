"""
PostgreSQL Schema for Tax-Ease Monolith Backend

Design Principles:
- Minimal, fast, low-cost
- JSONB for flexible tax form data (handles yearly T1 changes)
- Normalize only where required
- Optimize for reads (admin dashboards)
- UUID primary keys
- Local filesystem for documents (no S3)
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey,
    Index, JSON, Date
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """Client user accounts"""
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
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    otps = relationship("OTP", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """JWT refresh tokens"""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class OTP(Base):
    """One-time passwords for email verification"""
    __tablename__ = "otps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False)  # email_verification, password_reset
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="otps")


class Admin(Base):
    """Admin and superadmin users"""
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
    assigned_clients = relationship("AdminClientMap", back_populates="admin", cascade="all, delete-orphan")
    created_payments = relationship("Payment", back_populates="created_by_admin", foreign_keys="Payment.created_by_id")
    created_notifications = relationship("Notification", back_populates="created_by_admin", foreign_keys="Notification.created_by_id")


class Client(Base):
    """Client records linked to users"""
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic info (denormalized for fast queries)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    
    filing_year = Column(Integer, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="documents_pending", index=True)
    # Status: documents_pending, under_review, cost_estimate_sent, awaiting_payment,
    #         in_preparation, awaiting_approval, filed, completed
    
    payment_status = Column(String(20), nullable=False, default="pending", index=True)
    # Payment status: pending, partial, paid, overdue
    
    total_amount = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="clients")
    admin_assignments = relationship("AdminClientMap", back_populates="client", cascade="all, delete-orphan")
    tax_returns = relationship("TaxReturn", back_populates="client", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="client", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="client", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_client_status_year', 'status', 'filing_year'),
        Index('idx_client_payment_status', 'payment_status'),
    )


class AdminClientMap(Base):
    """Many-to-many mapping: Admins assigned to clients"""
    __tablename__ = "admin_client_map"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    admin = relationship("Admin", back_populates="assigned_clients")
    client = relationship("Client", back_populates="admin_assignments")
    
    # Unique constraint: one admin can be assigned to a client once
    __table_args__ = (
        Index('idx_admin_client_unique', 'admin_id', 'client_id', unique=True),
    )


class TaxReturn(Base):
    """Tax return records (T1 forms)"""
    __tablename__ = "tax_returns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    
    filing_year = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="draft", index=True)
    # Status: draft, submitted, under_review, filed, completed
    
    # JSONB for flexible tax form data (handles T1 changes year-to-year)
    form_data = Column(JSONB, nullable=False, default=dict)
    # Contains: personalInfo, questionnaire flags, sections (foreign_property, moving_expenses,
    #           self_employment, etc.), uploadedDocuments map
    
    # Quick access flags (denormalized for filtering)
    has_foreign_property = Column(Boolean, default=False, index=True)
    has_medical_expenses = Column(Boolean, default=False, index=True)
    has_charitable_donations = Column(Boolean, default=False, index=True)
    has_moving_expenses = Column(Boolean, default=False, index=True)
    is_self_employed = Column(Boolean, default=False, index=True)
    is_first_home_buyer = Column(Boolean, default=False, index=True)
    was_student = Column(Boolean, default=False, index=True)
    is_union_member = Column(Boolean, default=False, index=True)
    has_daycare_expenses = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="tax_returns")
    sections = relationship("TaxSection", back_populates="tax_return", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_return_client_year', 'client_id', 'filing_year'),
        Index('idx_tax_return_status', 'status'),
        # GIN index for JSONB queries
        Index('idx_tax_return_form_data', 'form_data', postgresql_using='gin'),
    )


class TaxSection(Base):
    """Tax form sections (for organizing documents and data)"""
    __tablename__ = "tax_sections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tax_return_id = Column(UUID(as_uuid=True), ForeignKey("tax_returns.id"), nullable=False, index=True)
    
    section_name = Column(String(100), nullable=False, index=True)
    # Section names: personal_info, foreign_property, medical_expenses, charitable_donations,
    #                moving_expenses, self_employment, uber_business, general_business,
    #                rental_income, first_home_buyer, property_sale, work_from_home,
    #                student, union_member, daycare, professional_dues, rrsp_fhsa,
    #                child_art_sport, other_income
    
    # JSONB for section-specific data (flexible structure)
    section_data = Column(JSONB, nullable=True, default=dict)
    
    is_complete = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tax_return = relationship("TaxReturn", back_populates="sections")
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_section_return_name', 'tax_return_id', 'section_name'),
        Index('idx_tax_section_data', 'section_data', postgresql_using='gin'),
    )


class Document(Base):
    """Document files uploaded by clients"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    tax_return_id = Column(UUID(as_uuid=True), ForeignKey("tax_returns.id"), nullable=True, index=True)
    
    # Document metadata
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)  # pdf, jpg, png, doc, etc.
    file_size = Column(Integer, nullable=False)  # bytes
    file_path = Column(String(500), nullable=False)  # Local filesystem path (encrypted file)
    encrypted = Column(Boolean, default=True, nullable=False)  # Whether file is encrypted
    encryption_key_hash = Column(String(255), nullable=True)  # Hash of encryption key used (for audit)
    
    # Organization
    section_name = Column(String(100), nullable=True, index=True)
    document_type = Column(String(100), nullable=False)  # receipt, form, statement, etc.
    
    status = Column(String(20), nullable=False, default="pending", index=True)
    # Status: pending, complete, missing, approved, reupload_requested
    
    version = Column(Integer, nullable=False, default=1)
    notes = Column(Text, nullable=True)
    
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="documents")
    
    # Indexes
    __table_args__ = (
        Index('idx_document_client_section', 'client_id', 'section_name'),
        Index('idx_document_status', 'status'),
    )


class Payment(Base):
    """Payment records"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)  # E-Transfer, Credit Card, Debit, etc.
    note = Column(Text, nullable=True)
    
    status = Column(String(20), nullable=False, default="pending", index=True)
    # Status: requested, received, pending, cancelled
    
    is_request = Column(Boolean, default=False, nullable=False)  # True if payment request, False if actual payment
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="payments")
    created_by_admin = relationship("Admin", back_populates="created_payments", foreign_keys=[created_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_client_status', 'client_id', 'status'),
    )


class Notification(Base):
    """Notifications for clients and admins"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True, index=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    
    # Notification details
    type = Column(String(50), nullable=False, index=True)
    # Types: document_request, payment_request, tax_file_approval, payment_received, status_update
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Related entity (for deep linking)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    related_entity_type = Column(String(50), nullable=True)  # client, document, payment, tax_file
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="notifications")
    created_by_admin = relationship("Admin", back_populates="created_notifications", foreign_keys=[created_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_client_read', 'client_id', 'is_read'),
        Index('idx_notification_type', 'type'),
    )


class ChatMessage(Base):
    """Chat messages between clients and admins"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    sender_role = Column(String(20), nullable=False)  # client, admin, superadmin
    message = Column(Text, nullable=False)
    
    read_by_client = Column(Boolean, default=False, nullable=False)
    read_by_admin = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_user_created', 'user_id', 'created_at'),
    )


class T1ReturnFlat(Base):
    """
    ONE TABLE to cover FULL T1 FORM
    NULL = NO / NA
    """

    __tablename__ = "t1_returns_flat"

    # --------------------------------------------------
    # CORE
    # --------------------------------------------------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filing_year = Column(Integer, nullable=False, index=True)

    status = Column(String(30), default="draft", index=True)
    payment_status = Column(String(20), default="pending", index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True))

    # --------------------------------------------------
    # PERSONAL INFORMATION
    # --------------------------------------------------
    first_name = Column(String(100))
    middle_name = Column(String(100))
    last_name = Column(String(100))
    sin = Column(String(9))
    date_of_birth = Column(Date)
    address = Column(String(500))
    phone = Column(String(20))
    email = Column(String(255))
    is_canadian_citizen = Column(Boolean)
    marital_status = Column(String(20))

    # --------------------------------------------------
    # SPOUSE
    # --------------------------------------------------
    spouse_first_name = Column(String(100))
    spouse_last_name = Column(String(100))
    spouse_sin = Column(String(9))
    spouse_date_of_birth = Column(Date)

    # --------------------------------------------------
    # CHILDREN
    # --------------------------------------------------
    has_children = Column(Boolean)
    children_count = Column(Integer)

    # --------------------------------------------------
    # QUESTIONNAIRE FLAGS
    # --------------------------------------------------
    has_foreign_property = Column(Boolean)
    has_medical_expenses = Column(Boolean)
    has_work_from_home = Column(Boolean)
    has_daycare_expenses = Column(Boolean)
    is_first_time_filer = Column(Boolean)
    is_province_filer = Column(Boolean)
    sold_property_short_term = Column(Boolean)
    was_student = Column(Boolean)
    is_union_member = Column(Boolean)
    has_other_income = Column(Boolean)
    has_professional_dues = Column(Boolean)
    has_rrsp_fhsa = Column(Boolean)
    has_child_art_sport = Column(Boolean)
    has_disability_tax_credit = Column(Boolean)
    is_filing_for_deceased = Column(Boolean)
    has_self_employment = Column(Boolean)

    # --------------------------------------------------
    # FOREIGN PROPERTY
    # --------------------------------------------------
    foreign_property_count = Column(Integer)
    foreign_property_max_cost = Column(Float)
    foreign_property_year_end_cost = Column(Float)
    foreign_property_total_income = Column(Float)
    foreign_property_total_gain_loss = Column(Float)

    # --------------------------------------------------
    # MEDICAL EXPENSES
    # --------------------------------------------------
    medical_expense_total_paid = Column(Float)
    medical_expense_insurance_covered = Column(Float)
    medical_expense_out_of_pocket = Column(Float)
    medical_expense_count = Column(Integer)

    # --------------------------------------------------
    # WORK FROM HOME
    # --------------------------------------------------
    wfh_total_house_area = Column(Float)
    wfh_work_area = Column(Float)
    wfh_rent_expense = Column(Float)
    wfh_mortgage_expense = Column(Float)
    wfh_utilities_expense = Column(Float)
    wfh_insurance_expense = Column(Float)

    # --------------------------------------------------
    # DAYCARE
    # --------------------------------------------------
    daycare_expense_total = Column(Float)
    daycare_weeks_total = Column(Integer)
    daycare_children_count = Column(Integer)

    # --------------------------------------------------
    # FIRST TIME FILER
    # --------------------------------------------------
    first_time_landing_date = Column(Date)
    income_outside_canada = Column(Float)
    back_home_income_2023 = Column(Float)
    back_home_income_2024 = Column(Float)

    # --------------------------------------------------
    # SHORT TERM PROPERTY SALE (FLIP)
    # --------------------------------------------------
    flip_property_address = Column(String(500))
    flip_purchase_date = Column(Date)
    flip_sell_date = Column(Date)
    flip_purchase_sell_expenses = Column(Float)

    # --------------------------------------------------
    # STUDENT
    # --------------------------------------------------
    student_tuition_amount = Column(Float)

    # --------------------------------------------------
    # UNION DUES
    # --------------------------------------------------
    union_dues_total = Column(Float)
    union_dues_count = Column(Integer)

    # --------------------------------------------------
    # OTHER INCOME
    # --------------------------------------------------
    other_income_description = Column(String(1000))
    other_income_amount = Column(Float)

    # --------------------------------------------------
    # PROFESSIONAL DUES
    # --------------------------------------------------
    professional_dues_total = Column(Float)
    professional_dues_count = Column(Integer)

    # --------------------------------------------------
    # RRSP / FHSA
    # --------------------------------------------------
    rrsp_fhsa_contribution_total = Column(Float)

    # --------------------------------------------------
    # CHILD ART / SPORT
    # --------------------------------------------------
    child_art_sport_total = Column(Float)
    child_art_sport_count = Column(Integer)

    # --------------------------------------------------
    # DISABILITY CREDIT
    # --------------------------------------------------
    disability_members_count = Column(Integer)
    disability_approved_year_min = Column(Integer)

    # --------------------------------------------------
    # PROVINCE FILER
    # --------------------------------------------------
    province_rent_property_tax_total = Column(Float)
    province_months_resided = Column(Integer)

    # --------------------------------------------------
    # SELF EMPLOYMENT
    # --------------------------------------------------
    self_employment_type = Column(String(20))  # uber | general | rental | mixed

    # ---- UBER ----
    uber_income = Column(Float)
    uber_total_km = Column(Float)
    uber_gas_expense = Column(Float)
    uber_insurance_expense = Column(Float)
    uber_maintenance_expense = Column(Float)
    uber_other_expense = Column(Float)

    # ---- GENERAL BUSINESS ----
    general_business_income = Column(Float)
    general_business_expenses = Column(Float)
    general_home_office_expense = Column(Float)
    general_vehicle_expense = Column(Float)

    # ---- RENTAL ----
    rental_property_address = Column(String(500))
    rental_gross_income = Column(Float)
    rental_total_expenses = Column(Float)
    rental_mortgage_interest = Column(Float)
    rental_property_tax = Column(Float)

    # --------------------------------------------------
    # FULL FORM DATA (JSONB) - Stores complete nested structure
    # --------------------------------------------------
    form_data = Column(JSONB, nullable=True)  # Complete form data from frontend


if __name__ == "__main__":
    """
    Run this script to create the database schema:
    python database/schemas.py
    """
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    from pathlib import Path
    import os

    # Load .env from project root
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path)  # ✅ MUST be called first

    # Get database URL from environment with proper defaults
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "taxease")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    # Handle case where env vars might be string 'None'
    if DB_PORT == "None" or DB_PORT is None:
        DB_PORT = "5432"
    if DB_HOST == "None" or DB_HOST is None:
        DB_HOST = "localhost"
    if DB_NAME == "None" or DB_NAME is None:
        DB_NAME = "taxease"
    if DB_USER == "None" or DB_USER is None:
        DB_USER = "postgres"
    if DB_PASSWORD == "None" or DB_PASSWORD is None:
        DB_PASSWORD = "postgres"

    # Validate all required values are present
    if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
        raise ValueError("❌ Database environment variables are missing or invalid")

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print(f"🔗 Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"   User: {DB_USER}")

    try:
        engine = create_engine(DATABASE_URL, echo=False)
        
        print("📦 Creating tables...")
        Base.metadata.create_all(engine)
        
        print("✅ Database schema created successfully!")
        print("\n📋 Tables created:")
        for table in Base.metadata.tables:
            print(f"  - {table}")
    except Exception as e:
        print(f"❌ Error creating database schema: {e}")
        raise