#!/usr/bin/env python3
"""
Test script to manually sync an existing file to admin backend
"""
import asyncio
import sys
import os

sys.path.insert(0, 'client_side/shared')
sys.path.insert(0, 'tax-hub-dashboard/backend')

from client_side.shared.database import AsyncSessionLocal as ClientSession
from client_side.shared.models import File, User
from client_side.shared.sync_to_admin import sync_file_to_admin_document
from sqlalchemy import select

async def sync_existing_files():
    """Sync all existing files to admin backend"""
    print("=" * 60)
    print("🔄 Syncing Existing Files to Admin Backend")
    print("=" * 60)
    print()
    
    async with ClientSession() as client_db:
        # Get all uploaded files
        result = await client_db.execute(
            select(File).where(File.upload_status == "uploaded")
        )
        files = result.scalars().all()
        
        print(f"Found {len(files)} uploaded files")
        print()
        
        synced = 0
        failed = 0
        
        for file_record in files:
            # Get user
            user_result = await client_db.execute(
                select(User).where(User.id == file_record.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                print(f"⚠️  User not found for file {file_record.id}")
                continue
            
            print(f"Syncing: {file_record.original_filename} (User: {user.email})")
            
            try:
                doc_id = await sync_file_to_admin_document(
                    file_id=str(file_record.id),
                    user_email=user.email,
                    filename=file_record.original_filename,
                    file_type=file_record.file_type,
                    file_size=file_record.file_size,
                    s3_key=file_record.s3_key,
                    db_session=None
                )
                
                if doc_id:
                    print(f"  ✅ Synced! Document ID: {doc_id}")
                    synced += 1
                else:
                    print(f"  ❌ Failed to sync")
                    failed += 1
            except Exception as e:
                print(f"  ❌ Error: {e}")
                failed += 1
        
        print()
        print("=" * 60)
        print(f"✅ Sync Complete!")
        print(f"   Synced: {synced}")
        print(f"   Failed: {failed}")
        print(f"   Total: {len(files)}")
        print()

if __name__ == "__main__":
    asyncio.run(sync_existing_files())

