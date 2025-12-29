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
        # Since both backends use the same database, query directly.
        # We support BOTH:
        # - legacy/encrypted: t1_personal_forms
        # - new business schema: t1_forms_main + t1_personal_info
        union_query_parts = [
            "SELECT * FROM (",
            "  SELECT",
            "    t1.id::text as id,",
            "    t1.user_id::text as user_id,",
            "    t1.tax_year::int as tax_year,",
            "    t1.status as status,",
            "    t1.first_name as first_name,",
            "    t1.last_name as last_name,",
            "    COALESCE(t1.email, u.email) as client_email,",
            "    t1.created_at as created_at,",
            "    t1.updated_at as updated_at,",
            "    t1.submitted_at as submitted_at",
            "  FROM t1_personal_forms t1",
            "  LEFT JOIN users u ON t1.user_id = u.id",
            "",
            "  UNION ALL",
            "",
            "  SELECT",
            "    tm.id::text as id,",
            "    tm.user_id::text as user_id,",
            "    EXTRACT(YEAR FROM tm.created_at)::int as tax_year,",
            "    tm.status as status,",
            "    pi.first_name as first_name,",
            "    pi.last_name as last_name,",
            "    COALESCE(pi.email, u.email) as client_email,",
            "    tm.created_at as created_at,",
            "    tm.updated_at as updated_at,",
            "    CASE WHEN tm.status = 'submitted' THEN tm.updated_at ELSE NULL END as submitted_at",
            "  FROM t1_forms_main tm",
            "  LEFT JOIN t1_personal_info pi ON pi.form_id = tm.id",
            "  LEFT JOIN users u ON tm.user_id = u.id",
            ") forms"
        ]

        count_query_parts = [
            "SELECT COUNT(*) as total FROM (",
            "  SELECT",
            "    t1.id::text as id,",
            "    t1.user_id::text as user_id,",
            "    t1.tax_year::int as tax_year,",
            "    t1.status as status,",
            "    t1.first_name as first_name,",
            "    t1.last_name as last_name,",
            "    COALESCE(t1.email, u.email) as client_email,",
            "    t1.created_at as created_at,",
            "    t1.updated_at as updated_at,",
            "    t1.submitted_at as submitted_at",
            "  FROM t1_personal_forms t1",
            "  LEFT JOIN users u ON t1.user_id = u.id",
            "  UNION ALL",
            "  SELECT",
            "    tm.id::text as id,",
            "    tm.user_id::text as user_id,",
            "    EXTRACT(YEAR FROM tm.created_at)::int as tax_year,",
            "    tm.status as status,",
            "    pi.first_name as first_name,",
            "    pi.last_name as last_name,",
            "    COALESCE(pi.email, u.email) as client_email,",
            "    tm.created_at as created_at,",
            "    tm.updated_at as updated_at,",
            "    CASE WHEN tm.status = 'submitted' THEN tm.updated_at ELSE NULL END as submitted_at",
            "  FROM t1_forms_main tm",
            "  LEFT JOIN t1_personal_info pi ON pi.form_id = tm.id",
            "  LEFT JOIN users u ON tm.user_id = u.id",
            ") forms"
        ]
        
        # Add filters
        conditions = []
        params = {}
        
        if client_id:
            try:
                user_uuid = uuid.UUID(client_id)
                conditions.append("forms.user_id = :user_id")
                params["user_id"] = str(user_uuid)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid client_id format")
        
        if client_email:
            conditions.append("LOWER(forms.client_email) = LOWER(:client_email)")
            params["client_email"] = client_email
        
        if status_filter:
            conditions.append("forms.status = :status")
            params["status"] = status_filter
        
        # Apply filters
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            union_query_parts.append(where_clause)
            count_query_parts.append(where_clause)
        
        # Build final queries
        base_query_sql = " ".join(union_query_parts) + " ORDER BY forms.created_at DESC LIMIT :limit OFFSET :offset"
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
                "tax_year": int(row[2]) if row[2] else datetime.utcnow().year,
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


