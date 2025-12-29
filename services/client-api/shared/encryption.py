"""
End-to-End Encryption Service for Document Security
Provides compression and encryption for sensitive documents
"""
import os
import gzip
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional, Dict, Any
import json
import secrets
from datetime import datetime, timedelta


class DocumentEncryption:
    """
    End-to-End Document Encryption Service
    Features:
    - AES-256 encryption for documents
    - RSA key pair generation for users
    - Document compression before encryption
    - Key derivation from user passwords
    - Secure key storage and management
    """
    
    def __init__(self):
        self.backend = default_backend()
        self.aes_key_size = 32  # 256 bits
        self.iv_size = 16      # 128 bits
        self.salt_size = 32    # 256 bits
        
    def generate_user_keypair(self, password: str) -> Dict[str, str]:
        """
        Generate RSA key pair for a user
        Returns encrypted private key and public key
        """
        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.backend
        )
        public_key = private_key.public_key()
        
        # Derive encryption key from password
        salt = os.urandom(self.salt_size)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = kdf.derive(password.encode())
        
        # Encrypt private key with derived key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(key)
        )
        
        # Get public key in PEM format
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'private_key': base64.b64encode(private_pem).decode('utf-8'),
            'public_key': base64.b64encode(public_pem).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8'),
            'created_at': datetime.utcnow().isoformat()
        }
    
    def compress_document(self, document_data: bytes) -> bytes:
        """
        Compress document data using gzip
        """
        return gzip.compress(document_data, compresslevel=9)
    
    def decompress_document(self, compressed_data: bytes) -> bytes:
        """
        Decompress document data
        """
        return gzip.decompress(compressed_data)
    
    def generate_document_key(self) -> Tuple[bytes, bytes]:
        """
        Generate a random AES key and IV for document encryption
        """
        key = os.urandom(self.aes_key_size)
        iv = os.urandom(self.iv_size)
        return key, iv
    
    def encrypt_document(self, document_data: bytes, aes_key: bytes, iv: bytes) -> bytes:
        """
        Encrypt document data using AES-256-CBC
        """
        # Compress first
        compressed_data = self.compress_document(document_data)
        
        # Pad data to block size
        padded_data = self._pad_data(compressed_data)
        
        # Encrypt
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data
    
    def decrypt_document(self, encrypted_data: bytes, aes_key: bytes, iv: bytes) -> bytes:
        """
        Decrypt document data and decompress
        """
        # Decrypt
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Unpad
        compressed_data = self._unpad_data(padded_data)
        
        # Decompress
        document_data = self.decompress_document(compressed_data)
        
        return document_data
    
    def encrypt_document_key(self, aes_key: bytes, iv: bytes, public_key_pem: str) -> str:
        """
        Encrypt the document AES key using RSA public key
        """
        public_key = serialization.load_pem_public_key(
            base64.b64decode(public_key_pem),
            backend=self.backend
        )
        
        # Combine key and IV
        key_data = aes_key + iv
        
        # Encrypt with RSA
        encrypted_key = public_key.encrypt(
            key_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(encrypted_key).decode('utf-8')
    
    def decrypt_document_key(self, encrypted_key_b64: str, private_key_pem: str, password: str, salt: str) -> Tuple[bytes, bytes]:
        """
        Decrypt the document AES key using RSA private key
        """
        # Derive key from password
        salt_bytes = base64.b64decode(salt)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
            backend=self.backend
        )
        derived_key = kdf.derive(password.encode())
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            base64.b64decode(private_key_pem),
            password=derived_key,
            backend=self.backend
        )
        
        # Decrypt the document key
        encrypted_key = base64.b64decode(encrypted_key_b64)
        key_data = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Split key and IV
        aes_key = key_data[:self.aes_key_size]
        iv = key_data[self.aes_key_size:]
        
        return aes_key, iv
    
    def create_encrypted_document(self, document_data: bytes, public_key_pem: str) -> Dict[str, Any]:
        """
        Full document encryption process
        Returns encrypted document with metadata
        """
        # Generate document encryption key
        aes_key, iv = self.generate_document_key()
        
        # Encrypt document
        encrypted_document = self.encrypt_document(document_data, aes_key, iv)
        
        # Encrypt the document key with user's public key
        encrypted_key = self.encrypt_document_key(aes_key, iv, public_key_pem)
        
        # Create metadata
        metadata = {
            'encrypted_key': encrypted_key,
            'original_size': len(document_data),
            'compressed_size': len(self.compress_document(document_data)),
            'encrypted_size': len(encrypted_document),
            'encryption_algorithm': 'AES-256-CBC',
            'key_algorithm': 'RSA-2048-OAEP',
            'created_at': datetime.utcnow().isoformat(),
            'checksum': hashlib.sha256(document_data).hexdigest()
        }
        
        return {
            'encrypted_data': base64.b64encode(encrypted_document).decode('utf-8'),
            'metadata': metadata
        }
    
    def decrypt_encrypted_document(self, encrypted_data_b64: str, metadata: Dict[str, Any], 
                                 private_key_pem: str, password: str, salt: str) -> bytes:
        """
        Full document decryption process
        """
        # Decrypt document key
        aes_key, iv = self.decrypt_document_key(
            metadata['encrypted_key'], 
            private_key_pem, 
            password, 
            salt
        )
        
        # Decrypt document
        encrypted_data = base64.b64decode(encrypted_data_b64)
        document_data = self.decrypt_document(encrypted_data, aes_key, iv)
        
        # Verify checksum
        if hashlib.sha256(document_data).hexdigest() != metadata['checksum']:
            raise ValueError("Document integrity check failed")
        
        return document_data
    
    def _pad_data(self, data: bytes) -> bytes:
        """
        PKCS7 padding for AES
        """
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, padded_data: bytes) -> bytes:
        """
        Remove PKCS7 padding
        """
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]


