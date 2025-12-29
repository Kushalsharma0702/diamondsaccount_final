"""
Firebase Authentication Service
Handles Firebase ID token verification and user management

This service works ALONGSIDE existing AWS Cognito/SES OTP flow.
Both authentication methods can be used independently.
"""

import os
import logging
from typing import Optional, Dict, Any
from decouple import config

logger = logging.getLogger(__name__)

# Firebase Admin SDK Configuration
FIREBASE_PROJECT_ID = config('FIREBASE_PROJECT_ID', default='taxease-ec35f')
FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', default=None)

# Firebase Admin SDK (lazy import to avoid errors if not installed)
firebase_admin = None
auth = None

def _initialize_firebase_admin():
    """Initialize Firebase Admin SDK (lazy loading)"""
    global firebase_admin, auth
    
    if firebase_admin is not None:
        return  # Already initialized
    
    try:
        import firebase_admin as fa
        from firebase_admin import credentials, auth as firebase_auth
        
        firebase_admin = fa
        auth = firebase_auth
        
        # Check if Firebase app already initialized
        try:
            firebase_admin.get_app()
            logger.info("✅ Firebase Admin SDK already initialized")
            return
        except ValueError:
            # App not initialized, proceed with initialization
            pass
        
        # Initialize Firebase Admin SDK
        if FIREBASE_CREDENTIALS_PATH and os.path.exists(FIREBASE_CREDENTIALS_PATH):
            # Use service account credentials file
            try:
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
                logger.info(f"✅ Firebase Admin SDK initialized with credentials: {FIREBASE_CREDENTIALS_PATH}")
                return
            except Exception as e:
                logger.error(f"❌ Failed to initialize Firebase with credentials file: {e}")
                logger.error(f"   Credentials path: {FIREBASE_CREDENTIALS_PATH}")
        else:
            logger.warning(f"⚠️ FIREBASE_CREDENTIALS_PATH not set or file not found")
            logger.warning(f"   Expected path: {FIREBASE_CREDENTIALS_PATH}")
            logger.warning(f"   Current working directory: {os.getcwd()}")
        
        # Try to use default credentials (for cloud environments like GCP)
        try:
            firebase_admin.initialize_app()
            logger.info("✅ Firebase Admin SDK initialized with default credentials")
            return
        except Exception as e:
            logger.warning(f"⚠️ Firebase Admin SDK initialization with default credentials failed: {e}")
        
        # If we get here, initialization failed
        logger.error("❌ Firebase Admin SDK initialization failed. Firebase authentication will be disabled.")
        logger.error("   To fix: Set FIREBASE_CREDENTIALS_PATH environment variable to your service account JSON file")
        firebase_admin = None
        auth = None
        
    except ImportError:
        logger.error("❌ firebase-admin package not installed. Firebase authentication will be disabled.")
        logger.error("   Install with: pip install firebase-admin")
        firebase_admin = None
        auth = None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Firebase Admin SDK: {e}", exc_info=True)
        firebase_admin = None
        auth = None


class FirebaseVerificationService:
    """
    Firebase ID Token Verification Service
    Verifies Firebase ID tokens and extracts user information
    """
    
    @staticmethod
    def verify_id_token(id_token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token and return decoded token claims
        
        Args:
            id_token: Firebase ID token string
            
        Returns:
            Dictionary containing decoded token claims (uid, email, etc.)
            
        Raises:
            Exception: If token is invalid or verification fails
        """
        _initialize_firebase_admin()
        
        if auth is None:
            raise Exception(
                "Firebase Admin SDK not initialized. "
                "Please install firebase-admin and configure credentials."
            )
        
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            
            logger.info(f"Firebase ID token verified for user: {decoded_token.get('uid')}")
            
            return {
                'uid': decoded_token.get('uid'),
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'firebase_claims': decoded_token,
            }
            
        except Exception as e:
            logger.error(f"Firebase ID token verification failed: {e}")
            raise Exception(f"Invalid Firebase ID token: {str(e)}")
    
    @staticmethod
    def is_available() -> bool:
        """Check if Firebase Admin SDK is available and initialized"""
        _initialize_firebase_admin()
        return auth is not None


def get_firebase_service() -> FirebaseVerificationService:
    """Get Firebase verification service instance"""
    return FirebaseVerificationService()

