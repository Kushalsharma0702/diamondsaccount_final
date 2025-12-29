"""
Report Service for TaxEase
Handles PDF report generation for tax forms and summaries
"""

import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import uuid
import logging
from typing import List
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from shared.database import get_db, Database
from shared.models import User, Report, T1PersonalForm
from shared.schemas import (
    ReportResponse, ReportRequest, MessageResponse, HealthResponse
)
from shared.auth import get_current_user
from shared.utils import S3Manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TaxEase Report Service",
    description="PDF report generation service for tax documents",
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

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await Database.create_tables()
    logger.info("Report service started successfully")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="report",
        version="1.0.0"
    )

@app.post("/api/v1/reports/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_data: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new report"""
    
    # Create report record
    report = Report(
        id=uuid.uuid4(),
        user_id=current_user.id,
        report_type=report_data.report_type,
        title=report_data.title,
        status="generating"
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    # Generate report in background
    background_tasks.add_task(
        generate_report_pdf, 
        str(report.id), 
        report_data.report_type, 
        str(current_user.id)
    )
    
    logger.info(f"Report generation started: {report.id}")
    return report

@app.get("/api/v1/reports", response_model=List[ReportResponse])
async def list_user_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of user's reports"""
    
    result = await db.execute(
        select(Report).where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
    )
    reports = result.scalars().all()
    
    return list(reports)

@app.get("/api/v1/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific report by ID"""
    
    result = await db.execute(
        select(Report).where(
            and_(
                Report.id == report_id,
                Report.user_id == current_user.id
            )
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report

@app.get("/api/v1/reports/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download report PDF"""
    
    result = await db.execute(
        select(Report).where(
            and_(
                Report.id == report_id,
                Report.user_id == current_user.id
            )
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report not ready for download"
        )
    
    if not report.file_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Report file not available"
        )
    
    # Redirect to S3 presigned URL or return the URL
    return RedirectResponse(url=report.file_url)

@app.delete("/api/v1/reports/{report_id}", response_model=MessageResponse)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete report"""
    
    result = await db.execute(
        select(Report).where(
            and_(
                Report.id == report_id,
                Report.user_id == current_user.id
            )
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Delete from S3 if exists
    if report.file_url:
        # Extract S3 key from URL and delete
        # This is simplified - in production, store S3 key separately
        pass
    
    # Delete from database
    await db.delete(report)
    await db.commit()
    
    logger.info(f"Report deleted: {report_id}")
    return MessageResponse(message="Report deleted successfully")

@app.get("/api/v1/reports/test")
async def test_endpoint():
    """Test endpoint for service health"""
    return {
        "message": "Report service is running!",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "report"
    }

async def generate_report_pdf(report_id: str, report_type: str, user_id: str):
    """Background task to generate PDF report"""
    
    try:
        from shared.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            # Get report record
            result = await db.execute(select(Report).where(Report.id == report_id))
            report = result.scalar_one_or_none()
            
            if not report:
                return
            
            # Generate PDF based on report type
            if report_type == "t1_summary":
                pdf_content = await generate_t1_summary_pdf(user_id, db)
            elif report_type == "tax_calculation":
                pdf_content = await generate_tax_calculation_pdf(user_id, db)
            else:
                report.status = "failed"
                await db.commit()
                return
            
            # Upload PDF to S3
            s3_key = f"reports/{user_id}/{report_id}.pdf"
            success = await s3_manager.upload_file(
                pdf_content, 
                s3_key, 
                "application/pdf"
            )
            
            if success:
                # Generate presigned URL
                download_url = s3_manager.generate_presigned_url(s3_key, expiration=3600*24)  # 24 hours
                
                report.status = "ready"
                report.file_url = download_url
                report.generated_at = datetime.utcnow()
            else:
                report.status = "failed"
            
            await db.commit()
            logger.info(f"Report generated: {report_id}")
            
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        # Update report status to failed
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Report).where(Report.id == report_id))
            report = result.scalar_one_or_none()
            if report:
                report.status = "failed"
                await db.commit()

async def generate_t1_summary_pdf(user_id: str, db: AsyncSession) -> bytes:
    """Generate T1 tax summary PDF"""
    
    # Get user and tax forms
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    
    forms_result = await db.execute(
        select(T1PersonalForm).where(T1PersonalForm.user_id == user_id)
        .order_by(T1PersonalForm.tax_year.desc())
    )
    forms = forms_result.scalars().all()
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"T1 Personal Tax Summary - {user.first_name} {user.last_name}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Summary table
    if forms:
        data = [['Tax Year', 'Total Income', 'Federal Tax', 'Provincial Tax', 'Total Tax', 'Status']]
        
        for form in forms:
            data.append([
                str(form.tax_year),
                f"${form.total_income:,.2f}",
                f"${form.federal_tax:,.2f}",
                f"${form.provincial_tax:,.2f}",
                f"${form.total_tax:,.2f}",
                form.status.title()
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    else:
        story.append(Paragraph("No tax forms found.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

async def generate_tax_calculation_pdf(user_id: str, db: AsyncSession) -> bytes:
    """Generate tax calculation details PDF"""
    
    # Similar implementation to T1 summary but with more detailed calculations
    # This is a simplified version
    return await generate_t1_summary_pdf(user_id, db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
