"""
API v1 routes
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .admin_users import router as admin_users_router
from .clients import router as clients_router
from .documents import router as documents_router
from .payments import router as payments_router
from .analytics import router as analytics_router
from .audit_logs import router as audit_logs_router
from .t1_forms import router as t1_forms_router
from .files import router as files_router
from .chat import router as chat_router
from .notifications import router as notifications_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin_users_router, prefix="/admin-users", tags=["Admin Users"])
api_router.include_router(clients_router, prefix="/clients", tags=["Clients"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(t1_forms_router)  # Router already has /t1-forms prefix
api_router.include_router(files_router)  # Router already has /files prefix
api_router.include_router(chat_router)  # Router already has /chat prefix
api_router.include_router(notifications_router)  # Router already has /notifications prefix


