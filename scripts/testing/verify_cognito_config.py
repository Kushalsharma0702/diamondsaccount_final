#!/usr/bin/env python3
"""
Verify Cognito App Client Configuration
Checks if USER_PASSWORD_AUTH is enabled and tests authentication flows
"""

import sys
import os
import boto3
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../client_side'))

from decouple import config
from shared.cognito_service import COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default=None)
AWS_REGION = config('AWS_REGION', default='ca-central-1')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def check_app_client_config():
    """Check Cognito app client configuration"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}Cognito App Client Configuration Check{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    
    try:
        cognito_client = boto3.client(
            'cognito-idp',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        print_info(f"User Pool ID: {COGNITO_USER_POOL_ID}")
        print_info(f"Client ID: {COGNITO_CLIENT_ID}\n")
        
        # Get app client details
        try:
            response = cognito_client.describe_user_pool_client(
                UserPoolId=COGNITO_USER_POOL_ID,
                ClientId=COGNITO_CLIENT_ID
            )
            
            client_info = response['UserPoolClient']
            app_client_name = client_info.get('ClientName', 'N/A')
            explicit_auth_flows = client_info.get('ExplicitAuthFlows', [])
            
            print_info(f"App Client Name: {app_client_name}")
            print_info(f"Explicit Auth Flows: {explicit_auth_flows}\n")
            
            # Check for USER_PASSWORD_AUTH
            has_user_password_auth = 'ALLOW_USER_PASSWORD_AUTH' in explicit_auth_flows
            has_user_srp_auth = 'ALLOW_USER_SRP_AUTH' in explicit_auth_flows
            has_admin_user_password_auth = 'ALLOW_ADMIN_USER_PASSWORD_AUTH' in explicit_auth_flows
            
            print(f"{Colors.YELLOW}Authentication Flows Status:{Colors.RESET}")
            print(f"  ALLOW_USER_PASSWORD_AUTH: {'✅ Enabled' if has_user_password_auth else '❌ Disabled'}")
            print(f"  ALLOW_USER_SRP_AUTH: {'✅ Enabled' if has_user_srp_auth else '❌ Disabled'}")
            print(f"  ALLOW_ADMIN_USER_PASSWORD_AUTH: {'✅ Enabled' if has_admin_user_password_auth else '❌ Disabled'}")
            
            if not has_user_password_auth:
                print(f"\n{Colors.RED}❌ USER_PASSWORD_AUTH is NOT enabled!{Colors.RESET}")
                print(f"{Colors.YELLOW}To enable it:{Colors.RESET}")
                print(f"  1. Go to AWS Cognito Console")
                print(f"  2. Select User Pool: {COGNITO_USER_POOL_ID}")
                print(f"  3. Go to App clients → {app_client_name}")
                print(f"  4. Click 'Edit'")
                print(f"  5. Check 'Sign in with username and password'")
                print(f"  6. Save changes")
                return False
            else:
                print(f"\n{Colors.GREEN}✅ USER_PASSWORD_AUTH is enabled!{Colors.RESET}")
                return True
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', '')
            print_error(f"Failed to get app client info: {error_code} - {error_msg}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

def test_auth_flow(email: str, password: str):
    """Test if authentication flow works"""
    print(f"\n{Colors.YELLOW}Testing Authentication Flow...{Colors.RESET}")
    print("-" * 70)
    
    try:
        cognito_client = boto3.client(
            'cognito-idp',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        try:
            response = cognito_client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            print_success("Authentication flow test PASSED!")
            print_info(f"  Challenge: {response.get('ChallengeName', 'None')}")
            print_info(f"  Has tokens: {bool(response.get('AuthenticationResult'))}")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', '')
            
            if 'USER_PASSWORD_AUTH' in error_msg or 'not enabled' in error_msg.lower():
                print_error("USER_PASSWORD_AUTH flow is not enabled for this client")
                return False
            elif error_code == 'NotAuthorizedException':
                print_warning("Authentication failed (invalid credentials, but flow is enabled)")
                return True  # Flow works, just wrong credentials
            else:
                print_error(f"Authentication error: {error_code} - {error_msg}")
                return False
                
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

if __name__ == "__main__":
    config_ok = check_app_client_config()
    
    if config_ok:
        # Test with a test email (won't authenticate but will test if flow is enabled)
        test_email = "kushalsharmacse@gmail.com"
        test_password = "Test123!@#"
        test_auth_flow(test_email, test_password)
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}\n")

