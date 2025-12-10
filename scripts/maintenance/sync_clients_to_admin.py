#!/usr/bin/env python3
"""
Script to sync existing users from client backend to admin backend as clients
Also syncs T1 forms information
"""

import asyncio
import sys
import os
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client_side', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tax-hub-dashboard', 'backend'))

from client_side.shared.database import AsyncSessionLocal as ClientSession
from client_side.shared.models import User, T1PersonalForm
from app.core.database import AsyncSessionLocal as AdminSession
from app.models.client import Client
from sqlalchemy import select
import httpx

# Admin backend URL
ADMIN_API_BASE = "http://localhost:8002/api/v1"
ADMIN_EMAIL = "superadmin@taxease.ca"
ADMIN_PASSWORD = "demo123"


async def get_admin_token():
    """Get admin authentication token"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{ADMIN_API_BASE}/auth/login",
                json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("token", {}).get("access_token")
    except Exception as e:
        print(f"Error getting admin token: {e}")
    return None


async def create_client_in_admin(email: str, first_name: str, last_name: str, token: str) -> str:
    """Create or get client in admin backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Check if client exists
            response = await client.get(
                f"{ADMIN_API_BASE}/clients",
                params={"email": email, "page_size": 1},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                if clients:
                    return clients[0].get("id")
            
            # Create new client
            name = f"{first_name} {last_name}".strip() or email.split("@")[0].replace(".", " ").title()
            
            client_data = {
                "name": name,
                "email": email.lower(),
                "filing_year": datetime.now().year,
                "status": "documents_pending",
                "payment_status": "pending"
            }
            
            create_response = await client.post(
                f"{ADMIN_API_BASE}/clients",
                json=client_data,
                headers=headers
            )
            
            if create_response.status_code in [200, 201]:
                result = create_response.json()
                return result.get("id")
            
    except Exception as e:
        print(f"Error creating client: {e}")
    return None


async def sync_users_to_clients():
    """Sync all users from client backend to admin backend as clients"""
    print("=" * 60)
    print("🔄 Syncing Users to Clients")
    print("=" * 60)
    print()
    
    # Get admin token
    print("1️⃣ Getting admin authentication token...")
    token = await get_admin_token()
    if not token:
        print("❌ Failed to get admin token!")
        return
    print("✅ Admin token obtained")
    print()
    
    # Get all users from client backend
    print("2️⃣ Fetching users from client backend...")
    async with ClientSession() as client_db:
        result = await client_db.execute(select(User))
        users = result.scalars().all()
        print(f"✅ Found {len(users)} users")
        print()
        
        created = 0
        skipped = 0
        failed = 0
        
        # Sync each user
        print("3️⃣ Syncing users to admin backend...")
        for user in users:
            try:
                client_id = await create_client_in_admin(
                    user.email,
                    user.first_name or "",
                    user.last_name or "",
                    token
                )
                
                if client_id:
                    print(f"   ✅ {user.email} → Client ID: {client_id}")
                    created += 1
                else:
                    print(f"   ⚠️  {user.email} → Already exists or failed")
                    skipped += 1
            except Exception as e:
                print(f"   ❌ {user.email} → Error: {e}")
                failed += 1
        
        print()
        print("=" * 60)
        print("✅ Sync Complete!")
        print("=" * 60)
        print(f"Created: {created}")
        print(f"Skipped/Existing: {skipped}")
        print(f"Failed: {failed}")
        print(f"Total: {len(users)}")
        print()


async def check_t1_forms():
    """Check T1 forms and provide summary"""
    print()
    print("=" * 60)
    print("📋 T1 Forms Summary")
    print("=" * 60)
    print()
    
    async with ClientSession() as client_db:
        result = await client_db.execute(select(T1PersonalForm))
        forms = result.scalars().all()
        
        print(f"Total T1 Forms: {len(forms)}")
        print()
        
        for form in forms:
            # Get user email
            user_result = await client_db.execute(
                select(User).where(User.id == form.user_id)
            )
            user = user_result.scalar_one_or_none()
            email = user.email if user else "Unknown"
            
            print(f"Form: {form.id}")
            print(f"  User: {email}")
            print(f"  Status: {form.status}")
            print(f"  Tax Year: {form.tax_year}")
            print()


async def main():
    """Main function"""
    await sync_users_to_clients()
    await check_t1_forms()
    
    print()
    print("💡 Note: T1 forms are stored in client backend database.")
    print("   They are encrypted and accessible via client API endpoints.")
    print()


if __name__ == "__main__":
    asyncio.run(main())

