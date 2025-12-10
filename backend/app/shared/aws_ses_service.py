"""
AWS SES Email Service - Production-Ready Implementation
Handles OTP and transactional emails via AWS Simple Email Service (SES)
"""
import os
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from typing import Optional
import logging
from decouple import config

logger = logging.getLogger(__name__)

# AWS SES Configuration - Load from environment variables
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default=None)
AWS_REGION = config('AWS_REGION', default='ca-central-1')
AWS_SES_FROM_EMAIL = config('AWS_SES_FROM_EMAIL', default='diamondacc.project@gmail.com')

# Development mode settings
DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=False, cast=bool)
DEVELOPER_OTP = config('DEVELOPER_OTP', default='123456')


class AWSEmailService:
    """
    AWS SES Email Service
    Production-ready email sending via AWS Simple Email Service
    """
    
    def __init__(self):
        """Initialize AWS SES client"""
        self.from_email = AWS_SES_FROM_EMAIL
        self.region = AWS_REGION
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize boto3 SES client with credentials"""
        try:
            if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
                logger.warning("AWS SES credentials not configured. Email sending will be disabled.")
                return
            
            self.client = boto3.client(
                'ses',
                region_name=self.region,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            
            # Test connection by getting account sending quota
            try:
                quota = self.client.get_send_quota()
                max_24h = quota.get('Max24HourSend', 0)
                sent_24h = quota.get('SentLast24Hours', 0)
                logger.info(f"AWS SES client initialized for region: {self.region}")
                logger.info(f"SES Quota: {sent_24h:.2f} / {max_24h:.2f} emails sent in last 24 hours")
            except Exception as e:
                logger.warning(f"Could not verify SES connection: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize AWS SES client: {e}")
            self.client = None
    
    def _get_otp_email_content(self, otp_code: str) -> tuple[str, str, str]:
        """
        Generate OTP email subject, text body, and HTML body
        
        Args:
            otp_code: 6-digit OTP code
            
        Returns:
            Tuple of (subject, body_text, body_html)
        """
        subject = "Your TaxEase Login OTP"
        
        body_text = f"""Hello,

Your OTP for accessing your TaxEase account is: {otp_code}

This code will expire in 5 minutes.

If you did not request this, please ignore this email.

