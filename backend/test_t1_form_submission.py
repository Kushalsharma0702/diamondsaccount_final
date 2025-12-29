#!/usr/bin/env python3
"""
Test T1 Form Submission - Sends dummy T1 form data through backend API
This ensures data flows: Frontend → Backend API → Database (not direct DB insert)
"""
import requests
import json
from datetime import datetime, date
import uuid

BASE_URL = "http://localhost:8001/api/v1"

# Generate test email
test_email = f"test_t1_{int(datetime.now().timestamp())}@example.com"

print("=" * 70)
print("T1 Form Submission Test - Through Backend API")
print("=" * 70)
print(f"Test Email: {test_email}")
print(f"Base URL: {BASE_URL}\n")

# Step 1: Create a test client/user first
print("Step 1: Creating test client...")
client_payload = {
    "email": test_email,
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-123-4567",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!"
}

try:
    # Register user
    register_response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": test_email,
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1-555-123-4567",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }, timeout=10)
    
    if register_response.status_code == 201:
        print("✅ User registered successfully")
    else:
        print(f"⚠️  Registration: {register_response.status_code} - {register_response.text}")
    
    # Add client record
    client_response = requests.post(f"{BASE_URL}/client/add", json=client_payload, timeout=10)
    if client_response.status_code == 200:
        client_data = client_response.json()
        print(f"✅ Client created: {client_data.get('id')}")
    else:
        print(f"⚠️  Client creation: {client_response.status_code} - {client_response.text}")
        # Try to continue anyway
except Exception as e:
    print(f"⚠️  Client setup error: {e}")
    print("Continuing with test...\n")

