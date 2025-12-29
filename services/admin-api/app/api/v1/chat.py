"""\
Chat endpoints (admin <-> client)

These endpoints operate on the shared PostgreSQL tables created by client-api:
- chat_messages
- notifications

Auth: admin JWT (admin-api)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
import uuid as uuidlib

from app.core.database import get_db
from app.core.dependencies import get_current_admin

router = APIRouter(prefix="/chat", tags=["Chat"])


class AdminChatMessage(BaseModel):
    id: str
    user_id: str
    sender_role: str
    message: str
    created_at: Optional[str] = None
    read_by_client: bool
    read_by_admin: bool


class AdminChatListResponse(BaseModel):
    messages: List[AdminChatMessage]
    total: int


class AdminChatSendRequest(BaseModel):
    client_id: UUID
    message: str


@router.get("/messages", response_model=AdminChatListResponse)
async def get_chat_messages(
    client_id: UUID = Query(...),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    try:
        sql = (
            "SELECT id::text, user_id::text, sender_role, message, created_at, read_by_client, read_by_admin "
            "FROM chat_messages "
            "WHERE user_id = :uid "
            "ORDER BY created_at DESC "
            "LIMIT :limit OFFSET :offset"
        )
        res = await db.execute(text(sql), {"uid": str(client_id), "limit": limit, "offset": offset})
        rows = res.fetchall()
        # reverse to ascending for UI
        rows = list(rows)[::-1]
        msgs = [
            AdminChatMessage(
                id=r[0],
                user_id=r[1],
                sender_role=r[2],
                message=r[3],
                created_at=r[4].isoformat() if r[4] else None,
                read_by_client=bool(r[5]),
                read_by_admin=bool(r[6]),
            )
            for r in rows
        ]
        return AdminChatListResponse(messages=msgs, total=len(msgs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages", response_model=AdminChatMessage, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    req: AdminChatSendRequest,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    try:
        msg_id = str(uuidlib.uuid4())
        await db.execute(
            text(
                """
                INSERT INTO chat_messages (id, user_id, sender_role, message, created_at, read_by_client, read_by_admin)
                VALUES (:id, :uid, 'admin', :msg, NOW(), false, true)
                """
            ),
            {"id": msg_id, "uid": str(req.client_id), "msg": req.message},
        )

        # Also insert a notification for the client
        await db.execute(
            text(
                """
                INSERT INTO notifications (id, user_id, type, title, message, payload, is_read, created_by, created_at)
                VALUES (:id, :uid, 'message', 'New message from admin', :msg, :payload::jsonb, false, 'admin', NOW())
                """
            ),
            {
                "id": str(uuidlib.uuid4()),
                "uid": str(req.client_id),
                "msg": req.message,
                "payload": '{"source":"admin","kind":"chat"}',
            },
        )

        await db.commit()

        # Fetch inserted message
        row = (await db.execute(
            text(
                "SELECT id::text, user_id::text, sender_role, message, created_at, read_by_client, read_by_admin "
                "FROM chat_messages WHERE id = :id"
            ),
            {"id": msg_id},
        )).fetchone()

        return AdminChatMessage(
            id=row[0],
            user_id=row[1],
            sender_role=row[2],
            message=row[3],
            created_at=row[4].isoformat() if row[4] else None,
            read_by_client=bool(row[5]),
            read_by_admin=bool(row[6]),
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
