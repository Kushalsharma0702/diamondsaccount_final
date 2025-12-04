#!/usr/bin/env python3
"""
Script to create a default developer user for testing
Email: Developer@aurocode.app
Password: Developer@123
"""

import asyncio
import sys
import os
from uuid import uuid4

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from shared.database import engine, AsyncSessionLocal, Base
from shared.models import User
from shared.auth import JWTManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_default_user():
    """Create the default developer user"""
    
    # Default user details
    email = "Developer@aurocode.app"
    password = "Developer@123"
    first_name = "Developer"
    last_name = "User"
    
    # Create database session
    async with AsyncSessionLocal() as db:
        try:
            # Check if user already exists
            result = await db.execute(select(User).where(User.email == email.lower()))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ User already exists: {email}")
                print(f"   User ID: {existing_user.id}")
                print(f"   Email Verified: {existing_user.email_verified}")
                print(f"   Is Active: {existing_user.is_active}")
                
                # Update user if needed
                if not existing_user.email_verified:
                    existing_user.email_verified = True
                    print("   ✅ Set email_verified = True")
                
                if not existing_user.is_active:
                    existing_user.is_active = True
                    print("   ✅ Set is_active = True")
                
                # Update password (in case it changed)
                hashed_password = JWTManager.hash_password(password)
                existing_user.password_hash = hashed_password
                print("   ✅ Updated password hash")
                
                await db.commit()
                print(f"\n✅ User updated successfully!")
                return existing_user
            
            # Create new user
            print(f"Creating default user...")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            
            # Hash password
            hashed_password = JWTManager.hash_password(password)
            
            # Create user
            new_user = User(
                id=uuid4(),
                email=email.lower(),  # Store email in lowercase for consistency
                first_name=first_name,
                last_name=last_name,
                password_hash=hashed_password,
                email_verified=True,  # Auto-verified for developer account
                is_active=True,
                accept_terms=True
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            print(f"\n✅ Default user created successfully!")
            print(f"   User ID: {new_user.id}")
            print(f"   Email: {new_user.email}")
            print(f"   Name: {new_user.first_name} {new_user.last_name}")
            print(f"   Email Verified: {new_user.email_verified}")
            print(f"   Is Active: {new_user.is_active}")
            
            return new_user
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating user: {e}")
            import traceback
            traceback.print_exc()
            raise


async def main():
    """Main function"""
    print("=" * 60)
    print("Creating Default Developer User")
    print("=" * 60)
    print()
    
    try:
        # Initialize database (create tables if needed)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database initialized")
        print()
        
        # Create default user
        user = await create_default_user()
        
        print()
        print("=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print()
        print("You can now login with:")
        print(f"  Email: Developer@aurocode.app")
        print(f"  Password: Developer@123")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Setup Failed!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