# Step 2: Prepare complete T1 form data matching T1Structure.json
print("\nStep 2: Preparing T1 form data...")
t1_form_data = {
    "status": "draft",
    "filingYear": 2023,
    "personalInfo": {
        "firstName": "John",
        "middleName": "Michael",
        "lastName": "Doe",
        "sin": "123456789",
        "dateOfBirth": "1990-05-15",
        "address": "123 Main Street, Toronto, ON M5H 2N2",
        "phoneNumber": "+1-555-123-4567",
        "email": test_email,
        "isCanadianCitizen": True,
        "maritalStatus": "married",
        "spouseInfo": {
            "firstName": "Jane",
            "middleName": "Elizabeth",
            "lastName": "Doe",
            "sin": "987654321",
            "dateOfBirth": "1992-08-20"
        },
        "children": [
            {
                "firstName": "Alice",
                "middleName": "Marie",
                "lastName": "Doe",
                "sin": "111222333",
                "dateOfBirth": "2015-03-10"
            },
            {
                "firstName": "Bob",
                "lastName": "Doe",
                "sin": "444555666",
                "dateOfBirth": "2018-07-22"
            }
        ]
    },
    # Questionnaire flags
    "hasForeignProperty": True,
    "hasMedicalExpenses": True,
    "hasWorkFromHomeExpense": True,
    "hasDaycareExpenses": True,
    "isFirstTimeFiler": False,
    "isProvinceFiler": True,
    "soldPropertyShortTerm": False,
    "wasStudentLastYear": False,
    "isUnionMember": True,
    "hasOtherIncome": False,
    "hasProfessionalDues": True,
    "hasRrspFhsaInvestment": True,
    "hasChildArtSportCredit": True,
    "hasDisabilityTaxCredit": False,
    "isFilingForDeceased": False,
    
    # Foreign Property (array)
    "foreignProperty": [
        {
            "investmentDetails": "Stocks in USA",
            "grossIncome": 5000.00,
            "gainLossOnSale": 1200.00,
            "maximumCostDuringTheYear": 50000.00,
            "costAmountAtTheYearEnd": 45000.00,
            "country": "USA"
        },
        {
            "investmentDetails": "Real Estate in UK",
            "grossIncome": 8000.00,
            "gainLossOnSale": -500.00,
            "maximumCostDuringTheYear": 75000.00,
            "costAmountAtTheYearEnd": 70000.00,
            "country": "UK"
        }
    ],
    
    # Medical Expenses (array)
    "medicalExpenses": [
        {
            "paymentDate": "2023-03-15",
            "patientName": "John Doe",
            "paymentMadeTo": "Toronto General Hospital",
            "descriptionOfExpense": "Dental surgery",
            "insuranceCovered": 500.00,
            "amountPaidFromPocket": 1200.00
        },
        {
            "paymentDate": "2023-07-20",
            "patientName": "Jane Doe",
            "paymentMadeTo": "Eye Care Clinic",
            "descriptionOfExpense": "Eye exam and glasses",
            "insuranceCovered": 200.00,
            "amountPaidFromPocket": 400.00
        }
    ],
    
    # Work From Home
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
    
    # Daycare Expenses (array)
    "daycareExpenses": [
        {
            "childcareProvider": "ABC Daycare Center",
            "amount": 8000.00,
            "identificationNumberSin": "123456789",
            "weeks": 52
        }
    ],
    
    # Union Dues (array)
    "unionDues": [
        {
            "institutionName": "Local 123 Union",
            "amount": 500.00
        }
    ],
    
    # Professional Dues (array)
    "professionalDues": [
        {
            "name": "Professional License",
            "organization": "Ontario Professional Association",
            "amount": 300.00
        }
    ],
    
    # Child Art/Sport (array)
    "childArtSportCredit": [
        {
            "instituteName": "Toronto Soccer Club",
            "description": "Soccer lessons",
            "amount": 600.00
        },
        {
            "instituteName": "Art Academy",
            "description": "Art classes",
            "amount": 400.00
        }
    ],
    
    # Province Filer (array)
    "provinceFiler": [
        {
            "rentOrPropertyTax": "Property Tax",
            "propertyAddress": "123 Main Street, Toronto",
            "postalCode": "M5H 2N2",
            "noOfMonthsResides": 12,
            "amountPaid": 3500.00
        }
    ],
    
    # Self Employment
    "selfEmployment": {
        "businessTypes": ["uber", "general"],
        "uberBusiness": {
            "uberSkipStatement": "2023 Annual Statement",
            "businessHstNumber": "123456789RT0001",
            "hstAccessCode": "ABC123",
            "hstFillingPeriod": "2023",
            "income": 35000.00,
            "totalKmForUberSkip": 15000.0,
            "totalOfficialKmDriven": 12000.0,
            "totalKmDrivenEntireYear": 20000.0,
            "businessNumberVehicleRegistration": 12345,
            "meals": 500.00,
            "telephone": 600.00,
            "parkingFees": 200.00,
            "cleaningExpenses": 300.00,
            "safetyInspection": 100.00,
            "winterTireChange": 150.00,
            "oilChangeAndMaintenance": 800.00,
            "depreciation": 5000.00,
            "insuranceOnVehicle": 2400.00,
            "gas": 3000.00,
            "financingCostInterest": 2000.00,
            "leaseCost": 0.0,
            "otherExpense": 500.00
        },
        "generalBusiness": {
            "clientName": "Various Clients",
            "businessName": "John's Consulting",
            "salesCommissionsFees": 50000.00,
            "minusHstCollected": 6500.00,
            "grossIncome": 43500.00,
            "openingInventory": 0.0,
            "purchasesDuringYear": 5000.00,
            "subcontracts": 3000.00,
            "directWageCosts": 0.0,
            "otherCosts": 2000.00,
            "purchaseReturns": 0.0,
            "advertising": 1000.00,
            "mealsEntertainment": 500.00,
            "badDebts": 0.0,
            "insurance": 1200.00,
            "interest": 500.00,
            "feesLicensesDues": 300.00,
            "officeExpenses": 800.00,
            "supplies": 600.00,
            "legalAccountingFees": 2000.00,
            "managementAdministration": 1000.00,
            "officeRent": 6000.00,
            "maintenanceRepairs": 400.00,
            "salariesWagesBenefits": 0.0,
            "propertyTax": 0.0,
            "travel": 1500.00,
            "telephoneUtilities": 1200.00,
            "fuelCosts": 800.00,
            "deliveryFreightExpress": 300.00,
            "otherExpense1": 200.00,
            "otherExpense2": 100.00,
            "otherExpense3": 0.0,
            "areaOfHomeForBusiness": "200",
            "totalAreaOfHome": "2000",
            "heat": 1800.00,
            "electricity": 1200.00,
            "houseInsurance": 1200.00,
            "homeMaintenance": 800.00,
            "mortgageInterest": 15000.00,
            "propertyTaxes": 3500.00,
            "houseRent": 0.0,
            "homeOtherExpense1": 0.0,
            "homeOtherExpense2": 0.0,
            "kmDrivenForBusiness": 5000.0,
            "totalKmDrivenInYear": 20000.0,
            "vehicleFuel": 800.00,
            "vehicleInsurance": 2400.00,
            "licenseRegistration": 200.00,
            "vehicleMaintenance": 600.00,
            "businessParking": 200.00,
            "vehicleOtherExpense": 100.00,
            "leasingFinancePayments": 0.0
        }
    }
}

