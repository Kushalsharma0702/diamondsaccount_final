"""\
Notifications endpoints (admin-side view/send)

Operates on shared client-api table: notifications
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

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class AdminNotification(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    is_read: bool
    created_by: str
    created_at: Optional[str] = None


class AdminNotificationListResponse(BaseModel):
    notifications: List[AdminNotification]
    total: int


class AdminSendNotificationRequest(BaseModel):
    client_id: UUID
    type: str = "general"
    title: str
    message: str


@router.get("", response_model=AdminNotificationListResponse)
async def list_notifications(
    client_id: UUID = Query(...),
    unread_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    try:
        where = "WHERE user_id = :uid"
        if unread_only:
            where += " AND is_read = false"
        sql = (
            "SELECT id::text, user_id::text, type, title, message, is_read, created_by, created_at "
            f"FROM notifications {where} "
            "ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        )
        res = await db.execute(text(sql), {"uid": str(client_id), "limit": limit, "offset": offset})
        rows = res.fetchall()
        notifs = [
            AdminNotification(
                id=r[0],
                user_id=r[1],
                type=r[2],
                title=r[3],
                message=r[4],
                is_read=bool(r[5]),
                created_by=r[6],
                created_at=r[7].isoformat() if r[7] else None,
            )
            for r in rows
        ]
        return AdminNotificationListResponse(notifications=notifs, total=len(notifs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=AdminNotification, status_code=status.HTTP_201_CREATED)
async def send_notification(
    req: AdminSendNotificationRequest,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    try:
        nid = str(uuidlib.uuid4())
        await db.execute(
            text(
                """
                INSERT INTO notifications (id, user_id, type, title, message, payload, is_read, created_by, created_at)
                VALUES (:id, :uid, :type, :title, :message, :payload::jsonb, false, 'admin', NOW())
                """
            ),
            {
                "id": nid,
                "uid": str(req.client_id),
                "type": req.type,
                "title": req.title,
                "message": req.message,
                "payload": '{"source":"admin"}',
            },
        )
        await db.commit()
        row = (await db.execute(
            text(
                "SELECT id::text, user_id::text, type, title, message, is_read, created_by, created_at "
                "FROM notifications WHERE id = :id"
            ),
            {"id": nid},
        )).fetchone()
        return AdminNotification(
            id=row[0],
            user_id=row[1],
            type=row[2],
            title=row[3],
            message=row[4],
            is_read=bool(row[5]),
            created_by=row[6],
            created_at=row[7].isoformat() if row[7] else None,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
