"""Complete admin endpoints for dashboard integration."""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from database import (
    Client, Admin, AdminClientMap, ChatMessage, User
)
from database.schemas_v2 import Filing, T1Form, Document, Payment, Notification, T1Answer
from backend.app.database import get_db
from backend.app.routes.filing_status import STATUS_DISPLAY_NAMES

router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ClientResponse(BaseModel):
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
    createdAt: str
    updatedAt: str


class ClientDetailResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    filingYear: int
    status: str
    paymentStatus: str
    totalAmount: float
    paidAmount: float
    assignedAdminId: Optional[str] = None
    assignedAdminName: Optional[str] = None
    createdAt: str
    updatedAt: str
    t1Return: Optional[Dict[str, Any]] = None
    documents: List[Dict[str, Any]] = []
    payments: List[Dict[str, Any]] = []
    chatMessages: List[Dict[str, Any]] = []


class ClientUpdateRequest(BaseModel):
    status: Optional[str] = None
    paymentStatus: Optional[str] = None
    assignedAdminId: Optional[str] = None
    totalAmount: Optional[float] = None
    paidAmount: Optional[float] = None


class DocumentResponse(BaseModel):
    id: str
    clientId: str
    name: str
    originalFilename: str
    fileType: str
    fileSize: int
    status: str
    sectionName: Optional[str]
    documentType: str
    uploadedAt: Optional[str]
    createdAt: str


class PaymentResponse(BaseModel):
    id: str
    clientId: str
    amount: float
    method: str
    status: str
    note: Optional[str]
    createdAt: str


class AnalyticsResponse(BaseModel):
    totalClients: int
    totalAdmins: int
    pendingDocuments: int
    pendingPayments: int
    completedFilings: int
    totalRevenue: float
    monthlyRevenue: List[Dict[str, Any]]
    clientsByStatus: List[Dict[str, Any]]
    adminWorkload: List[Dict[str, Any]]


# ============================================================================
# CLIENT ENDPOINTS
# ============================================================================

