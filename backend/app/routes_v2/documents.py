"""
Document endpoints for API v2
GET    /api/v1/documents
GET    /api/v1/documents/{id}
POST   /api/v1/documents/upload
GET    /api/v1/documents/{id}/download
PATCH  /api/v1/documents/{id}
DELETE /api/v1/documents/{id}
"""

import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, status, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import get_db
from backend.app.schemas.api_v2 import (
    DocumentResponse, DocumentUploadResponse, DocumentUpdate, SuccessResponse
)
from backend.app.core.auth import get_current_user, CurrentUser
from backend.app.services.document_service import DocumentService
from backend.app.core.errors import AuthorizationError, ValidationError, ErrorCodes
from backend.app.core.guards import require_email_verified, verify_document_access
from database.schemas_v2 import Filing

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("")
async def list_documents(
    filing_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List documents (user: own documents, admin: assigned filing documents)"""
    
    service = DocumentService(db)
    
    if current_user.is_admin:
        documents = service.get_admin_documents(
            admin_id=current_user.id,
            is_superadmin=current_user.is_superadmin,
            filing_id=filing_id
        )
    else:
        documents = service.get_user_documents(
            user_id=current_user.id,
            filing_id=filing_id,
            status=status
        )
    
    return {
        "data": [
            {
                "id": str(doc.id),
                "filing_id": str(doc.filing_id),
                "name": doc.name,
                "original_filename": doc.original_filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "section_name": doc.section_name,
                "document_type": doc.document_type,
                "status": doc.status,
                "uploaded_at": doc.uploaded_at,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at
            }
            for doc in documents
        ],
        "total": len(documents)
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document metadata"""
    
    service = DocumentService(db)
    document = service.get_document_by_id(document_id)
    
    # Authorization check
    if not current_user.is_admin:
        if str(document.user_id) != current_user.id:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTHZ_NOT_RESOURCE_OWNER,
                message="You do not own this document"
            )
    
    return {
        "id": str(document.id),
        "user_id": str(document.user_id),
        "filing_id": str(document.filing_id) if document.filing_id else None,
        "category": document.category,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "status": document.status,
        "admin_notes": document.admin_notes,
        "created_at": document.created_at,
        "updated_at": document.updated_at
    }


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    filing_id: str = Form(...),
    category: str = Form("other"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload document with encryption"""
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    file_type = file.filename.split('.')[-1].lower() if file.filename and '.' in file.filename else 'unknown'
    
    service = DocumentService(db)
    document = service.upload_document(
        filing_id=filing_id,
        file_content=content,
        original_filename=file.filename or "unknown",
        file_type=file_type,
        file_size=file_size,
        document_type=category
    )
    
    return {
        "id": str(document.id),
        "filing_id": str(document.filing_id),
        "name": document.name,
        "original_filename": document.original_filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "section_name": document.section_name,
        "document_type": document.document_type,
        "status": document.status,
        "uploaded_at": document.uploaded_at,
        "created_at": document.created_at
    }


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download document (decrypted)"""
    
    service = DocumentService(db)
    document = service.get_document_by_id(document_id)
    
    # Authorization check: verify user owns the filing
    if not current_user.is_admin:
        filing = db.query(Filing).filter(Filing.id == document.filing_id).first()
        if not filing or str(filing.user_id) != current_user.id:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTHZ_NOT_RESOURCE_OWNER,
                message="You do not own this document"
            )
    
    # Download and decrypt
    file_bytes, filename, file_type = service.download_document(document_id)
    
    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=f"application/{file_type}",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document_metadata(
    document_id: str,
    data: DocumentUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update document metadata (user) or status (admin)"""
    
    service = DocumentService(db)
    document = service.get_document_by_id(document_id)
    
    # Authorization check
    if not current_user.is_admin:
        if str(document.user_id) != current_user.id:
            raise AuthorizationError(
                error_code=ErrorCodes.AUTHZ_NOT_RESOURCE_OWNER,
                message="You do not own this document"
            )
    
    # Users can update filename/notes, admins can update status
    if current_user.is_admin:
        if data.status:
            document = service.update_document_status(
                document_id, 
                data.status, 
                data.admin_notes
            )
    else:
        document = service.update_document(document_id, data.filename, None)
    
    return {
        "id": str(document.id),
        "user_id": str(document.user_id),
        "filing_id": str(document.filing_id) if document.filing_id else None,
        "category": document.category,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "status": document.status,
        "admin_notes": document.admin_notes,
        "created_at": document.created_at,
        "updated_at": document.updated_at
    }


@router.delete("/{document_id}", response_model=SuccessResponse)
async def delete_document_endpoint(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document (physical file + DB record)"""
    
    service = DocumentService(db)
    document = service.get_document_by_id(document_id)
    
    # Authorization check - only user can delete their own documents
    if str(document.user_id) != current_user.id:
        raise AuthorizationError(
            error_code=ErrorCodes.AUTHZ_NOT_RESOURCE_OWNER,
            message="You do not own this document"
        )
    
    service.delete_document(document_id)
    
    return SuccessResponse(message="Document deleted successfully")
