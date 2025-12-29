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
        base_dir = os.path.dirname(__file__)
        admin_backend_paths = [
            os.path.join(base_dir, '..', '..', 'admin-dashboard', 'backend'),
            os.path.join(base_dir, '..', '..', 'tax-hub-dashboard', 'backend'),
            os.path.join(base_dir, '..', '..', '..', 'admin-dashboard', 'backend'),
        ]
        
        admin_path = None
        for path in admin_backend_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, 'app')):
                admin_path = abs_path
                break
        
        if not admin_path:
            logger.warning("Admin backend path not found for document sync")
            return None
        
        if admin_path not in sys.path:
            sys.path.insert(0, admin_path)
        
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
                name=filename,  # Document model uses 'name' field
                type=doc_type,  # Document model uses 'type' field
                status="complete",  # File is already uploaded
                uploaded_at=datetime.utcnow(),
                notes=f"Uploaded from client app. File ID: {file_id}, Storage key: {s3_key}"
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


async def _get_or_create_client_by_email(
    email: str,
    db_session=None,
    first_name: str = None,
    last_name: str = None,
    user_id: Optional[str] = None,
) -> Optional[str]:
    """
    Get client ID from admin backend by email, or create if doesn't exist
    Uses direct database access since both backends use same database
    """
    try:
        # Use direct database access (both use same taxease_db)
        # Try both possible paths for admin backend
        base_dir = os.path.dirname(__file__)
        admin_backend_paths = [
            os.path.join(base_dir, '..', '..', 'admin-dashboard', 'backend'),
            os.path.join(base_dir, '..', '..', 'tax-hub-dashboard', 'backend'),
            os.path.join(base_dir, '..', '..', '..', 'admin-dashboard', 'backend'),
        ]
        
        admin_path = None
        for path in admin_backend_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, 'app')):
                admin_path = abs_path
                break
        
        if not admin_path:
            # Fallback: Use direct SQL since both backends use same database
            logger.warning("Admin backend path not found, using direct SQL")
            return await _create_client_direct_sql(email, first_name, last_name, user_id=user_id)
        
        if admin_path not in sys.path:
            sys.path.insert(0, admin_path)
        
        from app.core.database import AsyncSessionLocal as AdminSession
        from app.models.client import Client as AdminClient
        from sqlalchemy import select
        from datetime import datetime
        
        async with AdminSession() as admin_db:
            # Check if client exists for current year
            current_year = datetime.now().year
            result = await admin_db.execute(
                select(AdminClient).where(
                    AdminClient.email == email.lower(),
                    AdminClient.filing_year == current_year
                )
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
                filing_year=current_year,
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
        logger.error(f"Error getting/creating client via admin backend: {e}", exc_info=True)
        # Fallback to direct SQL
        logger.info("Falling back to direct SQL for client creation")
        try:
            return await _create_client_direct_sql(email, first_name, last_name, user_id=user_id)
        except Exception as sql_error:
            logger.error(f"Direct SQL also failed: {sql_error}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
            return None


async def _create_client_direct_sql(email: str, first_name: str = None, last_name: str = None, user_id: Optional[str] = None) -> Optional[str]:
    """Fallback: Create client directly using SQL"""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        from datetime import datetime
        
        database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db')
        engine = create_async_engine(database_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            current_year = datetime.now().year
            
            # Check if client exists
            result = await session.execute(
                text('''
                    SELECT id FROM clients
                    WHERE LOWER(email) = LOWER(:email) AND filing_year = :year
                '''),
                {'email': email, 'year': current_year}
            )
            existing = result.fetchone()
            
            if existing:
                logger.info(f"Client already exists (SQL): {email} (ID: {existing[0]})")
                client_id = str(existing[0])
                await engine.dispose()
                return client_id
            
            # Create client
            name = f"{first_name or ''} {last_name or ''}".strip() if first_name or last_name else None
            if not name:
                name = email.split("@")[0].replace(".", " ").title()
            
            # IMPORTANT: Keep admin client.id aligned with client-api users.id when available.
            # This ensures admin dashboard filters (client_id) match files.user_id and forms.user_id.
            client_id = str(user_id) if user_id else str(uuid4())
            await session.execute(
                text('''
                    INSERT INTO clients (
                        id, email, name, filing_year, status, payment_status,
                        total_amount, paid_amount, created_at, updated_at
                    )
                    VALUES (
                        :id, :email, :name, :year, :status, :payment_status,
                        :total_amount, :paid_amount, :created_at, :updated_at
                    )
                '''),
                {
                    'id': client_id,
                    'email': email.lower(),
                    'name': name,
                    'year': current_year,
                    'status': 'documents_pending',
                    'payment_status': 'pending',
                    'total_amount': 0.0,
                    'paid_amount': 0.0,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            )
            await session.commit()
            
            logger.info(f"✅ Created client via direct SQL: {email} (ID: {client_id})")
            await engine.dispose()
            return client_id
            
    except Exception as e:
        logger.error(f"Error creating client via direct SQL: {e}", exc_info=True)
        return None


async def sync_t1_form_to_admin(
    user_email: str,
    first_name: str = None,
    last_name: str = None,
    form_id: str = None,
    tax_year: int = None,
    status: str = None
) -> Optional[str]:
    """
    Sync T1 form creation/update to admin dashboard
    Ensures client exists and updates client status based on form status
    """
    try:
        # Get or create client
        client_id = await _get_or_create_client_by_email(
            user_email,
            db_session=None,
            first_name=first_name,
            last_name=last_name
        )
        if not client_id:
            logger.warning(f"Could not sync T1 form - client not found for: {user_email}")
            return None
        
        # If form status is submitted, update client status
        if status == "submitted":
            try:
                admin_backend_paths = [
                    os.path.join(os.path.dirname(__file__), '..', '..', 'admin-dashboard', 'backend'),
                    os.path.join(os.path.dirname(__file__), '..', '..', 'tax-hub-dashboard', 'backend'),
                ]
                
                admin_path = None
                for path in admin_backend_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, 'app')):
                        admin_path = abs_path
                        break
                
                if admin_path and admin_path not in sys.path:
                    sys.path.insert(0, admin_path)
                
                if admin_path:
                    from app.core.database import AsyncSessionLocal as AdminSession
                    from app.models.client import Client as AdminClient
                    from sqlalchemy import select, update
                    
                    async with AdminSession() as admin_db:
                        # Update client status to under_review when form is submitted
                        await admin_db.execute(
                            update(AdminClient)
                            .where(AdminClient.id == UUID(client_id))
                            .values(
                                status="under_review",
                                updated_at=datetime.utcnow()
                            )
                        )
                        await admin_db.commit()
                        logger.info(f"✅ Updated client {client_id} status to 'under_review' after form submission")
                        
            except Exception as e:
                logger.warning(f"Failed to update client status: {e}")
        
        return client_id
    except Exception as e:
        logger.error(f"Error syncing T1 form to admin: {e}", exc_info=True)
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
