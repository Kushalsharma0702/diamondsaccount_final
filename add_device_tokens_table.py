"""
Migration script to add notification_device_tokens table

Run this after updating schemas_v2.py to create the new table in the database.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env file explicitly
env_file = os.path.join(project_root, ".env")
print(f"📄 Loading environment from: {env_file}")
load_dotenv(dotenv_path=env_file, override=True)

# Import AFTER loading env
from database.schemas_v2 import Base, NotificationDeviceToken

# Get DATABASE_SYNC_URL or build from components
DATABASE_URL = os.getenv("DATABASE_SYNC_URL")

if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        print("❌ Error: Missing database configuration")
        print(f"   DB_HOST: {DB_HOST}")
        print(f"   DB_PORT: {DB_PORT}")
        print(f"   DB_NAME: {DB_NAME}")
        print(f"   DB_USER: {DB_USER}")
        print("\n💡 Make sure your .env file has these variables set")
        sys.exit(1)
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🔗 Connecting to: {os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")

try:
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Create only the notification_device_tokens table
    NotificationDeviceToken.__table__.create(engine, checkfirst=True)
    
    print("\n✅ notification_device_tokens table created successfully!")
    
    # Verify table exists
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'notification_device_tokens'
        """))
        
        if result.fetchone():
            print("✅ Table verified in database")
        else:
            print("❌ Table not found after creation")
            
except Exception as e:
    print(f"❌ Error: {e}")
    raise
