"""Chat endpoints for client ↔ admin messaging."""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import Client, ChatMessage, User
from backend.app.database import get_db

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageRequest(BaseModel):
    client_id: str  # Accept as string, convert to UUID in handler
    message: str
    sender_role: Optional[str] = "client"  # For testing: "client" or "admin"


class ChatMessageResponse(BaseModel):
    id: str
    sender_role: str
    message: str
    created_at: str
    read_by_client: bool
    read_by_admin: bool


class ChatListResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total: int


@router.post("/send", status_code=status.HTTP_201_CREATED, response_model=ChatMessageResponse)
def send_message(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """Send a chat message (from client or admin)."""
    # Verify client exists
    client = db.query(Client).filter(Client.id == request.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # For testing: accept sender_role in request, default to "client"
    # In production, extract from JWT token
    sender_role = request.sender_role or "client"

    # Create chat message using ORM
    chat_message = ChatMessage(
        user_id=client.user_id,
        sender_role=sender_role,
        message=request.message,
        read_by_client=sender_role == "client",
        read_by_admin=sender_role == "admin",
    )
    
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)

    return ChatMessageResponse(
        id=str(chat_message.id),
        sender_role=chat_message.sender_role,
        message=chat_message.message,
        created_at=chat_message.created_at.isoformat(),
        read_by_client=chat_message.read_by_client,
        read_by_admin=chat_message.read_by_admin,
    )


@router.get("/{client_id}", response_model=ChatListResponse)
def get_messages(client_id: str, db: Session = Depends(get_db)):
    """Get all chat messages for a client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Get messages using ORM
    messages_query = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == client.user_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages_list = messages_query.all()

    messages = [
        ChatMessageResponse(
            id=str(msg.id),
            sender_role=msg.sender_role,
            message=msg.message,
            created_at=msg.created_at.isoformat(),
            read_by_client=msg.read_by_client,
            read_by_admin=msg.read_by_admin,
        )
        for msg in messages_list
    ]

    return ChatListResponse(messages=messages, total=len(messages))


@router.put("/{client_id}/mark-read")
def mark_messages_as_read(
    client_id: str,
    role: str,  # "client" or "admin"
    db: Session = Depends(get_db),
):
    """Mark all messages as read for a specific role."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if role not in ["client", "admin"]:
        raise HTTPException(status_code=400, detail="role must be 'client' or 'admin'")

    # Update read status
    if role == "client":
        db.query(ChatMessage).filter(
            ChatMessage.user_id == client.user_id,
            ChatMessage.read_by_client == False
        ).update({"read_by_client": True})
    else:
        db.query(ChatMessage).filter(
            ChatMessage.user_id == client.user_id,
            ChatMessage.read_by_admin == False
        ).update({"read_by_admin": True})

    db.commit()
    return {"message": f"Messages marked as read for {role}"}


@router.get("/{client_id}/unread-count")
def get_unread_count(
    client_id: str,
    role: str,  # "client" or "admin"
    db: Session = Depends(get_db),
):
    """Get count of unread messages for a specific role."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if role not in ["client", "admin"]:
        raise HTTPException(status_code=400, detail="role must be 'client' or 'admin'")

    if role == "client":
        count = db.query(ChatMessage).filter(
            ChatMessage.user_id == client.user_id,
            ChatMessage.read_by_client == False,
            ChatMessage.sender_role == "admin"
        ).count()
    else:
        count = db.query(ChatMessage).filter(
            ChatMessage.user_id == client.user_id,
            ChatMessage.read_by_admin == False,
            ChatMessage.sender_role == "client"
        ).count()

    return {"unread_count": count}
