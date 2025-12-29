"""Filing status endpoints for clients and admins."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import T1ReturnFlat, Client, Notification
from backend.app.database import get_db

router = APIRouter(prefix="/filing-status", tags=["filing-status"])


class FilingStatus(str, Enum):
    """Valid filing status values matching the UI workflow."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PAYMENT_REQUEST_SENT = "payment_request_sent"
    PAYMENT_RECEIVED = "payment_received"
    RETURN_IN_PROGRESS = "return_in_progress"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    UNDER_REVIEW_PENDING_APPROVAL = "under_review_pending_approval"
    APPROVED_FOR_FILING = "approved_for_filing"
    E_FILING_COMPLETED = "e_filing_completed"


# Status display names for frontend
STATUS_DISPLAY_NAMES = {
    "draft": "Form in Draft",
    "submitted": "Form Submitted",
    "payment_request_sent": "Payment Request Sent",
    "payment_received": "Payment Received",
    "return_in_progress": "Return in Progress",
    "additional_info_required": "Additional Information Required",
    "under_review_pending_approval": "Under Review / Pending Approval",
    "approved_for_filing": "Approved for Filing",
    "e_filing_completed": "E-Filing Completed - Acknowledgment and Documents Available for Download",
}

# Status order for timeline
STATUS_ORDER = [
    "draft",
    "submitted",
    "payment_request_sent",
    "payment_received",
    "return_in_progress",
    "additional_info_required",
    "under_review_pending_approval",
    "approved_for_filing",
    "e_filing_completed",
]


class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class StatusTimelineItem(BaseModel):
    status: str
    display_name: str
    is_completed: bool
    is_current: bool
    completed_at: Optional[str] = None


class FilingStatusResponse(BaseModel):
    return_id: str
    filing_year: int
    current_status: str
    current_status_display: str
    payment_status: str
    timeline: List[StatusTimelineItem]
    updated_at: str
    submitted_at: Optional[str] = None


class UpdateStatusResponse(BaseModel):
    return_id: str
    status: str
    status_display: str
    updated_at: str
    message: str


@router.get("/client/{client_id}", response_model=FilingStatusResponse)
def get_client_filing_status(
    client_id: str,
    filing_year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Get filing status with timeline for a client.
    Returns the most recent filing year if filing_year is not specified.
    """
    # Find client
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Find T1 return
    query = db.query(T1ReturnFlat).filter(T1ReturnFlat.client_id == client_id)
    
    if filing_year:
        query = query.filter(T1ReturnFlat.filing_year == filing_year)
    else:
        # Get latest year
        query = query.order_by(T1ReturnFlat.filing_year.desc())
    
    t1_return = query.first()
    if not t1_return:
        raise HTTPException(status_code=404, detail="No T1 return found for this client")
    
    # Build timeline
    current_status = t1_return.status or "draft"
    current_status_index = STATUS_ORDER.index(current_status) if current_status in STATUS_ORDER else 0
    
    timeline = []
    for i, status_key in enumerate(STATUS_ORDER):
        is_completed = i < current_status_index
        is_current = i == current_status_index
        
        timeline.append(
            StatusTimelineItem(
                status=status_key,
                display_name=STATUS_DISPLAY_NAMES.get(status_key, status_key),
                is_completed=is_completed,
                is_current=is_current,
                completed_at=t1_return.updated_at.isoformat() if is_completed and i == current_status_index - 1 else None,
            )
        )
    
    return FilingStatusResponse(
        return_id=str(t1_return.id),
        filing_year=t1_return.filing_year,
        current_status=current_status,
        current_status_display=STATUS_DISPLAY_NAMES.get(current_status, current_status),
        payment_status=t1_return.payment_status or "pending",
        timeline=timeline,
        updated_at=t1_return.updated_at.isoformat(),
        submitted_at=t1_return.submitted_at.isoformat() if t1_return.submitted_at else None,
    )


@router.get("/client", response_model=FilingStatusResponse)
def get_client_filing_status_by_email(
    email: str,
    filing_year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get filing status by client email."""
    client = db.query(Client).filter(Client.email == email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return get_client_filing_status(str(client.id), filing_year, db)


@router.put("/admin/{return_id}/status", response_model=UpdateStatusResponse)
def update_filing_status(
    return_id: str,
    request: StatusUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Admin endpoint to update T1 return filing status.
    Creates a notification for the client when status changes.
    """
    # Validate status
    if request.status not in STATUS_ORDER:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Valid values: {', '.join(STATUS_ORDER)}"
        )
    
    # Find T1 return
    t1_return = db.query(T1ReturnFlat).filter(T1ReturnFlat.id == return_id).first()
    if not t1_return:
        raise HTTPException(status_code=404, detail="T1 return not found")
    
    # Store old status for notification
    old_status = t1_return.status
    old_status_display = STATUS_DISPLAY_NAMES.get(old_status, old_status)
    
    # Update status
    t1_return.status = request.status
    t1_return.updated_at = datetime.utcnow()
    
    # Update client status if needed (sync with T1 return status)
    client = db.query(Client).filter(Client.id == t1_return.client_id).first()
    if client:
        # Map T1 status to client status
        status_mapping = {
            "draft": "documents_pending",
            "submitted": "under_review",
            "payment_request_sent": "awaiting_payment",
            "payment_received": "in_preparation",
            "return_in_progress": "in_preparation",
            "additional_info_required": "under_review",
            "under_review_pending_approval": "awaiting_approval",
            "approved_for_filing": "awaiting_approval",
            "e_filing_completed": "filed",
        }
        client.status = status_mapping.get(request.status, client.status)
        client.updated_at = datetime.utcnow()
    
    # Create notification for client
    if old_status != request.status:
        notification = Notification(
            client_id=t1_return.client_id,
            type="status_update",
            title="Filing Status Updated",
            message=f"Your T1 return status has been updated from '{old_status_display}' to '{STATUS_DISPLAY_NAMES.get(request.status, request.status)}'.",
            is_read=False,
        )
        if request.notes:
            notification.message += f"\n\nNotes: {request.notes}"
        db.add(notification)
    
    db.commit()
    db.refresh(t1_return)
    
    return UpdateStatusResponse(
        return_id=str(t1_return.id),
        status=t1_return.status,
        status_display=STATUS_DISPLAY_NAMES.get(t1_return.status, t1_return.status),
        updated_at=t1_return.updated_at.isoformat(),
        message="Status updated successfully",
    )


@router.get("/admin/returns", response_model=List[Dict[str, Any]])
def list_all_returns(
    status: Optional[str] = None,
    filing_year: Optional[int] = None,
    client_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Admin endpoint to list all T1 returns with filtering."""
    query = db.query(T1ReturnFlat)
    
    if status:
        query = query.filter(T1ReturnFlat.status == status)
    if filing_year:
        query = query.filter(T1ReturnFlat.filing_year == filing_year)
    if client_id:
        query = query.filter(T1ReturnFlat.client_id == client_id)
    
    returns = query.order_by(T1ReturnFlat.updated_at.desc()).all()
    
    result = []
    for t1_return in returns:
        result.append({
            "id": str(t1_return.id),
            "client_id": str(t1_return.client_id),
            "filing_year": t1_return.filing_year,
            "status": t1_return.status,
            "status_display": STATUS_DISPLAY_NAMES.get(t1_return.status, t1_return.status),
            "payment_status": t1_return.payment_status,
            "updated_at": t1_return.updated_at.isoformat(),
            "submitted_at": t1_return.submitted_at.isoformat() if t1_return.submitted_at else None,
        })
    
    return result




