"""
Test script for FCM device token registration endpoint

Usage:
1. Start the backend API on port 8001
2. Run this script: python test_device_token_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

# Test credentials (use your actual test user)
TEST_USER = {
    "email": "test@example.com",
    "password": "Test123!"
}

def login():
    """Login and get access token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=TEST_USER
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful")
        return data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None


def register_device_token(token):
    """Register a test FCM device token"""
    print("\n📱 Registering device token...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test FCM token (simulated)
    device_token_data = {
        "token": "test_fcm_token_" + "x" * 100,  # Simulated FCM token
        "platform": "android",
        "device_id": "test-device-001",
        "app_version": "1.0.0",
        "locale": "en_US"
    }
    
    response = requests.post(
        f"{BASE_URL}/notifications/device-tokens",
        headers=headers,
        json=device_token_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Device token registered successfully")
        print(f"   Token ID: {data['id']}")
        print(f"   Platform: {data['platform']}")
        print(f"   Active: {data['is_active']}")
        return data['id']
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        return None


def list_device_tokens(token):
    """List all device tokens for the user"""
    print("\n📋 Listing device tokens...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/notifications/device-tokens",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total']} device token(s)")
        for token_obj in data['tokens']:
            print(f"   - {token_obj['platform']}: {token_obj['token'][:50]}...")
    else:
        print(f"❌ Listing failed: {response.status_code}")
        print(response.text)


def delete_device_token(access_token, token_id):
    """Delete a device token"""
    print(f"\n🗑️  Deleting device token {token_id}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.delete(
        f"{BASE_URL}/notifications/device-tokens/{token_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        print(f"✅ Device token deleted successfully")
    else:
        print(f"❌ Deletion failed: {response.status_code}")
        print(response.text)


def main():
    print("=" * 60)
    print("FCM DEVICE TOKEN API TEST")
    print("=" * 60)
    
    # Step 1: Login
    access_token = login()
    if not access_token:
        return
    
    # Step 2: Register device token
    token_id = register_device_token(access_token)
    
    # Step 3: List device tokens
    list_device_tokens(access_token)
    
    # Step 4: Try registering same token again (should update)
    print("\n♻️  Re-registering same token (should update)...")
    register_device_token(access_token)
    
    # Step 5: List again
    list_device_tokens(access_token)
    
    # Step 6: Delete token
    if token_id:
        delete_device_token(access_token, token_id)
        list_device_tokens(access_token)
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
