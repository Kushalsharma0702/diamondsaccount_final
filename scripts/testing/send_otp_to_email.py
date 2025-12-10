#!/usr/bin/env python3
"""
Send OTP to Specific Email Address
Uses Cognito's resend_confirmation_code to send OTP to the specified email
"""

import sys
import os
import asyncio
import httpx
import random
import string

# Add client_side to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../client_side'))

from shared.cognito_service import get_cognito_service

BASE_URL = "http://localhost:8001/api/v1"
TARGET_EMAIL = "kushalsharmacse@gmail.com"

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

async def send_otp_via_cognito(email: str):
    """Send OTP using Cognito's resend_confirmation_code"""
    print_info(f"Sending OTP via Cognito to {email}...")
    
    try:
        cognito_service = get_cognito_service()
        result = await cognito_service.resend_confirmation_code(email)
        
        if result.get("success"):
            print_success("OTP sent successfully via Cognito!")
            print_info(f"Code delivery details: {result.get('code_delivery_details')}")
            return True
        else:
            print_error(f"Failed to send OTP: {result}")
            return False
    except Exception as e:
        print_error(f"Exception sending OTP via Cognito: {e}")
        return False

async def send_otp_via_api(email: str):
    """Send OTP using the API endpoint"""
    print_info(f"Requesting OTP via API for {email}...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "email": email,
            "purpose": "email_verification"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/auth/request-otp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"OTP requested via API! Response: {data}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print_error(f"OTP request failed: {error_detail}")
                return False
        except Exception as e:
            print_error(f"Exception requesting OTP via API: {e}")
            return False

async def get_developer_otp(email: str):
    """Get developer OTP if available"""
    print_info(f"Checking for developer OTP for {email}...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL.replace('/api/v1', '')}/dev/otps/{email}")
            
            if response.status_code == 200:
                data = response.json()
                developer_otp = data.get("developer_otp", "").split(" ")[0] if data.get("developer_otp") else None
                active_otps = data.get("active_otps", [])
                
                print_success("Developer OTP available!")
                print_info(f"  Developer OTP: {developer_otp}")
                if active_otps:
                    print_info(f"  Active OTPs in DB:")
                    for otp in active_otps[:3]:  # Show first 3
                        print_info(f"    - {otp.get('code')} (expires: {otp.get('expires_at')})")
                
                return developer_otp, active_otps
            else:
                print_warning("Developer OTP endpoint not available")
                return None, []
        except Exception as e:
            print_warning(f"Could not get developer OTP: {e}")
            return None, []

async def verify_otp(email: str, otp: str):
    """Verify the OTP"""
    print_info(f"Verifying OTP for {email}...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "email": email,
            "code": otp,
            "purpose": "email_verification"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/auth/verify-otp", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"OTP verified successfully! Response: {data}")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error")
                print_error(f"OTP verification failed: {error_detail}")
                return False
        except Exception as e:
            print_error(f"Exception verifying OTP: {e}")
            return False

async def main():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}Send OTP to Email Address{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    print_info(f"Target Email: {TARGET_EMAIL}\n")
    
    # Method 1: Send OTP via Cognito directly
    print(f"{Colors.YELLOW}[Method 1] Send OTP via Cognito{Colors.RESET}")
    print("-" * 70)
    cognito_success = await send_otp_via_cognito(TARGET_EMAIL)
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Method 2: Send OTP via API
    print(f"\n{Colors.YELLOW}[Method 2] Send OTP via API{Colors.RESET}")
    print("-" * 70)
    api_success = await send_otp_via_api(TARGET_EMAIL)
    
    # Wait a moment for OTP to be processed
    await asyncio.sleep(3)
    
    # Get Developer OTP (if available)
    print(f"\n{Colors.YELLOW}[Method 3] Check Developer OTP{Colors.RESET}")
    print("-" * 70)
    dev_otp, active_otps = await get_developer_otp(TARGET_EMAIL)
    
    if dev_otp:
        print_info("\nYou can use the developer OTP to verify the email.")
        print_info(f"Developer OTP: {Colors.GREEN}{dev_otp}{Colors.RESET}")
        
        # Ask if user wants to verify
        verify = input(f"\nDo you want to verify the email with OTP '{dev_otp}'? (y/n): ").strip().lower()
        if verify == 'y':
            await verify_otp(TARGET_EMAIL, dev_otp)
    else:
        print_warning("\nNo developer OTP available. Check your email for the OTP code.")
        print_warning("Or set DEVELOPMENT_MODE=true in your .env file to enable developer OTP.")
        
        # Ask for manual OTP entry (only in interactive mode)
        if cognito_success or api_success:
            try:
                otp = input("\nEnter the OTP code received in email (or press Enter to skip): ").strip()
                if otp:
                    await verify_otp(TARGET_EMAIL, otp)
            except EOFError:
                print_info("Non-interactive mode. Skipping manual OTP entry.")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}Complete{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    
    # Summary
    print(f"\n{Colors.YELLOW}Summary:{Colors.RESET}")
    print(f"  Cognito OTP Send: {'✅ Success' if cognito_success else '❌ Failed'}")
    print(f"  API OTP Send: {'✅ Success' if api_success else '❌ Failed'}")
    print(f"  Developer OTP: {'✅ Available' if dev_otp else '❌ Not available'}")

if __name__ == "__main__":
    asyncio.run(main())

