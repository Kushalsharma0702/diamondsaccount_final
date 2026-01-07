"""
Audit Logging for Tax-Ease API v2

Centralized audit logging with PII redaction.
Enforces INV-B009, AUDIT-001 through AUDIT-005.

Features:
- Logs all admin mutations to audit_logs table
- Redacts PII (passwords, tokens, SSNs)
- Captures authentication failures (401/403)
- Immutable audit trail
"""

import json
import re
import logging
from datetime import datetime
from typing import Optional, Any, Dict
from fastapi import Request, Response
from sqlalchemy.orm import Session

from database.schemas_v2 import AuditLog

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Configure Python logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

audit_logger = logging.getLogger("audit")


# ============================================================================
# PII REDACTION
# ============================================================================

# Patterns for PII detection
PII_PATTERNS = {
    "password": re.compile(r'"password"\s*:\s*"[^"]*"', re.IGNORECASE),
    "access_token": re.compile(r'"access_token"\s*:\s*"[^"]*"', re.IGNORECASE),
    "refresh_token": re.compile(r'"refresh_token"\s*:\s*"[^"]*"', re.IGNORECASE),
    "otp": re.compile(r'"otp"\s*:\s*"[^"]*"', re.IGNORECASE),
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "sin": re.compile(r'\b\d{3}-\d{3}-\d{3}\b'),  # Canadian SIN
    "credit_card": re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
}

REDACTED_VALUE = "[REDACTED]"


def redact_pii(data: str) -> str:
    """
    Redact PII from string data.
    
    Replaces:
    - Passwords
    - Tokens
    - OTP codes
    - SSN/SIN
    - Credit card numbers
    
    Returns: Redacted string
    """
    redacted = data
    
    # Redact JSON fields
    redacted = PII_PATTERNS["password"].sub(
        f'"password": "{REDACTED_VALUE}"',
        redacted
    )
    redacted = PII_PATTERNS["access_token"].sub(
        f'"access_token": "{REDACTED_VALUE}"',
        redacted
    )
    redacted = PII_PATTERNS["refresh_token"].sub(
        f'"refresh_token": "{REDACTED_VALUE}"',
        redacted
    )
    redacted = PII_PATTERNS["otp"].sub(
        f'"otp": "{REDACTED_VALUE}"',
        redacted
    )
    
    # Redact SSN/SIN
    redacted = PII_PATTERNS["ssn"].sub("XXX-XX-XXXX", redacted)
    redacted = PII_PATTERNS["sin"].sub("XXX-XXX-XXX", redacted)
    
    # Redact credit card
    redacted = PII_PATTERNS["credit_card"].sub("XXXX-XXXX-XXXX-XXXX", redacted)
    
    return redacted


