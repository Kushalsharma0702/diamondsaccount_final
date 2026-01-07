"""
State Machine Validation for Tax-Ease API v2

Enforces valid state transitions for Filing and Document resources.
CRITICAL: These rules prevent data corruption and workflow violations.

State machines are LOCKED and FINAL.
"""

from typing import Optional, Set, Tuple
from enum import Enum


# ============================================================================
# FILING STATE MACHINE
# ============================================================================

class FilingStatus(str, Enum):
    """Filing status enum - MUST match database enum"""
    DOCUMENTS_PENDING = "documents_pending"
    SUBMITTED = "submitted"
    PAYMENT_REQUEST_SENT = "payment_request_sent"
    PAYMENT_COMPLETED = "payment_completed"
    IN_PREPARATION = "in_preparation"
    AWAITING_APPROVAL = "awaiting_approval"
    FILED = "filed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ALLOWED TRANSITIONS (from_status → to_status)
FILING_TRANSITIONS: dict[FilingStatus, Set[FilingStatus]] = {
    FilingStatus.DOCUMENTS_PENDING: {
        FilingStatus.SUBMITTED,
        FilingStatus.CANCELLED,
    },
    FilingStatus.SUBMITTED: {
        FilingStatus.PAYMENT_REQUEST_SENT,
        FilingStatus.IN_PREPARATION,  # If prepayment not required
        FilingStatus.CANCELLED,
    },
    FilingStatus.PAYMENT_REQUEST_SENT: {
        FilingStatus.PAYMENT_COMPLETED,
        FilingStatus.CANCELLED,
    },
    FilingStatus.PAYMENT_COMPLETED: {
        FilingStatus.IN_PREPARATION,
    },
    FilingStatus.IN_PREPARATION: {
        FilingStatus.AWAITING_APPROVAL,
        FilingStatus.DOCUMENTS_PENDING,  # Need more docs
    },
    FilingStatus.AWAITING_APPROVAL: {
        FilingStatus.FILED,
        FilingStatus.IN_PREPARATION,  # Needs changes
    },
    FilingStatus.FILED: {
        FilingStatus.COMPLETED,
    },
    FilingStatus.COMPLETED: set(),  # Terminal state
    FilingStatus.CANCELLED: set(),  # Terminal state
}


def validate_filing_transition(
    from_status: str,
    to_status: str,
    user_role: str = "user"
) -> Tuple[bool, Optional[str]]:
    """
    Validate if a filing status transition is allowed.
    
    Args:
        from_status: Current filing status
        to_status: Desired filing status
        user_role: Role performing transition (user/admin/superadmin)
    
    Returns:
        (is_valid, error_message)
    
    Rules:
        - Users CANNOT change filing status (only admins)
        - Transitions must follow state machine
        - Terminal states (completed, cancelled) cannot be changed
        - Superadmin can override (with audit log)
    """
    
    # Rule: Only admins can change status
    if user_role == "user":
        return False, "Users cannot modify filing status"
    
    # Same status is always allowed (idempotent)
    if from_status == to_status:
        return True, None
    
    # Parse statuses
    try:
        from_state = FilingStatus(from_status)
        to_state = FilingStatus(to_status)
    except ValueError as e:
        return False, f"Invalid status value: {e}"
    
    # Check if transition is allowed
    allowed_transitions = FILING_TRANSITIONS.get(from_state, set())
    
    if to_state not in allowed_transitions:
        # Superadmin can override (but it's logged)
        if user_role == "superadmin":
            return True, None  # Allowed but will be audit-logged
        
        return False, (
            f"Invalid transition: {from_status} → {to_status}. "
            f"Allowed transitions: {[s.value for s in allowed_transitions]}"
        )
    
    return True, None


def get_allowed_filing_transitions(from_status: str) -> list[str]:
    """Get list of allowed next statuses from current status"""
    try:
        from_state = FilingStatus(from_status)
        return [s.value for s in FILING_TRANSITIONS.get(from_state, set())]
    except ValueError:
        return []


# ============================================================================
# DOCUMENT STATE MACHINE
# ============================================================================

class DocumentStatus(str, Enum):
    """Document status enum - MUST match database enum"""
    PENDING = "pending"
    COMPLETE = "complete"
    MISSING = "missing"
    APPROVED = "approved"
    REUPLOAD_REQUESTED = "reupload_requested"


# ALLOWED TRANSITIONS
DOCUMENT_TRANSITIONS: dict[DocumentStatus, Set[DocumentStatus]] = {
    DocumentStatus.PENDING: {
        DocumentStatus.COMPLETE,
        DocumentStatus.MISSING,
        DocumentStatus.REUPLOAD_REQUESTED,
    },
    DocumentStatus.COMPLETE: {
        DocumentStatus.APPROVED,
        DocumentStatus.REUPLOAD_REQUESTED,
    },
    DocumentStatus.MISSING: {
        DocumentStatus.PENDING,  # User uploads
    },
    DocumentStatus.APPROVED: {
        DocumentStatus.REUPLOAD_REQUESTED,  # Admin needs changes
    },
    DocumentStatus.REUPLOAD_REQUESTED: {
        DocumentStatus.PENDING,  # User uploads new version
    },
}


