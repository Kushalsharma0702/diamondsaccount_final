"""
File Service for TaxEase
Handles file uploads, storage, and retrieval with AWS S3 integration
"""

import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File as FastAPIFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import uuid
import logging
from typing import List
import magic

from shared.database import get_db, Database
from shared.models import User, File
from shared.schemas import (
    FileUploadResponse, FileListResponse, MessageResponse, HealthResponse
)
from shared.auth import get_current_user
from shared.utils import S3Manager, generate_filename, validate_file_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TaxEase File Service",
    description="File upload and storage service with AWS S3 integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize S3 manager
s3_manager = S3Manager()

# Allowed file types for tax documents
ALLOWED_FILE_TYPES = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await Database.create_tables()
    logger.info("File service started successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="file",
        version="1.0.0"
    )

@app.post("/api/v1/files/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file to S3 and store metadata"""
    
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024:.1f}MB"
        )
    
    # Validate file type
    if not validate_file_type(file.filename, ALLOWED_FILE_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Detect MIME type
    mime_type = magic.from_buffer(file_content, mime=True)
    
    # Generate unique filename
    unique_filename = generate_filename(file.filename)
    s3_key = f"user_{current_user.id}/{unique_filename}"
    
    # Create file record
    file_record = File(
        id=uuid.uuid4(),
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_type=mime_type,
        file_size=len(file_content),
        s3_bucket=s3_manager.bucket_name,
        s3_key=s3_key,
        upload_status="pending"
    )
    
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)
    
    try:
        # Upload to S3
        success = await s3_manager.upload_file(file_content, s3_key, mime_type)
        
        if success:
            file_record.upload_status = "uploaded"
            logger.info(f"File uploaded successfully: {s3_key}")
        else:
            file_record.upload_status = "failed"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage"
            )
        
        await db.commit()
        await db.refresh(file_record)
        
    except Exception as e:
        file_record.upload_status = "failed"
        await db.commit()
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )
    
    return file_record

@app.get("/api/v1/files", response_model=FileListResponse)
async def list_user_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get list of user's uploaded files"""
    
    # Get files with pagination
    result = await db.execute(
        select(File).where(File.user_id == current_user.id)
        .order_by(File.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    files = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(File).where(File.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())
    
    return FileListResponse(
        files=list(files),
        total=total
    )

@app.get("/api/v1/files/{file_id}", response_model=FileUploadResponse)
async def get_file_metadata(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get file metadata by ID"""
    
    result = await db.execute(
        select(File).where(
            and_(
                File.id == file_id,
                File.user_id == current_user.id
            )
        )
    )
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file_record

@app.get("/api/v1/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate presigned URL for file download"""
    
    result = await db.execute(
        select(File).where(
            and_(
                File.id == file_id,
                File.user_id == current_user.id
            )
        )
    )
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if file_record.upload_status != "uploaded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File not available for download"
        )
    
    # Generate presigned URL
    download_url = s3_manager.generate_presigned_url(file_record.s3_key)
    
    if not download_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download link"
        )
    
    # Redirect to presigned URL
    return RedirectResponse(url=download_url)

@app.delete("/api/v1/files/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete file from S3 and database"""
    
    result = await db.execute(
        select(File).where(
            and_(
                File.id == file_id,
                File.user_id == current_user.id
            )
        )
    )
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Delete from S3
        if file_record.s3_key:
            await s3_manager.delete_file(file_record.s3_key)
        
        # Delete from database
        await db.delete(file_record)
        await db.commit()
        
        logger.info(f"File deleted: {file_id}")
        return MessageResponse(message="File deleted successfully")
        
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

@app.get("/api/v1/files/test")
async def test_endpoint():
    """Test endpoint for service health"""
    return {
        "message": "File service is running!",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "file"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