@router.get("/clients", response_model=List[ClientResponse])
def get_clients(
    status: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get all clients with filtering."""
    query = db.query(Client)
    
    if status:
        query = query.filter(Client.status == status)
    if year:
        query = query.filter(Client.filing_year == year)
    if search:
        search_filter = or_(
            Client.name.ilike(f"%{search}%"),
            Client.email.ilike(f"%{search}%"),
            Client.phone.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    clients = query.order_by(Client.created_at.desc()).all()
    
    # Fetch admin names using assigned_admin_id directly
    admin_ids = {c.assigned_admin_id for c in clients if c.assigned_admin_id}
    admins = db.query(Admin).filter(Admin.id.in_(admin_ids)).all() if admin_ids else []
    admin_map = {str(a.id): a.name for a in admins}
    
    result = []
    for c in clients:
        assigned_admin_id = None
        assigned_admin_name = None
        if c.assigned_admin_id:
            assigned_admin_id = str(c.assigned_admin_id)
            assigned_admin_name = admin_map.get(assigned_admin_id)
        
        result.append(ClientResponse(
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
            createdAt=c.created_at.isoformat(),
            updatedAt=c.updated_at.isoformat(),
        ))
    
    return result


@router.get("/clients/{client_id}", response_model=ClientDetailResponse)
def get_client_detail(client_id: str, db: Session = Depends(get_db)):
    """Get detailed client information."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get assigned admin using assigned_admin_id directly
    assigned_admin_id = None
    assigned_admin_name = None
    if client.assigned_admin_id:
        admin = db.query(Admin).filter(Admin.id == client.assigned_admin_id).first()
        if admin:
            assigned_admin_id = str(admin.id)
            assigned_admin_name = admin.name
    
    # Get T1 form via user email → filing → t1_form
    t1_data = None
    user = db.query(User).filter(User.email == client.email).first()
    filing = None
    
    if user:
        # Get most recent filing for this user
        filing = db.query(Filing).filter(
            Filing.user_id == user.id
        ).order_by(Filing.filing_year.desc()).first()
        
        if filing:
            # Get T1 form for this filing
            t1_form = db.query(T1Form).filter(T1Form.filing_id == filing.id).first()
            if t1_form:
                # Get T1 answers for this form
                t1_answers = db.query(T1Answer).filter(T1Answer.t1_form_id == t1_form.id).all()
                
                # Convert answers to the format expected by frontend
                answers_list = []
                for answer in t1_answers:
                    # Determine which value field to use
                    value = None
                    if answer.value_boolean is not None:
                        value = answer.value_boolean
                    elif answer.value_text is not None:
                        value = answer.value_text
                    elif answer.value_numeric is not None:
                        value = answer.value_numeric
                    elif answer.value_date is not None:
                        value = answer.value_date.isoformat()
                    elif answer.value_array is not None:
                        value = answer.value_array
                    
                    answers_list.append({
                        "field_key": answer.field_key,
                        "value": value
                    })
                
                t1_data = {
                    "id": str(t1_form.id),
                    "filingYear": filing.filing_year,
                    "status": t1_form.status,
                    "statusDisplay": STATUS_DISPLAY_NAMES.get(t1_form.status, t1_form.status),
                    "paymentStatus": "pending",  # Not stored in t1_form
                    "submittedAt": t1_form.submitted_at.isoformat() if t1_form.submitted_at else None,
                    "updatedAt": t1_form.updated_at.isoformat(),
                    "completionPercentage": t1_form.completion_percentage,
                    "isLocked": t1_form.is_locked,
                    "answers": answers_list,
                    "formData": t1_form.form_data if hasattr(t1_form, 'form_data') else {}
                }
    
    # Get documents via filing_id
    documents_data = []
    if user and filing:
        documents = db.query(Document).filter(Document.filing_id == filing.id).all()
        documents_data = [
            {
                "id": str(d.id),
                "name": d.name,
                "originalFilename": d.original_filename,
                "fileType": d.file_type,
                "fileSize": d.file_size,
                "status": d.status,
                "sectionName": d.section_name,
                "documentType": d.document_type,
                "uploadedAt": d.uploaded_at.isoformat() if d.uploaded_at else None,
                "createdAt": d.created_at.isoformat(),
            }
            for d in documents
        ]
    
    # Get payments via filing_id
    payments_data = []
    if user and filing:
        payments = db.query(Payment).filter(Payment.filing_id == filing.id).all()
        payments_data = [
            {
                "id": str(p.id),
                "amount": p.amount,
                "method": p.method,
                "status": "paid",  # Payment status not stored in table
                "note": p.note,
                "createdAt": p.created_at.isoformat(),
            }
            for p in payments
        ]
    
    # Get chat messages via user_id (DISABLED - chat_messages table doesn't exist)
    # TODO: Replace with email_messages or remove if not needed
    chat_data = []
    # if user:
    #     chat_messages = db.query(ChatMessage).filter(
    #         ChatMessage.user_id == user.id
    #     ).order_by(ChatMessage.created_at.desc()).limit(50).all()
    #     
    #     chat_data = [
    #         {
    #             "id": str(m.id),
    #             "senderRole": m.sender_role,
    #             "message": m.message,
    #             "createdAt": m.created_at.isoformat(),
    #             "readByClient": m.read_by_client,
    #             "readByAdmin": m.read_by_admin,
    #         }
    #         for m in chat_messages
    #     ]
    
    return ClientDetailResponse(
        id=str(client.id),
        name=client.name,
        email=client.email,
        phone=client.phone,
        filingYear=client.filing_year,
        status=client.status,
        paymentStatus=client.payment_status,
        totalAmount=client.total_amount,
        paidAmount=client.paid_amount,
        assignedAdminId=assigned_admin_id,
        assignedAdminName=assigned_admin_name,
        createdAt=client.created_at.isoformat(),
        updatedAt=client.updated_at.isoformat(),
        t1Return=t1_data,
        documents=documents_data,
        payments=payments_data,
        chatMessages=chat_data,
    )


@router.patch("/clients/{client_id}")
def update_client(
    client_id: str,
    request: ClientUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update client information."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update fields
    if request.status is not None:
        client.status = request.status
    if request.paymentStatus is not None:
        client.payment_status = request.paymentStatus
    if request.totalAmount is not None:
        client.total_amount = request.totalAmount
    if request.paidAmount is not None:
        client.paid_amount = request.paidAmount
    
    # Handle admin assignment
    if request.assignedAdminId is not None:
        # Remove existing assignments
        db.query(AdminClientMap).filter(
            AdminClientMap.client_id == client.id
        ).delete()
        
        # Add new assignment
        if request.assignedAdminId:
            assignment = AdminClientMap(
                admin_id=request.assignedAdminId,
                client_id=client.id
            )
            db.add(assignment)
    
    client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(client)
    
    return {
        "id": str(client.id),
        "message": "Client updated successfully",
    }


@router.delete("/clients/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db)):
    """Delete a client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    
    return {"message": "Client deleted successfully"}


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@router.get("/documents", response_model=List[DocumentResponse])
def get_documents(
    client_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get documents with filtering."""
    query = db.query(Document)
    
    if client_id:
        query = query.filter(Document.client_id == client_id)
    if status:
        query = query.filter(Document.status == status)
    
    documents = query.order_by(Document.created_at.desc()).all()
    
    return [
        DocumentResponse(
            id=str(d.id),
            clientId=str(d.client_id),
            name=d.name,
            originalFilename=d.original_filename,
            fileType=d.file_type,
            fileSize=d.file_size,
            status=d.status,
            sectionName=d.section_name,
            documentType=d.document_type,
            uploadedAt=d.uploaded_at.isoformat() if d.uploaded_at else None,
            createdAt=d.created_at.isoformat(),
        )
        for d in documents
    ]


@router.patch("/documents/{document_id}")
def update_document(
    document_id: str,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Update document status."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if status is not None:
        document.status = status
    if notes is not None:
        document.notes = notes
    
    document.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Document updated successfully"}


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@router.get("/payments", response_model=List[PaymentResponse])
def get_payments(
    client_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get payments."""
    query = db.query(Payment)
    
    if client_id:
        query = query.filter(Payment.client_id == client_id)
    
    payments = query.order_by(Payment.created_at.desc()).all()
    
    return [
        PaymentResponse(
            id=str(p.id),
            clientId=str(p.client_id),
            amount=p.amount,
            method=p.method,
            status=p.status,
            note=p.note,
            createdAt=p.created_at.isoformat(),
        )
        for p in payments
    ]


@router.post("/payments")
def create_payment(
    client_id: str,
    amount: float,
    method: str,
    note: Optional[str] = None,
    admin_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Create a payment record."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    payment = Payment(
        client_id=client.id,
        created_by_id=admin_id or client.admin_assignments[0].admin_id if client.admin_assignments else None,
        amount=amount,
        method=method,
        note=note,
        status="received",
        is_request=False,
    )
    
    db.add(payment)
    
    # Update client paid amount
    client.paid_amount = (client.paid_amount or 0) + amount
    if client.paid_amount >= client.total_amount:
        client.payment_status = "paid"
    
    db.commit()
    db.refresh(payment)
    
    return {
        "id": str(payment.id),
        "message": "Payment created successfully",
    }


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    """Get analytics data."""
    # Total clients
    total_clients = db.query(Client).count()
    
    # Total admins
    total_admins = db.query(Admin).filter(Admin.is_active == True).count()
    
    # Pending documents
    pending_documents = db.query(Document).filter(
        Document.status.in_(["pending", "missing"])
    ).count()
    
    # Pending payments
    pending_payments = db.query(Client).filter(
        Client.payment_status.in_(["pending", "partial"])
    ).count()
    
    # Completed filings
    completed_filings = db.query(Client).filter(
        Client.status.in_(["filed", "completed"])
    ).count()
    
    # Total revenue
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "received",
        Payment.is_request == False
    ).scalar() or 0.0
    
    # Monthly revenue (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_payments = db.query(
        func.date_trunc('month', Payment.created_at).label('month'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        Payment.created_at >= six_months_ago,
        Payment.status == "received",
        Payment.is_request == False
    ).group_by('month').all()
    
    monthly_revenue = [
        {
            "month": row.month.strftime("%b"),
            "revenue": float(row.revenue or 0)
        }
        for row in monthly_payments
    ]
    
    # Clients by status
    status_counts = db.query(
        Client.status,
        func.count(Client.id).label('count')
    ).group_by(Client.status).all()
    
    clients_by_status = [
        {
            "status": STATUS_DISPLAY_NAMES.get(status, status),
            "count": count
        }
        for status, count in status_counts
    ]
    
    # Admin workload
    admin_workload = db.query(
        Admin.name,
        func.count(AdminClientMap.client_id).label('clients')
    ).join(
        AdminClientMap, Admin.id == AdminClientMap.admin_id
    ).group_by(Admin.id, Admin.name).all()
    
    admin_workload_data = [
        {
            "name": name,
            "clients": clients
        }
        for name, clients in admin_workload
    ]
    
    return AnalyticsResponse(
        totalClients=total_clients,
        totalAdmins=total_admins,
        pendingDocuments=pending_documents,
        pendingPayments=pending_payments,
        completedFilings=completed_filings,
        totalRevenue=float(total_revenue),
        monthlyRevenue=monthly_revenue,
        clientsByStatus=clients_by_status,
        adminWorkload=admin_workload_data,
    )


# ============================================================================
# ADMIN USER ENDPOINTS
# ============================================================================

@router.get("/admin-users", response_model=List[Dict[str, Any]])
def get_admin_users(db: Session = Depends(get_db)):
    """Get all admin users."""
    admins = db.query(Admin).order_by(Admin.created_at.desc()).all()
    
    return [
        {
            "id": str(a.id),
            "email": a.email,
            "name": a.name,
            "role": a.role,
            "permissions": a.permissions or [],
            "isActive": a.is_active,
            "createdAt": a.created_at.isoformat(),
            "lastLoginAt": a.last_login_at.isoformat() if a.last_login_at else None,
        }
        for a in admins
    ]