def validate_document_transition(
    from_status: str,
    to_status: str,
    user_role: str = "user"
) -> Tuple[bool, Optional[str]]:
    """
    Validate if a document status transition is allowed.
    
    Args:
        from_status: Current document status
        to_status: Desired document status
        user_role: Role performing transition
    
    Returns:
        (is_valid, error_message)
    
    Rules:
        - Users can only: missing → pending (by uploading)
        - Admins can: pending → complete/reupload_requested
        - Admins can: complete → approved/reupload_requested
        - Superadmin can override
    """
    
    # Same status is always allowed
    if from_status == to_status:
        return True, None
    
    # Parse statuses
    try:
        from_state = DocumentStatus(from_status)
        to_state = DocumentStatus(to_status)
    except ValueError as e:
        return False, f"Invalid status value: {e}"
    
    # Check role-based permissions
    if user_role == "user":
        # Users can only upload (missing → pending)
        if from_state == DocumentStatus.MISSING and to_state == DocumentStatus.PENDING:
            return True, None
        if from_state == DocumentStatus.REUPLOAD_REQUESTED and to_state == DocumentStatus.PENDING:
            return True, None
        return False, "Users can only upload documents to change status"
    
    # Check if transition is allowed
    allowed_transitions = DOCUMENT_TRANSITIONS.get(from_state, set())
    
    if to_state not in allowed_transitions:
        if user_role == "superadmin":
            return True, None  # Superadmin override (logged)
        
        return False, (
            f"Invalid transition: {from_status} → {to_status}. "
            f"Allowed transitions: {[s.value for s in allowed_transitions]}"
        )
    
    return True, None


def get_allowed_document_transitions(from_status: str, user_role: str = "admin") -> list[str]:
    """Get list of allowed next statuses from current status"""
    try:
        from_state = DocumentStatus(from_status)
        allowed = DOCUMENT_TRANSITIONS.get(from_state, set())
        
        # Filter by role
        if user_role == "user":
            # Users can only transition to pending (by uploading)
            if from_state in {DocumentStatus.MISSING, DocumentStatus.REUPLOAD_REQUESTED}:
                return [DocumentStatus.PENDING.value]
            return []
        
        return [s.value for s in allowed]
    except ValueError:
        return []


# ============================================================================
# T1 FORM STATE MACHINE
# ============================================================================

class T1FormStatus(str, Enum):
    """T1 form status enum"""
    DRAFT = "draft"
    SUBMITTED = "submitted"


def validate_t1_transition(
    from_status: str,
    to_status: str,
    user_role: str = "user"
) -> Tuple[bool, Optional[str]]:
    """
    Validate T1 form status transition.
    
    Rules:
        - Users can: draft → submitted (one-way, immutable)
        - Admins can edit draft forms
        - Submitted forms cannot be edited (create new version instead)
    """
    
    if from_status == to_status:
        return True, None
    
    try:
        from_state = T1FormStatus(from_status)
        to_state = T1FormStatus(to_status)
    except ValueError as e:
        return False, f"Invalid status: {e}"
    
    # Only valid transition: draft → submitted
    if from_state == T1FormStatus.DRAFT and to_state == T1FormStatus.SUBMITTED:
        return True, None
    
    # Submitted forms are immutable
    if from_state == T1FormStatus.SUBMITTED:
        return False, "Submitted T1 forms cannot be modified. Create a new version instead."
    
    return False, f"Invalid transition: {from_status} → {to_status}"


# ============================================================================
# ERROR CODES
# ============================================================================

ERROR_CODE_INVALID_TRANSITION = "BUSINESS_INVALID_STATUS_TRANSITION"
ERROR_CODE_TERMINAL_STATE = "BUSINESS_TERMINAL_STATE_IMMUTABLE"
ERROR_CODE_INSUFFICIENT_PERMISSION = "AUTHZ_INSUFFICIENT_PERMISSIONS"


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def is_terminal_state(status: str, resource_type: str) -> bool:
    """Check if status is terminal (cannot transition)"""
    if resource_type == "filing":
        return status in {FilingStatus.COMPLETED.value, FilingStatus.CANCELLED.value}
    elif resource_type == "document":
        return False  # Documents don't have terminal states
    elif resource_type == "t1_form":
        return status == T1FormStatus.SUBMITTED.value
    return False


def get_initial_state(resource_type: str) -> str:
    """Get initial state for new resources"""
    if resource_type == "filing":
        return FilingStatus.DOCUMENTS_PENDING.value
    elif resource_type == "document":
        return DocumentStatus.PENDING.value
    elif resource_type == "t1_form":
        return T1FormStatus.DRAFT.value
    raise ValueError(f"Unknown resource type: {resource_type}")


# ============================================================================
# INVARIANT CHECKS (for testing)
# ============================================================================

def verify_state_machine_completeness():
    """
    Verify that state machines are complete and valid.
    Call this at startup to ensure state machines are correctly defined.
    """
    errors = []
    
    # Check Filing state machine
    for status in FilingStatus:
        if status not in FILING_TRANSITIONS:
            errors.append(f"Missing Filing transition definition for: {status}")
    
    # Check Document state machine
    for status in DocumentStatus:
        if status not in DOCUMENT_TRANSITIONS:
            errors.append(f"Missing Document transition definition for: {status}")
    
    # Check for invalid references
    for from_status, to_statuses in FILING_TRANSITIONS.items():
        for to_status in to_statuses:
            if not isinstance(to_status, FilingStatus):
                errors.append(f"Invalid Filing transition: {from_status} → {to_status}")
    
    for from_status, to_statuses in DOCUMENT_TRANSITIONS.items():
        for to_status in to_statuses:
            if not isinstance(to_status, DocumentStatus):
                errors.append(f"Invalid Document transition: {from_status} → {to_status}")
    
    if errors:
        raise RuntimeError(f"State machine validation failed: {errors}")
    
    return True
