"""
T1 Personal Tax Form User APIs
===============================
User-facing endpoints for T1 form data collection and submission.

Endpoints:
- POST /api/v1/t1-forms/{filing_id}/answers - Save draft answers (partial, idempotent)
- GET /api/v1/t1-forms/{filing_id} - Fetch current draft with answers dict
- POST /api/v1/t1-forms/{filing_id}/submit - Submit T1 (one-way lock)
- GET /api/v1/t1-forms/{filing_id}/required-documents - Get required documents list
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from backend.app.core.auth import CurrentUser, get_current_user
from backend.app.core.guards import require_email_verified
from backend.app.services.t1_validation_engine import get_validation_engine
from database.schemas_v2 import T1Form, T1Answer, T1SectionProgress, Filing, AuditLog
from backend.app.database import get_db


router = APIRouter(prefix="/api/v1/t1-forms", tags=["T1 Forms (User)"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SaveDraftRequest(BaseModel):
    """Request body for saving draft answers"""
    answers: Dict[str, Any] = Field(..., description="Dictionary of field_key: value pairs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answers": {
                    "personalInfo.firstName": "John",
                    "personalInfo.lastName": "Doe",
                    "personalInfo.sin": "123456789",
                    "hasForeignProperty": False
                }
            }
        }


class T1FormResponse(BaseModel):
    """T1 form with answers"""
    id: str
    filing_id: str
    form_version: str
    status: str
    is_locked: bool
    completion_percentage: int
    submitted_at: Optional[str]
    answers: Dict[str, Any]
    created_at: str
    updated_at: str


class SubmitT1Response(BaseModel):
    """T1 submission response"""
    success: bool
    message: str
    t1_form_id: str
    submitted_at: str


class RequiredDocumentResponse(BaseModel):
    """Required document item"""
    label: str
    question_key: Optional[str]
    description: Optional[str]


class RequiredDocumentsResponse(BaseModel):
    """Required documents list"""
    filing_id: str
    t1_form_id: str
    required_documents: List[RequiredDocumentResponse]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_filing_uuid(filing_id: str) -> uuid.UUID:
    """
    Validate and convert filing_id string to UUID.
    Raises HTTPException with helpful error if invalid.
    """
    try:
        return uuid.UUID(filing_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILING_ID",
                "message": f"Invalid filing_id format: '{filing_id}'. Must be a valid UUID.",
                "hint": "First create a filing via POST /api/v1/filings to get a valid UUID"
            }
        )


def _get_t1_form_or_create(filing_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> T1Form:
    """Get or create T1 form for filing"""
    # Check if filing exists and belongs to user
    filing = db.query(Filing).filter(
        and_(Filing.id == filing_id, Filing.user_id == user_id)
    ).first()
    
    if not filing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Filing {filing_id} not found or access denied"
        )
    
    # Get or create T1 form
    t1_form = db.query(T1Form).filter(T1Form.filing_id == filing_id).first()
    if not t1_form:
        t1_form = T1Form(
            id=uuid.uuid4(),
            filing_id=filing_id,
            user_id=user_id,  # Required field
            status='draft',
            is_locked=False,
            completion_percentage=0
        )
        db.add(t1_form)
        db.commit()
        db.refresh(t1_form)
    
    return t1_form


def _serialize_value(value: Any) -> Any:
    """Serialize value for JSON response"""
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, uuid.UUID):
        return str(value)
    return value


def _deserialize_answer_value(answer: T1Answer) -> Any:
    """Extract the actual value from polymorphic T1Answer"""
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


def _save_answer(t1_form_id: uuid.UUID, field_key: str, value: Any, db: Session):
    """Save or update a single answer (upsert)"""
    # Get existing answer
    existing = db.query(T1Answer).filter(
        and_(T1Answer.t1_form_id == t1_form_id, T1Answer.field_key == field_key)
    ).first()
    
    # Determine which column to use based on value type
    answer_data = {
        'value_boolean': None,
        'value_text': None,
        'value_numeric': None,
        'value_date': None,
        'value_array': None
    }
    
    if isinstance(value, bool):
        answer_data['value_boolean'] = value
    elif isinstance(value, str):
        answer_data['value_text'] = value
    elif isinstance(value, (int, float)):
        answer_data['value_numeric'] = value
    elif isinstance(value, datetime):
        answer_data['value_date'] = value.date()
    elif isinstance(value, list) or isinstance(value, dict):
        answer_data['value_array'] = value
    else:
        # Try to convert to string
        answer_data['value_text'] = str(value)
    
    if existing:
        # Update existing answer
        for key, val in answer_data.items():
            setattr(existing, key, val)
        existing.updated_at = datetime.utcnow()
    else:
        # Create new answer
        new_answer = T1Answer(
            id=uuid.uuid4(),
            t1_form_id=t1_form_id,
            field_key=field_key,
            **answer_data
        )
        db.add(new_answer)


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/{filing_id}/answers", status_code=status.HTTP_200_OK)
async def save_draft_answers(
    filing_id: str,
    request: SaveDraftRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save draft T1 answers (partial validation, idempotent).
    
    - **Partial validation**: Only validates fields that are present
    - **Idempotent**: Can be called multiple times with same/different data
    - **Auto-save friendly**: No submission required
    - **Updates completion percentage**: Based on required fields filled
    
    **IMPORTANT**: filing_id must be a valid UUID returned from POST /api/v1/filings
    """
    require_email_verified(current_user)
    
    filing_uuid = _validate_filing_uuid(filing_id)
    t1_form = _get_t1_form_or_create(filing_uuid, current_user.user_id, db)
    
    # Check if form is locked
    if t1_form.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify submitted T1 form. Contact admin to request unlock."
        )
    
    # Validate answers (draft mode - partial validation)
    validator = get_validation_engine()
    is_valid, errors = validator.validate_draft_save(request.answers)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    # Save each answer
    for field_key, value in request.answers.items():
        _save_answer(t1_form.id, field_key, value, db)
    
    # Get all current answers for completion calculation
    all_answers_db = db.query(T1Answer).filter(T1Answer.t1_form_id == t1_form.id).all()
    all_answers_dict = {ans.field_key: _deserialize_answer_value(ans) for ans in all_answers_db}
    
    # Update completion percentage
    t1_form.completion_percentage = validator.calculate_completion_percentage(all_answers_dict)
    t1_form.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": "Draft saved successfully",
        "completion_percentage": t1_form.completion_percentage,
        "fields_saved": len(request.answers)
    }


