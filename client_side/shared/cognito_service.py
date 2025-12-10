"""
AWS Cognito Authentication Service
Handles user signup, confirmation, and authentication via AWS Cognito
"""
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
import logging
import re
from decouple import config

logger = logging.getLogger(__name__)

# AWS Cognito Configuration
AWS_REGION = "ca-central-1"
COGNITO_USER_POOL_ID = config('COGNITO_USER_POOL_ID', default='ca-central-1_FP2WE41eW')
COGNITO_CLIENT_ID = config('COGNITO_CLIENT_ID', default='504mgtvq1h97vlml90c3iibnt0')
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default=None)


class CognitoService:
    """
    AWS Cognito Authentication Service
    Production-ready Cognito integration for user authentication
    """
    
    def __init__(self):
        """Initialize AWS Cognito client"""
        self.user_pool_id = COGNITO_USER_POOL_ID
        self.client_id = COGNITO_CLIENT_ID
        self.region = AWS_REGION
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize boto3 Cognito client with credentials"""
        try:
            # Initialize Cognito client
            client_kwargs = {
                'service_name': 'cognito-idp',
                'region_name': self.region
            }
            
            # Add credentials if provided
            if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
                client_kwargs.update({
                    'aws_access_key_id': AWS_ACCESS_KEY_ID,
                    'aws_secret_access_key': AWS_SECRET_ACCESS_KEY
                })
            
            self.client = boto3.client(**client_kwargs)
            logger.info(f"AWS Cognito client initialized for region: {self.region}")
            logger.info(f"User Pool ID: {self.user_pool_id}")
            logger.info(f"Client ID: {self.client_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS Cognito client: {e}")
            self.client = None
    
    def _normalize_phone_number(self, phone: str) -> str:
        """
        Normalize phone number to E.164 format required by AWS Cognito
        
        Args:
            phone: Phone number in various formats
            
        Returns:
            Phone number in E.164 format (e.g., +17417119014)
        """
        if not phone:
            return phone
        
        # Remove all non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone.strip())
        
        # If already starts with +, return as is (assuming it's in E.164 format)
        if phone.startswith('+'):
            return phone
        
        # If starts with 1 (US/Canada country code), add +
        if phone.startswith('1') and len(phone) == 11:
            return '+' + phone
        
        # If 10 digits (US/Canada without country code), add +1
        if len(phone) == 10 and phone.isdigit():
            return '+1' + phone
        
        # For other formats, try to add +1 (default for ca-central-1 region)
        if phone.isdigit():
            return '+1' + phone
        
        # Return as is if format is unclear (will let Cognito validate)
        logger.warning(f"Could not normalize phone number format: {phone}")
        return phone
    
    def sign_up(self, email: str, password: str, first_name: str, last_name: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Sign up a new user in AWS Cognito
        
        Args:
            email: User's email address (used as username)
            password: User's password
            first_name: User's first name
            last_name: User's last name
            phone: Optional phone number
            
        Returns:
            Dictionary with Cognito response
            
        Raises:
            ClientError: If Cognito operation fails
        """
        if not self.client:
            raise Exception("AWS Cognito client not initialized")
        
        # Prepare user attributes
        user_attributes = [
            {"Name": "email", "Value": email},
            {"Name": "given_name", "Value": first_name},
            {"Name": "family_name", "Value": last_name},
        ]
        
        # Add phone number if provided (normalize to E.164 format)
        # Skip phone number if it might cause issues - it's optional for Cognito
        if phone and phone.strip():
            try:
                normalized_phone = self._normalize_phone_number(phone)
                if normalized_phone and normalized_phone.startswith('+'):
                    user_attributes.append({"Name": "phone_number", "Value": normalized_phone})
                    logger.info(f"Adding phone number attribute: {normalized_phone} (normalized from: {phone})")
                else:
                    logger.warning(f"Phone number validation failed for: {phone}, skipping phone attribute (optional)")
            except Exception as e:
                logger.warning(f"Error normalizing phone number {phone}, skipping (optional): {e}")
        
        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=user_attributes
            )
            
            logger.info(f"User signed up successfully in Cognito: {email}")
            return {
                "success": True,
                "user_sub": response.get("UserSub"),
                "code_delivery_details": response.get("CodeDeliveryDetails"),
                "message": "User created successfully. OTP sent to email."
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Cognito sign_up error for {email}: {error_code} - {error_message}")
            raise
    
    def confirm_sign_up(self, email: str, confirmation_code: str) -> Dict[str, Any]:
        """
        Confirm user signup with OTP code
        
        Args:
            email: User's email address (username)
            confirmation_code: OTP code sent to email
            
        Returns:
            Dictionary with confirmation result
            
        Raises:
            ClientError: If confirmation fails
        """
        if not self.client:
            raise Exception("AWS Cognito client not initialized")
        
        try:
            # Normalize confirmation code (strip whitespace)
            confirmation_code = str(confirmation_code).strip()
            
            self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code
            )
            
            logger.info(f"User signup confirmed successfully: {email}")
            return {
                "success": True,
                "message": "Signup confirmed successfully"
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Cognito confirm_sign_up error for {email}: {error_code} - {error_message}")
            
            # Map Cognito errors to user-friendly messages
            if error_code == 'CodeMismatchException':
                raise Exception("Invalid confirmation code. Please check your OTP and try again.")
            elif error_code == 'ExpiredCodeException':
                raise Exception("Confirmation code has expired. Please request a new OTP.")
            elif error_code == 'UserNotFoundException':
                raise Exception("User not found. Please sign up first.")
            else:
                raise Exception(f"Confirmation failed: {error_message}")
    
    def initiate_auth(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and get tokens
        
        Args:
            email: User's email address (username)
            password: User's password
            
        Returns:
            Dictionary with authentication tokens
            
        Raises:
            ClientError: If authentication fails
        """
        if not self.client:
            raise Exception("AWS Cognito client not initialized")
        
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password,
                }
            )
            
            auth_result = response.get("AuthenticationResult", {})
            
            tokens = {
                "id_token": auth_result.get("IdToken"),
                "access_token": auth_result.get("AccessToken"),
                "refresh_token": auth_result.get("RefreshToken"),
                "expires_in": auth_result.get("ExpiresIn", 3600),
                "token_type": auth_result.get("TokenType", "Bearer")
            }
            
            logger.info(f"User authenticated successfully: {email}")
            return {
                "success": True,
                "tokens": tokens
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Cognito initiate_auth error for {email}: {error_code} - {error_message}")
            
            # Map Cognito errors to user-friendly messages
            if error_code == 'NotAuthorizedException':
                raise Exception("Invalid email or password.")
            elif error_code == 'UserNotConfirmedException':
                raise Exception("Email not verified. Please confirm your email address first.")
            elif error_code == 'UserNotFoundException':
                raise Exception("User not found. Please sign up first.")
            elif error_code == 'TooManyFailedAttemptsException':
                raise Exception("Too many failed attempts. Please try again later.")
            else:
                raise Exception(f"Authentication failed: {error_message}")
    
    def resend_confirmation_code(self, email: str) -> Dict[str, Any]:
        """
        Resend confirmation code to user's email
        
        Args:
            email: User's email address (username)
            
        Returns:
            Dictionary with result
        """
        if not self.client:
            raise Exception("AWS Cognito client not initialized")
        
        try:
            response = self.client.resend_confirmation_code(
                ClientId=self.client_id,
                Username=email
            )
            
            logger.info(f"Confirmation code resent to: {email}")
            return {
                "success": True,
                "message": "Confirmation code sent successfully",
                "code_delivery_details": response.get("CodeDeliveryDetails")
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Cognito resend_confirmation_code error for {email}: {error_code} - {error_message}")
            raise


# Global instance
_cognito_service_instance = None

def get_cognito_service() -> CognitoService:
    """Get or create Cognito service instance"""
    global _cognito_service_instance
    if _cognito_service_instance is None:
        _cognito_service_instance = CognitoService()
    return _cognito_service_instance


