"""
Filing endpoints for API v2
GET    /api/v1/filings
GET    /api/v1/filings/{id}
POST   /api/v1/filings
GET    /api/v1/filings/{id}/timeline
"""

import sys
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Query, status, Request, HTTPException
from sqlalchemy.orm import Session

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import get_db
from backend.app.schemas.api_v2 import (
    FilingResponse, FilingCreate, PaginatedResponse
)
from backend.app.core.auth import get_current_user, CurrentUser
from backend.app.services.filing_service import FilingService
from backend.app.core.errors import AuthorizationError, ErrorCodes
from backend.app.core.guards import require_email_verified, verify_filing_access

router = APIRouter(prefix="/filings", tags=["Filings"])


def _validate_uuid(filing_id: str, param_name: str = "filing_id") -> str:
    """Validate UUID format and return cleaned string"""
    try:
        uuid.UUID(filing_id)
        return filing_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_UUID",
                "message": f"Invalid {param_name} format: '{filing_id}'. Must be a valid UUID.",
                "hint": "UUIDs have format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 characters)"
            }
        )


@router.get("", response_model=PaginatedResponse)
async def list_filings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    year: Optional[int] = Query(None, ge=2020, le=2030),
    status: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List filings (user: own filings, admin: assigned filings)"""
    
    service = FilingService(db)
    
    if current_user.is_admin:
        filings, total = service.get_admin_filings(
            admin_id=current_user.id,
            is_superadmin=current_user.is_superadmin,
            page=page,
            page_size=page_size,
            year=year,
            status=status
        )
    else:
        filings, total = service.get_user_filings(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            year=year,
            status=status
        )
    
    # Enrich with calculated fields
    filing_responses = []
    for filing in filings:
        filing_dict = {
            "id": str(filing.id),
            "user_id": str(filing.user_id),
            "filing_year": filing.filing_year,
            "status": filing.status,
            "total_fee": filing.total_fee,
            "paid_amount": service.calculate_paid_amount(filing.id),
            "payment_status": service.calculate_payment_status(filing),
            "email_thread_id": filing.email_thread_id,
            "created_at": filing.created_at,
            "updated_at": filing.updated_at,
            "assigned_admin": None  # TODO: Load admin info
        }
        filing_responses.append(filing_dict)
    
    return {
        "data": filing_responses,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "total_items": total
        }
    }


@router.get("/{filing_id}", response_model=FilingResponse)
async def get_filing(
    filing_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get filing details"""
    
    # Validate UUID format
    _validate_uuid(filing_id)
    
    service = FilingService(db)
    filing = service.get_filing_by_id(filing_id)
    
    # Authorization check
    if not current_user.is_admin:
        # User can only access own filings
        if str(filing.user_id) != current_user.id:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTHZ_NOT_RESOURCE_OWNER,
                message="You do not own this filing"
            )
    else:
        # Admin must be assigned (unless superadmin)
        if not current_user.is_superadmin:
            if not service.is_admin_assigned(filing_id, current_user.id):
                raise AuthorizationError(
                    error_code=ErrorCodes.AUTHZ_NOT_ASSIGNED,
                    message="You are not assigned to this filing"
                )
    
    return {
        "id": str(filing.id),
        "user_id": str(filing.user_id),
        "filing_year": filing.filing_year,
        "status": filing.status,
        "total_fee": filing.total_fee,
        "paid_amount": service.calculate_paid_amount(filing.id),
        "payment_status": service.calculate_payment_status(filing),
        "email_thread_id": filing.email_thread_id,
        "created_at": filing.created_at,
        "updated_at": filing.updated_at,
        "assigned_admin": None  # TODO: Load admin info
    }


@router.post("", response_model=FilingResponse, status_code=status.HTTP_201_CREATED)
async def create_filing(
    data: FilingCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new filing.
    Enforces INV-A010: Email must be verified.
    """
    
    # EMAIL VERIFICATION CHECK (INV-A010)
    require_email_verified(current_user)
    
    # Users create for themselves, admins can create for users
    if current_user.is_admin:
        raise AuthorizationError(
            message="Admins cannot create filings. Users must create their own filings."
        )
    
    service = FilingService(db)
    filing = service.create_filing(current_user.id, data.filing_year)
    
    return {
        "id": str(filing.id),
        "user_id": str(filing.user_id),
        "filing_year": filing.filing_year,
        "status": filing.status,
        "total_fee": filing.total_fee,
        "paid_amount": 0.0,
        "payment_status": "pending",
        "email_thread_id": filing.email_thread_id,
        "created_at": filing.created_at,
        "updated_at": filing.updated_at,
        "assigned_admin": None
    }


@router.get("/{filing_id}/timeline")
async def get_filing_timeline(
    filing_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get filing timeline events"""
    
    # Validate UUID format
    _validate_uuid(filing_id)
    
    service = FilingService(db)
    filing = service.get_filing_by_id(filing_id)
    
    # Authorization check (same as get_filing)
    if not current_user.is_admin:
        if str(filing.user_id) != current_user.id:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTHZ_NOT_RESOURCE_OWNER,
                message="You do not own this filing"
            )
    else:
        if not current_user.is_superadmin:
            if not service.is_admin_assigned(filing_id, current_user.id):
                raise AuthorizationError(
                    error_code=ErrorCodes.AUTHZ_NOT_ASSIGNED,
                    message="You are not assigned to this filing"
                )
    
    timeline = service.get_filing_timeline(filing_id)
    
    return {
        "data": [
            {
                "id": str(event.id),
                "filing_id": str(event.filing_id),
                "event_type": event.event_type,
                "description": event.description,
                "actor_type": event.actor_type,
                "actor_id": str(event.actor_id) if event.actor_id else None,
                "actor_name": event.actor_name,
                "created_at": event.created_at
            }
            for event in timeline
        ]
    }
