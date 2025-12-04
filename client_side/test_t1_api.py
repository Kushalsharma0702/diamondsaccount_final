#!/usr/bin/env python3
"""
Test script for T1 Enhanced Tax Form API
Tests all endpoints with comprehensive form data
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_{int(datetime.now().timestamp())}@example.com"
TEST_PASSWORD = "SecureTestPass123!"
ENCRYPTION_PASSWORD = "T1TestPassword123!"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

# Test data
def get_sample_t1_form():
    """Get sample T1 form data matching the JSON schema"""
    return {
        "status": "draft",
        "personalInfo": {
            "firstName": "Jane",
            "middleName": "Q",
            "lastName": "Doe",
            "sin": "123456789",
            "dateOfBirth": "1990-05-20",
            "address": "123 Main St, Toronto, ON",
            "phoneNumber": "+14165550123",
            "email": TEST_EMAIL,
            "isCanadianCitizen": True,
            "maritalStatus": "married",
            "spouseInfo": {
                "firstName": "John",
                "lastName": "Doe",
                "sin": "987654321",
                "dateOfBirth": "1989-09-09"
            },
            "children": [
                {
                    "firstName": "Kid",
                    "lastName": "Doe",
                    "sin": "001122334",
                    "dateOfBirth": "2018-03-15"
                }
            ]
        },
        "hasForeignProperty": True,
        "foreignProperties": [
            {
                "investmentDetails": "US ETF",
                "grossIncome": 1200.5,
                "gainLossOnSale": 100.0,
                "maxCostDuringYear": 12000.0,
                "costAmountYearEnd": 11500.0,
                "country": "US"
            }
        ],
        "hasMedicalExpenses": True,
        "hasCharitableDonations": True,
        "hasMovingExpenses": True,
        "movingExpenseForIndividual": True,
        "movingExpenseForSpouse": False,
        "movingExpenseIndividual": {
            "individual": "Jane Doe",
            "oldAddress": "Old Address",
            "newAddress": "New Address",
            "distanceFromOldToNew": "550 km",
            "distanceFromNewToOffice": "12 km",
            "airTicketCost": 350.75,
            "moversAndPackers": 800.0,
            "mealsAndOtherCost": 120.0,
            "anyOtherCost": 0.0,
            "dateOfTravel": "2024-06-01",
            "dateOfJoining": "2024-06-15",
            "companyName": "NewCo Inc.",
            "newEmployerAddress": "456 King St",
            "grossIncomeAfterMoving": 65000.0
        },
        "isSelfEmployed": True,
        "selfEmployment": {
            "businessTypes": ["general"],
            "generalBusiness": {
                "clientName": "Jane Doe",
                "businessName": "JD Consulting",
                "salesCommissionsFees": 50000.0,
                "minusHstCollected": 6500.0,
                "advertising": 500.0,
                "mealsEntertainment": 300.0,
                "insurance": 250.0,
                "officeExpenses": 900.0,
                "supplies": 400.0,
                "legalAccountingFees": 700.0,
                "travel": 600.0,
                "telephoneUtilities": 720.0,
                "areaOfHomeForBusiness": "200 sqft",
                "totalAreaOfHome": "1000 sqft",
                "heat": 200.0,
                "electricity": 300.0,
                "houseInsurance": 350.0,
                "homeMaintenance": 150.0,
                "houseRent": 18000.0,
                "kmDrivenForBusiness": 1200.0,
                "totalKmDrivenInYear": 8000.0
            }
        },
        "isFirstHomeBuyer": True,
        "hasWorkFromHomeExpense": True,
        "wasStudentLastYear": True,
        "isFirstTimeFiler": True,
        "hasRrspFhsaInvestment": True
    }

def test_user_registration():
    """Test 1: Register a new user"""
    print_info("Test 1: Registering new user...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "first_name": "Test",
            "last_name": "User",
            "phone": "+14165550100",
            "accept_terms": True
        }
    )
    
    if response.status_code == 201:
        print_success(f"User registered: {TEST_EMAIL}")
        return True
    else:
        print_error(f"Registration failed: {response.text}")
        return False

def test_user_login():
    """Test 2: Login and get JWT token"""
    print_info("Test 2: Logging in...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print_success(f"Login successful! Token: {token[:20]}...")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        return None

def test_encryption_setup(token):
    """Test 3: Setup encryption for the user"""
    print_info("Test 3: Setting up encryption...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/encryption/setup",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": ENCRYPTION_PASSWORD}
    )
    
    if response.status_code == 200:
        print_success("Encryption setup complete!")
        return True
    else:
        print_error(f"Encryption setup failed: {response.text}")
        return False

def test_create_t1_form(token):
    """Test 4: Create comprehensive T1 form"""
    print_info("Test 4: Creating T1 form...")
    
    form_data = get_sample_t1_form()
    
    response = requests.post(
        f"{BASE_URL}/api/v1/t1-forms/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=form_data
    )
    
    if response.status_code == 201:
        data = response.json()
        form_id = data.get("id")
        print_success(f"T1 form created! ID: {form_id}")
        print_info(f"Form status: {data.get('status')}")
        print_info(f"Encrypted: {data.get('is_encrypted')}")
        return form_id
    else:
        print_error(f"Form creation failed: {response.text}")
        return None

def test_list_t1_forms(token):
    """Test 5: List all T1 forms"""
    print_info("Test 5: Listing T1 forms...")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/t1-forms/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        total = data.get("total", 0)
        print_success(f"Found {total} T1 form(s)")
        return True
    else:
        print_error(f"List forms failed: {response.text}")
        return False

def test_get_t1_form(token, form_id):
    """Test 6: Get specific T1 form"""
    print_info(f"Test 6: Getting T1 form {form_id}...")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/t1-forms/{form_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved form: {data.get('id')}")
        print_info(f"Name: {data.get('personalInfo', {}).get('firstName')} {data.get('personalInfo', {}).get('lastName')}")
        print_info(f"Has foreign property: {data.get('hasForeignProperty')}")
        print_info(f"Self-employed: {data.get('isSelfEmployed')}")
        return True
    else:
        print_error(f"Get form failed: {response.text}")
        return False

def test_update_t1_form(token, form_id):
    """Test 7: Update T1 form"""
    print_info(f"Test 7: Updating T1 form {form_id}...")
    
    update_data = {
        "status": "submitted",
        "hasCharitableDonations": False
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/t1-forms/{form_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=update_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Form updated! New status: {data.get('status')}")
        return True
    else:
        print_error(f"Update form failed: {response.text}")
        return False

def test_schema_validation(token):
    """Test 8: Verify schema validation"""
    print_info("Test 8: Testing schema validation...")
    
    # Test with invalid SIN (not 9 digits)
    invalid_form = get_sample_t1_form()
    invalid_form["personalInfo"]["sin"] = "12345"  # Invalid - not 9 digits
    
    response = requests.post(
        f"{BASE_URL}/api/v1/t1-forms/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=invalid_form
    )
    
    if response.status_code == 422:
        print_success("Schema validation working - rejected invalid SIN")
        return True
    else:
        print_warning(f"Expected validation error, got: {response.status_code}")
        return False

def test_delete_t1_form(token, form_id):
    """Test 9: Delete T1 form"""
    print_info(f"Test 9: Deleting T1 form {form_id}...")
    
    response = requests.delete(
        f"{BASE_URL}/api/v1/t1-forms/{form_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print_success("Form deleted successfully")
        return True
    else:
        print_error(f"Delete form failed: {response.text}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*60)
    print("T1 ENHANCED FORM API - COMPREHENSIVE TEST SUITE")
    print("="*60 + "\n")
    
    # Test 1: Register
    if not test_user_registration():
        print_error("Test suite failed at registration")
        return
    
    print()
    
    # Test 2: Login
    token = test_user_login()
    if not token:
        print_error("Test suite failed at login")
        return
    
    print()
    
    # Test 3: Setup encryption
    if not test_encryption_setup(token):
        print_error("Test suite failed at encryption setup")
        return
    
    print()
    
    # Test 4: Create T1 form
    form_id = test_create_t1_form(token)
    if not form_id:
        print_error("Test suite failed at form creation")
        return
    
    print()
    
    # Test 5: List forms
    test_list_t1_forms(token)
    print()
    
    # Test 6: Get form
    test_get_t1_form(token, form_id)
    print()
    
    # Test 7: Update form
    test_update_t1_form(token, form_id)
    print()
    
    # Test 8: Schema validation
    test_schema_validation(token)
    print()
    
    # Test 9: Delete form
    test_delete_t1_form(token, form_id)
    
    print("\n" + "="*60)
    print_success("ALL TESTS COMPLETED!")
    print("="*60 + "\n")
    
    print(f"{Colors.BLUE}API Documentation:{Colors.END} {BASE_URL}/docs")
    print(f"{Colors.BLUE}Test Email:{Colors.END} {TEST_EMAIL}")
    print(f"{Colors.BLUE}Your JWT Token:{Colors.END} {token[:30]}...\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
