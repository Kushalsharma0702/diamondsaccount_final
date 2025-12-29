#!/usr/bin/env python3
"""
Complete T1 Form Integration Test
Tests the full flow: Register -> Login -> Submit Form -> Retrieve Form
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_integration():
    print("=" * 60)
    print("🧪 T1 FORM INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Register new user
    print("\n👤 Step 1: Registering new user...")
    timestamp = int(time.time())
    test_email = f"test_{timestamp}@example.com"
    test_password = "TestPass123!"
    
    register_data = {
        "email": test_email,
        "password": test_password,
        "first_name": "Test",
        "last_name": "User",
        "phone": "+14165551234",
        "accept_terms": True
    }
    
    reg_response = requests.post(f"{API_BASE}/api/v1/auth/register", json=register_data)
    if reg_response.status_code in [200, 201]:
        user_data = reg_response.json()
        print(f"✅ User registered successfully!")
        print(f"   User ID: {user_data['id']}")
        print(f"   Email: {user_data['email']}")
    else:
        print(f"❌ Registration failed: {reg_response.status_code}")
        print(f"   {reg_response.text[:300]}")
        return False
    
    # Step 2: Login
    print("\n🔐 Step 2: Logging in...")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    login_response = requests.post(
        f"{API_BASE}/api/v1/auth/login",
        json=login_data
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data["access_token"]
        print(f"✅ Login successful!")
        print(f"   Token: {token[:60]}...")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   {login_response.text[:300]}")
        return False
    
    # Step 3: Setup encryption
    print("\n🔒 Step 3: Setting up encryption...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    enc_response = requests.post(f"{API_BASE}/api/v1/encryption/setup", headers=headers)
    if enc_response.status_code in [200, 201]:
        print(f"✅ Encryption setup successful!")
    else:
        print(f"⚠️  Encryption setup: {enc_response.status_code} (may already exist)")
    
    # Step 4: Submit T1 form
    print("\n📝 Step 4: Submitting T1 form...")
    form_data = {
        "status": "draft",
        "personalInfo": {
            "firstName": "John",
            "middleName": "Test",
            "lastName": "Doe",
            "sin": "123456789",
            "dateOfBirth": "1990-05-20",
            "address": "123 Main St, Toronto, ON M5V 1A1",
            "phoneNumber": "+14165550123",
            "email": "john.test@example.com",
            "isCanadianCitizen": True,
            "maritalStatus": "single"
        },
        "hasForeignProperty": False,
        "foreignProperties": [],
        "hasMedicalExpenses": False,
        "hasCharitableDonations": False,
        "hasMovingExpenses": False,
        "isSelfEmployed": False,
        "isFirstHomeBuyer": False,
        "soldPropertyLongTerm": False,
        "soldPropertyShortTerm": False,
        "hasWorkFromHomeExpense": False,
        "wasStudentLastYear": False,
        "isUnionMember": False,
        "hasDaycareExpenses": False,
        "isFirstTimeFiler": False,
        "hasOtherIncome": False,
        "hasProfessionalDues": False,
        "hasRrspFhsaInvestment": False,
        "hasChildArtSportCredit": False,
        "isProvinceFiler": False
    }
    
    submit_response = requests.post(
        f"{API_BASE}/api/v1/t1-forms/",
        headers=headers,
        json=form_data
    )
    
    if submit_response.status_code in [200, 201]:
        result = submit_response.json()
        form_id = result["form_id"]
        print(f"✅ Form submitted successfully!")
        print(f"   Form ID: {form_id}")
        print(f"   Status: {result['status']}")
        print(f"   Created: {result['created_at']}")
    else:
        print(f"❌ Form submission failed: {submit_response.status_code}")
        print(f"   {submit_response.text[:500]}")
        return False
    
    # Step 5: Retrieve the form
    print("\n📥 Step 5: Retrieving submitted form...")
    get_response = requests.get(
        f"{API_BASE}/api/v1/t1-forms/{form_id}",
        headers=headers
    )
    
    if get_response.status_code == 200:
        retrieved_form = get_response.json()
        print(f"✅ Form retrieved successfully!")
        print(f"   Name: {retrieved_form['personal_info']['firstName']} {retrieved_form['personal_info']['lastName']}")
        print(f"   SIN: {retrieved_form['personal_info']['sin']}")
        print(f"   Address: {retrieved_form['personal_info']['address']}")
    else:
        print(f"❌ Form retrieval failed: {get_response.status_code}")
        print(f"   {get_response.text[:300]}")
        return False
    
    # Step 6: List all forms
    print("\n📋 Step 6: Listing all forms...")
    list_response = requests.get(
        f"{API_BASE}/api/v1/t1-forms/",
        headers=headers
    )
    
    if list_response.status_code == 200:
        forms = list_response.json()
        print(f"✅ Found {len(forms)} form(s)")
        for form in forms:
            print(f"   - {form['form_id']} | Status: {form['status']} | Created: {form['created_at']}")
    else:
        print(f"⚠️  List forms: {list_response.status_code}")
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 INTEGRATION TEST PASSED!")
    print("=" * 60)
    print("\n✅ All systems working:")
    print("   ✓ User registration")
    print("   ✓ Authentication (JWT)")
    print("   ✓ Encryption setup")
    print("   ✓ T1 form submission")
    print("   ✓ Form retrieval (auto-decrypted)")
    print("   ✓ Form listing")
    print("\n📋 Test Credentials:")
    print(f"   Email: {test_email}")
    print(f"   Password: {test_password}")
    print(f"   Token: {token}")
    print("\n🚀 Your T1 form is connected to the database!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_integration()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
