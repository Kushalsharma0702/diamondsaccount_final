"""
T1 Forms endpoints - Access client backend T1 forms from admin backend
Since both backends use the same database, we query directly from t1_personal_forms table
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy import text
from typing import Optional, List
import httpx
import os
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.client import Client
try:
    from app.schemas.t1_form import T1FormListResponse, T1FormResponse
except ImportError:
    # Fallback if schema not found
    from pydantic import BaseModel
    from typing import Optional, List
    
    class T1FormResponse(BaseModel):
        id: str
        user_id: Optional[str] = None
        tax_year: int
        status: str
        first_name: Optional[str] = None
        last_name: Optional[str] = None
        client_email: Optional[str] = None
        created_at: Optional[str] = None
        updated_at: Optional[str] = None
        submitted_at: Optional[str] = None
    
    class T1FormListResponse(BaseModel):
        forms: List[T1FormResponse]
        total: int
        offset: int
        limit: int
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/t1-forms", tags=["T1 Forms"])

# Client backend URL (for fallback if needed)
CLIENT_BACKEND_URL = os.getenv("CLIENT_BACKEND_URL", "http://localhost:8001/api/v1")


@router.get("", response_model=T1FormListResponse)
async def get_t1_forms(
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    client_email: Optional[str] = Query(None, description="Filter by client email"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Get T1 forms from client backend
    Admin can view all T1 forms or filter by client
    """
    try:
        # Since both backends use the same database, query directly from t1_personal_forms table
        # Build base query using raw SQL
        query_parts = [
            "SELECT",
            "    t1.id,",
            "    t1.user_id,",
            "    t1.tax_year,",
            "    t1.status,",
            "    t1.first_name,",
            "    t1.last_name,",
            "    COALESCE(t1.email, u.email) as client_email,",
            "    t1.created_at,",
            "    t1.updated_at,",
            "    t1.submitted_at",
            "FROM t1_personal_forms t1",
            "LEFT JOIN users u ON t1.user_id = u.id"
        ]
        
        count_query_parts = [
            "SELECT COUNT(*) as total",
            "FROM t1_personal_forms t1",
            "LEFT JOIN users u ON t1.user_id = u.id"
        ]
        
        # Add filters
        conditions = []
        params = {}
        
        if client_id:
            try:
                user_uuid = uuid.UUID(client_id)
                conditions.append("t1.user_id = :user_id")
                params["user_id"] = str(user_uuid)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid client_id format")
        
        if client_email:
            conditions.append("(LOWER(t1.email) = LOWER(:client_email) OR LOWER(u.email) = LOWER(:client_email))")
            params["client_email"] = client_email
        
        if status_filter:
            conditions.append("t1.status = :status")
            params["status"] = status_filter
        
        # Apply filters
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            query_parts.append(where_clause)
            count_query_parts.append(where_clause)
        
        # Build final queries
        base_query_sql = " ".join(query_parts) + " ORDER BY t1.created_at DESC LIMIT :limit OFFSET :offset"
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
        forms = []
        for row in rows:
            forms.append({
                "id": row[0],
                "user_id": str(row[1]) if row[1] else None,
                "tax_year": row[2],
                "status": row[3],
                "first_name": row[4],
                "last_name": row[5],
                "client_email": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None,
                "submitted_at": row[9].isoformat() if row[9] else None,
            })
        
        logger.info(f"✅ Retrieved {len(forms)} T1 forms from database (total: {total})")
        
        return {
            "forms": forms,
            "total": total,
            "offset": offset,
            "limit": limit
        }
                
    except httpx.RequestError as e:
        logger.error(f"Error connecting to client backend: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Client backend is not available"
        )
    except Exception as e:
        logger.error(f"Error fetching T1 forms: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )





