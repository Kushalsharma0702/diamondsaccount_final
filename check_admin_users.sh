#!/bin/bash

cd /home/cyberdude/Documents/Projects/CA-final/admin-dashboard/backend

source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate && pip install -q -r requirements.txt

python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, '.')

from app.core.database import AsyncSessionLocal
from app.models.admin_user import AdminUser
from sqlalchemy import select

async def check_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AdminUser))
        users = result.scalars().all()
        
        if users:
            print("=" * 60)
            print("📋 Admin Users in Database:")
            print("=" * 60)
            for user in users:
                print(f"\nEmail: {user.email}")
                print(f"Name: {user.name}")
                print(f"Role: {user.role}")
                print(f"Active: {user.is_active}")
        else:
            print("No admin users found. Run create_default_admin.py to create them.")

asyncio.run(check_users())
EOF

