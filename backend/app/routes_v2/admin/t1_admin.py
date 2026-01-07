"""
T1 Personal Tax Form Admin APIs
================================
Admin-facing endpoints for T1 form review, approval, and management.

Endpoints:
- GET /api/v1/admin/t1-forms/{id} - View full T1 with structured sections
- POST /api/v1/admin/t1-forms/{id}/unlock - Unlock submitted form for corrections
- POST /api/v1/admin/t1-forms/{id}/request-documents - Request additional documents
- POST /api/v1/admin/t1-forms/{id}/sections/{step}/{section}/review - Mark section reviewed
- GET /api/v1/admin/t1-forms/{id}/audit - View audit trail
- GET /api/v1/admin/dashboard/t1-filings - Dashboard overview
- GET /api/v1/admin/t1-forms/{id}/detailed - Detailed view with UI hints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from backend.app.core.auth import CurrentUser, get_current_user
from backend.app.services.t1_validation_engine import get_validation_engine
from database.schemas_v2 import (
    T1Form, T1Answer, T1SectionProgress, Filing, User, Admin,
    AuditLog, EmailThread, EmailMessage, Document
)
from backend.app.database import get_db


router = APIRouter(prefix="/api/v1/admin", tags=["T1 Forms (Admin)"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class UnlockT1Request(BaseModel):
    """Request to unlock submitted T1"""
    reason: str = Field(..., min_length=10, description="Reason for unlocking (audit trail)")


class UnlockT1Response(BaseModel):
    """Unlock response"""
    success: bool
    message: str
    unlocked_at: str


class RequestDocumentsRequest(BaseModel):
    """Request additional documents"""
    document_labels: List[str] = Field(..., description="List of document labels to request")
    message: str = Field(..., min_length=10, description="Message to user explaining request")


class RequestDocumentsResponse(BaseModel):
    """Document request response"""
    success: bool
    message: str
    thread_id: str
    email_sent: bool


class MarkSectionReviewedRequest(BaseModel):
    """Mark section as reviewed"""
    review_notes: Optional[str] = None


class MarkSectionReviewedResponse(BaseModel):
    """Section review response"""
    success: bool
    message: str
    reviewed_at: str


class AuditTrailEntry(BaseModel):
    """Single audit entry"""
    id: str
    timestamp: str
    action: str
    actor_id: str
    actor_name: str
    actor_role: str
    details: Dict[str, Any]


class AuditTrailResponse(BaseModel):
    """Audit trail response"""
    t1_form_id: str
    filing_id: str
    entries: List[AuditTrailEntry]


class T1DashboardItem(BaseModel):
    """Dashboard list item"""
    id: str
    filing_id: str
    user_name: str
    user_email: str
    filing_year: int
    status: str
    is_locked: bool
    completion_percentage: int
    submitted_at: Optional[str]
    created_at: str


class T1DashboardResponse(BaseModel):
    """Dashboard overview"""
    total_count: int
    draft_count: int
    submitted_count: int
    filings: List[T1DashboardItem]


class T1DetailedSection(BaseModel):
    """Detailed section view"""
    step_id: str
    section_id: Optional[str]
    section_title: str
    fields: List[Dict[str, Any]]
    is_complete: bool
    is_reviewed: bool
    reviewed_by: Optional[str]
    reviewed_at: Optional[str]
    review_notes: Optional[str]


class T1DetailedResponse(BaseModel):
    """Detailed T1 view with UI hints"""
    id: str
    filing_id: str
    user_id: str
    user_name: str
    filing_year: int
    status: str
    is_locked: bool
    completion_percentage: int
    submitted_at: Optional[str]
    sections: List[T1DetailedSection]
    required_documents: List[Dict[str, Any]]
    document_uploads: List[Dict[str, Any]]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _check_admin_access(current_user: CurrentUser):
    """Verify user is an admin"""
    if current_user.role not in ['admin', 'superadmin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def _get_t1_form_admin(t1_form_id: uuid.UUID, db: Session) -> T1Form:
    """Get T1 form for admin (no ownership check)"""
    t1_form = db.query(T1Form).filter(T1Form.id == t1_form_id).first()
    if not t1_form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"T1 form {t1_form_id} not found"
        )
    return t1_form


def _deserialize_answer_value(answer: T1Answer) -> Any:
    """Extract actual value from T1Answer"""
    if answer.value_boolean is not None:
        return answer.value_boolean
    elif answer.value_text is not None:
        return answer.value_text
    elif answer.value_numeric is not None:
        return answer.value_numeric
    elif answer.value_date is not None:
        return answer.value_date.isoformat()
    elif answer.value_array is not None:
        return answer.value_array
    return None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/t1-forms/{t1_form_id}")
async def view_full_t1(
    t1_form_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    View full T1 form with all answers and structured sections.
    
    Returns complete T1 data for admin review.
    """
    _check_admin_access(current_user)
    
    t1_uuid = uuid.UUID(t1_form_id)
    t1_form = _get_t1_form_admin(t1_uuid, db)
    
    # Get filing and user info
    filing = db.query(Filing).filter(Filing.id == t1_form.filing_id).first()
    user = db.query(User).filter(User.id == filing.user_id).first()
    
    # Get all answers
    answers_db = db.query(T1Answer).filter(T1Answer.t1_form_id == t1_uuid).all()
    answers_dict = {ans.field_key: _deserialize_answer_value(ans) for ans in answers_db}
    
    # Get sections progress
    sections = db.query(T1SectionProgress).filter(T1SectionProgress.t1_form_id == t1_uuid).all()
    
    return {
        "id": str(t1_form.id),
        "filing_id": str(t1_form.filing_id),
        "user_id": str(user.id),
        "user_name": f"{user.first_name} {user.last_name}",
        "user_email": user.email,
        "filing_year": filing.filing_year,
        "status": t1_form.status,
        "is_locked": t1_form.is_locked,
        "completion_percentage": t1_form.completion_percentage,
        "submitted_at": t1_form.submitted_at.isoformat() if t1_form.submitted_at else None,
        "answers": answers_dict,
        "sections_progress": [
            {
                "step_id": sec.step_id,
                "section_id": sec.section_id,
                "is_complete": sec.is_complete,
                "is_reviewed": sec.is_reviewed,
                "reviewed_at": sec.reviewed_at.isoformat() if sec.reviewed_at else None
            }
            for sec in sections
        ]
    }


