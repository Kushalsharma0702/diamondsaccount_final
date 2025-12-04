#!/usr/bin/env python3
"""
Direct database sync - Sync users from client backend to admin backend using same database
Since both use taxease_db, we can directly access both schemas
"""

import asyncio
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client_side', 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tax-hub-dashboard', 'backend'))

from client_side.shared.database import AsyncSessionLocal as ClientSession
from client_side.shared.models import User, T1PersonalForm
from app.core.database import AsyncSessionLocal as AdminSession
from app.models.client import Client
from sqlalchemy import select

async def sync_users_to_clients_direct():
    """Direct database sync - both use same taxease_db"""
    print("=" * 60)
    print("🔄 Direct Database Sync: Users → Clients")
    print("=" * 60)
    print()
    
    async with ClientSession() as client_db:
        # Get all users from client backend
        print("1️⃣ Fetching users from client database...")
        result = await client_db.execute(select(User))
        users = result.scalars().all()
        print(f"✅ Found {len(users)} users")
        print()
        
        created = 0
        updated = 0
        skipped = 0
        
        # Use admin session to create clients in same database
        async with AdminSession() as admin_db:
            print("2️⃣ Syncing to admin client table...")
            for user in users:
                try:
                    # Check if client already exists
                    result = await admin_db.execute(
                        select(Client).where(Client.email == user.email.lower())
                    )
                    existing_client = result.scalar_one_or_none()
                    
                    if existing_client:
                        print(f"   ℹ️  {user.email} → Already exists")
                        skipped += 1
                        continue
                    
                    # Create new client
                    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                    if not name:
                        name = user.email.split("@")[0].replace(".", " ").title()
                    
                    new_client = Client(
                        id=uuid4(),
                        name=name,
                        email=user.email.lower(),
                        filing_year=datetime.now().year,
                        status="documents_pending",
                        payment_status="pending",
                        total_amount=0.0,
                        paid_amount=0.0
                    )
                    
                    admin_db.add(new_client)
                    created += 1
                    print(f"   ✅ {user.email} → Created client")
                    
                except Exception as e:
                    print(f"   ❌ {user.email} → Error: {e}")
            
            await admin_db.commit()
        
        print()
        print("=" * 60)
        print("✅ Sync Complete!")
        print("=" * 60)
        print(f"Created: {created}")
        print(f"Skipped (already exists): {skipped}")
        print(f"Total processed: {len(users)}")
        print()


async def check_results():
    """Verify sync results"""
    print()
    print("=" * 60)
    print("📊 Verification")
    print("=" * 60)
    print()
    
    async with AdminSession() as admin_db:
        result = await admin_db.execute(select(Client))
        clients = result.scalars().all()
        
        print(f"✅ Total clients in admin database: {len(clients)}")
        print()
        
        if len(clients) > 0:
            print("Sample clients:")
            for client in clients[:10]:
                print(f"  - {client.name} ({client.email})")
            if len(clients) > 10:
                print(f"  ... and {len(clients) - 10} more")
        
    print()
    
    # Check T1 forms
    async with ClientSession() as client_db:
        result = await client_db.execute(select(T1PersonalForm))
        forms = result.scalars().all()
        
        print(f"✅ Total T1 forms in client database: {len(forms)}")
        print()
        
        if len(forms) > 0:
            print("T1 Forms:")
            for form in forms:
                # Get user
                user_result = await client_db.execute(
                    select(User).where(User.id == form.user_id)
                )
                user = user_result.scalar_one_or_none()
                email = user.email if user else "Unknown"
                
                print(f"  - {form.id}")
                print(f"    User: {email}")
                print(f"    Status: {form.status}")
                print(f"    Tax Year: {form.tax_year}")
                print()


async def main():
    """Main function"""
    await sync_users_to_clients_direct()
    await check_results()
    
    print()
    print("💡 T1 Forms are stored in client backend.")
    print("   They can be accessed via client API: /api/v1/t1-forms/")
    print("   Or through admin API if needed.")
    print()


if __name__ == "__main__":
    asyncio.run(main())