@router.get("/{form_id}/detailed", response_model=dict)
async def get_t1_form_with_files(
    form_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Get detailed T1 form data with categorized file attachments
    Shows form sections completion status and associated files
    """
    try:
        # Get T1 form basic info
        form_query = text("""
            SELECT 
                t1.id::text as id,
                t1.user_id::text as user_id,
                t1.tax_year as tax_year,
                t1.status as status,
                t1.first_name as first_name,
                t1.last_name as last_name,
                t1.email as email,
                t1.has_moving_expenses,
                t1.has_medical_expenses,
                t1.has_charitable_donations,
                t1.has_foreign_property,
                t1.is_self_employed,
                t1.form_data,
                t1.created_at,
                t1.updated_at,
                u.email as user_email
            FROM t1_personal_forms t1
            LEFT JOIN users u ON t1.user_id = u.id
            WHERE t1.id = :form_id
        """)
        
        result = await db.execute(form_query, {"form_id": form_id})
        form_row = result.fetchone()
        
        if not form_row:
            raise HTTPException(status_code=404, detail="T1 form not found")
        
        # Get files associated with this user
        files_query = text("""
            SELECT 
                f.id::text as id,
                f.filename as filename,
                f.original_filename as original_filename,
                f.file_type as file_type,
                f.file_size as file_size,
                f.upload_status as upload_status,
                f.created_at as created_at
            FROM files f
            WHERE f.user_id = :user_id
            ORDER BY f.created_at DESC
        """)
        
        files_result = await db.execute(files_query, {"user_id": form_row[1]})
        files_rows = files_result.fetchall()
        
        # Categorize files based on form data and naming patterns
        categorized_files = categorize_files_by_form_sections(files_rows, form_row)
        
        # Build form sections summary
        form_sections = build_form_sections_summary(form_row, categorized_files)
        
        # Format files for response
        all_files = []
        for row in files_rows:
            all_files.append({
                "id": row[0],
                "filename": row[1],
                "original_filename": row[2],
                "file_type": row[3],
                "file_size": row[4],
                "upload_status": row[5],
                "created_at": row[6].isoformat() if row[6] else None
            })
        
        return {
            "form": {
                "id": form_row[0],
                "user_id": form_row[1],
                "tax_year": form_row[2],
                "status": form_row[3],
                "first_name": form_row[4],
                "last_name": form_row[5],
                "email": form_row[6] or form_row[15],  # form email or user email
                "created_at": form_row[13].isoformat() if form_row[13] else None,
                "updated_at": form_row[14].isoformat() if form_row[14] else None
            },
            "form_sections": form_sections,
            "categorized_files": categorized_files,
            "all_files": all_files
        }
        
    except Exception as e:
        logger.error(f"Error fetching detailed T1 form: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def categorize_files_by_form_sections(files_rows, form_row):
    """
    Categorize uploaded files based on form sections and file naming patterns
    """
    categorized = {
        "Moving Expenses": [],
        "Self Employment": [],
        "Employment Income": [],
        "Medical Expenses": [],
        "Foreign Property": [],
        "Charitable Donations": [],
        "General Documents": []
    }
    
    # Define keywords for categorization
    keywords_map = {
        "Moving Expenses": ["moving", "relocation", "travel", "distance", "employer"],
        "Self Employment": ["business", "uber", "skip", "receipt", "invoice", "expense", "t2125", "home_office", "vehicle"],
        "Employment Income": ["t4", "employment", "pay_stub", "salary", "wage"],
        "Medical Expenses": ["medical", "dental", "prescription", "hospital", "doctor"],
        "Foreign Property": ["foreign", "international", "t1135", "currency"],
        "Charitable Donations": ["donation", "charitable", "charity", "receipt"]
    }
    
    for file_row in files_rows:
        filename = file_row[2].lower()  # original_filename
        categorized_file = {
            "id": file_row[0],
            "name": file_row[2],
            "size": format_file_size(file_row[4]),
            "type": get_file_type_category(file_row[3]),
            "created_at": file_row[6].isoformat() if file_row[6] else None
        }
        
        # Try to categorize based on filename keywords
        categorized_flag = False
        for category, keywords in keywords_map.items():
            if any(keyword in filename for keyword in keywords):
                # Additional checks based on form flags
                if category == "Moving Expenses" and form_row[7]:  # has_moving_expenses
                    categorized[category].append(categorized_file)
                    categorized_flag = True
                    break
                elif category == "Self Employment" and form_row[11]:  # is_self_employed
                    categorized[category].append(categorized_file)
                    categorized_flag = True
                    break
                elif category == "Medical Expenses" and form_row[8]:  # has_medical_expenses
                    categorized[category].append(categorized_file)
                    categorized_flag = True
                    break
                elif category == "Foreign Property" and form_row[10]:  # has_foreign_property
                    categorized[category].append(categorized_file)
                    categorized_flag = True
                    break
                elif category == "Charitable Donations" and form_row[9]:  # has_charitable_donations
                    categorized[category].append(categorized_file)
                    categorized_flag = True
                    break
                elif category == "Employment Income":
                    categorized[category].append(categorized_file)
                    categorized_flag = True
                    break
        
        # If not categorized, put in general documents
        if not categorized_flag:
            categorized["General Documents"].append(categorized_file)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}


def build_form_sections_summary(form_row, categorized_files):
    """
    Build form sections summary with completion status
    """
    sections = [
        {
            "name": "Personal Information",
            "icon": "fa-user",
            "completed": bool(form_row[4] and form_row[5]),  # first_name and last_name
            "description": "Basic personal details, SIN, address",
            "file_count": 0  # Personal info usually doesn't have files
        },
        {
            "name": "Employment Income", 
            "icon": "fa-briefcase",
            "completed": True,  # Assume completed if form exists
            "description": "T4 slips, employment details",
            "file_count": len(categorized_files.get("Employment Income", []))
        },
        {
            "name": "Moving Expenses",
            "icon": "fa-truck", 
            "completed": bool(form_row[7]),  # has_moving_expenses
            "description": "Moving receipts, travel expenses, company relocation",
            "file_count": len(categorized_files.get("Moving Expenses", []))
        },
        {
            "name": "Self Employment",
            "icon": "fa-store",
            "completed": bool(form_row[11]),  # is_self_employed
            "description": "Business income, expenses, receipts",
            "file_count": len(categorized_files.get("Self Employment", []))
        },
        {
            "name": "Medical Expenses",
            "icon": "fa-heart-pulse",
            "completed": bool(form_row[8]),  # has_medical_expenses  
            "description": "Medical receipts, insurance claims",
            "file_count": len(categorized_files.get("Medical Expenses", []))
        },
        {
            "name": "Charitable Donations",
            "icon": "fa-hand-holding-heart",
            "completed": bool(form_row[9]),  # has_charitable_donations
            "description": "Donation receipts, charitable contributions", 
            "file_count": len(categorized_files.get("Charitable Donations", []))
        },
        {
            "name": "Foreign Property",
            "icon": "fa-globe",
            "completed": bool(form_row[10]),  # has_foreign_property
            "description": "Foreign income, property details",
            "file_count": len(categorized_files.get("Foreign Property", []))
        }
    ]
    
    return sections


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def get_file_type_category(file_type):
    """Get file type category for icon display"""
    if 'pdf' in file_type.lower():
        return 'pdf'
    elif any(img_type in file_type.lower() for img_type in ['jpg', 'jpeg', 'png', 'gif', 'bmp']):
        return 'image'
    elif any(archive_type in file_type.lower() for archive_type in ['zip', 'rar', '7z', 'tar']):
        return 'zip'
    elif any(excel_type in file_type.lower() for excel_type in ['excel', 'xlsx', 'xls']):
        return 'excel'
    elif any(word_type in file_type.lower() for word_type in ['word', 'docx', 'doc']):
        return 'word'
    else:
        return 'default'