@router.post("/t1-forms/{t1_form_id}/unlock", response_model=UnlockT1Response)
async def unlock_t1_form(
    t1_form_id: str,
    request: UnlockT1Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlock submitted T1 form for corrections.
    
    - **Admin only**: Requires admin or superadmin role
    - **Audit logged**: Unlock reason recorded
    - **State change**: submitted → draft (temporarily)
    """
    _check_admin_access(current_user)
    
    t1_uuid = uuid.UUID(t1_form_id)
    t1_form = _get_t1_form_admin(t1_uuid, db)
    
    if not t1_form.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="T1 form is not locked"
        )
    
    # Unlock the form
    t1_form.is_locked = False
    t1_form.status = 'draft'
    t1_form.unlocked_by = current_user.user_id
    t1_form.unlocked_at = datetime.utcnow()
    t1_form.unlock_reason = request.reason
    
    # Audit log
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        user_id=current_user.user_id,
        action='T1_UNLOCKED',
        entity_type='t1_forms',
        entity_id=str(t1_form.id),
        details={'reason': request.reason, 'filing_id': str(t1_form.filing_id)},
        ip_address=None,
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    
    db.commit()
    
    return UnlockT1Response(
        success=True,
        message="T1 form unlocked successfully. User can now make corrections.",
        unlocked_at=t1_form.unlocked_at.isoformat()
    )


@router.post("/t1-forms/{t1_form_id}/request-documents", response_model=RequestDocumentsResponse)
async def request_additional_documents(
    t1_form_id: str,
    request: RequestDocumentsRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request additional documents from user.
    
    - **Email + notification**: Creates email thread and sends notification
    - **Document tracking**: Records requested documents
    """
    _check_admin_access(current_user)
    
    t1_uuid = uuid.UUID(t1_form_id)
    t1_form = _get_t1_form_admin(t1_uuid, db)
    
    # Get filing and user
    filing = db.query(Filing).filter(Filing.id == t1_form.filing_id).first()
    user = db.query(User).filter(User.id == filing.user_id).first()
    
    # Create or get email thread
    thread_id = f"T1-{str(t1_form.id)[:8]}-docs-{datetime.utcnow().strftime('%Y%m%d')}"
    thread = db.query(EmailThread).filter(EmailThread.thread_id == thread_id).first()
    
    if not thread:
        thread = EmailThread(
            id=uuid.uuid4(),
            thread_id=thread_id,
            t1_form_id=t1_form.id,
            user_id=user.id,
            admin_id=current_user.user_id,
            subject=f"Additional Documents Requested for {filing.filing_year} T1",
            status='open'
        )
        db.add(thread)
    
    # Add message to thread
    message = EmailMessage(
        id=uuid.uuid4(),
        thread_id=thread_id,
        sender_type='admin',
        sender_id=current_user.user_id,
        message_type='request',
        message_body=f"Documents requested:\n" + "\n".join(f"- {doc}" for doc in request.document_labels) + f"\n\nMessage:\n{request.message}",
        is_read=False
    )
    db.add(message)
    
    # Audit log
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        user_id=current_user.user_id,
        action='DOCUMENTS_REQUESTED',
        entity_type='t1_forms',
        entity_id=str(t1_form.id),
        details={'documents': request.document_labels, 'message': request.message},
        ip_address=None,
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    
    db.commit()
    
    # TODO: Send actual email via email service
    
    return RequestDocumentsResponse(
        success=True,
        message="Document request sent to user",
        thread_id=thread_id,
        email_sent=False  # Would be True after email service integration
    )


@router.post("/t1-forms/{t1_form_id}/sections/{step_id}/{section_id}/review", 
             response_model=MarkSectionReviewedResponse)
async def mark_section_reviewed(
    t1_form_id: str,
    step_id: str,
    section_id: str,
    request: MarkSectionReviewedRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a section as reviewed.
    
    - **Section tracking**: Updates section progress table
    - **Review notes**: Optional notes for internal use
    """
    _check_admin_access(current_user)
    
    t1_uuid = uuid.UUID(t1_form_id)
    t1_form = _get_t1_form_admin(t1_uuid, db)
    
    # Get or create section progress
    section_prog = db.query(T1SectionProgress).filter(
        and_(
            T1SectionProgress.t1_form_id == t1_uuid,
            T1SectionProgress.step_id == step_id,
            T1SectionProgress.section_id == section_id
        )
    ).first()
    
    if not section_prog:
        section_prog = T1SectionProgress(
            id=uuid.uuid4(),
            t1_form_id=t1_uuid,
            step_id=step_id,
            section_id=section_id,
            is_complete=True,
            is_reviewed=False
        )
        db.add(section_prog)
    
    # Mark as reviewed
    section_prog.is_reviewed = True
    section_prog.reviewed_by = current_user.user_id
    section_prog.reviewed_at = datetime.utcnow()
    section_prog.review_notes = request.review_notes
    
    # Audit log
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        user_id=current_user.user_id,
        action='SECTION_REVIEWED',
        entity_type='t1_sections_progress',
        entity_id=str(section_prog.id),
        details={'step_id': step_id, 'section_id': section_id, 't1_form_id': str(t1_form.id)},
        ip_address=None,
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    
    db.commit()
    
    return MarkSectionReviewedResponse(
        success=True,
        message=f"Section {step_id}/{section_id} marked as reviewed",
        reviewed_at=section_prog.reviewed_at.isoformat()
    )


@router.get("/t1-forms/{t1_form_id}/audit", response_model=AuditTrailResponse)
async def view_audit_trail(
    t1_form_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    View complete audit trail for T1 form.
    
    Shows all actions: submissions, unlocks, document requests, section reviews.
    """
    _check_admin_access(current_user)
    
    t1_uuid = uuid.UUID(t1_form_id)
    t1_form = _get_t1_form_admin(t1_uuid, db)
    
    # Get all audit entries for this T1 form
    audit_entries = db.query(AuditLog).filter(
        or_(
            and_(AuditLog.entity_type == 't1_forms', AuditLog.entity_id == str(t1_uuid)),
            and_(AuditLog.entity_type == 't1_sections_progress', 
                 AuditLog.details['t1_form_id'].astext == str(t1_uuid))
        )
    ).order_by(AuditLog.timestamp.desc()).all()
    
    # Format entries
    entries = []
    for entry in audit_entries:
        # Get actor info
        actor = db.query(User).filter(User.id == entry.user_id).first()
        if not actor:
            actor = db.query(Admin).filter(Admin.id == entry.user_id).first()
        
        entries.append(AuditTrailEntry(
            id=str(entry.id),
            timestamp=entry.timestamp.isoformat(),
            action=entry.action,
            actor_id=str(entry.user_id),
            actor_name=f"{actor.first_name} {actor.last_name}" if actor else "Unknown",
            actor_role=actor.role if hasattr(actor, 'role') else "user",
            details=entry.details or {}
        ))
    
    return AuditTrailResponse(
        t1_form_id=str(t1_form.id),
        filing_id=str(t1_form.filing_id),
        entries=entries
    )


@router.get("/dashboard/t1-filings", response_model=T1DashboardResponse)
async def get_t1_dashboard(
    status_filter: Optional[str] = Query(None, description="Filter by status: draft, submitted"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin dashboard overview of all T1 filings.
    
    Shows:
    - Total count
    - Status breakdown
    - List of T1 forms with user info
    """
    _check_admin_access(current_user)
    
    # Build query
    query = db.query(T1Form).join(Filing).join(User)
    
    if status_filter:
        query = query.filter(T1Form.status == status_filter)
    
    t1_forms = query.order_by(T1Form.created_at.desc()).all()
    
    # Get counts
    total_count = len(t1_forms)
    draft_count = len([f for f in t1_forms if f.status == 'draft'])
    submitted_count = len([f for f in t1_forms if f.status == 'submitted'])
    
    # Format list
    filings_list = []
    for t1_form in t1_forms:
        filing = db.query(Filing).filter(Filing.id == t1_form.filing_id).first()
        user = db.query(User).filter(User.id == filing.user_id).first()
        
        filings_list.append(T1DashboardItem(
            id=str(t1_form.id),
            filing_id=str(t1_form.filing_id),
            user_name=f"{user.first_name} {user.last_name}",
            user_email=user.email,
            filing_year=filing.filing_year,
            status=t1_form.status,
            is_locked=t1_form.is_locked,
            completion_percentage=t1_form.completion_percentage,
            submitted_at=t1_form.submitted_at.isoformat() if t1_form.submitted_at else None,
            created_at=t1_form.created_at.isoformat()
        ))
    
    return T1DashboardResponse(
        total_count=total_count,
        draft_count=draft_count,
        submitted_count=submitted_count,
        filings=filings_list
    )


@router.get("/t1-forms/{t1_form_id}/detailed", response_model=T1DetailedResponse)
async def get_detailed_t1_view(
    t1_form_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed T1 view with UI component hints for admin dashboard.
    
    Returns structured sections with review status and document checklist.
    """
    _check_admin_access(current_user)
    
    t1_uuid = uuid.UUID(t1_form_id)
    t1_form = _get_t1_form_admin(t1_uuid, db)
    
    # Get filing and user
    filing = db.query(Filing).filter(Filing.id == t1_form.filing_id).first()
    user = db.query(User).filter(User.id == filing.user_id).first()
    
    # Get all answers
    answers_db = db.query(T1Answer).filter(T1Answer.t1_form_id == t1_uuid).all()
    answers_dict = {ans.field_key: _deserialize_answer_value(ans) for ans in answers_db}
    
    # Get validation engine
    validator = get_validation_engine()
    required_docs = validator.get_required_documents(answers_dict)
    
    # Get uploaded documents
    documents = db.query(Document).filter(Document.filing_id == t1_form.filing_id).all()
    
    # Build sections (simplified - would iterate through T1Structure in production)
    sections = []
    sections_progress = db.query(T1SectionProgress).filter(
        T1SectionProgress.t1_form_id == t1_uuid
    ).all()
    
    for sec_prog in sections_progress:
        admin_reviewer = None
        if sec_prog.reviewed_by:
            admin = db.query(Admin).filter(Admin.id == sec_prog.reviewed_by).first()
            admin_reviewer = f"{admin.first_name} {admin.last_name}" if admin else None
        
        sections.append(T1DetailedSection(
            step_id=sec_prog.step_id,
            section_id=sec_prog.section_id,
            section_title=sec_prog.step_id.replace("_", " ").title(),
            fields=[],  # Would be populated from T1Structure
            is_complete=sec_prog.is_complete,
            is_reviewed=sec_prog.is_reviewed,
            reviewed_by=admin_reviewer,
            reviewed_at=sec_prog.reviewed_at.isoformat() if sec_prog.reviewed_at else None,
            review_notes=sec_prog.review_notes
        ))
    
    return T1DetailedResponse(
        id=str(t1_form.id),
        filing_id=str(t1_form.filing_id),
        user_id=str(user.id),
        user_name=f"{user.first_name} {user.last_name}",
        filing_year=filing.filing_year,
        status=t1_form.status,
        is_locked=t1_form.is_locked,
        completion_percentage=t1_form.completion_percentage,
        submitted_at=t1_form.submitted_at.isoformat() if t1_form.submitted_at else None,
        sections=sections,
        required_documents=required_docs,
        document_uploads=[
            {
                "id": str(doc.id),
                "file_name": doc.file_name,
                "section_name": doc.section_name,
                "uploaded_at": doc.uploaded_at.isoformat(),
                "is_approved": doc.is_approved
            }
            for doc in documents
        ]
    )
