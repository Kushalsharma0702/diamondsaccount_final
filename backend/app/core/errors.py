"""
Error handling system for Tax-Ease API v2

Standardized error responses with error codes
"""

from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel


# ============================================================================
# ERROR RESPONSE MODELS
# ============================================================================

class ErrorDetail(BaseModel):
    """Field-level error detail"""
    field: str
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None


# ============================================================================
# ERROR CODES
# ============================================================================

class ErrorCodes:
    """Standard error codes"""
    
    # Authentication (AUTH_*)
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_EMAIL_NOT_VERIFIED = "AUTH_EMAIL_NOT_VERIFIED"
    AUTH_ACCOUNT_INACTIVE = "AUTH_ACCOUNT_INACTIVE"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_TOKEN_REVOKED = "AUTH_TOKEN_REVOKED"
    AUTH_TOKEN_BLACKLISTED = "AUTH_TOKEN_BLACKLISTED"
    AUTH_MISSING_TOKEN = "AUTH_MISSING_TOKEN"
    AUTH_REFRESH_TOKEN_INVALID = "AUTH_REFRESH_TOKEN_INVALID"
    
    # Authorization (AUTHZ_*)
    AUTHZ_INSUFFICIENT_PERMISSIONS = "AUTHZ_INSUFFICIENT_PERMISSIONS"
    AUTHZ_NOT_RESOURCE_OWNER = "AUTHZ_NOT_RESOURCE_OWNER"
    AUTHZ_NOT_ASSIGNED = "AUTHZ_NOT_ASSIGNED"
    AUTHZ_ROLE_REQUIRED = "AUTHZ_ROLE_REQUIRED"
    
    # Validation (VALIDATION_*)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    VALIDATION_REQUIRED_FIELD = "VALIDATION_REQUIRED_FIELD"
    VALIDATION_INVALID_FORMAT = "VALIDATION_INVALID_FORMAT"
    VALIDATION_OUT_OF_RANGE = "VALIDATION_OUT_OF_RANGE"
    VALIDATION_TOO_LONG = "VALIDATION_TOO_LONG"
    VALIDATION_TOO_SHORT = "VALIDATION_TOO_SHORT"
    VALIDATION_INVALID_EMAIL = "VALIDATION_INVALID_EMAIL"
    VALIDATION_INVALID_PHONE = "VALIDATION_INVALID_PHONE"
    VALIDATION_INVALID_UUID = "VALIDATION_INVALID_UUID"
    VALIDATION_WEAK_PASSWORD = "VALIDATION_WEAK_PASSWORD"
    
    # Resource (RESOURCE_*)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RESOURCE_LOCKED = "RESOURCE_LOCKED"
    RESOURCE_DELETED = "RESOURCE_DELETED"
    
    # Business Logic (BUSINESS_*)
    BUSINESS_DUPLICATE_FILING = "BUSINESS_DUPLICATE_FILING"
    BUSINESS_T1_ALREADY_SUBMITTED = "BUSINESS_T1_ALREADY_SUBMITTED"
    BUSINESS_INVALID_STATUS_TRANSITION = "BUSINESS_INVALID_STATUS_TRANSITION"
    BUSINESS_PAYMENT_EXCEEDS_FEE = "BUSINESS_PAYMENT_EXCEEDS_FEE"
    BUSINESS_OTP_EXPIRED = "BUSINESS_OTP_EXPIRED"
    BUSINESS_OTP_INVALID = "BUSINESS_OTP_INVALID"
    BUSINESS_OTP_ALREADY_USED = "BUSINESS_OTP_ALREADY_USED"
    
    # File (FILE_*)
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_INVALID_TYPE = "FILE_INVALID_TYPE"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_ENCRYPTION_FAILED = "FILE_ENCRYPTION_FAILED"
    FILE_DECRYPTION_FAILED = "FILE_DECRYPTION_FAILED"
    
    # Rate Limiting (RATE_*)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Server (SERVER_*)
    SERVER_INTERNAL_ERROR = "SERVER_INTERNAL_ERROR"
    SERVER_DATABASE_ERROR = "SERVER_DATABASE_ERROR"
    SERVER_EXTERNAL_SERVICE_ERROR = "SERVER_EXTERNAL_SERVICE_ERROR"
    
    # Feature (FEATURE_*)
    FEATURE_NOT_IMPLEMENTED = "FEATURE_NOT_IMPLEMENTED"
    
    # Idempotency
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class APIException(HTTPException):
    """Base API exception with error code"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class AuthenticationError(APIException):
    """Authentication error (401)"""
    
    def __init__(self, error_code: str = ErrorCodes.AUTH_TOKEN_INVALID, message: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            message=message
        )


class AuthorizationError(APIException):
    """Authorization error (403)"""
    
    def __init__(self, error_code: str = ErrorCodes.AUTHZ_INSUFFICIENT_PERMISSIONS, message: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            message=message
        )


class ResourceNotFoundError(APIException):
    """Resource not found (404)"""
    
    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        details = {"resource_type": resource_type}
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCodes.RESOURCE_NOT_FOUND,
            message=f"{resource_type} not found",
            details=details
        )


class ResourceConflictError(APIException):
    """Resource conflict (409)"""
    
    def __init__(self, error_code: str, message: str, details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code=error_code,
            message=message,
            details=details
        )


class ValidationError(APIException):
    """Validation error (422)"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[List[ErrorDetail]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=ErrorCodes.VALIDATION_ERROR,
            message=message,
            details={"errors": [d.dict() if isinstance(d, ErrorDetail) else d for d in details]} if details else None
        )


