"""
Service layer for Filing operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from database.schemas_v2 import Filing, AdminFilingAssignment, Payment, FilingTimeline, User, Admin
from backend.app.core.errors import (
    ResourceNotFoundError,
    ResourceConflictError,
    AuthorizationError,
    ErrorCodes
)


class FilingService:
    """Business logic for Filing operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_filings(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        year: Optional[int] = None,
        status: Optional[str] = None
    ) -> tuple[List[Filing], int]:
        """Get all filings for a user"""
        query = self.db.query(Filing).filter(Filing.user_id == user_id)
        
        if year:
            query = query.filter(Filing.filing_year == year)
        if status:
            query = query.filter(Filing.status == status)
        
        total = query.count()
        
        filings = query.order_by(Filing.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return filings, total
    
    def get_admin_filings(
        self,
        admin_id: str,
        is_superadmin: bool,
        page: int = 1,
        page_size: int = 20,
        year: Optional[int] = None,
        status: Optional[str] = None
    ) -> tuple[List[Filing], int]:
        """Get filings for admin (assigned only, unless superadmin)"""
        query = self.db.query(Filing)
        
        # Non-superadmin can only see assigned filings
        if not is_superadmin:
            query = query.join(AdminFilingAssignment)\
                .filter(AdminFilingAssignment.admin_id == admin_id)
        
        if year:
            query = query.filter(Filing.filing_year == year)
        if status:
            query = query.filter(Filing.status == status)
        
        total = query.count()
        
        filings = query.order_by(Filing.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return filings, total
    
    def get_filing_by_id(self, filing_id: str) -> Filing:
        """Get filing by ID"""
        filing = self.db.query(Filing).filter(Filing.id == filing_id).first()
        if not filing:
            raise ResourceNotFoundError("Filing", filing_id)
        return filing
    
    def create_filing(self, user_id: str, filing_year: int) -> Filing:
        """Create new filing"""
        # Check for duplicate
        existing = self.db.query(Filing).filter(
            Filing.user_id == user_id,
            Filing.filing_year == filing_year
        ).first()
        
        if existing:
            raise ResourceConflictError(
                error_code=ErrorCodes.BUSINESS_DUPLICATE_FILING,
                message=f"Filing already exists for year {filing_year}",
                details={"filing_id": str(existing.id)}
            )
        
        # Create filing
        filing = Filing(
            user_id=user_id,
            filing_year=filing_year,
            status="documents_pending"
        )
        self.db.add(filing)
        self.db.commit()
        self.db.refresh(filing)
        
        # Add timeline event
        self._add_timeline_event(
            filing_id=filing.id,
            event_type="filing_created",
            description=f"Filing created for tax year {filing_year}",
            actor_type="user",
            actor_id=user_id
        )
        
        return filing
    
    def update_filing_status(
        self,
        filing_id: str,
        new_status: str,
        admin_id: str,
        admin_name: str
    ) -> Filing:
        """Update filing status"""
        filing = self.get_filing_by_id(filing_id)
        old_status = filing.status
        
        # TODO: Validate status transition
        
        filing.status = new_status
        filing.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(filing)
        
        # Add timeline event
        self._add_timeline_event(
            filing_id=filing.id,
            event_type="status_update",
            description=f"Status changed from {old_status} to {new_status}",
            actor_type="admin",
            actor_id=admin_id,
            actor_name=admin_name
        )
        
        return filing
    
    def update_filing_fee(
        self,
        filing_id: str,
        total_fee: float,
        admin_id: str,
        admin_name: str
    ) -> Filing:
        """Update filing total fee"""
        filing = self.get_filing_by_id(filing_id)
        
        filing.total_fee = total_fee
        filing.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(filing)
        
        # Add timeline event
        self._add_timeline_event(
            filing_id=filing.id,
            event_type="fee_set",
            description=f"Filing fee set to ${total_fee:.2f}",
            actor_type="admin",
            actor_id=admin_id,
            actor_name=admin_name
        )
        
        return filing
    
    def assign_admin(
        self,
        filing_id: str,
        admin_id: str,
        assigned_by_id: str,
        assigned_by_name: str
    ) -> Filing:
        """Assign admin to filing"""
        filing = self.get_filing_by_id(filing_id)
        
        # Check if admin exists
        admin = self.db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise ResourceNotFoundError("Admin", admin_id)
        
        # Check if already assigned
        existing = self.db.query(AdminFilingAssignment).filter(
            AdminFilingAssignment.admin_id == admin_id,
            AdminFilingAssignment.filing_id == filing_id
        ).first()
        
        if existing:
            raise ResourceConflictError(
                error_code=ErrorCodes.RESOURCE_CONFLICT,
                message="Admin already assigned to this filing"
            )
        
        # Create assignment
        assignment = AdminFilingAssignment(
            admin_id=admin_id,
            filing_id=filing_id
        )
        self.db.add(assignment)
        self.db.commit()
        
        # Add timeline event
        self._add_timeline_event(
            filing_id=filing.id,
            event_type="admin_assigned",
            description=f"Admin {admin.name} assigned to filing",
            actor_type="admin",
            actor_id=assigned_by_id,
            actor_name=assigned_by_name
        )
        
        self.db.refresh(filing)
        return filing
    
    def calculate_paid_amount(self, filing_id: str) -> float:
        """Calculate total paid amount for filing"""
        result = self.db.query(func.sum(Payment.amount))\
            .filter(Payment.filing_id == filing_id)\
            .scalar()
        return result or 0.0
    
    def calculate_payment_status(self, filing: Filing) -> str:
        """Calculate payment status based on paid amount vs total fee"""
        if not filing.total_fee or filing.total_fee <= 0:
            return "pending"
        
        paid_amount = self.calculate_paid_amount(filing.id)
        
        if paid_amount >= filing.total_fee:
            return "paid"
        elif paid_amount > 0:
            return "partial"
        elif filing.status in ["filed", "completed"]:
            return "overdue"
        else:
            return "pending"
    
    def get_filing_timeline(self, filing_id: str) -> List[FilingTimeline]:
        """Get timeline events for filing"""
        return self.db.query(FilingTimeline)\
            .filter(FilingTimeline.filing_id == filing_id)\
            .order_by(FilingTimeline.created_at.desc())\
            .all()
    
    def is_admin_assigned(self, filing_id: str, admin_id: str) -> bool:
        """Check if admin is assigned to filing"""
        assignment = self.db.query(AdminFilingAssignment).filter(
            AdminFilingAssignment.filing_id == filing_id,
            AdminFilingAssignment.admin_id == admin_id
        ).first()
        return assignment is not None
    
    def _add_timeline_event(
        self,
        filing_id: str,
        event_type: str,
        description: str,
        actor_type: str,
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None
    ):
        """Add timeline event"""
        event = FilingTimeline(
            filing_id=filing_id,
            event_type=event_type,
            description=description,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name
        )
        self.db.add(event)
        self.db.commit()
