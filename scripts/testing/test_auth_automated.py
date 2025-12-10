#!/usr/bin/env python3
"""
Automated Cognito Authentication Test
Runs all tests without user interaction
"""

import sys
import os
import asyncio
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../client_side'))

BASE_URL = "http://localhost:8001/api/v1"
TEST_EMAIL = "kushalsharmacse@gmail.com"
TEST_PASSWORD = "Test123!@#"
DEV_OTP = "123456"

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

async def test_request_otp(client: httpx.AsyncClient, email: str):
    """Test OTP request"""
    print_info(f"Requesting OTP for {email}...")
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

async def test_verify_otp(client: httpx.AsyncClient, email: str, otp: str):
    """Test OTP verification"""
    print_info(f"Verifying OTP for {email}...")
    try:
        response = await client.post(f"{BASE_URL}/auth/verify-otp", json={
            "email": email,
            "code": otp,
            "purpose": "email_verification"
        })
        if response.status_code == 200:
            print_success(f"OTP verified successfully!")
            return True
        else:
            print_error(f"OTP verification failed: {response.json().get('detail')}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

async def test_login(client: httpx.AsyncClient, email: str, password: str):
    """Test login"""
    print_info(f"Testing login for {email}...")
    try:
        response = await client.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            print_success("Login successful!")
            print_info(f"  Has Access Token: {bool(data.get('access_token'))}")
            print_info(f"  Has Refresh Token: {bool(data.get('refresh_token'))}")
            print_info(f"  Has ID Token: {bool(data.get('id_token'))}")
            return data.get('access_token')
        else:
            print_error(f"Login failed: {response.json().get('detail')}")
            return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None

async def test_me_endpoint(client: httpx.AsyncClient, token: str):
    """Test authenticated endpoint"""
    print_info("Testing /auth/me endpoint...")
    try:
        response = await client.get(f"{BASE_URL}/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        if response.status_code == 200:
            data = response.json()
            print_success("User info retrieved successfully!")
            print_info(f"  Email: {data.get('email')}")
            print_info(f"  Verified: {data.get('email_verified')}")
            return True
        else:
            print_error(f"Failed: {response.json().get('detail')}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

async def main():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}Automated Cognito Authentication Test{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    
    results = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Request OTP
        print(f"{Colors.YELLOW}[1/4] Request OTP{Colors.RESET}")
        print("-" * 70)
        results['otp_request'] = await test_request_otp(client, TEST_EMAIL)
        await asyncio.sleep(2)
        
        # Test 2: Verify OTP
        print(f"\n{Colors.YELLOW}[2/4] Verify OTP (using developer OTP: {DEV_OTP}){Colors.RESET}")
        print("-" * 70)
        results['otp_verify'] = await test_verify_otp(client, TEST_EMAIL, DEV_OTP)
        await asyncio.sleep(1)
        
        # Test 3: Login
        print(f"\n{Colors.YELLOW}[3/4] Login{Colors.RESET}")
        print("-" * 70)
        access_token = await test_login(client, TEST_EMAIL, TEST_PASSWORD)
        results['login'] = access_token is not None
        await asyncio.sleep(1)
        
        # Test 4: Authenticated Endpoint
        if access_token:
            print(f"\n{Colors.YELLOW}[4/4] Authenticated Endpoint{Colors.RESET}")
            print("-" * 70)
            results['me'] = await test_me_endpoint(client, access_token)
        else:
            print(f"\n{Colors.YELLOW}[4/4] Authenticated Endpoint{Colors.RESET}")
            print("-" * 70)
            print_error("Skipped (login failed)")
            results['me'] = False
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"  OTP Request:  {'✅ PASS' if results.get('otp_request') else '❌ FAIL'}")
    print(f"  OTP Verify:   {'✅ PASS' if results.get('otp_verify') else '❌ FAIL'}")
    print(f"  Login:        {'✅ PASS' if results.get('login') else '❌ FAIL'}")
    print(f"  Auth Endpoint:{'✅ PASS' if results.get('me') else '❌ FAIL'}")
    
    all_passed = all(results.values())
    print(f"\n{Colors.GREEN if all_passed else Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.GREEN if all_passed else Colors.RED}{'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}{Colors.RESET}")
    print(f"{Colors.GREEN if all_passed else Colors.RED}{'='*70}{Colors.RESET}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))