class RateLimitError(APIException):
    """Rate limit exceeded (429)"""
    
    def __init__(self, retry_after: int, limit: int, window: str):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
            message=f"Too many requests. Try again in {retry_after} seconds.",
            details={
                "retry_after": retry_after,
                "limit": limit,
                "window": window
            }
        )


class FeatureNotImplementedError(APIException):
    """Feature not implemented (501)"""
    
    def __init__(self, reason: str, alternative: str):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            error_code=ErrorCodes.FEATURE_NOT_IMPLEMENTED,
            message="This feature is not available.",
            details={
                "reason": reason,
                "alternative": alternative
            }
        )


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "details": exc.details,
                "trace_id": request.state.trace_id if hasattr(request.state, "trace_id") else None
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "code": error["type"],
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": ErrorCodes.VALIDATION_ERROR,
                "message": "Request validation failed",
                "details": {"errors": errors},
                "trace_id": request.state.trace_id if hasattr(request.state, "trace_id") else None
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    # Log the full error internally
    print(f"Unexpected error: {exc}")
    
    # Return generic error to user
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCodes.SERVER_INTERNAL_ERROR,
                "message": "An unexpected error occurred. Please try again later.",
                "trace_id": request.state.trace_id if hasattr(request.state, "trace_id") else None
            }
        }
    )


# ============================================================================
# ERROR FACTORY HELPERS
# ============================================================================

def create_validation_error(field: str, code: str, message: str) -> ErrorDetail:
    """Create a validation error detail"""
    return ErrorDetail(field=field, code=code, message=message)


def invalid_email_error(field: str = "email") -> ErrorDetail:
    """Invalid email error"""
    return create_validation_error(
        field=field,
        code=ErrorCodes.VALIDATION_INVALID_EMAIL,
        message="Invalid email format"
    )


def weak_password_error(field: str = "password") -> ErrorDetail:
    """Weak password error"""
    return create_validation_error(
        field=field,
        code=ErrorCodes.VALIDATION_WEAK_PASSWORD,
        message="Password must be at least 8 characters and contain uppercase, lowercase, and number"
    )


def required_field_error(field: str) -> ErrorDetail:
    """Required field missing"""
    return create_validation_error(
        field=field,
        code=ErrorCodes.VALIDATION_REQUIRED_FIELD,
        message=f"{field} is required"
    )
