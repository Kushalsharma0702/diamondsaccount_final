"""
Users routes - Fetch actual users from users table with their filings and T1 forms
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.utils import calculate_pagination

router = APIRouter()


class UserFilingData(BaseModel):
    """User with filing and T1 form data"""
    id: str
    email: str
    name: str
    phone: Optional[str]
    filing_count: int
    t1_form_count: int
    latest_filing: Optional[datetime]
    is_active: bool
    email_verified: bool
    created_at: datetime


class UserListResponse(BaseModel):
    """Response for user list"""
    users: list[UserFilingData]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    search: Optional[str] = None,
    has_filings: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get all users with their filing counts and T1 form data"""
    
    # Build the query
    base_query = """
        SELECT 
            u.id,
            u.email,
            CONCAT(COALESCE(u.first_name, ''), ' ', COALESCE(u.last_name, '')) as name,
            u.phone,
            u.is_active,
            u.email_verified,
            u.created_at,
            COUNT(DISTINCT f.id) as filing_count,
            COUNT(DISTINCT t.id) as t1_form_count,
            MAX(f.created_at) as latest_filing
        FROM users u
        LEFT JOIN filings f ON f.user_id = u.id
        LEFT JOIN t1_forms t ON t.user_id = u.id
        WHERE 1=1
    """
    
    params = {}
    
    # Add search filter
    if search:
        base_query += " AND (u.email ILIKE :search OR u.first_name ILIKE :search OR u.last_name ILIKE :search)"
        params['search'] = f"%{search}%"
    
    # Add filing filter
    if has_filings is not None:
        if has_filings:
            base_query += " AND EXISTS (SELECT 1 FROM filings f2 WHERE f2.user_id = u.id)"
        else:
            base_query += " AND NOT EXISTS (SELECT 1 FROM filings f2 WHERE f2.user_id = u.id)"
    
    base_query += " GROUP BY u.id, u.email, u.first_name, u.last_name, u.phone, u.is_active, u.email_verified, u.created_at"
    
    # Count total
    count_query = f"SELECT COUNT(*) FROM ({base_query}) as subquery"
    count_result = await db.execute(text(count_query), params)
    total = count_result.scalar()
    
    # Add ordering and pagination
    base_query += " ORDER BY latest_filing DESC NULLS LAST, u.created_at DESC"
    base_query += f" LIMIT :limit OFFSET :offset"
    params['limit'] = page_size
    params['offset'] = (page - 1) * page_size
    
    # Execute query
    result = await db.execute(text(base_query), params)
    rows = result.fetchall()
    
    # Format response
    users = []
    for row in rows:
        users.append(UserFilingData(
            id=str(row.id),
            email=row.email,
            name=row.name,
            phone=row.phone,
            is_active=row.is_active,
            email_verified=row.email_verified,
            filing_count=row.filing_count,
            t1_form_count=row.t1_form_count,
            latest_filing=row.latest_filing,
            created_at=row.created_at
        ))
    
    pagination = calculate_pagination(page, page_size, total)
    
    return UserListResponse(
        users=users,
        **pagination
    )


