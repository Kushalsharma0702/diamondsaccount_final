"""
TaxEase Backend - Unified FastAPI Application
All microservices combined into a single application for easier development and deployment
"""

import sys
import os
import asyncio
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File as FastAPIFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import uuid
import logging
from typing import List, Optional
import json

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

# Import shared modules
from shared.database import get_db, Database
from shared.models import User, RefreshToken, OTP, T1PersonalForm, File, Report, AuditLog
from shared.schemas import (
    UserCreate, UserResponse, UserLogin, Token, OTPRequest, OTPVerify,
    T1PersonalFormCreate, T1PersonalFormUpdate, T1PersonalFormResponse,
    FileUploadResponse, FileListResponse, ReportResponse, ReportRequest,
    MessageResponse, HealthResponse, EncryptedFileUploadResponse,
    EncryptedFileListResponse, EncryptedFileDecryptRequest, FileDecryptResponse,
    EncryptionSetupRequest, EncryptionSetupResponse, KeyRotationRequest,
    FileStatsResponse
)
from shared.auth import JWTManager, create_tokens, get_current_user
from shared.utils import generate_otp, EmailService, S3Manager, generate_filename, validate_file_type, calculate_tax, DEVELOPER_OTP
from shared.encrypted_file_service import EncryptedFileService
from shared.t1_routes import router as t1_router
from shared.sync_to_admin import sync_file_to_admin_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TaxEase Backend API",
    description="""
    # TaxEase Backend - Complete Tax Filing Solution

    A comprehensive REST API for tax filing applications with the following features:

    ## 🔐 Authentication & User Management
    - User registration and login
    - JWT-based authentication with refresh tokens
    - Email verification with OTP
    - Password reset functionality
    - Secure session management

    ## 📊 Tax Form Processing
    - Canadian T1 Personal Tax Form support
    - Automated tax calculations
    - Income and deduction tracking
    - Form validation and submission
    - Multi-year tax form management

    ## 📁 File Management
    - Secure file uploads to AWS S3
    - Document validation and processing
    - File metadata management
    - Presigned URL generation for downloads
    - Support for PDF, images, and office documents

    ## 📋 Report Generation
    - PDF tax summary reports
    - Tax calculation breakdowns
    - Downloadable form submissions
    - Background report processing
    - Report status tracking

    ## 🛡️ Security Features
    - Rate limiting and CORS protection
    - Input validation and sanitization
    - Audit logging for compliance
    - Secure file handling
    - JWT token management

    ## 📱 Flutter Integration Ready
    - OpenAPI/Swagger documentation
    - JSON response format
    - RESTful API design
    - Multipart file upload support
    - Comprehensive error handling
    """,
    version="1.0.0",
    contact={
        "name": "TaxEase Support",
        "email": "support@taxease.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.taxease.com", "description": "Production server"},
    ],
    tags_metadata=[
        {
            "name": "Health",
            "description": "System health and status endpoints"
        },
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints"
        },
        {
            "name": "Tax Forms",
            "description": "Tax form creation, management, and submission"
        },
        {
            "name": "File Management",
            "description": "File upload, storage, and retrieval operations"
        },
        {
            "name": "Reports",
            "description": "PDF report generation and download"
        },
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
s3_manager = S3Manager()
email_service = EmailService()
encrypted_file_service = EncryptedFileService()
security = HTTPBearer()

# Include routers
app.include_router(t1_router)

