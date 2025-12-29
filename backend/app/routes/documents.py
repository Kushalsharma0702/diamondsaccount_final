"""Document upload endpoints with encryption."""
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Client, Document
from backend.app.database import get_db
from backend.app.utils.encryption import encrypt_file_content, decrypt_file_content

# Load .env from project root
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

router = APIRouter(prefix="/documents", tags=["documents"])

STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage/uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx", ".txt"}

os.makedirs(STORAGE_PATH, exist_ok=True)


class DocumentResponse(BaseModel):
    id: str
    name: str
    original_filename: str
    file_type: str
    file_size: int
    section_name: Optional[str]
    status: str
    encrypted: bool
    created_at: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    client_id: Optional[str] = Form(None),
    section: Optional[str] = Form(None),
    document_type: str = Form("receipt"),
    db: Session = Depends(get_db),
):
    """
    Upload a document file with encryption.
    
    Files are encrypted before saving to disk.
    Metadata is stored in database.
    """
    # Verify client exists
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id is required")
    
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large (max {MAX_FILE_SIZE_MB}MB)"
        )
    
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Encrypt file content
    try:
        encrypted_content = encrypt_file_content(content)
        encryption_key_hash = hashlib.sha256(
            os.getenv("FILE_ENCRYPTION_KEY", "").encode()
        ).hexdigest()[:32]  # Store hash for audit, not the key itself
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")
    
    # Generate file path
    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}{ext}.enc"  # .enc extension for encrypted files
    file_path = os.path.join(STORAGE_PATH, stored_filename)
    
    # Save encrypted file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(encrypted_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create document record in database
    document = Document(
        client_id=client.id,
        name=file.filename,
        original_filename=file.filename,
        file_type=ext[1:] if ext else "unknown",
        file_size=len(content),  # Store original size, not encrypted size
        file_path=file_path,
        section_name=section,
        document_type=document_type,
        status="pending",
        encrypted=True,
        encryption_key_hash=encryption_key_hash,
        uploaded_at=datetime.utcnow(),
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return DocumentResponse(
        id=str(document.id),
        name=document.name,
        original_filename=document.original_filename,
        file_type=document.file_type,
        file_size=document.file_size,
        section_name=document.section_name,
        status=document.status,
        encrypted=document.encrypted,
        created_at=document.created_at.isoformat(),
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """
    Download a document (decrypts on-the-fly).
    
    Returns the decrypted file for download.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read encrypted file
    try:
        with open(document.file_path, "rb") as f:
            encrypted_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on disk")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
    
    # Decrypt file content
    try:
        if document.encrypted:
            decrypted_content = decrypt_file_content(encrypted_content)
        else:
            decrypted_content = encrypted_content  # Legacy unencrypted file
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
    
    # Return file as download
    return StreamingResponse(
        iter([decrypted_content]),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{document.original_filename}"',
            "Content-Length": str(len(decrypted_content)),
        }
    )


@router.get("/client/{client_id}", response_model=DocumentListResponse)
def list_client_documents(
    client_id: str,
    section: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all documents for a client."""
    query = db.query(Document).filter(Document.client_id == client_id)
    
    if section:
        query = query.filter(Document.section_name == section)
    
    documents = query.order_by(Document.created_at.desc()).all()
    
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=str(doc.id),
                name=doc.name,
                original_filename=doc.original_filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                section_name=doc.section_name,
                status=doc.status,
                encrypted=doc.encrypted,
                created_at=doc.created_at.isoformat(),
            )
            for doc in documents
        ],
        total=len(documents),
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Delete a document (removes file and database record)."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        # Log error but continue with DB deletion
        print(f"Warning: Failed to delete file {document.file_path}: {e}")
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
