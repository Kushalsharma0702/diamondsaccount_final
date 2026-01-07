"""
Service layer for Document operations
"""

from typing import List, Optional, BinaryIO
import os
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

from database.schemas_v2 import Document, Filing
from backend.app.core.errors import (
    ResourceNotFoundError,
    APIException,
    ErrorCodes
)


class DocumentService:
    """Business logic for Document operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.storage_path = os.getenv("STORAGE_PATH", "/var/taxease/storage")
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
    
    def get_user_documents(
        self,
        user_id: str,
        filing_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Document]:
        """Get all documents for a user"""
        query = self.db.query(Document)\
            .join(Filing)\
            .filter(Filing.user_id == user_id)
        
        if filing_id:
            query = query.filter(Document.filing_id == filing_id)
        if status:
            query = query.filter(Document.status == status)
        
        return query.order_by(Document.uploaded_at.desc()).all()
    
    def get_admin_documents(
        self,
        admin_id: str,
        is_superadmin: bool,
        filing_id: Optional[str] = None
    ) -> List[Document]:
        """Get documents for admin (assigned filings only, unless superadmin)"""
        # TODO: Filter by admin assignment
        query = self.db.query(Document)
        
        if filing_id:
            query = query.filter(Document.filing_id == filing_id)
        
        return query.order_by(Document.uploaded_at.desc()).all()
    
    def get_document_by_id(self, document_id: str) -> Document:
        """Get document by ID"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ResourceNotFoundError("Document", document_id)
        return document
    
    def upload_document(
        self,
        filing_id: str,
        file_content: bytes,
        original_filename: str,
        file_type: str,
        file_size: int,
        document_type: str,
        section_name: Optional[str] = None,
        name: Optional[str] = None
    ) -> Document:
        """Upload and encrypt document"""
        
        # Verify filing exists
        filing = self.db.query(Filing).filter(Filing.id == filing_id).first()
        if not filing:
            raise ResourceNotFoundError("Filing", filing_id)
        
        # Validate file size (10MB max)
        if file_size > 10 * 1024 * 1024:
            raise APIException(
                status_code=413,
                error_code=ErrorCodes.FILE_TOO_LARGE,
                message="File exceeds maximum size of 10MB"
            )
        
        # Validate file type
        allowed_types = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
        if file_type.lower() not in allowed_types:
            raise APIException(
                status_code=422,
                error_code=ErrorCodes.FILE_INVALID_TYPE,
                message=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.storage_path, f"{file_id}.enc")
        
        # Encrypt and save file
        try:
            encrypted_content = self._encrypt_file(file_content)
            with open(file_path, 'wb') as f:
                f.write(encrypted_content)
        except Exception as e:
            raise APIException(
                status_code=500,
                error_code=ErrorCodes.FILE_ENCRYPTION_FAILED,
                message=f"Failed to encrypt file: {str(e)}"
            )
        
        # Create document record
        document = Document(
            filing_id=filing_id,
            name=name or original_filename,
            original_filename=original_filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            encrypted=True,
            document_type=document_type,
            section_name=section_name,
            status="pending"
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def download_document(self, document_id: str) -> tuple[bytes, str, str]:
        """Download and decrypt document"""
        document = self.get_document_by_id(document_id)
        
        if not os.path.exists(document.file_path):
            raise APIException(
                status_code=404,
                error_code=ErrorCodes.RESOURCE_NOT_FOUND,
                message="Document file not found on disk"
            )
        
        try:
            with open(document.file_path, 'rb') as f:
                encrypted_content = f.read()
            
            decrypted_content = self._decrypt_file(encrypted_content)
            
            return decrypted_content, document.original_filename, document.file_type
        except Exception as e:
            raise APIException(
                status_code=500,
                error_code=ErrorCodes.FILE_DECRYPTION_FAILED,
                message=f"Failed to decrypt file: {str(e)}"
            )
    
    def update_document(
        self,
        document_id: str,
        name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Document:
        """Update document metadata"""
        document = self.get_document_by_id(document_id)
        
        if name:
            document.name = name
        if notes is not None:
            document.notes = notes
        
        document.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def update_document_status(
        self,
        document_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Document:
        """Update document status (admin only)"""
        document = self.get_document_by_id(document_id)
        
        document.status = status
        if notes:
            document.notes = notes
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def delete_document(self, document_id: str):
        """Delete document (admin only)"""
        document = self.get_document_by_id(document_id)
        
        # Delete file from disk
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete database record
        self.db.delete(document)
        self.db.commit()
    
    def _encrypt_file(self, content: bytes) -> bytes:
        """Encrypt file content using AES-256"""
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        import os
        
        # Get encryption key from environment (32 bytes for AES-256)
        key_str = os.getenv("ENCRYPTION_KEY") or os.getenv("FILE_ENCRYPTION_KEY")
        if not key_str:
            # Generate exactly 32 bytes default key
            key_str = "12345678901234567890123456789012"  # 32 chars
        key = key_str.encode()[:32]
        if len(key) != 32:
            # Pad to 32 bytes if needed
            key = key.ljust(32, b'0')
        iv = os.urandom(16)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad content to multiple of 16 bytes
        padding_length = 16 - (len(content) % 16)
        padded_content = content + bytes([padding_length]) * padding_length
        
        encrypted = encryptor.update(padded_content) + encryptor.finalize()
        
        # Prepend IV to encrypted content
        return iv + encrypted
    
    def _decrypt_file(self, encrypted_content: bytes) -> bytes:
        """Decrypt file content"""
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        import os
        
        # Get encryption key from environment (32 bytes for AES-256)
        key_str = os.getenv("ENCRYPTION_KEY") or os.getenv("FILE_ENCRYPTION_KEY")
        if not key_str:
            # Generate exactly 32 bytes default key
            key_str = "12345678901234567890123456789012"  # 32 chars
        key = key_str.encode()[:32]
        if len(key) != 32:
            # Pad to 32 bytes if needed
            key = key.ljust(32, b'0')
        
        # Extract IV and encrypted content
        iv = encrypted_content[:16]
        encrypted = encrypted_content[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_content = decryptor.update(encrypted) + decryptor.finalize()
        
        # Remove padding
        padding_length = padded_content[-1]
        content = padded_content[:-padding_length]
        
        return content
