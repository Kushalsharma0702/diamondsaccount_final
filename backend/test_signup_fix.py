#!/usr/bin/env python3
"""
Test signup endpoint with and without confirm_password.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

print("=" * 80)
print("TESTING SIGNUP ENDPOINT FIX")
print("=" * 80)
print()

# Test 1: Signup WITHOUT confirm_password (like the frontend sends)
print("=" * 80)
print("TEST 1: Signup WITHOUT confirm_password")
print("=" * 80)

test_email_1 = f"test_no_confirm_{int(datetime.now().timestamp())}@example.com"

payload_1 = {
    "email": test_email_1,
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1-555-123-4567",
    "password": "Test123!",
    "accept_terms": True
}

print(f"📤 Sending request WITHOUT confirm_password...")
print(f"   Payload: {json.dumps(payload_1, indent=2)}")
print()

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=payload_1,
        timeout=10
    )
    
    print(f"📥 Response Status: {response.status_code}")
    print(f"📥 Response Body: {json.dumps(response.json(), indent=2) if response.text else 'No body'}")
    
    if response.status_code == 201:
        print("✅ SUCCESS: Signup works without confirm_password!")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print()

# Test 2: Signup WITH confirm_password (matching passwords)
print("=" * 80)
print("TEST 2: Signup WITH confirm_password (matching)")
print("=" * 80)

test_email_2 = f"test_with_confirm_{int(datetime.now().timestamp())}@example.com"

payload_2 = {
    "email": test_email_2,
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1-555-123-4567",
    "password": "Test123!",
    "confirm_password": "Test123!",
    "accept_terms": True
}

print(f"📤 Sending request WITH confirm_password (matching)...")
print(f"   Payload: {json.dumps(payload_2, indent=2)}")
print()

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=payload_2,
        timeout=10
    )
    
    print(f"📥 Response Status: {response.status_code}")
    print(f"📥 Response Body: {json.dumps(response.json(), indent=2) if response.text else 'No body'}")
    
    if response.status_code == 201:
        print("✅ SUCCESS: Signup works with confirm_password!")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print()

# Test 3: Signup WITH confirm_password (non-matching passwords)
print("=" * 80)
print("TEST 3: Signup WITH confirm_password (non-matching)")
print("=" * 80)

test_email_3 = f"test_mismatch_{int(datetime.now().timestamp())}@example.com"

payload_3 = {
    "email": test_email_3,
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1-555-123-4567",
    "password": "Test123!",
    "confirm_password": "Different123!",
    "accept_terms": True
}

print(f"📤 Sending request WITH confirm_password (non-matching)...")
print(f"   Payload: {json.dumps(payload_3, indent=2)}")
print()

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=payload_3,
        timeout=10
    )
    
    print(f"📥 Response Status: {response.status_code}")
    print(f"📥 Response Body: {json.dumps(response.json(), indent=2) if response.text else 'No body'}")
    
    if response.status_code == 400:
        print("✅ SUCCESS: Correctly rejected non-matching passwords!")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print()
print("=" * 80)
print("TESTING COMPLETE")
print("=" * 80)







