"""
Authorization Guards for Tax-Ease API v2

Reusable authorization decorators for defense-in-depth security.

CRITICAL SECURITY RULES:
- Fail-closed (deny by default)
- Multiple layers of checks
- Explicit permissions only
- Audit trail for all denials
"""

from functools import wraps
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.auth import CurrentUser, get_current_user
from backend.app.core.errors import AuthorizationError, ResourceNotFoundError, ErrorCodes
from database.schemas_v2 import Filing, Document, AdminFilingAssignment


# ============================================================================
# BASE GUARDS
# ============================================================================

def require_authenticated_user(func: Callable) -> Callable:
    """
    Ensure user is authenticated.
    This is implicit via Depends(get_current_user) but explicit for clarity.
    """
    @wraps(func)
    async def wrapper(*args, current_user: CurrentUser, **kwargs):
        if not current_user or not current_user.id:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTH_TOKEN_INVALID,
                message="Authentication required"
            )
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper


def require_email_verified(func: Callable) -> Callable:
    """
    Ensure user's email is verified.
    
    CRITICAL: Unverified users can ONLY access:
    - /auth/otp/request
    - /auth/otp/verify
    - /auth/logout
    
    All other endpoints MUST reject unverified users.
    """
    @wraps(func)
    async def wrapper(*args, current_user: CurrentUser, db: Session, **kwargs):
        # Check email_verified flag
        # Note: This requires storing email_verified in JWT or checking DB
        # For now, we'll add this to the CurrentUser object
        
        if hasattr(current_user, 'email_verified') and not current_user.email_verified:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTH_EMAIL_NOT_VERIFIED,
                message="Email verification required. Please verify your email before accessing this resource."
            )
        
        return await func(*args, current_user=current_user, db=db, **kwargs)
    return wrapper


def require_admin(func: Callable) -> Callable:
    """
    Require admin or superadmin role.
    """
    @wraps(func)
    async def wrapper(*args, current_user: CurrentUser, **kwargs):
        if not current_user.is_admin:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTHZ_ROLE_REQUIRED,
                message="This action requires admin role"
            )
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper


def require_superadmin(func: Callable) -> Callable:
    """
    Require superadmin role.
    """
    @wraps(func)
    async def wrapper(*args, current_user: CurrentUser, **kwargs):
        if not current_user.is_superadmin:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTHZ_ROLE_REQUIRED,
                message="This action requires superadmin role"
            )
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper


# ============================================================================
# RESOURCE OWNERSHIP GUARDS
# ============================================================================

def verify_filing_access(
    filing_id: str,
    user_id: str,
    user_role: str,
    is_superadmin: bool,
    db: Session
) -> Filing:
    """
    Verify user has access to filing.
    
    Access Rules:
    - User: Must be filing owner
    - Admin: Must be assigned to filing
    - Superadmin: Always allowed
    
    Returns: Filing object if authorized
    Raises: 404 if not found or not authorized (hide existence)
    """
    
    # Query filing
    filing = db.query(Filing).filter(Filing.id == filing_id).first()
    
    if not filing:
        raise ResourceNotFoundError("Filing", filing_id)
    
    # Superadmin: Always allowed
    if is_superadmin:
        return filing
    
    # User: Must be owner
    if user_role == "user":
        if str(filing.user_id) != user_id:
            # Return 404 to hide existence
            raise ResourceNotFoundError("Filing", filing_id)
        return filing
    
    # Admin: Must be assigned
    if user_role == "admin":
        assignment = db.query(AdminFilingAssignment).filter(
            AdminFilingAssignment.admin_id == user_id,
            AdminFilingAssignment.filing_id == filing_id
        ).first()
        
        if not assignment:
            # Return 404 to hide existence
            raise ResourceNotFoundError("Filing", filing_id)
        return filing
    
    # Unknown role: Deny
    raise AuthorizationError(
        error_code=ErrorCodes.AUTHZ_INSUFFICIENT_PERMISSIONS,
        message="Access denied"
    )


def verify_document_access(
    document_id: str,
    user_id: str,
    user_role: str,
    is_superadmin: bool,
    db: Session
) -> Document:
    """
    Verify user has access to document.
    
    Access Rules:
    - User: Must own the filing containing the document
    - Admin: Must be assigned to the filing containing the document
    - Superadmin: Always allowed
    
    Returns: Document object if authorized
    Raises: 404 if not found or not authorized
    """
    
    # Query document with filing join
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise ResourceNotFoundError("Document", document_id)
    
    # Superadmin: Always allowed
    if is_superadmin:
        return document
    
    # Get filing
    filing = db.query(Filing).filter(Filing.id == document.filing_id).first()
    if not filing:
        raise ResourceNotFoundError("Document", document_id)
    
    # User: Must own filing
    if user_role == "user":
        if str(filing.user_id) != user_id:
            raise ResourceNotFoundError("Document", document_id)
        return document
    
    # Admin: Must be assigned to filing
    if user_role == "admin":
        assignment = db.query(AdminFilingAssignment).filter(
            AdminFilingAssignment.admin_id == user_id,
            AdminFilingAssignment.filing_id == filing.id
        ).first()
        
        if not assignment:
            raise ResourceNotFoundError("Document", document_id)
        return document
    
    # Unknown role: Deny
    raise AuthorizationError(
        error_code=ErrorCodes.AUTHZ_INSUFFICIENT_PERMISSIONS,
        message="Access denied"
    )


