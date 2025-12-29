#!/usr/bin/env python3
"""
Step-by-Step Test: Signup → Login → Fill Form → Verify Database After Each Step
"""
import requests
import json
from datetime import datetime
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_URL = "http://localhost:8001/api/v1"

# Load database credentials for verification
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "CA_Project")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Test data
test_email = f"step_test_{int(datetime.now().timestamp())}@example.com"
test_password = "TestPass123!"
test_first_name = "John"
test_last_name = "Doe"
test_phone = "+1-555-123-4567"

print("=" * 80)
print("STEP-BY-STEP TEST: Signup → Login → Fill Form → Verify Database")
print("=" * 80)
print(f"Test Email: {test_email}")
print(f"Base URL: {BASE_URL}\n")

# ============================================================================
# STEP 1: SIGNUP
# ============================================================================
print("=" * 80)
print("STEP 1: USER SIGNUP")
print("=" * 80)

signup_payload = {
    "email": test_email,
    "first_name": test_first_name,
    "last_name": test_last_name,
    "phone": test_phone,
    "password": test_password,
    "confirm_password": test_password
}

print(f"\n📤 Sending signup request...")
print(f"   Email: {test_email}")
print(f"   Name: {test_first_name} {test_last_name}")

try:
    response = requests.post(f"{BASE_URL}/auth/register", json=signup_payload, timeout=10)
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 201:
        user_data = response.json()
        print(f"✅ Signup Successful!")
        print(f"   User ID: {user_data.get('id')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
        user_id = user_data.get('id')
    else:
        print(f"❌ Signup Failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Verify in database
print(f"\n🔍 Verifying in database (users table)...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, email, first_name, last_name, phone, password_hash, 
                   email_verified, is_active, created_at
            FROM users
            WHERE email = :email
        """), {"email": test_email})
        
        row = result.fetchone()
        if row:
            print(f"✅ User found in database:")
            print(f"   ID: {row[0]}")
            print(f"   Email: {row[1]}")
            print(f"   Name: {row[2]} {row[3]}")
            print(f"   Phone: {row[4]}")
            print(f"   Password Hash: {'✅ Set' if row[5] else '❌ Missing'}")
            print(f"   Email Verified: {row[6]}")
            print(f"   Is Active: {row[7]}")
            print(f"   Created At: {row[8]}")
            db_user_id = str(row[0])
        else:
            print(f"❌ User NOT found in database!")
            exit(1)
except Exception as e:
    print(f"❌ Database verification error: {e}")
    exit(1)

print(f"\n✅ STEP 1 COMPLETE: User registered and verified in database")
time.sleep(2)

# ============================================================================
# STEP 2: LOGIN
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: USER LOGIN")
print("=" * 80)

login_payload = {
    "email": test_email,
    "password": test_password
}

print(f"\n📤 Sending login request...")
print(f"   Email: {test_email}")

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ Login Successful!")
        print(f"   Access Token: {token_data.get('access_token')[:50]}...")
        print(f"   Token Type: {token_data.get('token_type')}")
        print(f"   Expires In: {token_data.get('expires_in')} seconds")
        access_token = token_data.get('access_token')
    else:
        print(f"❌ Login Failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Verify login didn't create new records (should use existing user)
print(f"\n🔍 Verifying user still exists in database...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM users
            WHERE email = :email
        """), {"email": test_email})
        
        count = result.fetchone()[0]
        if count == 1:
            print(f"✅ User count correct: {count} (no duplicates)")
        else:
            print(f"⚠️  Unexpected user count: {count}")
except Exception as e:
    print(f"❌ Database verification error: {e}")

print(f"\n✅ STEP 2 COMPLETE: User logged in successfully")
time.sleep(2)

# ============================================================================
# STEP 3: CREATE CLIENT RECORD
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: CREATE CLIENT RECORD")
print("=" * 80)

client_payload = {
    "email": test_email,
    "first_name": test_first_name,
    "last_name": test_last_name,
    "phone": test_phone,
    "filing_year": 2023
}

print(f"\n📤 Sending client creation request...")

try:
    response = requests.post(f"{BASE_URL}/client/add", json=client_payload, timeout=10)
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        client_data = response.json()
        print(f"✅ Client Created!")
        print(f"   Client ID: {client_data.get('id')}")
        print(f"   Name: {client_data.get('name')}")
        print(f"   Email: {client_data.get('email')}")
        print(f"   Filing Year: {client_data.get('filing_year')}")
        print(f"   Status: {client_data.get('status')}")
        client_id = client_data.get('id')
    else:
        print(f"❌ Client Creation Failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Verify in database
print(f"\n🔍 Verifying in database (clients table)...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT c.id, c.user_id, c.name, c.email, c.phone, c.filing_year,
                   c.status, c.payment_status, c.created_at, u.email as user_email
            FROM clients c
            JOIN users u ON c.user_id = u.id
            WHERE c.email = :email AND c.filing_year = 2023
        """), {"email": test_email})
        
        row = result.fetchone()
        if row:
            print(f"✅ Client found in database:")
            print(f"   Client ID: {row[0]}")
            print(f"   User ID: {row[1]}")
            print(f"   Name: {row[2]}")
            print(f"   Email: {row[3]}")
            print(f"   Phone: {row[4]}")
            print(f"   Filing Year: {row[5]}")
            print(f"   Status: {row[6]}")
            print(f"   Payment Status: {row[7]}")
            print(f"   Created At: {row[8]}")
            print(f"   Linked User Email: {row[9]}")
            db_client_id = str(row[0])
        else:
            print(f"❌ Client NOT found in database!")
            exit(1)
except Exception as e:
    print(f"❌ Database verification error: {e}")
    exit(1)

print(f"\n✅ STEP 3 COMPLETE: Client record created and verified in database")
time.sleep(2)

# ============================================================================
# STEP 4: FILL T1 FORM
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: FILL T1 FORM")
print("=" * 80)

t1_form_data = {
    "status": "draft",
    "filingYear": 2023,
    "personalInfo": {
        "firstName": test_first_name,
        "middleName": "Michael",
        "lastName": test_last_name,
        "sin": "123456789",
        "dateOfBirth": "1990-05-15",
        "address": "123 Main Street, Toronto, ON M5H 2N2",
        "phoneNumber": test_phone,
        "email": test_email,
        "isCanadianCitizen": True,
        "maritalStatus": "married",
        "spouseInfo": {
            "firstName": "Jane",
            "lastName": "Doe",
            "sin": "987654321",
            "dateOfBirth": "1992-08-20"
        },
        "children": [
            {
                "firstName": "Alice",
                "lastName": "Doe",
                "sin": "111222333",
                "dateOfBirth": "2015-03-10"
            }
        ]
    },
    "hasForeignProperty": True,
    "hasMedicalExpenses": True,
    "hasWorkFromHomeExpense": True,
    "foreignProperty": [
        {
            "investmentDetails": "US Stocks",
            "grossIncome": 5000.00,
            "gainLossOnSale": 1200.00,
            "maximumCostDuringTheYear": 50000.00,
            "costAmountAtTheYearEnd": 45000.00,
            "country": "USA"
        }
    ],
    "medicalExpenses": [
        {
            "paymentDate": "2023-03-15",
            "patientName": f"{test_first_name} {test_last_name}",
            "paymentMadeTo": "Toronto General Hospital",
            "descriptionOfExpense": "Dental surgery",
            "insuranceCovered": 500.00,
            "amountPaidFromPocket": 1200.00
        }
    ],
    "workFromHomeExpense": {
        "totalHouseArea": 2000.0,
        "totalWorkArea": 200.0,
        "rentExpense": 0.0,
        "mortgageExpense": 15000.00,
        "wifiExpense": 600.00,
        "electricityExpense": 1200.00,
        "waterExpense": 400.00,
        "heatExpense": 1800.00,
        "totalInsuranceExpense": 1200.00
    },
    "selfEmployment": {
        "businessTypes": ["uber"],
        "uberBusiness": {
            "income": 35000.00,
            "totalKmDrivenEntireYear": 20000.0,
            "gas": 3000.00,
            "insuranceOnVehicle": 2400.00,
            "oilChangeAndMaintenance": 800.00
        }
    }
}

print(f"\n📤 Sending T1 form submission...")
print(f"   Form contains:")
print(f"     - Personal Info: {t1_form_data['personalInfo']['firstName']} {t1_form_data['personalInfo']['lastName']}")
print(f"     - Spouse: {t1_form_data['personalInfo']['spouseInfo']['firstName']}")
print(f"     - Children: {len(t1_form_data['personalInfo']['children'])}")
print(f"     - Foreign Property: {len(t1_form_data['foreignProperty'])} items")
print(f"     - Medical Expenses: {len(t1_form_data['medicalExpenses'])} items")
print(f"     - Self Employment: {t1_form_data['selfEmployment']['businessTypes']}")

try:
    payload = {"formData": t1_form_data}
    response = requests.post(
        f"{BASE_URL}/client/tax-return",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ T1 Form Submitted Successfully!")
        print(f"   T1 Return ID: {result.get('id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Filing Year: {result.get('filing_year')}")
        print(f"   Created At: {result.get('created_at')}")
        t1_return_id = result.get('id')
    else:
        print(f"❌ T1 Form Submission Failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Verify in database
print(f"\n🔍 Verifying in database (t1_returns_flat table)...")
try:
    with engine.connect() as conn:
        # Check flat columns
        result = conn.execute(text("""
            SELECT id, client_id, filing_year, status,
                   first_name, last_name, email, sin,
                   has_foreign_property, has_medical_expenses, has_self_employment,
                   foreign_property_count, medical_expense_count,
                   self_employment_type, uber_income,
                   form_data IS NOT NULL as has_form_data,
                   created_at
            FROM t1_returns_flat
            WHERE client_id = :client_id AND filing_year = 2023
        """), {"client_id": db_client_id})
        
        row = result.fetchone()
        if row:
            print(f"✅ T1 Return found in database:")
            print(f"   T1 Return ID: {row[0]}")
            print(f"   Client ID: {row[1]}")
            print(f"   Filing Year: {row[2]}")
            print(f"   Status: {row[3]}")
            print(f"\n   Personal Info (flat columns):")
            print(f"     Name: {row[4]} {row[5]}")
            print(f"     Email: {row[6]}")
            print(f"     SIN: {row[7]}")
            print(f"\n   Questionnaire Flags:")
            print(f"     Has Foreign Property: {row[8]}")
            print(f"     Has Medical Expenses: {row[9]}")
            print(f"     Has Self Employment: {row[10]}")
            print(f"\n   Aggregated Data:")
            print(f"     Foreign Property Count: {row[11]}")
            print(f"     Medical Expense Count: {row[12]}")
            print(f"     Self Employment Type: {row[13]}")
            print(f"     Uber Income: ${row[14]:,.2f}" if row[14] else "     Uber Income: N/A")
            print(f"\n   JSONB Form Data: {'✅ Stored' if row[15] else '❌ Missing'}")
            print(f"   Created At: {row[16]}")
            
            # Verify JSONB content
            result2 = conn.execute(text("""
                SELECT form_data
                FROM t1_returns_flat
                WHERE id = :id
            """), {"id": row[0]})
            
            json_row = result2.fetchone()
            if json_row and json_row[0]:
                form_data_json = json_row[0]
                print(f"\n   JSONB Content Verified:")
                print(f"     Personal Info First Name: {form_data_json.get('personalInfo', {}).get('firstName')}")
                print(f"     Personal Info Last Name: {form_data_json.get('personalInfo', {}).get('lastName')}")
                print(f"     Foreign Property Items: {len(form_data_json.get('foreignProperty', []))}")
                print(f"     Medical Expenses Items: {len(form_data_json.get('medicalExpenses', []))}")
                print(f"     Self Employment Types: {form_data_json.get('selfEmployment', {}).get('businessTypes', [])}")
        else:
            print(f"❌ T1 Return NOT found in database!")
            exit(1)
except Exception as e:
    print(f"❌ Database verification error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"\n✅ STEP 4 COMPLETE: T1 form filled and verified in database")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("FINAL SUMMARY - ALL STEPS COMPLETED")
print("=" * 80)

print(f"\n✅ Step 1: User Signup")
print(f"   → User created in 'users' table")
print(f"   → Email: {test_email}")

print(f"\n✅ Step 2: User Login")
print(f"   → Login successful")
print(f"   → Access token received")

print(f"\n✅ Step 3: Client Record Creation")
print(f"   → Client created in 'clients' table")
print(f"   → Linked to user via user_id")

print(f"\n✅ Step 4: T1 Form Submission")
print(f"   → T1 return created in 't1_returns_flat' table")
print(f"   → Flat columns populated")
print(f"   → JSONB form_data populated")

print(f"\n" + "=" * 80)
print("✅ ALL DATA SUCCESSFULLY SAVED THROUGH BACKEND API")
print("=" * 80)
print(f"\nDatabase Tables Updated:")
print(f"  1. users - User account created")
print(f"  2. clients - Client record created")
print(f"  3. t1_returns_flat - T1 form data saved (flat + JSONB)")
print(f"\n✅ Test Complete!")







