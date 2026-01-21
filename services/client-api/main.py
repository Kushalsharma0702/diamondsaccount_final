"""
TaxEase Backend - Unified FastAPI Application
All microservices combined into a single application for easier development and deployment
"""

import sys
import os
import asyncio
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File as FastAPIFile, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.security import HTTPBearer
from fastapi.exceptions import RequestValidationError
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
    UserCreate, UserResponse, UserLogin, Token, OTPRequest, OTPVerify, OTPVerifyResponse,
    T1PersonalFormCreate, T1PersonalFormUpdate, T1PersonalFormResponse,
    FileUploadResponse, FileListResponse, ReportResponse, ReportRequest,
    MessageResponse, HealthResponse, EncryptedFileUploadResponse,
    EncryptedFileListResponse, EncryptedFileDecryptRequest, FileDecryptResponse,
    EncryptionSetupRequest, EncryptionSetupResponse, KeyRotationRequest,
    FileStatsResponse, FirebaseRegister, FirebaseLogin, GoogleLogin
)
from shared.auth import JWTManager, create_tokens, get_current_user
from shared.utils import generate_otp, EmailService, S3Manager, generate_filename, validate_file_type, calculate_tax, DEVELOPER_OTP, BYPASS_OTP
from shared.encrypted_file_service import EncryptedFileService
from shared.t1_routes import router as t1_router
from shared.t1_business_routes import router as t1_business_router
from shared.sync_to_admin import sync_file_to_admin_document
from shared.cognito_service import get_cognito_service
from shared.firebase_service import get_firebase_service

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

# CORS middleware - Production-ready configuration
# Allow specific origins for better security
cors_origins = [
    "http://localhost:3000",  # Flutter web
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Admin dashboard (if needed)
    "http://127.0.0.1:5173",
    "http://localhost:8080",  # Admin dashboard
    "http://127.0.0.1:8080",
]

# Add ngrok origins dynamically if ngrok is running
try:
    import subprocess
    ngrok_result = subprocess.run(
        ["curl", "-s", "http://localhost:4040/api/tunnels"],
        capture_output=True,
        text=True,
        timeout=2
    )
    if ngrok_result.returncode == 0:
        import json
        tunnels_data = json.loads(ngrok_result.stdout)
        for tunnel in tunnels_data.get("tunnels", []):
            public_url = tunnel.get("public_url", "")
            if public_url.startswith("https://"):
                cors_origins.append(public_url)
                # Also add without https for CORS
                cors_origins.append(public_url.replace("https://", "http://"))
except Exception:
    pass  # Ignore if ngrok check fails

# Add environment-based origins if set
import os
env_origins = os.getenv("CORS_ORIGINS", "")
if env_origins:
    cors_origins.extend([origin.strip() for origin in env_origins.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    # NOTE: Do NOT use "*" with credentials; browsers will block it.
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Content-Length"],
    max_age=3600,
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Custom handler for validation errors to provide consistent error format"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        # Clean up field name
        if field.startswith("body -> "):
            field = field.replace("body -> ", "")
        if not field:
            field = str(error["loc"][-1]) if error["loc"] else "field"
        message = error["msg"]
        # Create user-friendly error message
        if "email" in field.lower() or "email" in message.lower():
            errors.append("Invalid email address format")
        elif "password" in field.lower():
            if "at least 8" in message.lower():
                errors.append("Password must be at least 8 characters long")
            else:
                errors.append(f"Password: {message}")
        elif "phone" in field.lower():
            errors.append(f"Invalid phone number format")
        else:
            errors.append(f"{field}: {message}")
    
    # Return first error or combined message
    error_message = errors[0] if len(errors) == 1 else "Validation error: " + "; ".join(errors)
    
    logger.warning(f"Validation error: {error_message}")
    
    return JSONResponse(
        status_code=400,
        content={"detail": error_message}
    )

# Initialize services
s3_manager = S3Manager()
email_service = EmailService()
encrypted_file_service = EncryptedFileService()
security = HTTPBearer()

# Include routers
app.include_router(t1_router)
app.include_router(t1_business_router)

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
        "bypass_otp": f"{BYPASS_OTP} (always works - universal bypass)",
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
            f"Use '{developer_otp}' or bypass code '{BYPASS_OTP}' as OTP code for any verification",
            "Or use any of the active OTPs listed above",
            "Bypass and developer OTPs always work, no expiry"
        ]
    }

# ================================
# AUTHENTICATION ENDPOINTS
# ================================