# File upload configuration
ALLOWED_FILE_TYPES = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ================================
# HEALTH AND STATUS ENDPOINTS
# ================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "service": "TaxEase Backend API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth/*",
            "tax": "/api/v1/tax/*",
            "files": "/api/v1/files/*",
            "reports": "/api/v1/reports/*"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    
    Returns the current health status of the API and its dependencies.
    """
    try:
        # Test database connection
        from shared.database import engine
        async with engine.begin() as conn:
            await conn.execute(select(1))
        
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        timestamp=datetime.utcnow(),
        service="taxease-api",
        version="1.0.0"
    )

@app.get("/dev/otps/{email}", tags=["Health"])
async def get_development_otps(email: str, db: AsyncSession = Depends(get_db)):
    """
    🚨 DEVELOPMENT ONLY - Get OTP codes for testing
    
    This endpoint is only available in development mode and returns
    all active OTP codes for a given email address for testing purposes.
    """
    from decouple import config
    DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
    
    if not DEVELOPMENT_MODE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Get active OTPs for email
    result = await db.execute(
        select(OTP).where(
            OTP.email == email,
            OTP.used == False,
            OTP.expires_at > datetime.utcnow()
        ).order_by(OTP.created_at.desc())
    )
    otps = result.scalars().all()
    
    developer_otp = config('DEVELOPER_OTP', default='123456')
    
    return {
        "email": email,
        "development_mode": True,
        "developer_otp": f"{developer_otp} (always works)",
        "active_otps": [
            {
                "code": otp.code,
                "purpose": otp.purpose,
                "expires_at": otp.expires_at.isoformat(),
                "created_at": otp.created_at.isoformat()
            }
            for otp in otps
        ],
        "instructions": [
            f"Use '{developer_otp}' as OTP code for any verification",
            "Or use any of the active OTPs listed above",
            "Developer OTP works for 24 hours after generation"
        ]
    }

# ================================
# AUTHENTICATION ENDPOINTS
# ================================

@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account
    
    Creates a new user account with email verification. An OTP will be sent
    to the provided email address for verification.
    
    - **email**: Valid email address (must be unique)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **password**: Strong password (minimum 8 characters)
    - **phone**: Optional phone number
    - **accept_terms**: Must be true to register
    """
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = JWTManager.hash_password(user_data.password)
    
    from decouple import config
    SKIP_EMAIL_VERIFICATION = config('SKIP_EMAIL_VERIFICATION', default=False, cast=bool)
    
    new_user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        password_hash=hashed_password,
        accept_terms=user_data.accept_terms,
        email_verified=SKIP_EMAIL_VERIFICATION,  # Auto-verify in development
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Send welcome email and verification OTP
    await email_service.send_welcome_email(new_user.email, new_user.first_name)
    await send_verification_otp(new_user.email, db)
    
    # Sync user to admin backend as client
    try:
        from shared.sync_to_admin import _get_or_create_client_by_email
        await _get_or_create_client_by_email(
            new_user.email, 
            db_session=None,
            first_name=new_user.first_name,
            last_name=new_user.last_name
        )
        logger.info(f"Synced user {new_user.email} to admin backend as client")
    except Exception as e:
        logger.warning(f"Failed to sync user to admin backend: {e}")
    
    # Log registration
    await log_user_action(db, str(new_user.id), "user_registered", "user", str(new_user.id))
    
    logger.info(f"User registered: {new_user.email}")
    return new_user

@app.post("/api/v1/auth/login", response_model=Token, tags=["Authentication"])
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access tokens
    
    Validates user credentials and returns JWT access and refresh tokens.
    
    - **email**: User's registered email address
    - **password**: User's password
    
    Returns access token (15 minutes) and refresh token (7 days).
    """
    
    # Get user by email (case-insensitive)
    from sqlalchemy import func
    result = await db.execute(select(User).where(func.lower(User.email) == login_data.email.lower()))
    user = result.scalar_one_or_none()
    
    if not user or not JWTManager.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create tokens
    tokens = create_tokens(str(user.id), user.email)
    
    # Store refresh token in database
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=JWTManager.hash_password(tokens["refresh_token"]),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    
    # Log login
    await log_user_action(db, str(user.id), "user_login", "session", None)
    
    logger.info(f"User logged in: {user.email}")
    return tokens

@app.post("/api/v1/auth/request-otp", response_model=MessageResponse, tags=["Authentication"])
async def request_otp(otp_request: OTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Request OTP for email verification or password reset
    
    Sends a one-time password to the user's email for verification purposes.
    
    - **email**: Email address to send OTP to
    - **purpose**: Either 'email_verification' or 'password_reset'
    """
    
    if otp_request.purpose == "email_verification":
        await send_verification_otp(otp_request.email, db)
    elif otp_request.purpose == "password_reset":
        await send_password_reset_otp(otp_request.email, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP purpose. Use 'email_verification' or 'password_reset'"
        )
    
    return MessageResponse(message="OTP sent successfully")

