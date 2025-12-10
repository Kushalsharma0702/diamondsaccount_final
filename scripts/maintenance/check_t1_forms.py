#!/usr/bin/env python3
"""
Script to check how many T1 forms you have
"""

import requests
import json
import sys

CLIENT_BACKEND_URL = "http://localhost:8001"
EMAIL = "Developer@aurocode.app"
PASSWORD = "Developer@123"

def main():
    print("🔍 Checking T1 Forms...")
    print()
    
    # Step 1: Login
    print("1️⃣ Logging in...")
    try:
        login_response = requests.post(
            f"{CLIENT_BACKEND_URL}/api/v1/auth/login",
            json={"email": EMAIL, "password": PASSWORD},
            timeout=10
        )
        login_response.raise_for_status()
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("❌ Login failed: No access token received")
            print(f"Response: {login_response.text}")
            sys.exit(1)
        
        print("✅ Login successful!")
        print()
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        sys.exit(1)
    
    # Step 2: Get T1 forms
    print("2️⃣ Fetching T1 forms...")
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        forms_response = requests.get(
            f"{CLIENT_BACKEND_URL}/api/v1/t1-forms/",
            headers=headers,
            timeout=10
        )
        forms_response.raise_for_status()
        forms_data = forms_response.json()
        
        total = forms_data.get("total", 0)
        forms = forms_data.get("forms", [])
        
        print()
        print("=" * 60)
        print("📊 T1 Forms Summary")
        print("=" * 60)
        print(f"Total Forms: {total}")
        print()
        
        if total > 0:
            print(f"📋 Form Details ({len(forms)} forms):")
            print()
            for i, form in enumerate(forms, 1):
                print(f"Form #{i}:")
                print(f"  ID: {form.get('id', 'N/A')}")
                print(f"  Status: {form.get('status', 'N/A')}")
                print(f"  Created: {form.get('created_at', 'N/A')}")
                
                personal_info = form.get('personalInfo', {})
                first_name = personal_info.get('firstName', 'N/A')
                last_name = personal_info.get('lastName', 'N/A')
                print(f"  Name: {first_name} {last_name}")
                
                # Show form flags
                flags = []
                if form.get('hasForeignProperty'):
                    flags.append("Foreign Property")
                if form.get('hasMedicalExpenses'):
                    flags.append("Medical Expenses")
                if form.get('hasMovingExpenses'):
                    flags.append("Moving Expenses")
                if form.get('isSelfEmployed'):
                    flags.append("Self Employed")
                if form.get('isFirstHomeBuyer'):
                    flags.append("First Home Buyer")
                
                if flags:
                    print(f"  Sections: {', '.join(flags)}")
                
                print()
        else:
            print("   ℹ️  No forms found.")
            print("   Start by creating a new T1 form!")
            print()
        
        print("=" * 60)
        print("✅ Done!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch forms: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()