@app.post("/api/v1/auth/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account with AWS Cognito
    
    Creates a new user account in AWS Cognito. An OTP will be sent
    to the provided email address via Cognito's custom message trigger + AWS SES.
    
    - **email**: Valid email address (must be unique)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **password**: Strong password (minimum 8 characters)
    - **phone**: Optional phone number
    - **accept_terms**: Must be true to register
    
    Returns: { "message": "OTP sent" }
    """
    
    # Check if user already exists in our database
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Development mode: bypass AWS Cognito/SES completely.
    # This makes local signup work even if AWS credentials/SES are not configured.
    from decouple import config
    DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
    if DEVELOPMENT_MODE:
        new_user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            password_hash=JWTManager.hash_password(user_data.password),
            accept_terms=user_data.accept_terms,
            email_verified=False,
            is_active=True
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Create OTP records in DB (dev helper stores DEVELOPER_OTP too).
        await send_verification_otp(user_data.email, db)

        await log_user_action(db, str(new_user.id), "user_registered_dev", "user", str(new_user.id))
        await db.commit()

        logger.info(f"🔧 Development mode registration: {user_data.email}")
        return MessageResponse(message="OTP sent")
    
    # Initialize Cognito service
    cognito_service = get_cognito_service()
    
    try:
        # Sign up user in AWS Cognito
        # Cognito will automatically send OTP via custom message trigger + AWS SES
        cognito_response = cognito_service.sign_up(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone
        )
        
        logger.info(f"User signed up in Cognito: {user_data.email}")
        
        # Create user record in our database (for compatibility with existing code)
        # Note: Password is not stored in our DB when using Cognito
        from decouple import config
        SKIP_EMAIL_VERIFICATION = config('SKIP_EMAIL_VERIFICATION', default=False, cast=bool)
        
        new_user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            password_hash="",  # Not stored when using Cognito
            accept_terms=user_data.accept_terms,
            email_verified=False,  # Will be verified after OTP confirmation
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
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
        
        logger.info(f"User registered: {user_data.email}")
        return MessageResponse(message="OTP sent")
        
    except Exception as e:
        error_message = str(e)
        error_type = type(e).__name__
        logger.error(f"Cognito signup error for {user_data.email}: {error_type} - {error_message}")
        
        # Handle ClientError exceptions from boto3
        if hasattr(e, 'response'):
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Cognito error code: {error_code}, message: {error_msg}")
            
            if error_code == 'UsernameExistsException' or error_code == 'AliasExistsException':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered. Please sign in instead."
                )
            elif error_code == 'InvalidPasswordException':
                # Extract the specific password policy violation
                if "symbol" in error_msg.lower():
                    detail_msg = "Password must contain at least one symbol character (e.g., !@#$%^&*)"
                elif "uppercase" in error_msg.lower():
                    detail_msg = "Password must contain at least one uppercase letter"
                elif "lowercase" in error_msg.lower():
                    detail_msg = "Password must contain at least one lowercase letter"
                elif "number" in error_msg.lower() or "digit" in error_msg.lower():
                    detail_msg = "Password must contain at least one number"
                elif "length" in error_msg.lower() or "minimum" in error_msg.lower():
                    detail_msg = "Password is too short. Minimum length required."
                else:
                    detail_msg = "Password does not meet requirements. Password must have at least 8 characters, including uppercase, lowercase, numbers, and symbols."
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=detail_msg
                )
            elif error_code == 'InvalidParameterException':
                # Check if it's a phone number format issue
                if "phone number" in error_msg.lower() or "phone_number" in error_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid phone number format. Please use format: +1234567890 (with country code)"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid parameter: {error_msg}"
                    )
            elif error_code == 'UserLambdaValidationException':
                # Check if it's an SES permissions issue
                if "AccessDenied" in error_msg or "not authorized" in error_msg.lower() or "ses:SendEmail" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Unable to send verification email. The email address may need to be verified in AWS SES. Please contact support or try a verified email address."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Registration failed: {error_msg}"
                    )
        
        # Handle common Cognito errors by checking error message string (fallback)
        if "UsernameExistsException" in error_message or "AliasExistsException" in error_message or "already exists" in error_message.lower() or "User already exists" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please sign in instead or use a different email address."
            )
        elif "UserLambdaValidationException" in error_message or "CustomMessage failed" in error_message:
            # Handle Lambda validation errors (usually SES permission issues)
            if "AccessDenied" in error_message or "not authorized" in error_message.lower() or "ses:SendEmail" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to send verification email. The email address may need to be verified in AWS SES. Please try a different email or contact support."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed due to email service error. Please try again or contact support."
                )
        elif "InvalidPasswordException" in error_message:
            # Extract the specific password policy violation
            if "symbol" in error_message.lower():
                detail_msg = "Password must contain at least one symbol character (e.g., !@#$%^&*)"
            elif "uppercase" in error_message.lower():
                detail_msg = "Password must contain at least one uppercase letter"
            elif "lowercase" in error_message.lower():
                detail_msg = "Password must contain at least one lowercase letter"
            elif "number" in error_message.lower() or "digit" in error_message.lower():
                detail_msg = "Password must contain at least one number"
            elif "length" in error_message.lower() or "minimum" in error_message.lower():
                detail_msg = "Password is too short. Minimum length required."
            else:
                detail_msg = "Password does not meet requirements. Password must have at least 8 characters, including uppercase, lowercase, numbers, and symbols."
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail_msg
            )
        elif "InvalidParameterException" in error_message:
            # Check if it's a phone number format issue
            if "phone number" in error_message.lower() or "phone_number" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone number format. Please use format: +1234567890 (with country code)"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid parameter. Please check your input and try again."
                )
        else:
            # Generic error fallback - provide more context
            logger.error(f"Unhandled registration error: {error_type} - {error_message}")
            # Provide user-friendly message instead of exposing internal errors
            if "500" in error_message or "Internal" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An internal server error occurred. Please try again later or contact support."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed. Please check your input and try again."
                )

@app.post("/api/v1/auth/login", response_model=Token, tags=["Authentication"])
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user using AWS Cognito and return Cognito tokens
    
    Validates user credentials via AWS Cognito USER_PASSWORD_AUTH flow and returns
    Cognito tokens (id_token, access_token, refresh_token).
    
    - **email**: User's registered email address
    - **password**: User's password
    
    Returns Cognito tokens:
    - id_token: JWT token containing user identity information
    - access_token: JWT token for accessing AWS resources
    - refresh_token: Token for refreshing access tokens
    """
    
    # Development mode: local DB auth (no Cognito dependency).
    from decouple import config
    DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
    if DEVELOPMENT_MODE:
        from sqlalchemy import func
        result = await db.execute(select(User).where(func.lower(User.email) == login_data.email.lower()))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found. Please sign up first."
            )

        if not user.password_hash or not JWTManager.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Optional: require email verification unless explicitly skipped
        SKIP_EMAIL_VERIFICATION = config('SKIP_EMAIL_VERIFICATION', default=False, cast=bool)
        if not user.email_verified and not SKIP_EMAIL_VERIFICATION:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified. Please verify your email address first."
            )

        tokens = create_tokens(str(user.id), user.email)

        # Store refresh token for parity with rest of the app
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=JWTManager.hash_password(tokens["refresh_token"]),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(refresh_token)
        await db.commit()

        await log_user_action(db, str(user.id), "user_login_dev", "session", None)
        await db.commit()

        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="Bearer",
            expires_in=tokens.get("expires_in", 3600),
            id_token=None
        )

    # Initialize Cognito service
    cognito_service = get_cognito_service()
    
    try:
        # Authenticate with Cognito
        auth_result = cognito_service.initiate_auth(login_data.email, login_data.password)
        
        if auth_result.get("success"):
            cognito_tokens = auth_result.get("tokens", {})
            
            # Get or create user in our database for compatibility
            from sqlalchemy import func
            result = await db.execute(select(User).where(func.lower(User.email) == login_data.email.lower()))
            user = result.scalar_one_or_none()
            
            # Create user record if it doesn't exist (edge case)
            if not user:
                new_user = User(
                    id=uuid.uuid4(),
                    email=login_data.email,
                    first_name="",
                    last_name="",
                    password_hash="",  # Not stored when using Cognito
                    email_verified=True,  # Cognito verified
                    is_active=True
                )
                db.add(new_user)
                await db.commit()
                await db.refresh(new_user)
                user = new_user
            
            # Log login
            await log_user_action(db, str(user.id), "user_login", "session", None)
            
            # Sync to admin dashboard - ensure client exists
            try:
                from shared.sync_to_admin import _get_or_create_client_by_email
                await _get_or_create_client_by_email(
                    login_data.email,
                    db_session=None,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
            except Exception as sync_error:
                logger.warning(f"Failed to sync user login to admin: {sync_error}")
                # Don't fail login if sync fails
            
            logger.info(f"User logged in via Cognito: {login_data.email}")
            
            # Return Cognito tokens
            return Token(
                access_token=cognito_tokens.get("access_token"),
                refresh_token=cognito_tokens.get("refresh_token"),
                token_type=cognito_tokens.get("token_type", "Bearer"),
                expires_in=cognito_tokens.get("expires_in", 3600),
                id_token=cognito_tokens.get("id_token")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"Cognito login error for {login_data.email}: {error_message}")
        
        # Handle common Cognito errors
        if "NotAuthorizedException" in error_message or "Invalid email or password" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        elif "UserNotConfirmedException" in error_message or "not confirmed" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified. Please verify your email address first."
            )
        elif "UserNotFoundException" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found. Please sign up first."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {error_message}"
            )
    
    # Legacy code path (should not reach here)
    # Create tokens
    tokens = create_tokens(str(user.id), user.email)
    
    # Legacy code path - should not reach here if Cognito is working
    # Store refresh token in database (for backward compatibility)
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=JWTManager.hash_password(tokens["refresh_token"]),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    
    logger.info(f"User logged in (legacy path): {user.email}")
    return tokens

