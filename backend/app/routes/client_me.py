"""Client endpoints for authenticated clients to get their own information."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Client, User
from backend.app.database import get_db
from backend.app.auth.jwt import get_current_user

router = APIRouter(prefix="/client", tags=["client"])


class ClientInfoResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str | None
    filing_year: int
    status: str
    payment_status: str


@router.get("/me", response_model=ClientInfoResponse)
def get_my_client_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current authenticated user's client record. Auto-creates if missing."""
    from datetime import datetime
    
    # Find client record for this user
    client = db.query(Client).filter(Client.user_id == current_user.id).first()
    
    # Auto-create client record if it doesn't exist
    if not client:
        year = datetime.utcnow().year
        name = f"{current_user.first_name} {current_user.last_name}".strip()
        if not name:
            name = current_user.email.split('@')[0]  # Fallback to email username
        
        client = Client(
            user_id=current_user.id,
            name=name,
            email=current_user.email,
            phone=current_user.phone,
            filing_year=year,
            status="documents_pending",
            payment_status="pending",
            total_amount=0.0,
            paid_amount=0.0,
        )
        db.add(client)
        db.commit()
        db.refresh(client)
    
    return ClientInfoResponse(
        id=str(client.id),
        name=client.name,
        email=client.email,
        phone=client.phone,
        filing_year=client.filing_year,
        status=client.status,
        payment_status=client.payment_status,
    )

