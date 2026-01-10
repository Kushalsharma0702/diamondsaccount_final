"""
Document routes
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.utils import create_audit_log
from app.models.document import Document
from app.models.client import Client
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse

router = APIRouter()


@router.get("", response_model=DocumentListResponse)
async def get_documents(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    client_id: Optional[UUID] = Query(None),
    filing_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get all documents with filters - client_id is actually user_id"""
    query = select(Document)
    
    conditions = []
    if status_filter:
        conditions.append(Document.status == status_filter)
    
    # client_id is actually user_id - need to join with filings
    if client_id:
        # Use text for subquery to avoid needing Filing model
        from sqlalchemy import text as sql_text
        filing_ids_result = await db.execute(
            sql_text("SELECT id FROM filings WHERE user_id = :user_id"),
            {"user_id": str(client_id)}
        )
        filing_ids = [row[0] for row in filing_ids_result]
        if filing_ids:
            conditions.append(Document.filing_id.in_(filing_ids))
        else:
            # No filings for this user, return empty
            conditions.append(Document.filing_id == None)
    
    if filing_id:
        conditions.append(Document.filing_id == filing_id)
    
    if search:
        conditions.append(
            or_(
                Document.name.ilike(f"%{search}%"),
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Document.created_at.desc())
    result = await db.execute(query)
    documents = result.scalars().all()
    
    # Count total
    count_query = select(func.count()).select_from(Document)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Format response
    doc_responses = []
    for doc in documents:
        # Map Document model fields to DocumentResponse schema
        doc_dict = {
            "id": doc.id,
            "name": doc.name,
            "type": doc.file_type,  # Map file_type to type
            "status": doc.status,
            "client_id": doc.filing_id,  # Use filing_id as client_id for now
            "client_name": None,
            "version": 1,  # Default version
            "uploaded_at": doc.uploaded_at,
            "notes": doc.notes,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at
        }
        doc_responses.append(DocumentResponse(**doc_dict))
    
    return DocumentListResponse(documents=doc_responses, total=total)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc_data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create a new document"""
    # Verify client exists
    client_query = select(Client).where(Client.id == doc_data.client_id)
    client_result = await db.execute(client_query)
    if not client_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Client not found")
    
    document = Document(**doc_data.model_dump())
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Create audit log
    await create_audit_log(
        db, "Document Created", "document", str(document.id), current_admin.id,
        new_value=f"Document: {document.name}"
    )
    
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete a document"""
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_name = document.name
    await db.delete(document)
    await db.commit()
    
    # Create audit log
    await create_audit_log(
        db, "Document Deleted", "document", str(document_id), current_admin.id,
        old_value=f"Document: {doc_name}"
    )