@router.get("/{user_id}/filings")
async def get_user_filings(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get all filings for a specific user with T1 form details"""
    
    query = text("""
        SELECT 
            f.id as filing_id,
            f.filing_year,
            f.status as filing_status,
            f.created_at as filing_created,
            f.updated_at as filing_updated,
            t.id as t1_form_id,
            t.status as t1_status,
            t.completion_percentage,
            t.is_locked,
            t.submitted_at,
            (SELECT COUNT(*) FROM t1_answers a WHERE a.t1_form_id = t.id) as answer_count
        FROM filings f
        LEFT JOIN t1_forms t ON t.filing_id = f.id
        WHERE f.user_id = :user_id
        ORDER BY f.created_at DESC
    """)
    
    result = await db.execute(query, {"user_id": str(user_id)})
    rows = result.fetchall()
    
    filings = []
    for row in rows:
        filing_data = {
            "filing_id": str(row.filing_id),
            "filing_year": row.filing_year,
            "filing_status": row.filing_status,
            "filing_created": row.filing_created.isoformat() if row.filing_created else None,
            "filing_updated": row.filing_updated.isoformat() if row.filing_updated else None,
            "t1_form": None
        }
        
        if row.t1_form_id:
            filing_data["t1_form"] = {
                "id": str(row.t1_form_id),
                "status": row.t1_status,
                "completion_percentage": row.completion_percentage,
                "is_locked": row.is_locked,
                "submitted_at": row.submitted_at.isoformat() if row.submitted_at else None,
                "answer_count": row.answer_count
            }
        
        filings.append(filing_data)
    
    return {
        "user_id": str(user_id),
        "total_filings": len(filings),
        "filings": filings
    }


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get a single user's basic information"""
    
    query = text("""
        SELECT 
            u.id,
            u.email,
            CONCAT(COALESCE(u.first_name, ''), ' ', COALESCE(u.last_name, '')) as name,
            u.phone,
            u.is_active,
            u.email_verified,
            u.created_at,
            COUNT(DISTINCT f.id) as filing_count,
            COUNT(DISTINCT t.id) as t1_form_count,
            MAX(f.created_at) as latest_filing
        FROM users u
        LEFT JOIN filings f ON f.user_id = u.id
        LEFT JOIN t1_forms t ON t.user_id = u.id
        WHERE u.id = :user_id
        GROUP BY u.id, u.email, u.first_name, u.last_name, u.phone, u.is_active, u.email_verified, u.created_at
    """)
    
    result = await db.execute(query, {"user_id": str(user_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(row.id),
        "email": row.email,
        "name": row.name,
        "phone": row.phone,
        "is_active": row.is_active,
        "email_verified": row.email_verified,
        "filing_count": row.filing_count,
        "t1_form_count": row.t1_form_count,
        "latest_filing": row.latest_filing.isoformat() if row.latest_filing else None,
        "created_at": row.created_at.isoformat() if row.created_at else None
    }


@router.get("/{user_id}/t1-form-data")
async def get_user_t1_form_data(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get user's T1 form data with all answers organized by section"""
    
    # Get T1 form info
    t1_query = text("""
        SELECT 
            t.id,
            t.filing_id,
            t.status,
            t.completion_percentage,
            t.is_locked,
            t.submitted_at,
            t.created_at,
            t.updated_at,
            f.filing_year
        FROM t1_forms t
        LEFT JOIN filings f ON t.filing_id = f.id
        WHERE t.user_id = :user_id
        ORDER BY t.created_at DESC
        LIMIT 1
    """)
    
    t1_result = await db.execute(t1_query, {"user_id": str(user_id)})
    t1_row = t1_result.fetchone()
    
    if not t1_row:
        return {
            "user_id": str(user_id),
            "has_t1_form": False,
            "t1_form": None
        }
    
    # Get all answers for this T1 form
    answers_query = text("""
        SELECT 
            a.id,
            a.field_key,
            a.value_boolean,
            a.value_text,
            a.value_numeric,
            a.value_date,
            a.value_array,
            a.created_at,
            a.updated_at
        FROM t1_answers a
        WHERE a.t1_form_id = :t1_form_id
        ORDER BY a.field_key
    """)
    
    answers_result = await db.execute(answers_query, {"t1_form_id": str(t1_row.id)})
    answers_rows = answers_result.fetchall()
    
    # Organize answers by field_key
    answers = []
    for answer_row in answers_rows:
        # Determine the actual value based on which value field is populated
        value = None
        value_type = None
        
        if answer_row.value_boolean is not None:
            value = answer_row.value_boolean
            value_type = "boolean"
        elif answer_row.value_text is not None:
            value = answer_row.value_text
            value_type = "text"
        elif answer_row.value_numeric is not None:
            value = float(answer_row.value_numeric)
            value_type = "numeric"
        elif answer_row.value_date is not None:
            value = answer_row.value_date.isoformat()
            value_type = "date"
        elif answer_row.value_array is not None:
            value = answer_row.value_array
            value_type = "array"
        
        answers.append({
            "id": str(answer_row.id),
            "field_key": answer_row.field_key,
            "value": value,
            "value_type": value_type,
            "created_at": answer_row.created_at.isoformat() if answer_row.created_at else None,
            "updated_at": answer_row.updated_at.isoformat() if answer_row.updated_at else None
        })
    
    return {
        "user_id": str(user_id),
        "has_t1_form": True,
        "t1_form": {
            "id": str(t1_row.id),
            "filing_id": str(t1_row.filing_id) if t1_row.filing_id else None,
            "filing_year": t1_row.filing_year,
            "status": t1_row.status,
            "completion_percentage": t1_row.completion_percentage,
            "is_locked": t1_row.is_locked,
            "submitted_at": t1_row.submitted_at.isoformat() if t1_row.submitted_at else None,
            "created_at": t1_row.created_at.isoformat() if t1_row.created_at else None,
            "updated_at": t1_row.updated_at.isoformat() if t1_row.updated_at else None,
            "answer_count": len(answers_rows),
            "answers": answers
        }
    }
