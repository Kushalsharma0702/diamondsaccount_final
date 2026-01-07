"""
Health check endpoint
GET /api/v1/health
"""

import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import get_db
from backend.app.schemas.api_v2 import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    
    # Test database connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "2.0.0",
        "timestamp": datetime.utcnow()
    }
