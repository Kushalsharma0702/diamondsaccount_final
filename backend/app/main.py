"""FastAPI monolith entrypoint for Tax-Ease backend (dummy auth, client/admin CRUD)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes import auth as auth_routes
from backend.app.routes import client as client_routes
from backend.app.routes import client_me as client_me_routes
from backend.app.routes import admin as admin_routes
from backend.app.routes import admin_auth as admin_auth_routes
from backend.app.routes import admin_full as admin_full_routes
from backend.app.routes import chat as chat_routes
from backend.app.routes import documents as documents_routes
from backend.app.routes import t1 as t1_routes
from backend.app.routes import filing_status as filing_status_routes

app = FastAPI(title="Tax-Ease Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(client_routes.router, prefix="/api/v1")
app.include_router(client_me_routes.router, prefix="/api/v1")
app.include_router(admin_routes.router, prefix="/api/v1")
app.include_router(admin_auth_routes.router, prefix="/api/v1")
app.include_router(admin_full_routes.router, prefix="/api/v1")
app.include_router(chat_routes.router, prefix="/api/v1")
app.include_router(documents_routes.router, prefix="/api/v1")
app.include_router(t1_routes.router, prefix="/api/v1")
app.include_router(filing_status_routes.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"status": "ok"}
