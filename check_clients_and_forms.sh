#!/bin/bash

# Quick check script for clients and T1 forms

echo "🔍 Checking Database Status..."
echo ""

# Check clients
echo "📊 Clients in Admin Database:"
python3 << 'EOF'
import asyncio
import sys
import os
sys.path.insert(0, 'tax-hub-dashboard/backend')
from app.core.database import AsyncSessionLocal
from app.models.client import Client
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Client))
        clients = result.scalars().all()
        print(f"   Total: {len(clients)}")
        if len(clients) > 0:
            print("   Sample:")
            for c in clients[:5]:
                print(f"     - {c.name} ({c.email})")

asyncio.run(check())
EOF

echo ""
echo "📋 T1 Forms in Client Database:"
python3 << 'EOF'
import asyncio
import sys
import os
sys.path.insert(0, 'client_side/shared')
from database import AsyncSessionLocal
from models import T1PersonalForm
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(T1PersonalForm))
        forms = result.scalars().all()
        print(f"   Total: {len(forms)}")
        if len(forms) > 0:
            print("   Forms:")
            for f in forms:
                print(f"     - {f.id} (Status: {f.status}, Year: {f.tax_year})")

asyncio.run(check())
EOF

echo ""
echo "✅ Done!"


