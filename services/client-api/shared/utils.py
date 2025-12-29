"""
Utility functions and helpers
"""

import os
import secrets
import string
from typing import Optional
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
import logging
from decouple import config

logger = logging.getLogger(__name__)

# Development mode settings
DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
DEVELOPER_OTP = config('DEVELOPER_OTP', default='123456')
# Bypass OTP code that always works for testing (works in both dev and production)
BYPASS_OTP = config('BYPASS_OTP', default='698745')
SKIP_EMAIL_VERIFICATION = config('SKIP_EMAIL_VERIFICATION', default=False, cast=bool)

def generate_otp(length: int = 6) -> str:
    """
    Generate a random, unpredictable OTP code
    Exactly 6 digits, numeric only
    
    Args:
        length: Length of OTP (default 6)
        
    Returns:
        6-digit numeric OTP string
    """
    digits = string.digits
    # Use secrets module for cryptographically strong randomness
    return ''.join(secrets.choice(digits) for _ in range(length))

def generate_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving extension"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_string = secrets.token_urlsafe(8)
    
    # Get file extension
    if '.' in original_filename:
        name, ext = original_filename.rsplit('.', 1)
        return f"{timestamp}_{random_string}.{ext}"
    else:
        return f"{timestamp}_{random_string}"

class S3Manager:
    """
    Local filesystem file management (replaces S3 for local development)
    Maintains S3-like interface for compatibility
    """
    
    def __init__(self):
        # Use local storage directory
        base_dir = os.getenv('STORAGE_BASE_DIR', os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'uploads'))
        self.storage_base = os.path.abspath(base_dir)
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_base, exist_ok=True)
        
        # For compatibility with existing code
        self.bucket_name = "local-storage"
        logger.info(f"Local file storage initialized at: {self.storage_base}")
    
    def _get_local_path(self, key: str) -> str:
        """Convert S3 key to local filesystem path"""
        # Remove any leading slashes
        key = key.lstrip('/')
        # Join with storage base, ensuring no directory traversal
        safe_key = os.path.normpath(key).replace('..', '')
        return os.path.join(self.storage_base, safe_key)
    
    async def upload_file(self, file_content: bytes, key: str, content_type: str) -> bool:
        """Upload file to local filesystem"""
        try:
            local_path = self._get_local_path(key)
            
            # Create parent directories if needed
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Write file
            with open(local_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"File uploaded to local storage: {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file to local storage: {e}")
            return False
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from local filesystem"""
        try:
            local_path = self._get_local_path(key)
            if os.path.exists(local_path):
                os.remove(local_path)
                logger.info(f"File deleted from local storage: {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from local storage: {e}")
            return False
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate local file URL for download
        Returns path relative to storage base for serving via HTTP
        """
        try:
            # Return the key as-is, server will handle serving the file
            # Format: /files/download/{key}
            return f"/files/download/{key}"
        except Exception as e:
            logger.error(f"Failed to generate file URL: {e}")
            return None
    
    def get_file_path(self, key: str) -> Optional[str]:
        """Get absolute local file path for serving"""
        try:
            local_path = self._get_local_path(key)
            if os.path.exists(local_path):
                return local_path
            return None
        except Exception as e:
            logger.error(f"Failed to get file path: {e}")
            return None

