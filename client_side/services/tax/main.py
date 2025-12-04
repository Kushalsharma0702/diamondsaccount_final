"""
Tax Service for TaxEase
Handles tax form creation, calculation, and submission
"""

import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import uuid
import logging
from typing import List

from shared.database import get_db, Database
from shared.models import User, T1PersonalForm
from shared.schemas import (
    T1PersonalFormCreate, T1PersonalFormUpdate, T1PersonalFormResponse,
    MessageResponse, HealthResponse
)
from shared.auth import get_current_user
from shared.utils import calculate_tax

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TaxEase Tax Service",
    description="Tax form processing and calculation service",
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

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await Database.create_tables()
    logger.info("Tax service started successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="tax",
        version="1.0.0"
    )

@app.post("/api/v1/tax/t1-personal", response_model=T1PersonalFormResponse, status_code=status.HTTP_201_CREATED)
async def create_t1_form(
    form_data: T1PersonalFormCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new T1 Personal Tax Form"""
    
    # Check if user already has a form for this tax year
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.user_id == current_user.id,
                T1PersonalForm.tax_year == form_data.tax_year
            )
        )
    )
    existing_form = result.scalar_one_or_none()
    
    if existing_form:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"T1 form for {form_data.tax_year} already exists"
        )
    
    # Create new form
    new_form = T1PersonalForm(
        id=uuid.uuid4(),
        user_id=current_user.id,
        tax_year=form_data.tax_year,
        sin=form_data.sin,
        marital_status=form_data.marital_status,
        employment_income=form_data.employment_income,
        self_employment_income=form_data.self_employment_income,
        investment_income=form_data.investment_income,
        other_income=form_data.other_income,
        rrsp_contributions=form_data.rrsp_contributions,
        charitable_donations=form_data.charitable_donations,
        status="draft"
    )
    
    # Calculate totals and taxes
    await calculate_form_taxes(new_form)
    
    db.add(new_form)
    await db.commit()
    await db.refresh(new_form)
    
    logger.info(f"T1 form created for user {current_user.email}, year {form_data.tax_year}")
    return new_form

@app.get("/api/v1/tax/t1-personal", response_model=List[T1PersonalFormResponse])
async def get_user_tax_forms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all T1 forms for current user"""
    
    result = await db.execute(
        select(T1PersonalForm).where(T1PersonalForm.user_id == current_user.id)
        .order_by(T1PersonalForm.tax_year.desc())
    )
    forms = result.scalars().all()
    
    return list(forms)

@app.get("/api/v1/tax/t1-personal/{form_id}", response_model=T1PersonalFormResponse)
async def get_tax_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific T1 form by ID"""
    
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.id == form_id,
                T1PersonalForm.user_id == current_user.id
            )
        )
    )
    form = result.scalar_one_or_none()
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    return form

@app.put("/api/v1/tax/t1-personal/{form_id}", response_model=T1PersonalFormResponse)
async def update_tax_form(
    form_id: str,
    form_data: T1PersonalFormUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update T1 form"""
    
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.id == form_id,
                T1PersonalForm.user_id == current_user.id
            )
        )
    )
    form = result.scalar_one_or_none()
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    if form.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update submitted form"
        )
    
    # Update form fields
    update_data = form_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(form, field):
            setattr(form, field, value)
    
    # Recalculate taxes
    await calculate_form_taxes(form)
    
    form.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(form)
    
    logger.info(f"T1 form updated: {form_id}")
    return form

@app.post("/api/v1/tax/t1-personal/{form_id}/submit", response_model=MessageResponse)
async def submit_tax_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit T1 form for processing"""
    
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.id == form_id,
                T1PersonalForm.user_id == current_user.id
            )
        )
    )
    form = result.scalar_one_or_none()
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    if form.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form already submitted"
        )
    
    # Validate required fields
    if not form.sin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SIN is required for submission"
        )
    
    # Submit form
    form.status = "submitted"
    form.submitted_at = datetime.utcnow()
    await db.commit()
    
    logger.info(f"T1 form submitted: {form_id}")
    return MessageResponse(message="Tax form submitted successfully")

@app.delete("/api/v1/tax/t1-personal/{form_id}", response_model=MessageResponse)
async def delete_tax_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete T1 form (only if not submitted)"""
    
    result = await db.execute(
        select(T1PersonalForm).where(
            and_(
                T1PersonalForm.id == form_id,
                T1PersonalForm.user_id == current_user.id
            )
        )
    )
    form = result.scalar_one_or_none()
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    if form.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete submitted form"
        )
    
    await db.delete(form)
    await db.commit()
    
    logger.info(f"T1 form deleted: {form_id}")
    return MessageResponse(message="Tax form deleted successfully")

@app.get("/api/v1/tax/test")
async def test_endpoint():
    """Test endpoint for service health"""
    return {
        "message": "Tax service is running!",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "tax"
    }

# Helper functions
async def calculate_form_taxes(form: T1PersonalForm):
    """Calculate taxes for T1 form"""
    
    # Calculate total income
    form.total_income = (
        (form.employment_income or 0) +
        (form.self_employment_income or 0) +
        (form.investment_income or 0) +
        (form.other_income or 0)
    )
    
    # Calculate taxable income (simplified - deduct RRSP and charitable donations)
    taxable_income = form.total_income - (form.rrsp_contributions or 0) - (form.charitable_donations or 0)
    
    if taxable_income > 0:
        # Calculate taxes using utility function
        tax_calculation = calculate_tax(taxable_income, "ON")  # Assuming Ontario
        
        form.federal_tax = tax_calculation["federal_tax"]
        form.provincial_tax = tax_calculation["provincial_tax"]
        form.total_tax = tax_calculation["total_tax"]
        
        # Calculate refund or amount owing (simplified)
        # In reality, this would consider tax deductions, credits, and amounts already paid
        form.refund_or_owing = form.total_tax
    else:
        form.federal_tax = 0.0
        form.provincial_tax = 0.0
        form.total_tax = 0.0
        form.refund_or_owing = 0.0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
