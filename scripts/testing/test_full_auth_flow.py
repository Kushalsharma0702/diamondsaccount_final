#!/usr/bin/env python3
"""
Complete Authentication Flow Test
Tests: Registration → OTP Verification → Login → Authorization
"""

import sys
import os
import asyncio
import httpx
from datetime import datetime
import random
import string

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../client_side'))

BASE_URL = "http://localhost:8001/api/v1"
TEST_EMAIL = "kushalsharmacse@gmail.com"
TEST_PASSWORD = "Test123!@#"
TEST_FIRST_NAME = "Kushal"
TEST_LAST_NAME = "Sharma"
TEST_PHONE = "+17417119014"
DEV_OTP = "123456"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_step(msg):
    print(f"{Colors.CYAN}▶ {msg}{Colors.RESET}")

async def register_user(client: httpx.AsyncClient, email: str, password: str, first_name: str, last_name: str, phone: str = None):
    """Register a new user"""
    print_step(f"Registering user: {email}")
    
    payload = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "accept_terms": True
    }
    if phone:
        payload["phone"] = phone
    
    try:
        response = await client.post(f"{BASE_URL}/auth/register", json=payload)
        
        if response.status_code == 201:
            print_success("Registration successful")
            return True
        elif response.status_code == 400:
            error = response.json().get("detail", "")
            if "already registered" in error.lower():
                print_info("User already exists, proceeding...")
                return "exists"
            else:
                print_error(f"Registration failed: {error}")
                return False
        else:
            print_error(f"Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

async def request_otp(client: httpx.AsyncClient, email: str):
    """Request OTP"""
    print_step(f"Requesting OTP for: {email}")
    
    try:
        response = await client.post(f"{BASE_URL}/auth/request-otp", json={
            "email": email,
            "purpose": "email_verification"
        })
        
        if response.status_code == 200:
            print_success("OTP requested successfully")
            return True
        else:
            print_error(f"OTP request failed: {response.json().get('detail')}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

async def verify_otp(client: httpx.AsyncClient, email: str, otp: str):
    """Verify OTP"""
    print_step(f"Verifying OTP for: {email}")
    
    try:
        response = await client.post(f"{BASE_URL}/auth/verify-otp", json={
            "email": email,
            "code": otp,
            "purpose": "email_verification"
        })
        
        if response.status_code == 200:
            print_success("OTP verified successfully")
            return True
        else:
            print_error(f"OTP verification failed: {response.json().get('detail')}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

async def login_user(client: httpx.AsyncClient, email: str, password: str):
    """Login user"""
    print_step(f"Logging in user: {email}")
    
    try:
        response = await client.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login successful!")
            print_info(f"  Access Token: {data.get('access_token', '')[:50]}...")
            print_info(f"  Refresh Token: {data.get('refresh_token', '')[:50]}...")
            print_info(f"  ID Token: {bool(data.get('id_token'))}")
            return data.get('access_token')
        else:
            error = response.json().get("detail", "Unknown error")
            print_error(f"Login failed: {error}")
            
            # Check if it's a flow issue or credential issue
            if "not enabled" in error.lower() or "USER_PASSWORD_AUTH" in error:
                print_error("\n⚠️  USER_PASSWORD_AUTH flow is NOT enabled in Cognito!")
                print_info("Please enable 'Sign in with username and password' in Cognito console")
            elif "not verified" in error.lower() or "not confirmed" in error.lower():
                print_info("User email not verified. Verify OTP first.")
            elif "invalid" in error.lower() or "not found" in error.lower():
                print_info("Credentials might be incorrect, or user needs to register/verify first")
            
            return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None

async def test_authorized_endpoint(client: httpx.AsyncClient, token: str):
    """Test an authorized endpoint"""
    print_step("Testing authorized endpoint (/auth/me)")
    
    try:
        response = await client.get(f"{BASE_URL}/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            data = response.json()
            print_success("Authorized endpoint access successful!")
            print_info(f"  Email: {data.get('email')}")
            print_info(f"  Name: {data.get('first_name')} {data.get('last_name')}")
            print_info(f"  Verified: {data.get('email_verified')}")
            return True
        else:
            print_error(f"Authorization failed: {response.json().get('detail')}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

async def main():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}Complete Authentication & Authorization Flow Test{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    
    print_info(f"Test Email: {TEST_EMAIL}")
    print_info(f"Test Password: {TEST_PASSWORD}\n")
    
    results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Register (if needed)
        print(f"{Colors.YELLOW}[Step 1/5] Registration{Colors.RESET}")
        print("-" * 70)
        reg_result = await register_user(client, TEST_EMAIL, TEST_PASSWORD, TEST_FIRST_NAME, TEST_LAST_NAME, TEST_PHONE)
        results['registration'] = reg_result
        await asyncio.sleep(2)
        
        # Step 2: Request OTP
        print(f"\n{Colors.YELLOW}[Step 2/5] Request OTP{Colors.RESET}")
        print("-" * 70)
        otp_request = await request_otp(client, TEST_EMAIL)
        results['otp_request'] = otp_request
        await asyncio.sleep(2)
        
        # Step 3: Verify OTP
        print(f"\n{Colors.YELLOW}[Step 3/5] Verify OTP{Colors.RESET}")
        print("-" * 70)
        print_info(f"Using developer OTP: {DEV_OTP}")
        otp_verify = await verify_otp(client, TEST_EMAIL, DEV_OTP)
        results['otp_verify'] = otp_verify
        await asyncio.sleep(2)
        
        # Step 4: Login
        print(f"\n{Colors.YELLOW}[Step 4/5] Login{Colors.RESET}")
        print("-" * 70)
        access_token = await login_user(client, TEST_EMAIL, TEST_PASSWORD)
        results['login'] = access_token is not None
        await asyncio.sleep(1)
        
        # Step 5: Test Authorization
        if access_token:
            print(f"\n{Colors.YELLOW}[Step 5/5] Authorization Test{Colors.RESET}")
            print("-" * 70)
            results['authorization'] = await test_authorized_endpoint(client, access_token)
        else:
            print(f"\n{Colors.YELLOW}[Step 5/5] Authorization Test{Colors.RESET}")
            print("-" * 70)
            print_error("Skipped (login failed)")
            results['authorization'] = False
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"  Registration:    {'✅ PASS' if results.get('registration') else '❌ FAIL'}")
    print(f"  OTP Request:     {'✅ PASS' if results.get('otp_request') else '❌ FAIL'}")
    print(f"  OTP Verify:      {'✅ PASS' if results.get('otp_verify') else '❌ FAIL'}")
    print(f"  Login:           {'✅ PASS' if results.get('login') else '❌ FAIL'}")
    print(f"  Authorization:   {'✅ PASS' if results.get('authorization') else '❌ FAIL'}")
    
    all_passed = all([r for r in results.values() if isinstance(r, bool)])
    print(f"\n{Colors.GREEN if all_passed else Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.GREEN if all_passed else Colors.RED}{'ALL TESTS PASSED ✅' if all_passed else 'SOME TESTS FAILED ❌'}{Colors.RESET}")
    print(f"{Colors.GREEN if all_passed else Colors.RED}{'='*70}{Colors.RESET}\n")
    
    # Next steps
    if not results.get('login'):
        print(f"{Colors.YELLOW}⚠️  Next Steps:{Colors.RESET}")
        print("  1. Verify USER_PASSWORD_AUTH is enabled in Cognito console")
        print("  2. Check that email is verified in Cognito")
        print("  3. Verify password matches in Cognito user pool")
        print(f"  4. See: {Colors.CYAN}scripts/testing/COGNITO_CHECKLIST.md{Colors.RESET} for details")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))

