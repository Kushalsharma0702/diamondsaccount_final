"""
File encryption utilities for document storage.
Uses Fernet (symmetric encryption) for encrypting/decrypting files.
"""
import os
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv("FILE_ENCRYPTION_KEY", None)

if not ENCRYPTION_KEY:
    # Generate a new key if not set (for development only)
    # In production, this should be set in .env file
    print("⚠️  WARNING: FILE_ENCRYPTION_KEY not set, generating new key (not secure for production!)")
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"Generated key (add to .env): FILE_ENCRYPTION_KEY={ENCRYPTION_KEY}")

try:
    # Ensure key is bytes
    if isinstance(ENCRYPTION_KEY, str):
        ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
    fernet = Fernet(ENCRYPTION_KEY)
except Exception as e:
    raise ValueError(f"Invalid encryption key: {e}")


def encrypt_file_content(file_content: bytes) -> bytes:
    """
    Encrypt file content using Fernet symmetric encryption.
    
    Args:
        file_content: Raw file bytes to encrypt
        
    Returns:
        Encrypted file bytes
    """
    if not file_content:
        raise ValueError("File content is empty")
    
    try:
        encrypted_content = fernet.encrypt(file_content)
        return encrypted_content
    except Exception as e:
        raise ValueError(f"Encryption failed: {e}")


def decrypt_file_content(encrypted_content: bytes) -> bytes:
    """
    Decrypt file content using Fernet symmetric encryption.
    
    Args:
        encrypted_content: Encrypted file bytes
        
    Returns:
        Decrypted file bytes
    """
    if not encrypted_content:
        raise ValueError("Encrypted content is empty")
    
    try:
        decrypted_content = fernet.decrypt(encrypted_content)
        return decrypted_content
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")


def encrypt_file(file_path: str) -> bytes:
    """
    Read and encrypt a file from disk.
    
    Args:
        file_path: Path to file to encrypt
        
    Returns:
        Encrypted file bytes
    """
    with open(file_path, "rb") as f:
        file_content = f.read()
    return encrypt_file_content(file_content)


def decrypt_file(encrypted_content: bytes, output_path: str):
    """
    Decrypt and save a file to disk.
    
    Args:
        encrypted_content: Encrypted file bytes
        output_path: Path to save decrypted file
    """
    decrypted_content = decrypt_file_content(encrypted_content)
    with open(output_path, "wb") as f:
        f.write(decrypted_content)


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    Use this to create a key for production.
    
    Returns:
        Base64-encoded encryption key string
    """
    return Fernet.generate_key().decode()

