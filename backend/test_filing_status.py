#!/usr/bin/env python3
"""
Test Filing Status API endpoints.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

print("=" * 80)
print("TESTING FILING STATUS API")
print("=" * 80)
print()

# Use demo client
demo_email = "demo@taxease.com"
demo_password = "Demo123!"

# Step 1: Login to get client_id
print("=" * 80)
print("STEP 1: Login as Demo Client")
print("=" * 80)

try:
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": demo_email, "password": demo_password},
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        exit(1)
    
    print(f"✅ Login successful")
    print()
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Step 2: Get client ID
print("=" * 80)
print("STEP 2: Get Client ID")
print("=" * 80)

try:
    clients_response = requests.get(f"{BASE_URL}/admin/clients", timeout=10)
    if clients_response.status_code == 200:
        clients = clients_response.json()
        demo_client = next((c for c in clients if c.get("email") == demo_email), None)
        if demo_client:
            client_id = demo_client["id"]
            print(f"✅ Client ID: {client_id}")
        else:
            print("❌ Demo client not found in admin list")
            exit(1)
    else:
        print(f"❌ Failed to get clients: {clients_response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 3: Create a T1 return if it doesn't exist
print()
print("=" * 80)
print("STEP 3: Ensure T1 Return Exists")
print("=" * 80)

try:
    # Try to get existing T1 return
    status_response = requests.get(
        f"{BASE_URL}/filing-status/client/{client_id}",
        timeout=10
    )
    
    if status_response.status_code == 404:
        # Create a dummy T1 return
        print("Creating dummy T1 return...")
        t1_data = {
            "formData": {
                "personalInfo": {
                    "email": demo_email,
                    "firstName": "Demo",
                    "lastName": "User"
                },
                "filingYear": 2024,
                "status": "draft"
            }
        }
        create_response = requests.post(
            f"{BASE_URL}/client/tax-return",
            json=t1_data,
            timeout=10
        )
        if create_response.status_code == 200:
            print("✅ T1 return created")
        else:
            print(f"⚠️  T1 return creation: {create_response.text}")
    else:
        print("✅ T1 return exists")
except Exception as e:
    print(f"⚠️  Error checking T1 return: {e}")

# Step 4: Get current filing status
print()
print("=" * 80)
print("STEP 4: Get Current Filing Status (Client View)")
print("=" * 80)

try:
    status_response = requests.get(
        f"{BASE_URL}/filing-status/client/{client_id}",
        timeout=10
    )
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"✅ Filing Status Retrieved:")
        print(f"   Return ID: {status_data.get('return_id')}")
        print(f"   Filing Year: {status_data.get('filing_year')}")
        print(f"   Current Status: {status_data.get('current_status')}")
        print(f"   Status Display: {status_data.get('current_status_display')}")
        print(f"   Payment Status: {status_data.get('payment_status')}")
        print(f"   Updated At: {status_data.get('updated_at')}")
        print()
        print(f"   Timeline ({len(status_data.get('timeline', []))} steps):")
        for item in status_data.get('timeline', []):
            marker = "✅" if item.get('is_completed') else ("🔄" if item.get('is_current') else "⏳")
            print(f"     {marker} {item.get('display_name')}")
        
        return_id = status_data.get('return_id')
    else:
        print(f"❌ Failed to get status: {status_response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 5: Update status as admin
print()
print("=" * 80)
print("STEP 5: Update Status (Admin Action)")
print("=" * 80)

statuses_to_test = [
    "submitted",
    "payment_request_sent",
    "payment_received",
    "return_in_progress",
    "under_review_pending_approval",
]

for new_status in statuses_to_test[:2]:  # Test first 2 statuses
    try:
        print(f"\n📤 Updating status to: {new_status}")
        update_response = requests.put(
            f"{BASE_URL}/filing-status/admin/{return_id}/status",
            json={
                "status": new_status,
                "notes": f"Status updated via API test at {datetime.now().isoformat()}"
            },
            timeout=10
        )
        
        if update_response.status_code == 200:
            update_data = update_response.json()
            print(f"✅ Status updated successfully:")
            print(f"   New Status: {update_data.get('status_display')}")
            print(f"   Updated At: {update_data.get('updated_at')}")
        else:
            print(f"❌ Update failed: {update_response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Step 6: Verify status change reflected
print()
print("=" * 80)
print("STEP 6: Verify Status Change Reflected")
print("=" * 80)

try:
    status_response = requests.get(
        f"{BASE_URL}/filing-status/client/{client_id}",
        timeout=10
    )
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"✅ Updated Status: {status_data.get('current_status_display')}")
        print(f"   Updated At: {status_data.get('updated_at')}")
        
        # Show current step in timeline
        for item in status_data.get('timeline', []):
            if item.get('is_current'):
                print(f"   Current Step: {item.get('display_name')}")
                break
except Exception as e:
    print(f"❌ Error: {e}")

# Step 7: List all returns (admin view)
print()
print("=" * 80)
print("STEP 7: List All Returns (Admin View)")
print("=" * 80)

try:
    list_response = requests.get(
        f"{BASE_URL}/filing-status/admin/returns",
        timeout=10
    )
    
    if list_response.status_code == 200:
        returns = list_response.json()
        print(f"✅ Found {len(returns)} returns")
        for ret in returns[:3]:  # Show first 3
            print(f"   - {ret.get('filing_year')}: {ret.get('status_display')} (ID: {ret.get('id')[:8]}...)")
except Exception as e:
    print(f"⚠️  Error: {e}")

print()
print("=" * 80)
print("TESTING COMPLETE")
print("=" * 80)