class EmailService:
    """Email service for OTP and notifications - uses AWS SES"""
    
    def __init__(self):
        """Initialize email service with AWS SES"""
        try:
            from shared.aws_ses_service import get_aws_email_service
            self.aws_service = get_aws_email_service()
        except ImportError:
            logger.warning("AWS SES email service not available, using fallback")
            self.aws_service = None
    
    async def send_otp_email(self, email: str, otp_code: str, purpose: str) -> bool:
        """
        Send OTP via AWS SES email
        
        Args:
            email: Recipient email address
            otp_code: 6-digit OTP code
            purpose: Purpose of OTP (login, email_verification, password_reset)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Use AWS SES service if available
            if self.aws_service:
                return await self.aws_service.send_otp_email(email, otp_code, purpose)
            
            # Fallback to development mode logging
            if DEVELOPMENT_MODE:
                logger.info(f"🔥 DEVELOPMENT MODE - OTP for {email}: {otp_code}")
                logger.info(f"📧 Purpose: {purpose}")
                logger.info(f"💡 Use developer OTP: {DEVELOPER_OTP} for testing")
                print(f"\n🚨 DEVELOPMENT MODE OTP 🚨")
                print(f"📧 Email: {email}")
                print(f"🔐 OTP Code: {otp_code}")
                print(f"🎯 Purpose: {purpose}")
                print(f"💻 Developer OTP (always works): {DEVELOPER_OTP}")
                print(f"{'='*50}\n")
                return True
            else:
                logger.warning(f"AWS SES not configured. OTP {otp_code} for {email} not sent.")
                return False
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}", exc_info=True)
            return False
    
    async def send_welcome_email(self, email: str, first_name: str) -> bool:
        """
        Send welcome email to new user via AWS SES
        
        Args:
            email: Recipient email address
            first_name: User's first name
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Use AWS SES service if available
            if self.aws_service:
                return await self.aws_service.send_welcome_email(email, first_name)
            
            # Fallback logging
            if DEVELOPMENT_MODE:
                logger.info(f"Welcome email would be sent to {email} (Development mode)")
                return True
            else:
                logger.warning(f"AWS SES not configured. Welcome email for {email} not sent.")
                return False
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}", exc_info=True)
            return False

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate file type based on extension"""
    if '.' not in filename:
        return False
    
    file_extension = filename.rsplit('.', 1)[1].lower()
    return file_extension in allowed_types

def calculate_tax(income: float, province: str = "ON") -> dict:
    """Calculate Canadian federal and provincial tax (simplified)"""
    
    # This is a simplified calculation - in production, use proper tax tables
    federal_tax = 0.0
    provincial_tax = 0.0
    
    # Federal tax brackets (2023 - simplified)
    if income <= 53359:
        federal_tax = income * 0.15
    elif income <= 106717:
        federal_tax = 53359 * 0.15 + (income - 53359) * 0.205
    elif income <= 165430:
        federal_tax = 53359 * 0.15 + (106717 - 53359) * 0.205 + (income - 106717) * 0.26
    else:
        federal_tax = 53359 * 0.15 + (106717 - 53359) * 0.205 + (165430 - 106717) * 0.26 + (income - 165430) * 0.29
    
    # Provincial tax (Ontario rates - simplified)
    if province == "ON":
        if income <= 49231:
            provincial_tax = income * 0.0505
        elif income <= 98463:
            provincial_tax = 49231 * 0.0505 + (income - 49231) * 0.0915
        else:
            provincial_tax = 49231 * 0.0505 + (98463 - 49231) * 0.0915 + (income - 98463) * 0.1116
    
    total_tax = federal_tax + provincial_tax
    
    return {
        "federal_tax": round(federal_tax, 2),
        "provincial_tax": round(provincial_tax, 2),
        "total_tax": round(total_tax, 2)
    }

async def log_user_action(
    db, 
    user_id: str, 
    action: str, 
    resource_type: str, 
    resource_id: str,
    metadata: dict = None
):
    """
    Log user actions for audit trail and security monitoring
    
    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Action performed (e.g., 't1_form_created', 'file_uploaded')
        resource_type: Type of resource (e.g., 't1_form', 'file')
        resource_id: ID of the resource affected
        metadata: Additional context information
    """
    try:
        from shared.models import AuditLog
        from datetime import datetime
        import json
        
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=json.dumps(metadata) if metadata else None,
            created_at=datetime.utcnow()
        )
        
        db.add(audit_entry)
        # Note: Don't commit here - let the calling function handle commits
        
        logger.info(f"Action logged: {action} on {resource_type}:{resource_id} by user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to log user action: {str(e)}")
        # Don't raise exception to avoid breaking the main operation
