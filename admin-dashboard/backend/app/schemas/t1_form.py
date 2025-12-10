"""
T1 Form schemas for admin dashboard
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class T1FormResponse(BaseModel):
    """T1 Form response schema"""
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
    
    class Config:
        from_attributes = True


class T1FormListResponse(BaseModel):
    """T1 Form list response schema"""
    forms: list[T1FormResponse]
    total: int
    offset: int
    limit: int