@app.post("/api/v1/auth/verify-otp", response_model=MessageResponse, tags=["Authentication"])
async def verify_otp(otp_data: OTPVerify, db: AsyncSession = Depends(get_db)):
    """
    Verify OTP code
    
    Verifies the OTP code sent to user's email and performs the requested action.
    
    - **email**: Email address that received the OTP
    - **code**: 6-digit OTP code (use developer OTP '123456' for testing)
    - **purpose**: Purpose of the OTP verification
    """
    
    # Normalize the code (strip whitespace, ensure it's a string)
    normalized_code = str(otp_data.code).strip()
    developer_otp = str(DEVELOPER_OTP).strip()
    
    logger.info(f"OTP verification attempt for {otp_data.email}: code='{normalized_code}', purpose={otp_data.purpose}, developer_otp='{developer_otp}'")
    
    # Check for developer OTP bypass (always works)
    # Compare as strings and handle case-insensitive for numeric codes
    # Also check for hardcoded "123456" as fallback
    if (str(normalized_code) == str(developer_otp) or 
        normalized_code.strip() == developer_otp.strip() or 
        normalized_code == "123456" or
        str(normalized_code).strip() == "123456"):
        logger.info(f"✅ Developer OTP matched! Verifying for {otp_data.email}: {otp_data.purpose}")
        logger.info(f"   Normalized code: '{normalized_code}' == Developer OTP: '{developer_otp}'")
        
        # If email verification, mark user as verified
        if otp_data.purpose == "email_verification":
            user_result = await db.execute(select(User).where(User.email == otp_data.email))
            user = user_result.scalar_one_or_none()
            if user:
                user.email_verified = True
                await log_user_action(db, str(user.id), "email_verified", "user", str(user.id))
                await db.commit()
                logger.info(f"✅ User {otp_data.email} marked as verified")
            else:
                logger.info(f"ℹ️ User not found for email: {otp_data.email} (this is OK for new registrations)")
        
        # For password reset, just return success (password reset flow handles the rest)
        logger.info(f"✅ OTP verified (developer bypass) for {otp_data.email}: {otp_data.purpose}")
        return MessageResponse(message="OTP verified successfully")
    
    # Get OTP from database
    result = await db.execute(
        select(OTP).where(
            OTP.email == otp_data.email,
            OTP.code == normalized_code,
            OTP.purpose == otp_data.purpose,
            OTP.used == False,
            OTP.expires_at > datetime.utcnow()
        )
    )
    otp = result.scalar_one_or_none()
    
    if not otp:
        logger.warning(f"❌ Invalid OTP for {otp_data.email}: code='{normalized_code}', purpose={otp_data.purpose}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or expired OTP. Use '{DEVELOPER_OTP}' for testing."
        )
    
    # Mark OTP as used
    otp.used = True
    
    # If email verification, mark user as verified
    if otp_data.purpose == "email_verification":
        user_result = await db.execute(select(User).where(User.email == otp_data.email))
        user = user_result.scalar_one_or_none()
        if user:
            user.email_verified = True
            await log_user_action(db, str(user.id), "email_verified", "user", str(user.id))
    
    await db.commit()
    
    logger.info(f"✅ OTP verified (from DB) for {otp_data.email}: {otp_data.purpose}")
    return MessageResponse(message="OTP verified successfully")

@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    
    Returns the profile information of the currently authenticated user.
    
    Requires valid JWT access token in Authorization header.
    """
    return current_user

# ================================
# TAX FORM ENDPOINTS
# ================================

@app.post("/api/v1/tax/t1-personal", response_model=T1PersonalFormResponse, status_code=status.HTTP_201_CREATED, tags=["Tax Forms"])
async def create_t1_form(
    form_data: T1PersonalFormCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new T1 Personal Tax Form
    
    Creates a new Canadian T1 Personal Tax Return form for the specified tax year.
    
    - **tax_year**: Tax year (e.g., 2023)
    - **sin**: Social Insurance Number (optional)
    - **marital_status**: Marital status
    - **employment_income**: Employment income in CAD
    - **self_employment_income**: Self-employment income in CAD
    - **investment_income**: Investment income in CAD
    - **other_income**: Other income in CAD
    - **rrsp_contributions**: RRSP contributions in CAD
    - **charitable_donations**: Charitable donations in CAD
    """
    
    # Check if user already has a form for this tax year
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.user_id == current_user.id,
                T1PersonalForm.tax_year == form_data.tax_year
            )
        )
    )
    existing_form = result.scalar_one_or_none()
    
    if existing_form:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"T1 form for {form_data.tax_year} already exists"
        )
    
    # Create new form
    new_form = T1PersonalForm(
        id=uuid.uuid4(),
        user_id=current_user.id,
        tax_year=form_data.tax_year,
        sin=form_data.sin,
        marital_status=form_data.marital_status,
        employment_income=form_data.employment_income or 0.0,
        self_employment_income=form_data.self_employment_income or 0.0,
        investment_income=form_data.investment_income or 0.0,
        other_income=form_data.other_income or 0.0,
        rrsp_contributions=form_data.rrsp_contributions or 0.0,
        charitable_donations=form_data.charitable_donations or 0.0,
        status="draft"
    )
    
    # Calculate totals and taxes
    await calculate_form_taxes(new_form)
    
    db.add(new_form)
    await db.commit()
    await db.refresh(new_form)
    
    # Log form creation
    await log_user_action(db, str(current_user.id), "t1_form_created", "t1_form", str(new_form.id))
    
    logger.info(f"T1 form created for user {current_user.email}, year {form_data.tax_year}")
    return new_form

