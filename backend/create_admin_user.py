#!/usr/bin/env python3
"""
Create admin user for testing.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import Admin
from backend.app.auth.password import hash_password

# Load .env
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

ADMINS = [
    {
        "email": "admin@taxease.com",
        "name": "Admin User",
        "password": "Admin123!",
        "role": "admin",
        "permissions": []
    },
    {
        "email": "superadmin@taxease.com",
        "name": "Super Admin",
        "password": "Super123!",
        "role": "superadmin",
        "permissions": []
    }
]

def create_admins():
    db = SessionLocal()
    
    print("=" * 80)
    print("CREATING ADMIN USERS")
    print("=" * 80)
    print()
    
    for admin_data in ADMINS:
        try:
            existing = db.query(Admin).filter(Admin.email == admin_data["email"]).first()
            if existing:
                existing.name = admin_data["name"]
                existing.password_hash = hash_password(admin_data["password"])
                existing.role = admin_data["role"]
                existing.is_active = True
                db.commit()
                print(f"✅ Updated: {admin_data['email']}")
            else:
                admin = Admin(
                    email=admin_data["email"],
                    name=admin_data["name"],
                    password_hash=hash_password(admin_data["password"]),
                    role=admin_data["role"],
                    permissions=admin_data["permissions"],
                    is_active=True,
                )
                db.add(admin)
                db.commit()
                db.refresh(admin)
                print(f"✅ Created: {admin_data['email']}")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()
    
    db.close()
    
    print()
    print("=" * 80)
    print("ADMIN CREDENTIALS")
    print("=" * 80)
    for admin_data in ADMINS:
        print(f"📧 Email:    {admin_data['email']}")
        print(f"🔑 Password: {admin_data['password']}")
        print(f"👤 Role:     {admin_data['role']}")
        print()
    print("=" * 80)

if __name__ == "__main__":
    create_admins()




