"""RBAC helpers for admin permissions and client/admin access control."""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import Admin, Client, AdminClientMap
from backend.app.database import get_db
from backend.app.auth.jwt import get_current_admin, get_current_user

PERMISSIONS = {
    "ADD_EDIT_PAYMENT": "add_edit_payment",
    "ADD_EDIT_CLIENT": "add_edit_client",
    "REQUEST_DOCUMENTS": "request_documents",
    "ASSIGN_CLIENTS": "assign_clients",
    "VIEW_ANALYTICS": "view_analytics",
    "APPROVE_COST_ESTIMATE": "approve_cost_estimate",
    "UPDATE_WORKFLOW": "update_workflow",
}


def has_permission(admin: Admin, perm: str) -> bool:
    if admin.role == "superadmin":
        return True
    return perm in (admin.permissions or [])


def require_permission(perm: str):
    def dependency(current_admin: Admin = Depends(get_current_admin)) -> Admin:
        if not has_permission(current_admin, perm):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{perm}' required",
            )
        return current_admin

    return dependency


def require_client_access(
    client_id: str,
    db: Session,
    current_admin: Admin,
) -> Client:
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    if current_admin.role != "superadmin":
        assignment = (
            db.query(AdminClientMap)
            .filter(
                AdminClientMap.admin_id == current_admin.id,
                AdminClientMap.client_id == client.id,
            )
            .first()
        )
        if not assignment:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Client not assigned to this admin")
    return client