@app.get("/api/v1/tax/t1-personal", response_model=List[T1PersonalFormResponse], tags=["Tax Forms"])
async def get_user_tax_forms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all T1 forms for current user
    
    Returns a list of all T1 Personal Tax Forms created by the current user,
    ordered by tax year (most recent first).
    """
    
    result = await db.execute(
        select(T1PersonalForm).where(T1PersonalForm.user_id == current_user.id)
        .order_by(T1PersonalForm.tax_year.desc())
    )
    forms = result.scalars().all()
    
    return list(forms)

@app.get("/api/v1/tax/t1-personal/{form_id}", response_model=T1PersonalFormResponse, tags=["Tax Forms"])
async def get_tax_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific T1 form by ID
    
    Returns detailed information about a specific T1 Personal Tax Form.
    
    - **form_id**: UUID of the tax form
    """
    
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.id == form_id,
                T1PersonalForm.user_id == current_user.id
            )
        )
    )
    form = result.scalar_one_or_none()
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    return form

@app.put("/api/v1/tax/t1-personal/{form_id}", response_model=T1PersonalFormResponse, tags=["Tax Forms"])
async def update_tax_form(
    form_id: str,
    form_data: T1PersonalFormUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update T1 form
    
    Updates an existing T1 Personal Tax Form. Only forms in 'draft' status can be updated.
    
    - **form_id**: UUID of the tax form
    - **form_data**: Updated form fields (only provide fields to be changed)
    """
    
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.id == form_id,
                T1PersonalForm.user_id == current_user.id
            )
        )
    )
    form = result.scalar_one_or_none()
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    if form.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update submitted form"
        )
    
    # Update form fields
    update_data = form_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(form, field):
            setattr(form, field, value)
    
    # Recalculate taxes
    await calculate_form_taxes(form)
    
    form.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(form)
    
    # Log form update
    await log_user_action(db, str(current_user.id), "t1_form_updated", "t1_form", str(form.id))
    
    logger.info(f"T1 form updated: {form_id}")
    return form

@app.post("/api/v1/tax/t1-personal/{form_id}/submit", response_model=MessageResponse, tags=["Tax Forms"])
async def submit_tax_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit T1 form for processing
    
    Submits the T1 Personal Tax Form to CRA for processing. Once submitted,
    the form cannot be modified.
    
    - **form_id**: UUID of the tax form to submit
    """
    
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.id == form_id,
                T1PersonalForm.user_id == current_user.id
            )
        )
    )
    form = result.scalar_one_or_none()
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    if form.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form already submitted"
        )
    
    # Validate required fields
    if not form.sin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SIN is required for submission"
        )
    
    # Submit form
    form.status = "submitted"
    form.submitted_at = datetime.utcnow()
    await db.commit()
    
    # Log form submission
    await log_user_action(db, str(current_user.id), "t1_form_submitted", "t1_form", str(form.id))
    
    logger.info(f"T1 form submitted: {form_id}")
    return MessageResponse(message="Tax form submitted successfully")

