"""Admin endpoints: list clients and delete client (dummy auth for now)."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Client, Admin, AdminClientMap
from backend.app.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminClientResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    filingYear: int
    status: str
    paymentStatus: str
    assignedAdminId: Optional[str] = None
    assignedAdminName: Optional[str] = None
    totalAmount: float
    paidAmount: float


@router.get("/clients", response_model=List[AdminClientResponse])
def get_clients(
    status: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Return all clients (no RBAC yet, dummy for now)."""
    q = db.query(Client)
    if status:
        q = q.filter(Client.status == status)
    if year:
        q = q.filter(Client.filing_year == year)

    clients = q.order_by(Client.created_at.desc()).all()

    # Fetch admin names
    admin_ids = {c.admin_assignments[0].admin_id for c in clients if c.admin_assignments}
    admins = (
        db.query(Admin).filter(Admin.id.in_(admin_ids)).all() if admin_ids else []
    )
    admin_map = {a.id: a.name for a in admins}

    resp: List[AdminClientResponse] = []
    for c in clients:
        assigned_admin_id = None
        assigned_admin_name = None
        if c.admin_assignments:
            assigned_admin_id = str(c.admin_assignments[0].admin_id)
            assigned_admin_name = admin_map.get(c.admin_assignments[0].admin_id)
        resp.append(
            AdminClientResponse(
                id=str(c.id),
                name=c.name,
                email=c.email,
                phone=c.phone,
                filingYear=c.filing_year,
                status=c.status,
                paymentStatus=c.payment_status,
                assignedAdminId=assigned_admin_id,
                assignedAdminName=assigned_admin_name,
                totalAmount=c.total_amount,
                paidAmount=c.paid_amount,
            )
        )
    return resp
