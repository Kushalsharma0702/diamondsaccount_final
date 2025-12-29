#!/usr/bin/env python3
"""
Create demo login credentials for development/testing.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import User, Client
from backend.app.auth.password import hash_password

# Load .env from project root
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "CA_Project")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Demo credentials
DEMO_USERS = [
    {
        "email": "demo@taxease.com",
        "first_name": "Demo",
        "last_name": "User",
        "phone": "+1-555-000-0001",
        "password": "Demo123!",
        "role": "client"
    },
    {
        "email": "admin@taxease.com",
        "first_name": "Admin",
        "last_name": "User",
        "phone": "+1-555-000-0002",
        "password": "Admin123!",
        "role": "admin"
    },
    {
        "email": "test@taxease.com",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1-555-000-0003",
        "password": "Test123!",
        "role": "client"
    }
]

def create_demo_users():
    """Create demo users in the database."""
    db = SessionLocal()
    
    print("=" * 80)
    print("CREATING DEMO LOGIN CREDENTIALS")
    print("=" * 80)
    print()
    
    created_count = 0
    updated_count = 0
    
    for user_data in DEMO_USERS:
        try:
            # Check if user exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                # Update existing user
                existing_user.first_name = user_data["first_name"]
                existing_user.last_name = user_data["last_name"]
                existing_user.phone = user_data["phone"]
                existing_user.password_hash = hash_password(user_data["password"])
                existing_user.is_active = True
                existing_user.email_verified = True
                db.commit()
                updated_count += 1
                print(f"✅ Updated: {user_data['email']}")
            else:
                # Create new user
                new_user = User(
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    phone=user_data["phone"],
                    password_hash=hash_password(user_data["password"]),
                    is_active=True,
                    email_verified=True,
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                created_count += 1
                print(f"✅ Created: {user_data['email']}")
            
            # Create client record for client users
            if user_data["role"] == "client":
                user_id = existing_user.id if existing_user else new_user.id
                existing_client = db.query(Client).filter(Client.user_id == user_id).first()
                if not existing_client:
                    client = Client(
                        user_id=user_id,
                        filing_year=2024,
                        status="documents_pending"
                    )
                    db.add(client)
                    db.commit()
                    print(f"   └─ Client record created")
            
        except Exception as e:
            print(f"❌ Error creating {user_data['email']}: {e}")
            db.rollback()
    
    db.close()
    
    print()
    print("=" * 80)
    print("DEMO CREDENTIALS SUMMARY")
    print("=" * 80)
    print()
    print("You can now login with these credentials:")
    print()
    for user_data in DEMO_USERS:
        print(f"📧 Email:    {user_data['email']}")
        print(f"🔑 Password: {user_data['password']}")
        print(f"👤 Role:     {user_data['role']}")
        print()
    print("=" * 80)
    print(f"✅ Created: {created_count} users")
    print(f"✅ Updated: {updated_count} users")
    print("=" * 80)

if __name__ == "__main__":
    create_demo_users()