def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact PII from dictionary.
    
    Returns: New dict with sensitive fields redacted
    """
    sensitive_keys = {
        "password",
        "access_token",
        "refresh_token",
        "otp",
        "ssn",
        "sin",
        "credit_card",
        "cvv",
        "pin"
    }
    
    redacted = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys:
            redacted[key] = REDACTED_VALUE
        elif isinstance(value, dict):
            redacted[key] = redact_dict(value)
        elif isinstance(value, list):
            redacted[key] = [
                redact_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            redacted[key] = value
    
    return redacted


# ============================================================================
# AUDIT LOG FUNCTIONS
# ============================================================================

def log_admin_mutation(
    db: Session,
    admin_user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    old_value: Optional[Dict] = None,
    new_value: Optional[Dict] = None,
    ip_address: Optional[str] = None
) -> None:
    """
    Log admin mutation to audit_logs table.
    
    Enforces INV-B009: All admin mutations MUST be logged.
    
    Args:
        db: Database session
        admin_user_id: ID of admin performing action
        action: Action type (CREATE, UPDATE, DELETE, STATUS_CHANGE)
        resource_type: Type of resource (Filing, Document, Payment, User)
        resource_id: ID of affected resource
        old_value: Previous value (for updates)
        new_value: New value (for creates/updates)
        ip_address: Admin's IP address
    """
    
    # Redact PII from values
    old_value_safe = redact_dict(old_value) if old_value else None
    new_value_safe = redact_dict(new_value) if new_value else None
    
    audit_log = AuditLog(
        user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_value=old_value_safe,
        new_value=new_value_safe,
        ip_address=ip_address,
        timestamp=datetime.utcnow()
    )
    
    db.add(audit_log)
    db.commit()
    
    # Also log to Python logger
    audit_logger.info(
        f"ADMIN_MUTATION: admin={admin_user_id} action={action} "
        f"resource={resource_type}/{resource_id} ip={ip_address}"
    )


def log_authentication_failure(
    user_id: Optional[str],
    email: Optional[str],
    reason: str,
    ip_address: str,
    endpoint: str
) -> None:
    """
    Log authentication/authorization failure.
    
    Enforces AUDIT-004: Log all 401/403 events.
    
    Args:
        user_id: User ID if known
        email: Email if known
        reason: Failure reason
        ip_address: Client IP
        endpoint: Attempted endpoint
    """
    
    audit_logger.warning(
        f"AUTH_FAILURE: user_id={user_id} email={email} "
        f"reason={reason} ip={ip_address} endpoint={endpoint}"
    )


def log_suspicious_activity(
    user_id: Optional[str],
    activity: str,
    details: Dict[str, Any],
    ip_address: str
) -> None:
    """
    Log suspicious activity.
    
    Examples:
    - Multiple failed OTP attempts
    - Account lockout triggered
    - Access to resources outside ownership
    
    Args:
        user_id: User ID if known
        activity: Type of suspicious activity
        details: Additional details
        ip_address: Client IP
    """
    
    details_safe = redact_dict(details)
    
    audit_logger.warning(
        f"SUSPICIOUS_ACTIVITY: user_id={user_id} activity={activity} "
        f"details={json.dumps(details_safe)} ip={ip_address}"
    )


def log_superadmin_action(
    db: Session,
    admin_user_id: str,
    action: str,
    target_user_id: Optional[str],
    details: Dict[str, Any],
    ip_address: str
) -> None:
    """
    Log superadmin privileged action.
    
    Enforces INV-B009: Superadmin actions MUST be logged.
    
    Examples:
    - Override authorization (access any filing)
    - Assign filing to admin
    - Modify user roles
    
    Args:
        db: Database session
        admin_user_id: Superadmin user ID
        action: Action performed
        target_user_id: User affected (if applicable)
        details: Action details
        ip_address: Superadmin's IP
    """
    
    details_safe = redact_dict(details)
    
    audit_log = AuditLog(
        user_id=admin_user_id,
        action=f"SUPERADMIN_{action}",
        resource_type="User" if target_user_id else "System",
        resource_id=target_user_id or "system",
        new_value=details_safe,
        ip_address=ip_address,
        timestamp=datetime.utcnow()
    )
    
    db.add(audit_log)
    db.commit()
    
    audit_logger.warning(
        f"SUPERADMIN_ACTION: admin={admin_user_id} action={action} "
        f"target={target_user_id} ip={ip_address}"
    )


# ============================================================================
# REQUEST/RESPONSE LOGGING
# ============================================================================

async def log_request(
    request: Request,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log incoming request.
    
    Returns: Request metadata for response logging
    """
    
    # Get client IP
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0].strip() if forwarded else (
        request.client.host if request.client else "unknown"
    )
    
    # Body logging disabled - causes request stream consumption
    # The proper fix requires implementing custom middleware with body caching
    # See: https://fastapi.tiangolo.com/advanced/middleware/#accessing-the-request-body-in-middleware  
    body = None
    
    metadata = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "query": str(request.query_params),
        "user_id": user_id,
        "ip": ip,
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "body": body
    }
    
    # Log info-level for normal requests
    audit_logger.info(
        f"REQUEST: {request.method} {request.url.path} "
        f"user={user_id} ip={ip}"
    )
    
    return metadata


def log_response(
    request_metadata: Dict[str, Any],
    response: Response,
    status_code: int
) -> None:
    """
    Log response.
    
    Special handling for 401/403 (auth failures).
    """
    
    duration = (
        datetime.utcnow() - 
        datetime.fromisoformat(request_metadata["timestamp"])
    ).total_seconds()
    
    # Log auth failures at WARNING level
    if status_code in [401, 403]:
        audit_logger.warning(
            f"AUTH_FAILURE_RESPONSE: {request_metadata['method']} "
            f"{request_metadata['path']} status={status_code} "
            f"user={request_metadata.get('user_id')} "
            f"ip={request_metadata['ip']} duration={duration:.3f}s"
        )
        
        # Log to dedicated function
        log_authentication_failure(
            user_id=request_metadata.get("user_id"),
            email=None,  # Extract from request if needed
            reason=f"HTTP {status_code}",
            ip_address=request_metadata["ip"],
            endpoint=request_metadata["path"]
        )
    else:
        audit_logger.info(
            f"RESPONSE: {request_metadata['method']} "
            f"{request_metadata['path']} status={status_code} "
            f"user={request_metadata.get('user_id')} "
            f"duration={duration:.3f}s"
        )


# ============================================================================
# MIDDLEWARE
# ============================================================================

async def audit_middleware(request: Request, call_next):
    """
    Audit logging middleware.
    
    Logs:
    - All requests
    - All responses
    - Authentication failures (401/403)
    - Response times
    
    PII is automatically redacted.
    """
    
    # Extract user_id from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    
    # Log request
    request_metadata = await log_request(request, user_id)
    
    # Call next middleware/endpoint
    response = await call_next(request)
    
    # Log response
    log_response(request_metadata, response, response.status_code)
    
    return response


# ============================================================================
# HELPER: GET CLIENT IP
# ============================================================================

def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