print("✅ T1 form data prepared with:")
print(f"   - Personal Info: {t1_form_data['personalInfo']['firstName']} {t1_form_data['personalInfo']['lastName']}")
print(f"   - Spouse: {t1_form_data['personalInfo']['spouseInfo']['firstName']}")
print(f"   - Children: {len(t1_form_data['personalInfo']['children'])}")
print(f"   - Foreign Property: {len(t1_form_data['foreignProperty'])} items")
print(f"   - Medical Expenses: {len(t1_form_data['medicalExpenses'])} items")
print(f"   - Self Employment: {', '.join(t1_form_data['selfEmployment']['businessTypes'])}")

# Step 3: Submit T1 form through backend API
print("\nStep 3: Submitting T1 form through backend API...")
try:
    payload = {
        "formData": t1_form_data
    }
    
    response = requests.post(
        f"{BASE_URL}/client/tax-return",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ T1 Form submitted successfully!")
        print(f"\nResponse:")
        print(f"  ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Filing Year: {result.get('filing_year')}")
        print(f"  Created At: {result.get('created_at')}")
        print(f"  Updated At: {result.get('updated_at')}")
        
        # Step 4: Verify data was saved by retrieving it
        print("\nStep 4: Verifying data retrieval from database...")
        get_response = requests.get(
            f"{BASE_URL}/client/tax-return",
            params={"email": test_email, "filing_year": 2023},
            timeout=10
        )
        
        if get_response.status_code == 200:
            retrieved_data = get_response.json()
            print("✅ Data retrieved successfully!")
            print(f"\nRetrieved Form Data:")
            if isinstance(retrieved_data, dict):
                personal_info = retrieved_data.get("personalInfo", {})
                print(f"  Name: {personal_info.get('firstName')} {personal_info.get('lastName')}")
                print(f"  Email: {personal_info.get('email')}")
                print(f"  SIN: {personal_info.get('sin')}")
                print(f"  Has Foreign Property: {retrieved_data.get('hasForeignProperty')}")
                print(f"  Has Medical Expenses: {retrieved_data.get('hasMedicalExpenses')}")
                print(f"  Self Employment Types: {retrieved_data.get('selfEmployment', {}).get('businessTypes', [])}")
                print(f"\n✅ SUCCESS: Data flowed through backend API and was saved to database!")
            else:
                print(f"  Retrieved: {retrieved_data}")
        else:
            print(f"⚠️  Get request failed: {get_response.status_code} - {get_response.text}")
            
    else:
        print(f"❌ T1 Form submission failed!")
        print(f"Response: {response.text}")
        try:
            error_detail = response.json()
            print(f"Error Detail: {json.dumps(error_detail, indent=2)}")
        except:
            pass
            
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to backend server!")
    print("   Make sure backend is running on http://localhost:8001")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test Complete")
print("=" * 70)







