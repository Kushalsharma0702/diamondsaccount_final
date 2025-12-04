"""
Encrypted File Service for TaxEase
Handles end-to-end encrypted file operations
"""
import json
import hashlib
from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status
from datetime import datetime

from .encryption import SecureDocumentManager, KeyManager
from .models import User, File, EncryptedDocument
from .database import get_db


class EncryptedFileService:
    """
    Service for handling encrypted file operations
    """
    
    def __init__(self):
        self.doc_manager = SecureDocumentManager()
        self.key_manager = KeyManager()
    
    async def setup_user_encryption(self, user: User, password: str, db: AsyncSession) -> bool:
        """
        Set up encryption keys for a user
        """
        try:
            # Generate encryption keys
            keys = self.key_manager.store_user_keys(str(user.id), password)
            
            # Store keys in user record
            user.public_key = keys['public_key']
            user.private_key = keys['private_key']
            user.key_salt = keys['salt']
            user.key_created_at = datetime.utcnow()
            
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to setup encryption keys: {str(e)}"
            )
    
    async def verify_user_encryption_access(self, user: User, password: str) -> bool:
        """
        Verify user can access their encryption keys
        """
        if not all([user.private_key, user.key_salt]):
            return False
            
        return self.key_manager.verify_user_access(
            user.private_key, password, user.key_salt
        )
    
    async def encrypt_and_store_file(self, user: User, file_data: bytes, 
                                   filename: str, file_type: str, 
                                   db: AsyncSession) -> File:
        """
        Encrypt and store a file for a user
        """
        try:
            # Verify user has encryption setup
            if not user.public_key:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User encryption not set up. Please complete account setup."
                )
            
            # Encrypt the document
            encrypted_doc = self.doc_manager.encrypt_and_store_document(
                file_data, filename, user.public_key
            )
            
            # Create file record
            file_record = File(
                user_id=user.id,
                filename=self._generate_secure_filename(),
                original_filename=filename,
                file_type=file_type,
                file_size=len(file_data),
                encrypted_key=encrypted_doc['metadata']['encrypted_key'],
                encryption_metadata=json.dumps(encrypted_doc['metadata']),
                is_encrypted=True,
                upload_status="encrypting"
            )
            
            db.add(file_record)
            await db.flush()  # Get the file ID
            
            # Store encrypted data separately for large files
            if len(encrypted_doc['encrypted_data']) > 1024 * 1024:  # > 1MB
                encrypted_document = EncryptedDocument(
                    file_id=file_record.id,
                    encrypted_data=encrypted_doc['encrypted_data'].encode('utf-8'),
                    checksum=encrypted_doc['metadata']['checksum'],
                    compression_ratio=encrypted_doc['metadata']['compressed_size'] / encrypted_doc['metadata']['original_size']
                )
                db.add(encrypted_document)
                file_record.encrypted_data = None  # Don't store large data in file table
            else:
                # Store small files directly in file table
                file_record.encrypted_data = encrypted_doc['encrypted_data'].encode('utf-8')
            
            file_record.upload_status = "encrypted"
            await db.commit()
            
            return file_record
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to encrypt and store file: {str(e)}"
            )
    
    async def decrypt_and_retrieve_file(self, user: User, file_id: str, 
                                      password: str, db: AsyncSession) -> Tuple[bytes, str, str]:
        """
        Decrypt and retrieve a file for a user
        """
        try:
            # Get file record
            result = await db.execute(
                select(File).where(and_(File.id == file_id, File.user_id == user.id))
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            if not file_record.is_encrypted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File is not encrypted"
                )
            
            # Verify user can access encryption keys
            if not await self.verify_user_encryption_access(user, password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password, could not decrypt key"
                )
            
            # Get encrypted data
            encrypted_data_b64 = None
            if file_record.encrypted_data:
                encrypted_data_b64 = file_record.encrypted_data.decode('utf-8')
            else:
                # Check separate encrypted document table
                result = await db.execute(
                    select(EncryptedDocument).where(EncryptedDocument.file_id == file_record.id)
                )
                encrypted_doc = result.scalar_one_or_none()
                if encrypted_doc:
                    encrypted_data_b64 = encrypted_doc.encrypted_data.decode('utf-8')
            
            if not encrypted_data_b64:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Encrypted file data not found"
                )
            
            # Decrypt the file
            metadata = json.loads(file_record.encryption_metadata)
            
            document_data, original_filename = self.doc_manager.decrypt_and_retrieve_document(
                encrypted_data_b64,
                metadata,
                user.private_key,
                password,
                user.key_salt
            )
            
            return document_data, original_filename, file_record.file_type
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to decrypt file: {str(e)}"
            )
    
    async def list_user_files(self, user: User, db: AsyncSession, 
                            limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List user's files with metadata
        """
        try:
            result = await db.execute(
                select(File)
                .where(File.user_id == user.id)
                .order_by(File.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            files = result.scalars().all()
            
            file_list = []
            for file_record in files:
                file_info = {
                    'id': str(file_record.id),
                    'original_filename': file_record.original_filename,
                    'file_type': file_record.file_type,
                    'file_size': file_record.file_size,
                    'is_encrypted': file_record.is_encrypted,
                    'upload_status': file_record.upload_status,
                    'created_at': file_record.created_at.isoformat()
                }
                
                # Add encryption metadata if available
                if file_record.encryption_metadata:
                    metadata = json.loads(file_record.encryption_metadata)
                    file_info.update({
                        'compressed_size': metadata.get('compressed_size'),
                        'encryption_algorithm': metadata.get('encryption_algorithm'),
                        'compression_ratio': metadata.get('compressed_size', 0) / metadata.get('original_size', 1)
                    })
                
                file_list.append(file_info)
            
            return file_list
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files: {str(e)}"
            )
    
    async def delete_encrypted_file(self, user: User, file_id: str, 
                                  password: str, db: AsyncSession) -> bool:
        """
        Delete an encrypted file after verifying user access
        """
        try:
            # Verify user can access encryption keys
            if not await self.verify_user_encryption_access(user, password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid password for file deletion"
                )
            
            # Get file record
            result = await db.execute(
                select(File).where(and_(File.id == file_id, File.user_id == user.id))
            )
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Delete encrypted document if exists
            await db.execute(
                EncryptedDocument.__table__.delete().where(EncryptedDocument.file_id == file_id)
            )
            
            # Delete file record
            await db.delete(file_record)
            await db.commit()
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    async def rotate_user_keys(self, user: User, old_password: str, 
                             new_password: str, db: AsyncSession) -> bool:
        """
        Rotate user's encryption keys (when password changes)
        This requires re-encrypting all user files
        """
        try:
            # Verify current password
            if not self.verify_user_encryption_access(user, old_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid current password"
                )
            
            # Generate new keys
            new_keys = self.key_manager.rotate_user_keys(
                str(user.id), old_password, new_password,
                user.private_key, user.key_salt
            )
            
            # Get all user's encrypted files
            result = await db.execute(
                select(File).where(and_(File.user_id == user.id, File.is_encrypted == True))
            )
            files = result.scalars().all()
            
            # Re-encrypt all files with new keys
            for file_record in files:
                # Decrypt with old keys
                encrypted_data_b64 = None
                if file_record.encrypted_data:
                    encrypted_data_b64 = file_record.encrypted_data.decode('utf-8')
                else:
                    result = await db.execute(
                        select(EncryptedDocument).where(EncryptedDocument.file_id == file_record.id)
                    )
                    encrypted_doc = result.scalar_one()
                    encrypted_data_b64 = encrypted_doc.encrypted_data.decode('utf-8')
                
                metadata = json.loads(file_record.encryption_metadata)
                
                # Decrypt with old keys
                document_data, _ = self.doc_manager.decrypt_and_retrieve_document(
                    encrypted_data_b64, metadata,
                    user.private_key, old_password, user.key_salt
                )
                
                # Re-encrypt with new keys
                new_encrypted_doc = self.doc_manager.encrypt_and_store_document(
                    document_data, file_record.original_filename, new_keys['public_key']
                )
                
                # Update file record
                file_record.encrypted_key = new_encrypted_doc['metadata']['encrypted_key']
                file_record.encryption_metadata = json.dumps(new_encrypted_doc['metadata'])
                
                # Update encrypted data
                if file_record.encrypted_data:
                    file_record.encrypted_data = new_encrypted_doc['encrypted_data'].encode('utf-8')
                else:
                    # Update separate encrypted document
                    result = await db.execute(
                        select(EncryptedDocument).where(EncryptedDocument.file_id == file_record.id)
                    )
                    encrypted_doc = result.scalar_one()
                    encrypted_doc.encrypted_data = new_encrypted_doc['encrypted_data'].encode('utf-8')
                    encrypted_doc.checksum = new_encrypted_doc['metadata']['checksum']
            
            # Update user keys
            user.public_key = new_keys['public_key']
            user.private_key = new_keys['private_key']
            user.key_salt = new_keys['salt']
            user.key_created_at = datetime.utcnow()
            
            await db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to rotate encryption keys: {str(e)}"
            )
    
    def _generate_secure_filename(self) -> str:
        """
        Generate a secure random filename
        """
        import secrets
        return secrets.token_hex(16) + ".enc"
    
    async def get_file_stats(self, user: User, db: AsyncSession) -> Dict[str, Any]:
        """
        Get file storage statistics for user
        """
        try:
            result = await db.execute(
                select(File).where(File.user_id == user.id)
            )
            files = result.scalars().all()
            
            total_files = len(files)
            encrypted_files = len([f for f in files if f.is_encrypted])
            total_original_size = sum(f.file_size for f in files)
            
            # Calculate compression stats for encrypted files
            total_compressed_size = 0
            for file_record in files:
                if file_record.is_encrypted and file_record.encryption_metadata:
                    metadata = json.loads(file_record.encryption_metadata)
                    total_compressed_size += metadata.get('compressed_size', file_record.file_size)
                else:
                    total_compressed_size += file_record.file_size
            
            return {
                'total_files': total_files,
                'encrypted_files': encrypted_files,
                'total_original_size': total_original_size,
                'total_compressed_size': total_compressed_size,
                'compression_ratio': total_compressed_size / max(total_original_size, 1),
                'encryption_coverage': encrypted_files / max(total_files, 1)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get file statistics: {str(e)}"
            )