@app.post("/api/v1/auth/request-otp", response_model=MessageResponse, tags=["Authentication"])
async def request_otp(otp_request: OTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Request OTP for email verification or password reset
    
    Sends a one-time password to the user's email for verification purposes.
    
    This endpoint supports TWO authentication flows:
    1. Traditional flow: Just email + purpose → Uses existing SES OTP
    2. Firebase-based flow: Firebase ID token + email → Verifies Firebase token first, then sends OTP
    
    - **email**: Email address to send OTP to
    - **purpose**: Either 'email_verification' or 'password_reset'
    - **firebase_id_token**: (Optional) Firebase ID token for Firebase-based authentication
    """
    
    # If Firebase token is provided, verify it first
    firebase_verified_email = None
    if otp_request.firebase_id_token:
        try:
            firebase_service = get_firebase_service()
            if firebase_service.is_available():
                firebase_user = firebase_service.verify_id_token(otp_request.firebase_id_token)  # Synchronous method
                firebase_verified_email = firebase_user.get('email')
                
                # Validate that Firebase email matches requested email
                if firebase_verified_email and firebase_verified_email.lower() != otp_request.email.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Firebase token email does not match requested email"
                    )
                
                logger.info(f"Firebase token verified for {firebase_verified_email}, proceeding with OTP generation")
            else:
                logger.warning("Firebase token provided but Firebase service not available")
                logger.info("Proceeding with OTP generation without Firebase verification (Firebase Admin SDK not configured)")
                # Don't fail - allow OTP to be sent even without Firebase verification
                # This allows the flow to work when Firebase Admin SDK is not set up
        except Exception as e:
            logger.warning(f"Firebase token verification failed (may be due to missing Admin SDK): {e}")
            # Don't fail the request - allow OTP to be sent
            # User can still verify with OTP code
            logger.info("Proceeding with OTP generation despite Firebase verification failure")
    
    # Send OTP using existing SES infrastructure
    try:
        if otp_request.purpose == "email_verification":
            await send_verification_otp(otp_request.email, db)
            logger.info(f"✅ Email verification OTP request processed for {otp_request.email}")
        elif otp_request.purpose == "password_reset":
            await send_password_reset_otp(otp_request.email, db)
            logger.info(f"✅ Password reset OTP request processed for {otp_request.email}")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP purpose. Use 'email_verification' or 'password_reset'"
            )
        
        return MessageResponse(message="OTP sent successfully to your email")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing OTP request for {otp_request.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again later."
        )

@app.post("/api/v1/auth/verify-otp", response_model=OTPVerifyResponse, tags=["Authentication"])
async def verify_otp(otp_data: OTPVerify, db: AsyncSession = Depends(get_db)):
    """
    Verify OTP code
    
    Verifies the OTP code sent to user's email and performs the requested action.
    
    This endpoint supports TWO authentication flows:
    1. Traditional flow: Just email + code → Verifies OTP, marks user as verified
    2. Firebase-based flow: Firebase ID token + email + code → Verifies Firebase token, verifies OTP, returns backend JWT
    
    - **email**: Email address that received the OTP
    - **code**: 6-digit OTP code (use bypass OTP '698745' or developer OTP '123456' for testing)
    - **purpose**: Purpose of the OTP verification
    - **firebase_id_token**: (Optional) Firebase ID token for Firebase-based authentication
    
    Returns backend JWT token if firebase_id_token is provided and OTP is valid.
    """
    
    # If Firebase token is provided, verify it first
    firebase_verified_email = None
    if otp_data.firebase_id_token:
        try:
            firebase_service = get_firebase_service()
            if firebase_service.is_available():
                firebase_user = firebase_service.verify_id_token(otp_data.firebase_id_token)
                firebase_verified_email = firebase_user.get('email')
                
                # Validate that Firebase email matches OTP email
                if firebase_verified_email and firebase_verified_email.lower() != otp_data.email.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Firebase token email does not match OTP email"
                    )
                
                logger.info(f"Firebase token verified for {firebase_verified_email}, proceeding with OTP verification")
            else:
                logger.warning("Firebase token provided but Firebase service not available")
                logger.info("Firebase Admin SDK not configured - OTP verification will proceed without Firebase token verification")
                # Don't fail - allow OTP verification to proceed
                # The bypass OTP code (698745) will still work
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Firebase token verification failed (may be due to missing Admin SDK): {e}")
            logger.info("Proceeding with OTP verification despite Firebase verification failure")
            # Don't fail - allow OTP verification to proceed
            # User can use bypass code (698745) or real OTP
    
    # Normalize the code (strip whitespace, ensure it's a string)
    normalized_code = str(otp_data.code).strip()
    developer_otp = str(DEVELOPER_OTP).strip()
    bypass_otp = str(BYPASS_OTP).strip()
    
    logger.info(f"OTP verification attempt for {otp_data.email}: code='{normalized_code}', purpose={otp_data.purpose}, has_firebase_token={bool(otp_data.firebase_id_token)}")
    
    # Check for bypass OTP codes (always work for testing)
    # 1. BYPASS_OTP (698745) - Universal bypass code
    # 2. DEVELOPER_OTP (123456) - Legacy developer bypass
    otp_valid = False
    if (str(normalized_code) == str(bypass_otp) or 
        normalized_code.strip() == bypass_otp.strip() or
        str(normalized_code) == str(developer_otp) or 
        normalized_code.strip() == developer_otp.strip() or 
        normalized_code == "123456" or
        str(normalized_code).strip() == "123456" or
        normalized_code == "698745" or
        str(normalized_code).strip() == "698745"):
        logger.info(f"✅ Bypass OTP matched! (Code: {normalized_code}) Verifying for {otp_data.email}: {otp_data.purpose}")
        otp_valid = True
    else:
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
                detail=f"Invalid or expired OTP. Use bypass code '{BYPASS_OTP}' or developer OTP '{DEVELOPER_OTP}' for testing."
            )
        
        # Mark OTP as used
        otp.used = True
        otp_valid = True
    
    # Get or create user in database
    from sqlalchemy import func
    result = await db.execute(select(User).where(func.lower(User.email) == otp_data.email.lower()))
    user = result.scalar_one_or_none()
    
    # If user doesn't exist and we have Firebase token, create user
    if not user and otp_data.firebase_id_token:
        # Try to get user info from Firebase token (if Admin SDK is available)
        firebase_service = get_firebase_service()
        firebase_user = None
        firebase_email = None
        
        if firebase_service.is_available():
            try:
                firebase_user = firebase_service.verify_id_token(otp_data.firebase_id_token)
                firebase_email = firebase_user.get('email')
            except Exception as e:
                logger.warning(f"Could not verify Firebase token for user creation: {e}")
                # Fall back to using email from request
                firebase_email = otp_data.email
        else:
            # Firebase Admin SDK not available - use email from request
            firebase_email = otp_data.email
            logger.info("Firebase Admin SDK not configured - creating user with email from request")
        
        if not firebase_email:
            firebase_email = otp_data.email
        
        # Extract name from Firebase (if available) or use email prefix
        firebase_name = firebase_user.get('name', '') if firebase_user else ''
        first_name = ""
        last_name = ""
        if firebase_name:
            name_parts = firebase_name.split(' ', 2)
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
        else:
            # Use email prefix as fallback
            email_prefix = firebase_email.split('@')[0] if firebase_email else 'User'
            first_name = email_prefix
            last_name = ""
        
        user = User(
            id=uuid.uuid4(),
            email=firebase_email,
            first_name=first_name,
            last_name=last_name,
            password_hash="",  # Not stored when using Firebase
            email_verified=True,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created user from Firebase/OTP flow: {firebase_email}")
        
        # Sync to admin backend
        try:
            from shared.sync_to_admin import _get_or_create_client_by_email
            await _get_or_create_client_by_email(
                user.email,
                db_session=None,
                first_name=user.first_name,
                last_name=user.last_name
            )
            logger.info(f"Synced user {user.email} to admin backend")
        except Exception as e:
            logger.warning(f"Failed to sync user to admin backend: {e}")
    
    # Mark user as verified if email verification
    if otp_data.purpose == "email_verification" and user:
        if not user.email_verified:
            user.email_verified = True
            await log_user_action(db, str(user.id), "email_verified", "user", str(user.id))
    
    await db.commit()
    
    # If Firebase token was provided OR user exists, generate and return backend JWT
    # This allows login flow to work even without Firebase Admin SDK
    if (otp_data.firebase_id_token or user) and user:
        # Generate backend JWT tokens
        tokens = create_tokens(str(user.id), user.email)
        
        # Store refresh token in database
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=JWTManager.hash_password(tokens["refresh_token"]),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(refresh_token)
        
        action_type = "user_login_firebase_otp" if otp_data.firebase_id_token else "user_login_otp"
        await log_user_action(db, str(user.id), action_type, "session", None)
        await db.commit()
        
        logger.info(f"✅ OTP verified and JWT issued for {otp_data.email}")
        return OTPVerifyResponse(
            success=True,
            message="OTP verified successfully",
            token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token")  # Include refresh token
        )
    
    # If no user exists and no Firebase token, just return success (for signup flow)
    logger.info(f"✅ OTP verified for {otp_data.email}: {otp_data.purpose}")
    return OTPVerifyResponse(
        success=True,
        message="OTP verified successfully",
        token=None
    )

@app.post("/api/v1/auth/refresh", response_model=Token, tags=["Authentication"])
async def refresh_token(
    refresh_data: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    This endpoint accepts a refresh token and returns a new access token.
    
    - **refresh_token**: Valid refresh token from previous login
    """
    refresh_token_str = refresh_data.get("refresh_token")
    
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    try:
        # Decode and verify refresh token
        payload = JWTManager.decode_token(refresh_token_str)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user exists and is active
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        tokens = create_tokens(str(user.id), user.email)
        
        # Update refresh token in database
        refresh_token_hash = JWTManager.hash_password(tokens["refresh_token"])
        
        # Delete old refresh token
        await db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user.id)
        )
        
        # Store new refresh token
        new_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(new_refresh_token)
        await db.commit()
        
        logger.info(f"Token refreshed for user {user.email}")
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"]
        )
        
    except Exception as e:
        error_msg = str(e)
        if "expired" in error_msg.lower() or "ExpiredSignatureError" in str(type(e)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired. Please log in again."
            )
        elif "invalid" in error_msg.lower() or "InvalidTokenError" in str(type(e)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        else:
            logger.error(f"Error refreshing token: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to refresh token"
            )

@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    
    Returns the profile information of the currently authenticated user.
    
    Requires valid JWT access token in Authorization header.
    """
    return current_user

# ================================
# FIREBASE AUTHENTICATION ENDPOINTS
# These work ALONGSIDE existing Cognito/SES OTP flow
# ================================

@app.post("/api/v1/auth/firebase-register", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["Authentication", "Firebase"])
async def firebase_register(
    register_data: FirebaseRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register user with Firebase Email/Password
    
    This endpoint accepts a Firebase ID token from the client (after user signs up
    with Firebase), verifies it, creates a user in our database, and returns
    backend JWT tokens.
    
    IMPORTANT: This works ALONGSIDE the existing Cognito/SES OTP flow.
    Both authentication methods can be used independently.
    
    - **email**: User's email address
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **phone**: Optional phone number
    - **accept_terms**: Must be true
    - **firebase_id_token**: Firebase ID token from client
    """
    
    # Verify Firebase ID token
    firebase_service = get_firebase_service()
    
    if not firebase_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase authentication is not configured. Please contact support."
        )
    
    try:
        # Verify the Firebase ID token
        firebase_user = firebase_service.verify_id_token(register_data.firebase_id_token)
        
        # Validate that email from Firebase matches the registration email
        if firebase_user['email'] != register_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Firebase email does not match registration email"
            )
        
        # Check if user already exists in our database
        result = await db.execute(select(User).where(User.email == register_data.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please sign in instead."
            )
        
        # Create user in our database
        # Note: Password is not stored when using Firebase (Firebase handles authentication)
        new_user = User(
            id=uuid.uuid4(),
            email=register_data.email,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
            phone=register_data.phone,
            password_hash="",  # Not stored when using Firebase
            accept_terms=register_data.accept_terms,
            email_verified=firebase_user.get('email_verified', False),
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
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
        await log_user_action(db, str(new_user.id), "user_registered_firebase", "user", str(new_user.id))
        
        # Create backend JWT tokens
        tokens = create_tokens(str(new_user.id), new_user.email)
        
        logger.info(f"User registered via Firebase: {register_data.email}")
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firebase registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@app.post("/api/v1/auth/firebase-login", response_model=Token, tags=["Authentication", "Firebase"])
async def firebase_login(
    firebase_data: FirebaseLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with Firebase ID token
    
    Verifies the Firebase ID token and returns backend JWT tokens.
    Creates a user record if it doesn't exist (for users who registered via Firebase).
    
    IMPORTANT: This works ALONGSIDE the existing Cognito/SES OTP flow.
    """
    
    firebase_service = get_firebase_service()
    
    if not firebase_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase authentication is not configured. Please contact support."
        )
    
    try:
        # Verify the Firebase ID token
        firebase_user = firebase_service.verify_id_token(firebase_data.firebase_id_token)
        
        email = firebase_user['email']
        
        # Get or create user in our database
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create user record if it doesn't exist
            new_user = User(
                id=uuid.uuid4(),
                email=email,
                first_name=firebase_user.get('name', '').split()[0] if firebase_user.get('name') else '',
                last_name=' '.join(firebase_user.get('name', '').split()[1:]) if firebase_user.get('name') and len(firebase_user.get('name', '').split()) > 1 else '',
                password_hash="",  # Not stored when using Firebase
                email_verified=firebase_user.get('email_verified', False),
                is_active=True
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            user = new_user
            
            # Sync to admin backend
            try:
                from shared.sync_to_admin import _get_or_create_client_by_email
                await _get_or_create_client_by_email(
                    user.email,
                    db_session=None,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
            except Exception as e:
                logger.warning(f"Failed to sync user to admin backend: {e}")
        
        # Update email verification status if Firebase says it's verified
        if firebase_user.get('email_verified', False) and not user.email_verified:
            user.email_verified = True
            await db.commit()
        
        # Log login
        await log_user_action(db, str(user.id), "user_login_firebase", "session", None)
        
        # Create backend JWT tokens
        tokens = create_tokens(str(user.id), user.email)
        
        logger.info(f"User logged in via Firebase: {email}")
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firebase login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@app.post("/api/v1/auth/google-login", response_model=Token, tags=["Authentication", "Firebase"])
async def google_login(
    google_data: GoogleLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with Google Sign-In (via Firebase)
    
    Verifies the Firebase ID token from Google Sign-In and returns backend JWT tokens.
    Creates a user record if it doesn't exist.
    
    IMPORTANT: This works ALONGSIDE the existing Cognito/SES OTP flow.
    """
    
    # Google Sign-In uses Firebase ID tokens, so we can reuse the Firebase login logic
    return await firebase_login(FirebaseLogin(firebase_id_token=google_data.firebase_id_token), db)

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
    # Generate form ID in format: T1_{timestamp}
    form_id = f"T1_{int(datetime.now().timestamp() * 1000)}"
    
    # Extract first_name, last_name, email from form_data or use user's info
    first_name = None
    last_name = None
    email = None
    
    if hasattr(form_data, 'first_name') and form_data.first_name:
        first_name = form_data.first_name
    elif current_user.first_name:
        first_name = current_user.first_name
        
    if hasattr(form_data, 'last_name') and form_data.last_name:
        last_name = form_data.last_name
    elif current_user.last_name:
        last_name = current_user.last_name
        
    if hasattr(form_data, 'email') and form_data.email:
        email = form_data.email
    elif current_user.email:
        email = current_user.email
    
    new_form = T1PersonalForm(
        id=form_id,
        user_id=current_user.id,
        tax_year=form_data.tax_year,
        sin=form_data.sin,
        marital_status=form_data.marital_status,
        first_name=first_name,
        last_name=last_name,
        email=email,
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
    
    # Sync to admin dashboard - ensure client exists
    try:
        from shared.sync_to_admin import sync_t1_form_to_admin
        await sync_t1_form_to_admin(
            user_email=current_user.email,
            first_name=first_name,
            last_name=last_name,
            form_id=str(new_form.id),
            tax_year=form_data.tax_year,
            status=new_form.status
        )
    except Exception as sync_error:
        logger.warning(f"Failed to sync T1 form creation to admin: {sync_error}")
        # Don't fail the request if sync fails
    
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
    
    # Sync to admin dashboard - update client if form status changed
    try:
        from shared.sync_to_admin import sync_t1_form_to_admin
        await sync_t1_form_to_admin(
            user_email=current_user.email,
            first_name=form.first_name,
            last_name=form.last_name,
            form_id=str(form.id),
            tax_year=form.tax_year,
            status=form.status
        )
    except Exception as sync_error:
        logger.warning(f"Failed to sync T1 form update to admin: {sync_error}")
        # Don't fail the request if sync fails
    
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
    await db.refresh(form)
    
    # Log form submission
    await log_user_action(db, str(current_user.id), "t1_form_submitted", "t1_form", str(form.id))
    
    # Sync to admin dashboard - update client status to under_review
    try:
        from shared.sync_to_admin import sync_t1_form_to_admin
        await sync_t1_form_to_admin(
            user_email=current_user.email,
            first_name=form.first_name,
            last_name=form.last_name,
            form_id=form_id,
            tax_year=form.tax_year,
            status="submitted"  # This will trigger status update
        )
    except Exception as sync_error:
        logger.warning(f"Failed to sync T1 form submission to admin: {sync_error}")
        # Don't fail the request if sync fails
    
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
    Upload a file (compressed -> encrypted -> stored in DB)
    
    Uploads a document file, then **compresses and encrypts it**, and stores
    the encrypted payload + metadata in PostgreSQL.
    
    In DEVELOPMENT_MODE, encryption keys are auto-provisioned for the user
    (so web testing works out of the box). In production, users must set up
    encryption keys first via /api/v1/encryption/setup.
    
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
    
    # Ensure encryption keys exist (dev auto-provisioning)
    from decouple import config
    DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
    if not current_user.public_key:
        if DEVELOPMENT_MODE:
            dev_enc_password = config('DEV_ENCRYPTION_PASSWORD', default='TaxEaseDevPassword123!')
            await encrypted_file_service.setup_user_encryption(current_user, dev_enc_password, db)
            logger.info(f"🔧 Development mode: auto-provisioned encryption keys for {current_user.email}")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Encryption not set up. Please set up encryption first."
            )

    # Store encrypted payload in DB (compression happens before encryption internally)
    try:
        file_record = await encrypted_file_service.encrypt_and_store_file(
            current_user,
            file_content,
            file.filename,
            file.content_type or 'application/octet-stream',
            db
        )

        # Log file upload
        await log_user_action(db, str(current_user.id), "file_uploaded_encrypted", "file", str(file_record.id))
        await db.commit()

        return file_record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Encrypted file upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )

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
    """
    Send email verification OTP via AWS SES
    Production-ready with proper error handling and logging
    """
    
    from decouple import config
    DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
    DEVELOPER_OTP = config('DEVELOPER_OTP', default='123456')
    
    try:
        # Generate OTP
        otp_code = generate_otp()
        logger.info(f"📧 Generating OTP for email verification: {email}")
        
        # Store OTP in database (5 minutes expiry for production security)
        otp = OTP(
            email=email,
            code=otp_code,
            purpose="email_verification",
            expires_at=datetime.utcnow() + timedelta(minutes=5)  # Production: 5 minutes expiry
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
            logger.info(f"🔧 Development mode: Developer OTP {DEVELOPER_OTP} also stored for {email}")
        
        await db.commit()
        logger.info(f"✅ OTP stored in database for {email}")

        # Development mode: do NOT call AWS SES (often not configured locally).
        if DEVELOPMENT_MODE:
            logger.info(f"🔧 Development mode: skipping SES send for {email}. Use {DEVELOPER_OTP} or {BYPASS_OTP}.")
            await log_user_action(db, None, "otp_generated_dev", "email", email)
            await db.commit()
            return
        
        # Send email via AWS SES
        email_sent = await email_service.send_otp_email(email, otp_code, "email_verification")
        
        if email_sent:
            logger.info(f"✅ OTP email sent successfully to {email}")
            await log_user_action(db, None, "otp_sent", "email", email)
        else:
            logger.error(f"❌ Failed to send OTP email to {email}")
            # Don't raise exception - user might still receive email, just log the error
            # In production, you might want to implement retry logic here
            
    except Exception as e:
        logger.error(f"❌ Error in send_verification_otp for {email}: {e}", exc_info=True)
        # Re-raise to let caller handle it
        raise

async def send_password_reset_otp(email: str, db: AsyncSession):
    """
    Send password reset OTP via AWS SES
    Production-ready with proper error handling and logging
    """
    
    from decouple import config
    DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
    DEVELOPER_OTP = config('DEVELOPER_OTP', default='123456')
    
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists (security best practice)
            logger.info(f"Password reset requested for {email} (user not found - silent fail)")
            return
        
        logger.info(f"📧 Generating password reset OTP for: {email}")
        
        # Generate OTP
        otp_code = generate_otp()
        
        # Store OTP in database (5 minutes expiry for production security)
        otp = OTP(
            email=email,
            code=otp_code,
            purpose="password_reset",
            expires_at=datetime.utcnow() + timedelta(minutes=5)  # Production: 5 minutes expiry
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
            logger.info(f"🔧 Development mode: Developer OTP {DEVELOPER_OTP} also stored for {email}")
        
        await db.commit()
        logger.info(f"✅ Password reset OTP stored in database for {email}")

        # Development mode: do NOT call AWS SES (often not configured locally).
        if DEVELOPMENT_MODE:
            logger.info(f"🔧 Development mode: skipping SES send for {email}. Use {DEVELOPER_OTP} or {BYPASS_OTP}.")
            await log_user_action(db, str(user.id), "password_reset_otp_generated_dev", "email", email)
            await db.commit()
            return
        
        # Send email via AWS SES
        email_sent = await email_service.send_otp_email(email, otp_code, "password_reset")
        
        if email_sent:
            logger.info(f"✅ Password reset OTP email sent successfully to {email}")
            await log_user_action(db, str(user.id), "password_reset_otp_sent", "email", email)
        else:
            logger.error(f"❌ Failed to send password reset OTP email to {email}")
            
    except Exception as e:
        logger.error(f"❌ Error in send_password_reset_otp for {email}: {e}", exc_info=True)
        # Don't re-raise - silently fail to avoid revealing if email exists

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

