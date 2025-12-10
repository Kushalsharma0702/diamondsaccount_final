#!/usr/bin/env python3
"""
Comprehensive Cognito Authentication Test Script
Tests registration, OTP sending, OTP verification, and login flow
"""

import sys
import os
import asyncio
import httpx
from datetime import datetime

# Add client_side to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../client_side'))

BASE_URL = "http://localhost:8001/api/v1"
TEST_EMAIL = "kushalsharmacse@gmail.com"
TEST_PASSWORD = "Test123!@#"
TEST_PHONE = "+17417119014"

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

async def test_registration(client: httpx.AsyncClient, email: str, password: str, first_name: str, last_name: str, phone: str = None):
    """Test user registration with Cognito"""
    print_info(f"Testing registration for {email}...")
    
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
            data = response.json()
            print_success(f"Registration successful! Response: {data}")
            return True
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Unknown error")
            if "already registered" in error_detail.lower():
                print_warning(f"User already exists: {error_detail}")
                return "exists"
            else:
                print_error(f"Registration failed: {error_detail}")
                return False
        else:
            print_error(f"Registration failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration exception: {e}")
        return False

async def test_request_otp(client: httpx.AsyncClient, email: str, purpose: str = "email_verification"):
    """Test OTP request"""
    print_info(f"Requesting OTP for {email} (purpose: {purpose})...")
    
    payload = {
        "email": email,
        "purpose": purpose
    }
    
    try:
        response = await client.post(f"{BASE_URL}/auth/request-otp", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"OTP requested successfully! Response: {data}")
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_error(f"OTP request failed: {error_detail}")
            return False
    except Exception as e:
        print_error(f"OTP request exception: {e}")
        return False

async def test_verify_otp(client: httpx.AsyncClient, email: str, otp: str, purpose: str = "email_verification"):
    """Test OTP verification"""
    print_info(f"Verifying OTP for {email}...")
    
    payload = {
        "email": email,
        "code": otp,
        "purpose": purpose
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
        print_error(f"OTP verification exception: {e}")
        return False

async def test_login(client: httpx.AsyncClient, email: str, password: str):
    """Test user login"""
    print_info(f"Testing login for {email}...")
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = await client.post(f"{BASE_URL}/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Login successful!")
            print_info(f"  Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print_info(f"  Refresh Token: {data.get('refresh_token', 'N/A')[:50]}...")
            print_info(f"  ID Token: {data.get('id_token', 'N/A')[:50]}...")
            return data
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_error(f"Login failed: {error_detail}")
            return None
    except Exception as e:
        print_error(f"Login exception: {e}")
        return None

async def test_me_endpoint(client: httpx.AsyncClient, token: str):
    """Test authenticated endpoint"""
    print_info("Testing /auth/me endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"User info retrieved successfully!")
            print_info(f"  Email: {data.get('email')}")
            print_info(f"  Name: {data.get('first_name')} {data.get('last_name')}")
            print_info(f"  Verified: {data.get('email_verified')}")
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            print_error(f"Failed to get user info: {error_detail}")
            return False
    except Exception as e:
        print_error(f"Me endpoint exception: {e}")
        return False

async def get_developer_otp(client: httpx.AsyncClient, email: str):
    """Get developer OTP from backend (if available)"""
    print_info(f"Getting developer OTP for {email}...")
    
    try:
        response = await client.get(f"{BASE_URL.replace('/api/v1', '')}/dev/otps/{email}")
        
        if response.status_code == 200:
            data = response.json()
            developer_otp = data.get("developer_otp", "").split(" ")[0] if data.get("developer_otp") else None
            print_info(f"Developer OTP: {developer_otp}")
            return developer_otp
        else:
            print_warning("Developer OTP endpoint not available (requires DEVELOPMENT_MODE=true)")
            return None
    except Exception as e:
        print_warning(f"Could not get developer OTP: {e}")
        return None

async def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Cognito Authentication Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Registration
        print(f"\n{Colors.YELLOW}[TEST 1] Registration{Colors.RESET}")
        print("-" * 60)
        registration_result = await test_registration(
            client, TEST_EMAIL, TEST_PASSWORD, "Kushal", "Sharma", TEST_PHONE
        )
        
        if registration_result == False:
            print_error("Registration failed. Cannot continue with other tests.")
            return
        elif registration_result == "exists":
            print_info("User already exists. Proceeding with OTP tests...")
        
        # Test 2: Request OTP
        print(f"\n{Colors.YELLOW}[TEST 2] Request OTP{Colors.RESET}")
        print("-" * 60)
        otp_requested = await test_request_otp(client, TEST_EMAIL, "email_verification")
        
        if not otp_requested:
            print_warning("OTP request failed. Trying developer OTP...")
        
        # Test 3: Get Developer OTP (if available)
        print(f"\n{Colors.YELLOW}[TEST 3] Get Developer OTP{Colors.RESET}")
        print("-" * 60)
        developer_otp = await get_developer_otp(client, TEST_EMAIL)
        
        # Test 4: Verify OTP
        print(f"\n{Colors.YELLOW}[TEST 4] Verify OTP{Colors.RESET}")
        print("-" * 60)
        if developer_otp:
            print_info(f"Using developer OTP: {developer_otp}")
            otp_verified = await test_verify_otp(client, TEST_EMAIL, developer_otp, "email_verification")
        else:
            print_warning("No developer OTP available. Using default developer OTP: 123456")
            print_info("Note: Set DEVELOPMENT_MODE=true to enable developer OTP endpoint")
            otp_verified = await test_verify_otp(client, TEST_EMAIL, "123456", "email_verification")
            if not otp_verified:
                try:
                    print_warning("Default OTP failed. Please enter OTP manually:")
                    otp = input("Enter OTP code (or press Enter to skip): ").strip()
                    if otp:
                        otp_verified = await test_verify_otp(client, TEST_EMAIL, otp, "email_verification")
                except EOFError:
                    print_warning("Non-interactive mode. Skipping manual OTP entry.")
        
        if not otp_verified:
            print_warning("OTP verification failed or skipped. Attempting login anyway...")
        
        # Test 5: Login
        print(f"\n{Colors.YELLOW}[TEST 5] Login{Colors.RESET}")
        print("-" * 60)
        login_result = await test_login(client, TEST_EMAIL, TEST_PASSWORD)
        
        if login_result:
            access_token = login_result.get("access_token")
            
            # Test 6: Authenticated Endpoint
            print(f"\n{Colors.YELLOW}[TEST 6] Authenticated Endpoint (/auth/me){Colors.RESET}")
            print("-" * 60)
            await test_me_endpoint(client, access_token)
        else:
            print_error("Login failed. Cannot test authenticated endpoint.")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Test Suite Complete{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())