@router.get("/{filing_id}", response_model=T1FormResponse)
async def get_t1_draft(
    filing_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch current T1 draft with all saved answers.
    
    Returns:
    - T1 form metadata (status, completion, timestamps)
    - Answers dictionary (field_key: value)
    """
    require_email_verified(current_user)
    
    filing_uuid = _validate_filing_uuid(filing_id)
    t1_form = _get_t1_form_or_create(filing_uuid, current_user.user_id, db)
    
    # Fetch all answers
    answers_db = db.query(T1Answer).filter(T1Answer.t1_form_id == t1_form.id).all()
    answers_dict = {ans.field_key: _deserialize_answer_value(ans) for ans in answers_db}
    
    return T1FormResponse(
        id=str(t1_form.id),
        filing_id=str(t1_form.filing_id),
        form_version="2024",  # Default version since not stored in DB
        status=t1_form.status,
        is_locked=t1_form.is_locked,
        completion_percentage=t1_form.completion_percentage,
        submitted_at=t1_form.submitted_at.isoformat() if t1_form.submitted_at else None,
        answers=answers_dict,
        created_at=t1_form.created_at.isoformat(),
        updated_at=t1_form.updated_at.isoformat()
    )


@router.post("/{filing_id}/submit", response_model=SubmitT1Response)
async def submit_t1_form(
    filing_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit T1 form (one-way lock with complete validation).
    
    - **Complete validation**: All required fields must be filled
    - **One-way lock**: Cannot be undone without admin intervention
    - **State change**: draft → submitted
    - **Audit logged**: Submission action recorded
    """
    require_email_verified(current_user)
    
    filing_uuid = _validate_filing_uuid(filing_id)
    t1_form = _get_t1_form_or_create(filing_uuid, current_user.user_id, db)
    
    # Check if already submitted
    if t1_form.status == 'submitted' and t1_form.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="T1 form already submitted. Contact admin to request changes."
        )
    
    # Get all answers
    answers_db = db.query(T1Answer).filter(T1Answer.t1_form_id == t1_form.id).all()
    answers_dict = {ans.field_key: _deserialize_answer_value(ans) for ans in answers_db}
    
    # Complete validation
    validator = get_validation_engine()
    is_valid, errors = validator.validate_submission(answers_dict)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "T1 form is incomplete or contains errors",
                "errors": errors,
                "completion_percentage": t1_form.completion_percentage
            }
        )
    
    # Lock the form
    t1_form.status = 'submitted'
    t1_form.is_locked = True
    t1_form.locked_at = datetime.utcnow()
    t1_form.submitted_at = datetime.utcnow()
    t1_form.completion_percentage = 100
    
    # Audit log
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        user_id=current_user.user_id,
        action='T1_SUBMITTED',
        entity_type='t1_forms',
        entity_id=str(t1_form.id),
        details={'filing_id': str(filing_uuid), 'form_version': t1_form.form_version},
        ip_address=None,  # Will be populated by audit middleware
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    
    db.commit()
    
    return SubmitT1Response(
        success=True,
        message="T1 form submitted successfully. Your filing is now under review.",
        t1_form_id=str(t1_form.id),
        submitted_at=t1_form.submitted_at.isoformat()
    )


@router.get("/{filing_id}/required-documents", response_model=RequiredDocumentsResponse)
async def get_required_documents(
    filing_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of required documents based on questionnaire answers.
    
    - **Conditional logic**: Documents computed from T1Structure.json rules
    - **Real-time**: Updates as user answers questionnaire
    - **Upload guidance**: Shows what user needs to provide
    """
    require_email_verified(current_user)
    
    filing_uuid = _validate_filing_uuid(filing_id)
    t1_form = _get_t1_form_or_create(filing_uuid, current_user.user_id, db)
    
    # Get all answers
    answers_db = db.query(T1Answer).filter(T1Answer.t1_form_id == t1_form.id).all()
    answers_dict = {ans.field_key: _deserialize_answer_value(ans) for ans in answers_db}
    
    # Compute required documents
    validator = get_validation_engine()
    required_docs = validator.get_required_documents(answers_dict)
    
    # Format response
    docs_response = [
        RequiredDocumentResponse(
            label=doc['label'],
            question_key=doc.get('question_key'),
            description=f"Required because: {doc.get('question_key', 'always required')}"
        )
        for doc in required_docs
    ]
    
    return RequiredDocumentsResponse(
        filing_id=filing_id,
        t1_form_id=str(t1_form.id),
        required_documents=docs_response
    )


@router.get("/structure", status_code=status.HTTP_200_OK)
async def get_t1_structure():
    """
    Serve T1Structure.json to frontend (public endpoint).
    
    - **Single source of truth**: Frontend reads same JSON as backend
    - **Validation sync**: Frontend can pre-validate using same rules
    - **Dynamic forms**: Frontend renders form fields from this structure
    - **Public access**: No authentication required (form structure is not sensitive)
    """
    validator = get_validation_engine()
    return validator.get_structure_json()