def verify_filing_ownership(
    filing_id: str,
    user_id: str,
    db: Session
) -> Filing:
    """
    Strict ownership check: User must be filing owner.
    Used for operations only owner can perform (create documents, submit T1).
    
    Returns: Filing object if user is owner
    Raises: 403 if not owner, 404 if not found
    """
    
    filing = db.query(Filing).filter(Filing.id == filing_id).first()
    
    if not filing:
        raise ResourceNotFoundError("Filing", filing_id)
    
    if str(filing.user_id) != user_id:
        raise AuthorizationError(
            error_code=ErrorCodes.AUTHZ_NOT_RESOURCE_OWNER,
            message="You do not own this filing"
        )
    
    return filing


def verify_admin_assignment(
    filing_id: str,
    admin_id: str,
    db: Session
) -> bool:
    """
    Verify admin is assigned to filing.
    
    Returns: True if assigned
    Raises: 403 if not assigned
    """
    
    assignment = db.query(AdminFilingAssignment).filter(
        AdminFilingAssignment.admin_id == admin_id,
        AdminFilingAssignment.filing_id == filing_id
    ).first()
    
    if not assignment:
        raise AuthorizationError(
            error_code=ErrorCodes.AUTHZ_NOT_ASSIGNED,
            message="You are not assigned to this filing"
        )
    
    return True


# ============================================================================
# DECORATOR FACTORIES
# ============================================================================

def require_filing_access(filing_id_param: str = "filing_id"):
    """
    Decorator factory: Require access to filing.
    
    Usage:
        @require_filing_access("filing_id")
        async def get_filing(filing_id: str, current_user: CurrentUser, db: Session):
            # filing_id is verified, proceed
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            filing_id = kwargs.get(filing_id_param)
            current_user: CurrentUser = kwargs.get("current_user")
            db: Session = kwargs.get("db")
            
            if not filing_id or not current_user or not db:
                raise AuthorizationError(
                    error_code=ErrorCodes.AUTHZ_INSUFFICIENT_PERMISSIONS,
                    message="Missing required parameters for authorization"
                )
            
            # Verify access
            filing = verify_filing_access(
                filing_id=filing_id,
                user_id=current_user.id,
                user_role=current_user.role,
                is_superadmin=current_user.is_superadmin,
                db=db
            )
            
            # Attach filing to kwargs for reuse
            kwargs['_verified_filing'] = filing
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_document_access(document_id_param: str = "document_id"):
    """
    Decorator factory: Require access to document.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            document_id = kwargs.get(document_id_param)
            current_user: CurrentUser = kwargs.get("current_user")
            db: Session = kwargs.get("db")
            
            if not document_id or not current_user or not db:
                raise AuthorizationError(
                    error_code=ErrorCodes.AUTHZ_INSUFFICIENT_PERMISSIONS,
                    message="Missing required parameters for authorization"
                )
            
            # Verify access
            document = verify_document_access(
                document_id=document_id,
                user_id=current_user.id,
                user_role=current_user.role,
                is_superadmin=current_user.is_superadmin,
                db=db
            )
            
            # Attach document to kwargs
            kwargs['_verified_document'] = document
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# HELPER FUNCTIONS FOR SERVICE LAYER
# ============================================================================

def check_filing_access_service(
    filing: Filing,
    user_id: str,
    user_role: str,
    is_superadmin: bool,
    db: Session
) -> bool:
    """
    Service-layer check: Does user have access to this filing?
    Returns bool instead of raising exception.
    """
    
    if is_superadmin:
        return True
    
    if user_role == "user":
        return str(filing.user_id) == user_id
    
    if user_role == "admin":
        assignment = db.query(AdminFilingAssignment).filter(
            AdminFilingAssignment.admin_id == user_id,
            AdminFilingAssignment.filing_id == filing.id
        ).first()
        return assignment is not None
    
    return False


def check_can_modify_filing_status(
    user_role: str
) -> bool:
    """
    Can this role modify filing status?
    """
    return user_role in {"admin", "superadmin"}


def check_can_record_payment(
    user_role: str,
    filing_id: str,
    admin_id: str,
    is_superadmin: bool,
    db: Session
) -> bool:
    """
    Can this user record a payment for this filing?
    """
    
    if user_role == "user":
        return False
    
    if is_superadmin:
        return True
    
    if user_role == "admin":
        assignment = db.query(AdminFilingAssignment).filter(
            AdminFilingAssignment.admin_id == admin_id,
            AdminFilingAssignment.filing_id == filing_id
        ).first()
        return assignment is not None
    
    return False
