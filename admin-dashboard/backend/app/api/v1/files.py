"""
Files/Documents endpoints - Access uploaded files from client backend
Since both backends use the same database, we query directly from files table
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, List
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["Files"])


class FileResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    upload_status: str
    created_at: Optional[str] = None
    client_email: Optional[str] = None


class FileListResponse(BaseModel):
    files: List[FileResponse]
    total: int
    offset: int
    limit: int


@router.get("", response_model=FileListResponse)
async def get_files(
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    client_email: Optional[str] = Query(None, description="Filter by client email"),
    status_filter: Optional[str] = Query(None, description="Filter by upload status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Get uploaded files from client backend
    Admin can view all uploaded files or filter by client
    """
    try:
        # Query directly from files table (same database)
        query_parts = [
            "SELECT",
            "    f.id::text,",
            "    f.user_id::text,",
            "    f.filename,",
            "    f.original_filename,",
            "    f.file_type,",
            "    f.file_size,",
            "    f.upload_status,",
            "    f.created_at,",
            "    COALESCE(u.email, '') as client_email",
            "FROM files f",
            "LEFT JOIN users u ON f.user_id = u.id"
        ]
        
        count_query_parts = [
            "SELECT COUNT(*) as total",
            "FROM files f",
            "LEFT JOIN users u ON f.user_id = u.id"
        ]
        
        # Add filters
        conditions = []
        params = {}
        
        if client_id:
            try:
                user_uuid = uuid.UUID(client_id)
                conditions.append("f.user_id = :user_id")
                params["user_id"] = str(user_uuid)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid client_id format")
        
        if client_email:
            conditions.append("(LOWER(u.email) = LOWER(:client_email))")
            params["client_email"] = client_email
        
        if status_filter:
            conditions.append("f.upload_status = :status")
            params["status"] = status_filter
        
        # Apply filters
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            query_parts.append(where_clause)
            count_query_parts.append(where_clause)
        
        # Build final queries
        base_query_sql = " ".join(query_parts) + " ORDER BY f.created_at DESC LIMIT :limit OFFSET :offset"
        count_query_sql = " ".join(count_query_parts)
        
        params["limit"] = limit
        params["offset"] = offset
        
        # Execute queries
        result = await db.execute(text(base_query_sql), params)
        rows = result.fetchall()
        
        count_params = {k: v for k, v in params.items() if k != "limit" and k != "offset"}
        count_result = await db.execute(text(count_query_sql), count_params)
        total = count_result.scalar()
        
        # Format response
        files = []
        for row in rows:
            files.append({
                "id": str(row[0]),
                "user_id": str(row[1]) if row[1] else None,
                "filename": row[2],
                "original_filename": row[3],
                "file_type": row[4],
                "file_size": row[5],
                "upload_status": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "client_email": row[8] if row[8] else None,
            })
        
        logger.info(f"✅ Retrieved {len(files)} files from database (total: {total})")
        
        return {
            "files": files,
            "total": total,
            "offset": offset,
            "limit": limit
        }
                
    except Exception as e:
        logger.error(f"Error fetching files: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

