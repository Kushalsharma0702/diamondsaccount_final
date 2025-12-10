"""
Sync service to bridge client-side File uploads with admin-side Document records
This allows admin dashboard to see files uploaded by clients
Uses direct database access since both backends use the same database (taxease_db)
"""
import os
import sys
import logging
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

logger = logging.getLogger(__name__)

# Admin backend base URL (fallback if direct DB access fails)
ADMIN_API_BASE = os.getenv('ADMIN_API_BASE_URL', 'http://localhost:8002/api/v1')


async def sync_file_to_admin_document(
    file_id: str,
    user_email: str,
    filename: str,
    file_type: str,
    file_size: int,
    s3_key: str,
    db_session=None
) -> Optional[str]:
    """
    Sync a client-uploaded File to admin-side Document record
    Uses direct database access since both backends use the same database
    
    Args:
        file_id: Client-side File ID
        user_email: User's email (used to find/create Client)
        filename: Original filename
        file_type: MIME type
        file_size: File size in bytes
        s3_key: Storage key (local path)
        db_session: Database session (optional, not used - creates new admin session)
    
    Returns:
        Document ID if successful, None otherwise
    """
    try:
        # Map file extension to document type
        doc_type = _map_file_type_to_document_type(filename, file_type)
        
        # Get or create client by email (gets client_id from admin backend)
        client_id = await _get_or_create_client_by_email(user_email, db_session=None)
        if not client_id:
            logger.warning(f"Could not find/create client for email: {user_email}")
            return None
        
        # Use direct database access to create document in admin backend's Document table
        # Since both backends use the same database (taxease_db), we can access admin models directly
        admin_backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'tax-hub-dashboard', 'backend')
        if admin_backend_path not in sys.path:
            sys.path.insert(0, admin_backend_path)
        
        from app.core.database import AsyncSessionLocal as AdminSession
        from app.models.document import Document as AdminDocument
        from app.models.client import Client as AdminClient
        from sqlalchemy import select
        
        async with AdminSession() as admin_db:
            # Verify client exists
            result = await admin_db.execute(
                select(AdminClient).where(AdminClient.id == UUID(client_id))
            )
            client = result.scalar_one_or_none()
            
            if not client:
                logger.error(f"Client {client_id} not found in admin database")
                return None
            
            # Create document in admin backend's Document table
            admin_document = AdminDocument(
                id=uuid4(),
                client_id=UUID(client_id),
                name=filename,
                type=doc_type,
                status="complete",  # File is already uploaded
                uploaded_at=datetime.utcnow(),
                notes=f"Uploaded from client app. File ID: {file_id}, Storage key: {s3_key}",
            )
            
            admin_db.add(admin_document)
            await admin_db.commit()
            await admin_db.refresh(admin_document)
            
            logger.info(f"✅ Synced file {file_id} to admin document {admin_document.id} for client {client.name}")
            return str(admin_document.id)
                
    except Exception as e:
        logger.error(f"❌ Error syncing file to admin: {e}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
        return None


async def _get_or_create_client_by_email(email: str, db_session=None, first_name: str = None, last_name: str = None) -> Optional[str]:
    """
    Get client ID from admin backend by email, or create if doesn't exist
    Uses direct database access since both backends use same database
    """
    try:
        # Use direct database access (both use same taxease_db)
        admin_backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'tax-hub-dashboard', 'backend')
        if admin_backend_path not in sys.path:
            sys.path.insert(0, admin_backend_path)
        
        from app.core.database import AsyncSessionLocal as AdminSession
        from app.models.client import Client as AdminClient
        from sqlalchemy import select
        from datetime import datetime
        
        async with AdminSession() as admin_db:
            # Check if client exists
            result = await admin_db.execute(
                select(AdminClient).where(AdminClient.email == email.lower())
            )
            existing_client = result.scalar_one_or_none()
            
            if existing_client:
                logger.info(f"Client already exists: {email} (ID: {existing_client.id})")
                return str(existing_client.id)
            
            # Create new client
            name = f"{first_name or ''} {last_name or ''}".strip() if first_name or last_name else None
            if not name:
                name = email.split("@")[0].replace(".", " ").title()
            
            new_client = AdminClient(
                id=uuid4(),
                name=name,
                email=email.lower(),
                filing_year=datetime.now().year,
                status="documents_pending",
                payment_status="pending",
                total_amount=0.0,
                paid_amount=0.0
            )
            
            admin_db.add(new_client)
            await admin_db.commit()
            await admin_db.refresh(new_client)
            
            logger.info(f"✅ Created client in admin DB: {email} (ID: {new_client.id})")
            return str(new_client.id)
            
    except Exception as e:
        logger.error(f"Error getting/creating client: {e}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
        return None


def _map_file_type_to_document_type(filename: str, mime_type: str) -> str:
    """
    Map file type to admin document type
    """
    filename_lower = filename.lower()
    
    # Income documents
    if any(keyword in filename_lower for keyword in ['t4', 't4a', 'employment', 'income', 'salary', 'wage']):
        return "income"
    
    # Investment documents
    if any(keyword in filename_lower for keyword in ['t5', 't3', 'investment', 'dividend', 'interest']):
        return "investment"
    
    # Deduction documents
    if any(keyword in filename_lower for keyword in ['receipt', 'deduction', 'medical', 'charitable', 'donation']):
        return "deduction"
    
    # Property documents
    if any(keyword in filename_lower for keyword in ['property', 'rental', 't776']):
        return "property"
    
    # Business documents
    if any(keyword in filename_lower for keyword in ['business', 't2125', 'self-employed']):
        return "business"
    
    # Default
    return "other"