Best regards,
TaxEase Team
"""
        
        body_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaxEase OTP</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
        <h1 style="color: #ffffff; margin: 0; font-size: 28px;">TaxEase</h1>
    </div>
    
    <div style="background-color: #ffffff; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: #2c3e50; margin-top: 0;">Your Login OTP</h2>
        
        <p style="font-size: 16px;">Hello,</p>
        
        <p style="font-size: 16px;">Your OTP for accessing your TaxEase account is:</p>
        
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 8px; text-align: center; margin: 30px 0;">
            <h1 style="color: #ffffff; font-size: 42px; letter-spacing: 10px; margin: 0; font-family: 'Courier New', monospace; font-weight: bold;">
                {otp_code}
            </h1>
        </div>
        
        <p style="color: #e74c3c; font-weight: bold; font-size: 14px; text-align: center; background-color: #ffeaa7; padding: 15px; border-radius: 5px;">
            ⏰ This code will expire in 5 minutes.
        </p>
        
        <p style="color: #7f8c8d; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
            If you did not request this OTP, please ignore this email. Your account remains secure.
        </p>
    </div>
    
    <div style="text-align: center; margin-top: 20px; padding: 20px;">
        <p style="color: #95a5a6; font-size: 12px; margin: 0;">
            Best regards,<br>
            <strong style="color: #2c3e50;">TaxEase Team</strong>
        </p>
    </div>
</body>
</html>
"""
        
        return subject, body_text, body_html
    
    async def send_otp_email(self, email: str, otp_code: str, purpose: str = "login") -> bool:
        """
        Send OTP email via AWS SES
        
        Args:
            email: Recipient email address
            otp_code: 6-digit OTP code
            purpose: Purpose of OTP (login, email_verification, password_reset)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Development mode: Just log, don't send
            if DEVELOPMENT_MODE:
                logger.info(f"🔥 DEVELOPMENT MODE - OTP for {email}: {otp_code}")
                logger.info(f"📧 Purpose: {purpose}")
                logger.info(f"💡 Use developer OTP: {DEVELOPER_OTP} for testing")
                print(f"\n{'='*60}")
                print(f"🚨 DEVELOPMENT MODE OTP 🚨")
                print(f"{'='*60}")
                print(f"📧 Email: {email}")
                print(f"🔐 OTP Code: {otp_code}")
                print(f"🎯 Purpose: {purpose}")
                print(f"💻 Developer OTP (always works): {DEVELOPER_OTP}")
                print(f"{'='*60}\n")
                return True
            
            # Check if SES client is available
            if not self.client:
                logger.error("AWS SES client not initialized. Cannot send email.")
                return False
            
            # Generate email content
            subject, body_text, body_html = self._get_otp_email_content(otp_code)
            
            # Send email via AWS SES
            try:
                response = self.client.send_email(
                    Source=self.from_email,
                    Destination={
                        'ToAddresses': [email]
                    },
                    Message={
                        'Subject': {
                            'Data': subject,
                            'Charset': 'UTF-8'
                        },
                        'Body': {
                            'Text': {
                                'Data': body_text,
                                'Charset': 'UTF-8'
                            },
                            'Html': {
                                'Data': body_html,
                                'Charset': 'UTF-8'
                            }
                        }
                    }
                )
                
                message_id = response.get('MessageId')
                logger.info(f"✅ OTP email sent successfully to {email}. MessageId: {message_id}")
                return True
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                error_message = e.response.get('Error', {}).get('Message', str(e))
                logger.error(f"❌ AWS SES error sending OTP to {email}: {error_code} - {error_message}")
                
                # Handle common errors with helpful messages
                if error_code == 'MessageRejected':
                    logger.error(f"   Email address may not be verified in SES sandbox mode")
                    logger.error(f"   Verify {email} in AWS SES console or request production access")
                elif error_code == 'MailFromDomainNotVerified':
                    logger.error(f"   Sender email domain not verified in SES")
                    logger.error(f"   Verify {self.from_email} in AWS SES console")
                elif error_code == 'ConfigurationSetDoesNotExist':
                    logger.error(f"   SES configuration set not found")
                elif error_code == 'AccountSendingPausedException':
                    logger.error(f"   Account sending is paused. Check AWS SES console")
                elif error_code == 'SendingPausedException':
                    logger.error(f"   Sending is paused for this region. Check AWS SES console")
                
                return False
                
            except BotoCoreError as e:
                logger.error(f"❌ AWS SDK error sending OTP to {email}: {e}")
                return False
                
            except Exception as e:
                logger.error(f"❌ Unexpected error sending OTP to {email}: {e}", exc_info=True)
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send OTP email to {email}: {e}", exc_info=True)
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
            if DEVELOPMENT_MODE:
                logger.info(f"Welcome email would be sent to {email} (Development mode)")
                return True
            
            if not self.client:
                logger.warning("AWS SES client not initialized. Skipping welcome email.")
                return False
            
            subject = "Welcome to TaxEase!"
            
            body_text = f"""Hello {first_name},

Welcome to TaxEase! Your account has been successfully created.

You can now start managing your tax filings with ease.

If you have any questions, feel free to reach out to our support team.

Best regards,
TaxEase Team
"""
            
            body_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to TaxEase</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
        <h1 style="color: #ffffff; margin: 0;">Welcome to TaxEase!</h1>
    </div>
    
    <div style="background-color: #ffffff; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <p style="font-size: 16px;">Hello {first_name},</p>
        
        <p style="font-size: 16px;">Welcome to TaxEase! Your account has been successfully created.</p>
        
        <p style="font-size: 16px;">You can now start managing your tax filings with ease.</p>
        
        <p style="font-size: 16px;">If you have any questions, feel free to reach out to our support team.</p>
        
        <p style="margin-top: 30px;">Best regards,<br><strong>TaxEase Team</strong></p>
    </div>
</body>
</html>
"""
            
            response = self.client.send_email(
                Source=self.from_email,
                Destination={
                    'ToAddresses': [email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': body_html,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            message_id = response.get('MessageId')
            logger.info(f"✅ Welcome email sent to {email}. MessageId: {message_id}")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"❌ AWS SES error sending welcome email: {error_code}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send welcome email: {e}")
            return False


# Global instance - singleton pattern
_aws_email_service_instance = None

def get_aws_email_service() -> AWSEmailService:
    """Get or create AWS email service instance"""
    global _aws_email_service_instance
    if _aws_email_service_instance is None:
        _aws_email_service_instance = AWSEmailService()
    return _aws_email_service_instance