class SecureDocumentManager:
    """
    High-level interface for secure document management
    """
    
    def __init__(self):
        self.encryption = DocumentEncryption()
    
    def setup_user_encryption(self, user_id: str, password: str) -> Dict[str, str]:
        """
        Set up encryption keys for a new user
        """
        keypair = self.encryption.generate_user_keypair(password)
        keypair['user_id'] = user_id
        return keypair
    
    def encrypt_and_store_document(self, document_data: bytes, filename: str, 
                                 public_key_pem: str) -> Dict[str, Any]:
        """
        Encrypt document and prepare for storage
        """
        encrypted_doc = self.encryption.create_encrypted_document(document_data, public_key_pem)
        
        # Add file metadata
        encrypted_doc['metadata'].update({
            'original_filename': filename,
            'file_extension': os.path.splitext(filename)[1].lower(),
            'mime_type': self._get_mime_type(filename)
        })
        
        return encrypted_doc
    
    def decrypt_and_retrieve_document(self, encrypted_data_b64: str, metadata: Dict[str, Any],
                                    private_key_pem: str, password: str, salt: str) -> Tuple[bytes, str]:
        """
        Decrypt document and return data with filename
        """
        document_data = self.encryption.decrypt_encrypted_document(
            encrypted_data_b64, metadata, private_key_pem, password, salt
        )
        
        filename = metadata.get('original_filename', 'document')
        return document_data, filename
    
    def _get_mime_type(self, filename: str) -> str:
        """
        Get MIME type based on file extension
        """
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain'
        }
        return mime_types.get(ext, 'application/octet-stream')


# Key Management Service
class KeyManager:
    """
    Secure key management for user encryption keys
    """
    
    def __init__(self):
        self.encryption = DocumentEncryption()
    
    def store_user_keys(self, user_id: str, password: str) -> Dict[str, str]:
        """
        Generate and return user encryption keys
        Keys should be stored securely in database
        """
        return self.encryption.generate_user_keypair(password)
    
    def rotate_user_keys(self, user_id: str, old_password: str, new_password: str, 
                        current_private_key: str, salt: str) -> Dict[str, str]:
        """
        Rotate user keys when password changes
        """
        # First verify old password can decrypt current key
        try:
            salt_bytes = base64.b64decode(salt)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
                backend=default_backend()
            )
            old_derived_key = kdf.derive(old_password.encode())
            
            # Try to load the private key with old password
            serialization.load_pem_private_key(
                base64.b64decode(current_private_key),
                password=old_derived_key,
                backend=default_backend()
            )
        except Exception:
            raise ValueError("Invalid old password")
        
        # Generate new keys with new password
        return self.encryption.generate_user_keypair(new_password)
    
    def verify_user_access(self, private_key_pem: str, password: str, salt: str) -> bool:
        """
        Verify user can access their private key
        """
        try:
            salt_bytes = base64.b64decode(salt)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
                backend=default_backend()
            )
            derived_key = kdf.derive(password.encode())
            
            serialization.load_pem_private_key(
                base64.b64decode(private_key_pem),
                password=derived_key,
                backend=default_backend()
            )
            return True
        except Exception:
            return False


# Usage example and testing
if __name__ == "__main__":
    # Example usage
    doc_manager = SecureDocumentManager()
    key_manager = KeyManager()
    
    # Setup user
    user_keys = key_manager.store_user_keys("user123", "SecurePassword123!")
    
    # Encrypt document
    document_data = b"This is a confidential tax document with sensitive information."
    encrypted_doc = doc_manager.encrypt_and_store_document(
        document_data, 
        "tax_document.pdf", 
        user_keys['public_key']
    )
    
    print("Document encrypted successfully!")
    print(f"Original size: {encrypted_doc['metadata']['original_size']} bytes")
    print(f"Compressed size: {encrypted_doc['metadata']['compressed_size']} bytes")
    print(f"Encrypted size: {encrypted_doc['metadata']['encrypted_size']} bytes")
    
    # Decrypt document
    decrypted_data, filename = doc_manager.decrypt_and_retrieve_document(
        encrypted_doc['encrypted_data'],
        encrypted_doc['metadata'],
        user_keys['private_key'],
        "SecurePassword123!",
        user_keys['salt']
    )
    
    print(f"\nDocument decrypted successfully!")
    print(f"Filename: {filename}")
    print(f"Content: {decrypted_data.decode()}")
    print(f"Integrity check: {'PASSED' if document_data == decrypted_data else 'FAILED'}")
