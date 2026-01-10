"""AWS S3 Storage Integration for Document Management."""
import os
import logging
from typing import Optional, BinaryIO
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class S3StorageService:
    """Service for handling file storage on AWS S3."""
    
    def __init__(self):
        """Initialize S3 client with AWS credentials from environment."""
        self.use_s3 = os.getenv("USE_S3_STORAGE", "false").lower() == "true"
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "taxease-prod-documents")
        self.region = os.getenv("AWS_REGION", "ca-central-1")
        
        if self.use_s3:
            try:
                # Initialize S3 client
                # If running on EC2 with IAM role, credentials are automatic
                # Otherwise, uses AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from env
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.region,
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                )
                
                # Verify bucket exists
                self._verify_bucket()
                logger.info(f"S3 storage initialized: bucket={self.bucket_name}, region={self.region}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                raise
        else:
            logger.info("Using local file storage (S3 disabled)")
            self.local_storage_path = os.getenv("STORAGE_PATH", "./storage/uploads")
            os.makedirs(self.local_storage_path, exist_ok=True)
    
    def _verify_bucket(self):
        """Verify that the S3 bucket exists and is accessible."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                raise Exception(f"S3 bucket '{self.bucket_name}' does not exist")
            elif error_code == '403':
                raise Exception(f"Access denied to S3 bucket '{self.bucket_name}'")
            else:
                raise Exception(f"Error accessing S3 bucket: {e}")
    
    def upload_file(
        self, 
        file_content: bytes, 
        file_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload a file to S3 or local storage.
        
        Args:
            file_content: Binary content of the file
            file_key: Unique key/path for the file (e.g., "documents/uuid.pdf.enc")
            content_type: MIME type of the file
            metadata: Additional metadata to store with the file
        
        Returns:
            The file key/path where the file was stored
        """
        if self.use_s3:
            return self._upload_to_s3(file_content, file_key, content_type, metadata)
        else:
            return self._upload_to_local(file_content, file_key)
    
    def _upload_to_s3(
        self, 
        file_content: bytes, 
        file_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to S3 bucket."""
        try:
            extra_args = {}
            
            if content_type:
                extra_args['ContentType'] = content_type
            
            if metadata:
                extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}
            
            # Upload encrypted file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ServerSideEncryption='AES256',  # Server-side encryption
                **extra_args
            )
            
            logger.info(f"File uploaded to S3: s3://{self.bucket_name}/{file_key}")
            return file_key
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found")
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception(f"Failed to upload file to S3: {e}")
    
    def _upload_to_local(self, file_content: bytes, file_key: str) -> str:
        """Upload file to local storage."""
        file_path = os.path.join(self.local_storage_path, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"File uploaded to local storage: {file_path}")
        return file_path
    
    def download_file(self, file_key: str) -> bytes:
        """
        Download a file from S3 or local storage.
        
        Args:
            file_key: The key/path of the file to download
        
        Returns:
            Binary content of the file
        """
        if self.use_s3:
            return self._download_from_s3(file_key)
        else:
            return self._download_from_local(file_key)
    
    def _download_from_s3(self, file_key: str) -> bytes:
        """Download file from S3 bucket."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            content = response['Body'].read()
            logger.info(f"File downloaded from S3: s3://{self.bucket_name}/{file_key}")
            return content
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchKey':
                raise FileNotFoundError(f"File not found in S3: {file_key}")
            else:
                logger.error(f"S3 download failed: {e}")
                raise Exception(f"Failed to download file from S3: {e}")
    
    def _download_from_local(self, file_key: str) -> bytes:
        """Download file from local storage."""
        file_path = file_key if os.path.isabs(file_key) else os.path.join(self.local_storage_path, file_key)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        logger.info(f"File downloaded from local storage: {file_path}")
        return content
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3 or local storage.
        
        Args:
            file_key: The key/path of the file to delete
        
        Returns:
            True if deletion was successful
        """
        if self.use_s3:
            return self._delete_from_s3(file_key)
        else:
            return self._delete_from_local(file_key)
    
    def _delete_from_s3(self, file_key: str) -> bool:
        """Delete file from S3 bucket."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"File deleted from S3: s3://{self.bucket_name}/{file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            return False
    
    def _delete_from_local(self, file_key: str) -> bool:
        """Delete file from local storage."""
        file_path = file_key if os.path.isabs(file_key) else os.path.join(self.local_storage_path, file_key)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted from local storage: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Local file deletion failed: {e}")
            return False
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3 or local storage.
        
        Args:
            file_key: The key/path of the file to check
        
        Returns:
            True if file exists
        """
        if self.use_s3:
            return self._file_exists_in_s3(file_key)
        else:
            return self._file_exists_locally(file_key)
    
    def _file_exists_in_s3(self, file_key: str) -> bool:
        """Check if file exists in S3 bucket."""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError:
            return False
    
    def _file_exists_locally(self, file_key: str) -> bool:
        """Check if file exists in local storage."""
        file_path = file_key if os.path.isabs(file_key) else os.path.join(self.local_storage_path, file_key)
        return os.path.exists(file_path)
    
    def get_file_url(self, file_key: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned URL for file download (S3 only).
        
        Args:
            file_key: The key/path of the file
            expires_in: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Presigned URL for file access
        """
        if not self.use_s3:
            raise NotImplementedError("Presigned URLs are only available for S3 storage")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise Exception(f"Failed to generate file URL: {e}")


# Singleton instance
_storage_service = None

def get_storage_service() -> S3StorageService:
    """Get or create the storage service singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = S3StorageService()
    return _storage_service
