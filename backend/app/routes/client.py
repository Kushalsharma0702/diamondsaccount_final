"""Client endpoints: add/delete client records and basic status."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import Client, User
from backend.app.database import get_db

router = APIRouter(prefix="/client", tags=["client"])


class ClientCreateRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    filing_year: Optional[int] = None


class ClientResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    filing_year: int
    status: str
    payment_status: str


@router.post("/add", response_model=ClientResponse)
def add_client(request: ClientCreateRequest, db: Session = Depends(get_db)):
    """Create a client row for an existing user (or create user if needed)."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            password_hash="",  # will be set via /auth/register if needed
            email_verified=False,
            is_active=True,
        )
        db.add(user)
        db.flush()

    year = request.filing_year or datetime.utcnow().year
    name = f"{request.first_name} {request.last_name}".strip()

    client = Client(
        user_id=user.id,
        name=name,
        email=request.email,
        phone=request.phone,
        filing_year=year,
        status="documents_pending",
        payment_status="pending",
        total_amount=0.0,
        paid_amount=0.0,
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    return ClientResponse(
        id=str(client.id),
        name=client.name,
        email=client.email,
        phone=client.phone,
        filing_year=client.filing_year,
        status=client.status,
        payment_status=client.payment_status,
    )


@router.delete("/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db)):
    """Delete a client row (and keep user record for now)."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": "Client deleted"}