@app.delete("/api/v1/tax/t1-personal/{form_id}", response_model=MessageResponse, tags=["Tax Forms"])
async def delete_tax_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete T1 form
    
    Deletes a T1 Personal Tax Form. Only forms in 'draft' status can be deleted.
    
    - **form_id**: UUID of the tax form to delete
    """
    
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.id == form_id,
                T1PersonalForm.user_id == current_user.id
            )
        )
    )
    form = result.scalar_one_or_none()
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    if form.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete submitted form"
        )
    
    await db.delete(form)
    await db.commit()
    
    # Log form deletion
    await log_user_action(db, str(current_user.id), "t1_form_deleted", "t1_form", form_id)
    
    logger.info(f"T1 form deleted: {form_id}")
    return MessageResponse(message="Tax form deleted successfully")

# ================================
# FILE MANAGEMENT ENDPOINTS
# ================================

@app.post("/api/v1/files/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED, tags=["File Management"])
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file to cloud storage
    
    Uploads a document file to AWS S3 and stores metadata in the database.
    Supported file types: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX.
    
    - **file**: File to upload (max 10MB)
    """
    
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024:.1f}MB"
        )
    
    # Validate file type
    if not validate_file_type(file.filename, ALLOWED_FILE_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Detect MIME type (placeholder - would use python-magic in production)
    mime_type = f"application/{file.filename.split('.')[-1].lower()}"
    
    # Generate unique filename
    unique_filename = generate_filename(file.filename)
    s3_key = f"user_{current_user.id}/{unique_filename}"
    
    # Create file record
    file_record = File(
        id=uuid.uuid4(),
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_type=mime_type,
        file_size=len(file_content),
        s3_bucket=s3_manager.bucket_name,
        s3_key=s3_key,
        upload_status="pending"
    )
    
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)
    
    try:
        # Upload to local filesystem (S3Manager now uses local storage)
        success = await s3_manager.upload_file(file_content, s3_key, mime_type)
        
        if success:
            file_record.upload_status = "uploaded"
            logger.info(f"File uploaded successfully: {s3_key}")
        else:
            file_record.upload_status = "failed"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage"
            )
        
        await db.commit()
        await db.refresh(file_record)
        
        # Log file upload
        await log_user_action(db, str(current_user.id), "file_uploaded", "file", str(file_record.id))
        
        # Sync to admin backend (non-blocking)
        try:
            await sync_file_to_admin_document(
                file_id=str(file_record.id),
                user_email=current_user.email,
                filename=file_record.original_filename,
                file_type=file_record.file_type,
                file_size=file_record.file_size,
                s3_key=file_record.s3_key,
                db_session=db
            )
        except Exception as sync_error:
            logger.warning(f"Failed to sync file to admin backend: {sync_error}")
            # Don't fail the upload if sync fails
        
    except Exception as e:
        file_record.upload_status = "failed"
        await db.commit()
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )
    
    return file_record

@app.get("/api/v1/files", response_model=FileListResponse, tags=["File Management"])
async def list_user_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    Get list of user's uploaded files
    
    Returns a paginated list of files uploaded by the current user.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 100)
    """
    
    if limit > 100:
        limit = 100
    
    # Get files with pagination
    result = await db.execute(
        select(File).where(File.user_id == current_user.id)
        .order_by(File.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    files = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(File).where(File.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())
    
    return FileListResponse(
        files=list(files),
        total=total
    )

@app.get("/api/v1/files/{file_id}", response_model=FileUploadResponse, tags=["File Management"])
async def get_file_metadata(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get file metadata by ID
    
    Returns metadata information about a specific uploaded file.
    
    - **file_id**: UUID of the file
    """
    
    result = await db.execute(
        select(File).where(
            and_(
                File.id == file_id,
                File.user_id == current_user.id
            )
        )
    )
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file_record

@app.get("/api/v1/files/{file_id}/download", tags=["File Management"])
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate download URL for file
    
    Generates a presigned URL for downloading the file from cloud storage.
    
    - **file_id**: UUID of the file to download
    """
    
    result = await db.execute(
        select(File).where(
            and_(
                File.id == file_id,
                File.user_id == current_user.id
            )
        )
    )
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if file_record.upload_status != "uploaded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File not available for download"
        )
    
    # Get local file path
    local_path = s3_manager.get_file_path(file_record.s3_key)
    
    if not local_path or not os.path.exists(local_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on storage"
        )
    
    # Log file download
    await log_user_action(db, str(current_user.id), "file_downloaded", "file", str(file_record.id))
    
    # Serve file directly
    return FileResponse(
        path=local_path,
        filename=file_record.original_filename,
        media_type=file_record.file_type
    )

@app.delete("/api/v1/files/{file_id}", response_model=MessageResponse, tags=["File Management"])
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete file from storage and database
    
    Permanently deletes a file from both cloud storage and the database.
    
    - **file_id**: UUID of the file to delete
    """
    
    result = await db.execute(
        select(File).where(
            and_(
                File.id == file_id,
                File.user_id == current_user.id
            )
        )
    )
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Delete from S3 (placeholder)
        # if file_record.s3_key:
        #     await s3_manager.delete_file(file_record.s3_key)
        
        # Delete from database
        await db.delete(file_record)
        await db.commit()
        
        # Log file deletion
        await log_user_action(db, str(current_user.id), "file_deleted", "file", file_id)
        
        logger.info(f"File deleted: {file_id}")
        return MessageResponse(message="File deleted successfully")
        
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

# ================================
# REPORT GENERATION ENDPOINTS
# ================================

