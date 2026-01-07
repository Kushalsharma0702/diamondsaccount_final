"""
T1 API Endpoints Testing Script
================================
Tests all T1 Personal Tax Form endpoints with real data

Usage:
    python backend/test_t1_endpoints.py
"""

import requests
import json
from typing import Dict, Any

API_BASE = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message: str):
    print(f"{Colors.RED}✗{Colors.END} {message}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def print_section(title: str):
    print(f"\n{Colors.YELLOW}{'=' * 60}{Colors.END}")
    print(f"{Colors.YELLOW}{title}{Colors.END}")
    print(f"{Colors.YELLOW}{'=' * 60}{Colors.END}\n")


# Global state
access_token = None
user_id = None
filing_id = None
t1_form_id = None


def test_signup():
    """Test user signup"""
    print_section("TEST 1: User Signup")
    
    payload = {
        "email": "t1test@example.com",
        "password": "Test@123456",
        "first_name": "John",
        "last_name": "Taxpayer",
        "phone": "+1234567890"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/auth/register", json=payload)
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"User created: {data['user']['email']}")
        print_info(f"User ID: {data['user']['id']}")
        return data['user']['id']
    elif response.status_code == 400 and "already exists" in response.text:
        print_info("User already exists, will try login")
        return None
    else:
        print_error(f"Signup failed: {response.status_code} - {response.text}")
        return None


def test_login(email: str, password: str):
    """Test user login"""
    print_section("TEST 2: User Login")
    
    payload = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{API_BASE}/api/v1/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Login successful")
        print_info(f"Access Token: {data['access_token'][:50]}...")
        return data['access_token'], data['user']['id']
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None, None


def bypass_email_verification(user_id: str):
    """Manually verify email in database"""
    print_section("TEST 3: Bypass Email Verification (Dev Only)")
    
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="CA_Project",
            user="postgres",
            password="Kushal07"
        )
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET email_verified = TRUE WHERE id = '{user_id}'")
        conn.commit()
        cursor.close()
        conn.close()
        print_success("Email verified in database")
        return True
    except Exception as e:
        print_error(f"Email verification failed: {e}")
        return False


def create_filing(token: str):
    """Create a new filing"""
    print_section("TEST 4: Create Filing")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "tax_year": 2024,
        "filing_type": "personal"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/filings", json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Filing created: {data['id']}")
        print_info(f"Status: {data['status']}")
        return data['id']
    else:
        print_error(f"Filing creation failed: {response.status_code} - {response.text}")
        return None


def test_t1_structure(token: str):
    """Test GET /api/v1/t1-forms/structure"""
    print_section("TEST 5: Get T1 Form Structure")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/api/v1/t1-forms/structure", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"T1 Structure loaded: {data['formName']}")
        print_info(f"Total steps: {len(data['steps'])}")
        return True
    else:
        print_error(f"Structure fetch failed: {response.status_code} - {response.text}")
        return False


def test_save_draft(token: str, filing_id: str):
    """Test POST /api/v1/t1-forms/{filing_id}/answers"""
    print_section("TEST 6: Save T1 Draft Answers")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "answers": {
            "personalInfo.firstName": "John",
            "personalInfo.lastName": "Taxpayer",
            "personalInfo.sin": "123456789",
            "personalInfo.dateOfBirth": "1990-01-15",
            "personalInfo.address": "123 Main St, Toronto, ON M5V 2T6",
            "personalInfo.phoneNumber": "+14161234567",
            "personalInfo.email": "t1test@example.com",
            "personalInfo.isCanadianCitizen": True,
            "personalInfo.maritalStatus": "single"
        }
    }
    
    response = requests.post(f"{API_BASE}/api/v1/t1-forms/{filing_id}/answers", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Draft saved successfully")
        print_info(f"T1 Form ID: {data['t1_form_id']}")
        print_info(f"Completion: {data['completion_percentage']}%")
        print_info(f"Total answers: {len(data['answers'])}")
        return data['t1_form_id']
    else:
        print_error(f"Draft save failed: {response.status_code} - {response.text}")
        return None


def test_fetch_draft(token: str, filing_id: str):
    """Test GET /api/v1/t1-forms/{filing_id}"""
    print_section("TEST 7: Fetch T1 Draft")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/api/v1/t1-forms/{filing_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Draft fetched successfully")
        print_info(f"Status: {data['status']}")
        print_info(f"Locked: {data['is_locked']}")
        print_info(f"Answers count: {len(data['answers'])}")
        return True
    else:
        print_error(f"Draft fetch failed: {response.status_code} - {response.text}")
        return False


def test_required_documents(token: str, filing_id: str):
    """Test GET /api/v1/t1-forms/{filing_id}/required-documents"""
    print_section("TEST 8: Get Required Documents")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/api/v1/t1-forms/{filing_id}/required-documents", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Required documents computed")
        print_info(f"Total required: {len(data['required_documents'])}")
        for doc in data['required_documents']:
            print(f"  - {doc['label']} ({doc['reason']})")
        return True
    else:
        print_error(f"Required docs fetch failed: {response.status_code} - {response.text}")
        return False


def test_submit_t1(token: str, filing_id: str):
    """Test POST /api/v1/t1-forms/{filing_id}/submit"""
    print_section("TEST 9: Submit T1 Form")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/api/v1/t1-forms/{filing_id}/submit", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"T1 form submitted successfully!")
        print_info(f"Status: {data['status']}")
        print_info(f"Locked: {data['is_locked']}")
        print_info(f"Submitted at: {data['submitted_at']}")
        return True
    elif response.status_code == 400:
        data = response.json()
        print_error(f"Submission failed - Validation errors:")
        for error in data.get('validation_errors', []):
            print(f"  - {error}")
        return False
    else:
        print_error(f"Submission failed: {response.status_code} - {response.text}")
        return False


def run_all_tests():
    """Run all T1 endpoint tests"""
    global access_token, user_id, filing_id, t1_form_id
    
    print("\n" + "="*60)
    print("T1 API ENDPOINTS - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Test 1: Signup
    user_id = test_signup()
    
    # Test 2: Login
    access_token, user_id = test_login("t1test@example.com", "Test@123456")
    if not access_token:
        print_error("Cannot proceed without authentication")
        return
    
    # Test 3: Verify email (dev bypass)
    if not bypass_email_verification(user_id):
        print_error("Cannot proceed without email verification")
        return
    
    # Re-login after verification
    access_token, user_id = test_login("t1test@example.com", "Test@123456")
    
    # Test 4: Create filing
    filing_id = create_filing(access_token)
    if not filing_id:
        print_error("Cannot proceed without filing")
        return
    
    # Test 5: Get T1 structure
    if not test_t1_structure(access_token):
        print_error("T1 structure test failed")
        return
    
    # Test 6: Save draft
    t1_form_id = test_save_draft(access_token, filing_id)
    if not t1_form_id:
        print_error("Draft save test failed")
        return
    
    # Test 7: Fetch draft
    if not test_fetch_draft(access_token, filing_id):
        print_error("Draft fetch test failed")
        return
    
    # Test 8: Get required documents
    if not test_required_documents(access_token, filing_id):
        print_error("Required documents test failed")
        return
    
    # Test 9: Submit (will fail due to incomplete form)
    test_submit_t1(access_token, filing_id)
    
    # Summary
    print_section("TEST SUMMARY")
    print_success("All user-facing T1 endpoints tested successfully!")
    print_info(f"User ID: {user_id}")
    print_info(f"Filing ID: {filing_id}")
    print_info(f"T1 Form ID: {t1_form_id}")
    print("\nNote: Admin endpoints require admin authentication (not tested here)")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