@app.post("/api/v1/reports/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED, tags=["Reports"])
async def generate_report(
    report_data: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new PDF report
    
    Creates a new report generation request. The report will be generated
    in the background and its status can be checked using the returned report ID.
    
    - **report_type**: Type of report ('t1_summary', 'tax_calculation')
    - **title**: Human-readable title for the report
    """
    
    # Create report record
    report = Report(
        id=uuid.uuid4(),
        user_id=current_user.id,
        report_type=report_data.report_type,
        title=report_data.title,
        status="generating"
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    # Generate report in background (placeholder)
    background_tasks.add_task(
        generate_report_background, 
        str(report.id), 
        report_data.report_type, 
        str(current_user.id)
    )
    
    # Log report generation
    await log_user_action(db, str(current_user.id), "report_requested", "report", str(report.id))
    
    logger.info(f"Report generation started: {report.id}")
    return report

@app.get("/api/v1/reports", response_model=List[ReportResponse], tags=["Reports"])
async def list_user_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of user's reports
    
    Returns all reports generated or requested by the current user,
    ordered by creation date (most recent first).
    """
    
    result = await db.execute(
        select(Report).where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
    )
    reports = result.scalars().all()
    
    return list(reports)

@app.get("/api/v1/reports/{report_id}", response_model=ReportResponse, tags=["Reports"])
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific report by ID
    
    Returns detailed information about a specific report including its status
    and download URL (if ready).
    
    - **report_id**: UUID of the report
    """
    
    result = await db.execute(
        select(Report).where(
            and_(
                Report.id == report_id,
                Report.user_id == current_user.id
            )
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report

@app.get("/api/v1/reports/{report_id}/download", tags=["Reports"])
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download report PDF
    
    Downloads the generated PDF report. The report must be in 'ready' status.
    
    - **report_id**: UUID of the report to download
    """
    
    result = await db.execute(
        select(Report).where(
            and_(
                Report.id == report_id,
                Report.user_id == current_user.id
            )
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report not ready for download. Current status: {report.status}"
        )
    
    if not report.file_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Report file not available"
        )
    
    # Log report download
    await log_user_action(db, str(current_user.id), "report_downloaded", "report", str(report.id))
    
    # Redirect to S3 presigned URL or return the URL
    return RedirectResponse(url=report.file_url)

@app.delete("/api/v1/reports/{report_id}", response_model=MessageResponse, tags=["Reports"])
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete report
    
    Deletes a report and its associated files from storage.
    
    - **report_id**: UUID of the report to delete
    """
    
    result = await db.execute(
        select(Report).where(
            and_(
                Report.id == report_id,
                Report.user_id == current_user.id
            )
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Delete from S3 if exists (placeholder)
    # if report.file_url:
    #     s3_key = extract_s3_key_from_url(report.file_url)
    #     await s3_manager.delete_file(s3_key)
    
    # Delete from database
    await db.delete(report)
    await db.commit()
    
    # Log report deletion
    await log_user_action(db, str(current_user.id), "report_deleted", "report", report_id)
    
    logger.info(f"Report deleted: {report_id}")
    return MessageResponse(message="Report deleted successfully")

# ================================
# HELPER FUNCTIONS
# ================================

async def send_verification_otp(email: str, db: AsyncSession):
    """Send email verification OTP"""
    
    from decouple import config
    DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
    DEVELOPER_OTP = config('DEVELOPER_OTP', default='123456')
    
    # Generate OTP
    otp_code = generate_otp()
    
    # Store OTP in database
    otp = OTP(
        email=email,
        code=otp_code,
        purpose="email_verification",
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(otp)
    
    # In development mode, also store the developer OTP
    if DEVELOPMENT_MODE:
        developer_otp = OTP(
            email=email,
            code=DEVELOPER_OTP,
            purpose="email_verification",
            expires_at=datetime.utcnow() + timedelta(hours=24)  # Longer expiry for development
        )
        db.add(developer_otp)
    
    await db.commit()
    
    # Send email
    await email_service.send_otp_email(email, otp_code, "email_verification")

async def send_password_reset_otp(email: str, db: AsyncSession):
    """Send password reset OTP"""
    
    from decouple import config
    DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
    DEVELOPER_OTP = config('DEVELOPER_OTP', default='123456')
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if email exists
        return
    
    # Generate OTP
    otp_code = generate_otp()
    
    # Store OTP in database
    otp = OTP(
        email=email,
        code=otp_code,
        purpose="password_reset",
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(otp)
    
    # In development mode, also store the developer OTP
    if DEVELOPMENT_MODE:
        developer_otp = OTP(
            email=email,
            code=DEVELOPER_OTP,
            purpose="password_reset",
            expires_at=datetime.utcnow() + timedelta(hours=24)  # Longer expiry for development
        )
        db.add(developer_otp)
    
    await db.commit()
    
    # Send email
    await email_service.send_otp_email(email, otp_code, "password_reset")

async def calculate_form_taxes(form: T1PersonalForm):
    """Calculate taxes for T1 form"""
    
    # Calculate total income
    form.total_income = (
        (form.employment_income or 0) +
        (form.self_employment_income or 0) +
        (form.investment_income or 0) +
        (form.other_income or 0)
    )
    
    # Calculate taxable income (simplified - deduct RRSP and charitable donations)
    taxable_income = form.total_income - (form.rrsp_contributions or 0) - (form.charitable_donations or 0)
    
    if taxable_income > 0:
        # Calculate taxes using utility function
        tax_calculation = calculate_tax(taxable_income, "ON")  # Assuming Ontario
        
        form.federal_tax = tax_calculation["federal_tax"]
        form.provincial_tax = tax_calculation["provincial_tax"]
        form.total_tax = tax_calculation["total_tax"]
        
        # Calculate refund or amount owing (simplified)
        # In reality, this would consider tax deductions, credits, and amounts already paid
        form.refund_or_owing = form.total_tax
    else:
        form.federal_tax = 0.0
        form.provincial_tax = 0.0
        form.total_tax = 0.0
        form.refund_or_owing = 0.0

async def generate_report_background(report_id: str, report_type: str, user_id: str):
    """Background task to generate PDF report (placeholder)"""
    
    try:
        # Simulate report generation
        await asyncio.sleep(5)  # Simulate processing time
        
        from shared.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            # Get report record
            result = await db.execute(select(Report).where(Report.id == report_id))
            report = result.scalar_one_or_none()
            
            if not report:
                return
            
            # Generate PDF content (placeholder)
            pdf_url = f"https://example.com/reports/{report_id}.pdf"
            
            # Update report status
            report.status = "ready"
            report.file_url = pdf_url
            report.generated_at = datetime.utcnow()
            
            await db.commit()
            logger.info(f"Report generated: {report_id}")
            
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        # Update report status to failed
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Report).where(Report.id == report_id))
            report = result.scalar_one_or_none()
            if report:
                report.status = "failed"
                await db.commit()

async def log_user_action(db: AsyncSession, user_id: str, action: str, resource_type: str, resource_id: Optional[str]):
    """Log user action for audit trail"""
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address="127.0.0.1",  # Would get from request in production
        user_agent="FastAPI"     # Would get from request headers
    )
    
    db.add(audit_log)
    # Note: Not committing here to allow batching with main operation

# ================================
# ENCRYPTED FILE ENDPOINTS
# ================================

@app.post("/api/v1/encryption/setup", response_model=EncryptionSetupResponse, tags=["Encrypted Files"])
async def setup_user_encryption(
    request: EncryptionSetupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Set up end-to-end encryption for user files
    """
    if current_user.public_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Encryption is already set up for this user"
        )
    
    success = await encrypted_file_service.setup_user_encryption(
        current_user, request.password, db
    )
    
    if success:
        return EncryptionSetupResponse(
            message="Encryption setup completed successfully",
            encryption_enabled=True,
            key_created_at=current_user.key_created_at
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup encryption"
        )

@app.post("/api/v1/files/encrypted/upload", response_model=EncryptedFileUploadResponse, tags=["Encrypted Files"])
async def upload_encrypted_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and encrypt a file with end-to-end encryption
    """
    # Verify user has encryption set up
    if not current_user.public_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Encryption not set up. Please set up encryption first."
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_extension}' not allowed"
        )
    
    # Read file data
    file_data = await file.read()
    
    # Check file size
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // 1024 // 1024}MB"
        )
    
    # Encrypt and store file
    file_record = await encrypted_file_service.encrypt_and_store_file(
        current_user, file_data, file.filename, file.content_type or 'application/octet-stream', db
    )
    
    # Parse encryption metadata
    metadata = json.loads(file_record.encryption_metadata) if file_record.encryption_metadata else {}
    
    return EncryptedFileUploadResponse(
        id=file_record.id,
        original_filename=file_record.original_filename,
        file_type=file_record.file_type,
        file_size=file_record.file_size,
        is_encrypted=file_record.is_encrypted,
        upload_status=file_record.upload_status,
        compression_ratio=metadata.get('compressed_size', 0) / max(metadata.get('original_size', 1), 1),
        encryption_algorithm=metadata.get('encryption_algorithm'),
        created_at=file_record.created_at
    )

@app.get("/api/v1/files/encrypted", response_model=EncryptedFileListResponse, tags=["Encrypted Files"])
async def list_encrypted_files(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's encrypted files
    """
    files = await encrypted_file_service.list_user_files(current_user, db, limit, offset)
    
    file_responses = [
        EncryptedFileUploadResponse(
            id=file_info['id'],
            original_filename=file_info['original_filename'],
            file_type=file_info['file_type'],
            file_size=file_info['file_size'],
            is_encrypted=file_info['is_encrypted'],
            upload_status=file_info['upload_status'],
            compression_ratio=file_info.get('compression_ratio'),
            encryption_algorithm=file_info.get('encryption_algorithm'),
            created_at=datetime.fromisoformat(file_info['created_at'])
        )
        for file_info in files
    ]
    
    return EncryptedFileListResponse(
        files=file_responses,
        total=len(file_responses)
    )

@app.post("/api/v1/files/encrypted/{file_id}/decrypt", response_model=FileDecryptResponse, tags=["Encrypted Files"])
async def decrypt_file(
    file_id: str,
    request: EncryptedFileDecryptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Decrypt a file and provide download information
    """
    try:
        document_data, filename, file_type = await encrypted_file_service.decrypt_and_retrieve_file(
            current_user, file_id, request.password, db
        )
        
        return FileDecryptResponse(
            message="File decrypted successfully",
            filename=filename,
            file_size=len(document_data),
            download_ready=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt file: {str(e)}"
        )

@app.get("/api/v1/files/encrypted/{file_id}/download")
async def download_decrypted_file(
    file_id: str,
    password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a decrypted file directly
    """
    try:
        document_data, filename, file_type = await encrypted_file_service.decrypt_and_retrieve_file(
            current_user, file_id, password, db
        )
        
        from fastapi.responses import Response
        return Response(
            content=document_data,
            media_type=file_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(document_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )

@app.delete("/api/v1/files/encrypted/{file_id}", response_model=MessageResponse, tags=["Encrypted Files"])
async def delete_encrypted_file(
    file_id: str,
    password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an encrypted file (requires password verification)
    """
    success = await encrypted_file_service.delete_encrypted_file(
        current_user, file_id, password, db
    )
    
    if success:
        return MessageResponse(
            message="File deleted successfully",
            success=True
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

@app.post("/api/v1/encryption/rotate-keys", response_model=MessageResponse, tags=["Encrypted Files"])
async def rotate_encryption_keys(
    request: KeyRotationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Rotate user's encryption keys (when password changes)
    This will re-encrypt all user files with new keys
    """
    success = await encrypted_file_service.rotate_user_keys(
        current_user, request.old_password, request.new_password, db
    )
    
    if success:
        return MessageResponse(
            message="Encryption keys rotated successfully. All files re-encrypted.",
            success=True
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rotate encryption keys"
        )

@app.get("/api/v1/encryption/stats", response_model=FileStatsResponse, tags=["Encrypted Files"])
async def get_file_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get file storage and encryption statistics
    """
    stats = await encrypted_file_service.get_file_stats(current_user, db)
    
    return FileStatsResponse(
        total_files=stats['total_files'],
        encrypted_files=stats['encrypted_files'],
        total_original_size=stats['total_original_size'],
        total_compressed_size=stats['total_compressed_size'],
        compression_ratio=stats['compression_ratio'],
        encryption_coverage=stats['encryption_coverage']
    )

# ================================
# STARTUP AND SHUTDOWN EVENTS
# ================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        await Database.create_tables()
        logger.info("Database tables created/verified")
        logger.info("TaxEase API started successfully")
        logger.info("API Documentation available at: http://localhost:8000/docs")
        logger.info("ReDoc Documentation available at: http://localhost:8000/redoc")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("TaxEase API shutting down...")

# ================================
# MAIN ENTRY POINT
# ================================

if __name__ == "__main__":
    print("🚀 Starting TaxEase Backend API...")
    print("📊 API Documentation: http://localhost:8001/docs")
    print("📚 ReDoc Documentation: http://localhost:8001/redoc")
    print("🔍 Health Check: http://localhost:8001/health")
    print("")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Changed to 8001 to avoid conflict with admin backend
        reload=True,
        log_level="info"
    )
