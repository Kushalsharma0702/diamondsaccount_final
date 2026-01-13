#!/usr/bin/env python3
"""
Database Initialization Script for Tax-Ease
===========================================
This script:
1. Cleans/drops ALL existing tables from the database
2. Creates fresh schemas from database/schemas_v2.py
3. Creates default admin and superadmin users
4. Optionally creates test data

Usage:
    python3 init_database.py              # Interactive mode
    python3 init_database.py --yes        # Auto-confirm
    python3 init_database.py --test-data  # Also create test users
"""

import sys
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime
import uuid

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

# Import schemas
from database.schemas_v2 import Base, Admin, User, FilingStatus

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")


def get_database_url():
    """Get database URL from environment variables"""
    # Try DATABASE_URL first
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # Convert asyncpg to psycopg2 if needed
        if "asyncpg" in db_url:
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        return db_url
    
    # Build from individual components
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_database_info():
    """Get database connection info for display"""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "postgres")
    
    return {
        "host": db_host,
        "port": db_port,
        "database": db_name,
        "user": db_user
    }


def test_connection(engine):
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print_success(f"Connected to database")
            print_info(f"PostgreSQL version: {version[:50]}...")
            return True
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        return False


def drop_all_tables(engine):
    """Drop all tables in the database"""
    print_header("Step 1: Cleaning Database")
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print_info("No tables found. Database is already clean.")
            return True
        
        print_warning(f"Found {len(tables)} tables to drop:")
        for table in tables:
            print(f"  • {table}")
        
        print()
        
        with engine.connect() as conn:
            # Drop all tables using CASCADE to handle foreign keys
            print_info("Dropping tables...")
            conn.execute(text("DROP SCHEMA public CASCADE;"))
            conn.execute(text("CREATE SCHEMA public;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
            conn.commit()
        
        print_success("All tables dropped successfully!")
        return True
        
    except Exception as e:
        print_error(f"Failed to drop tables: {e}")
        return False


def create_all_tables(engine):
    """Create all tables from SQLAlchemy models"""
    print_header("Step 2: Creating Database Schema")
    
    try:
        print_info("Creating tables from schemas_v2.py...")
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print_success(f"Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  • {table}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_admin_users(session):
    """Create default admin users"""
    print_header("Step 3: Creating Admin Users")
    
    admin_users = [
        {
            "email": "superadmin@taxease.com",
            "name": "Super Admin",
            "password": "SuperAdmin123!",
            "role": "superadmin",
            "permissions": ["*"]  # All permissions
        },
        {
            "email": "admin@taxease.com",
            "name": "Admin User",
            "password": "Admin123!",
            "role": "admin",
            "permissions": ["view_filings", "edit_filings", "view_users", "manage_documents"]
        },
        {
            "email": "ca@taxease.com",
            "name": "CA Administrator",
            "password": "CA123456!",
            "role": "admin",
            "permissions": ["view_filings", "edit_filings", "view_users"]
        }
    ]
    
    created_admins = []
    
    for admin_data in admin_users:
        try:
            # Check if admin already exists
            existing = session.query(Admin).filter_by(email=admin_data["email"]).first()
            if existing:
                print_warning(f"Admin {admin_data['email']} already exists, skipping...")
                continue
            
            # Hash password
            password_hash = pwd_context.hash(admin_data["password"])
            
            # Create admin
            admin = Admin(
                id=uuid.uuid4(),
                email=admin_data["email"],
                name=admin_data["name"],
                password_hash=password_hash,
                role=admin_data["role"],
                permissions=admin_data["permissions"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(admin)
            session.commit()
            
            print_success(f"Created {admin_data['role']}: {admin_data['email']}")
            print_info(f"  Name: {admin_data['name']}")
            print_info(f"  Password: {admin_data['password']}")
            print_info(f"  ID: {admin.id}")
            
            created_admins.append(admin)
            
        except Exception as e:
            print_error(f"Failed to create admin {admin_data['email']}: {e}")
            session.rollback()
            continue
    
    return created_admins


def create_test_users(session):
    """Create test user accounts"""
    print_header("Step 4: Creating Test Users (Optional)")
    
    test_users = [
        {
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+14165551234",
            "password": "User123!"
        },
        {
            "email": "jane.smith@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "+14165555678",
            "password": "User123!"
        },
        {
            "email": "test@taxease.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+14165559999",
            "password": "Test123!"
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        try:
            # Check if user already exists
            existing = session.query(User).filter_by(email=user_data["email"]).first()
            if existing:
                print_warning(f"User {user_data['email']} already exists, skipping...")
                continue
            
            # Hash password
            password_hash = pwd_context.hash(user_data["password"])
            
            # Create user
            user = User(
                id=uuid.uuid4(),
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                phone=user_data["phone"],
                password_hash=password_hash,
                email_verified=True,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(user)
            session.commit()
            
            print_success(f"Created user: {user_data['email']}")
            print_info(f"  Name: {user_data['first_name']} {user_data['last_name']}")
            print_info(f"  Password: {user_data['password']}")
            print_info(f"  ID: {user.id}")
            
            created_users.append(user)
            
        except Exception as e:
            print_error(f"Failed to create user {user_data['email']}: {e}")
            session.rollback()
            continue
    
    return created_users


def verify_setup(session):
    """Verify the database setup"""
    print_header("Verification")
    
    try:
        # Count admins
        admin_count = session.query(Admin).count()
        print_info(f"Total Admins: {admin_count}")
        
        # List admins
        admins = session.query(Admin).all()
        for admin in admins:
            print(f"  • {admin.email} ({admin.role}) - {admin.name}")
        
        print()
        
        # Count users
        user_count = session.query(User).count()
        print_info(f"Total Users: {user_count}")
        
        # List users
        users = session.query(User).all()
        for user in users:
            print(f"  • {user.email} - {user.first_name} {user.last_name}")
        
        return True
        
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False


def print_summary(db_info):
    """Print final summary"""
    print_header("Summary")
    
    print_success("Database initialization completed successfully!")
    print()
    print_info("Database Connection Details:")
    print(f"  Host: {db_info['host']}")
    print(f"  Port: {db_info['port']}")
    print(f"  Database: {db_info['database']}")
    print(f"  User: {db_info['user']}")
    print()
    print_info("Admin Credentials:")
    print(f"  {Colors.BOLD}Superadmin:{Colors.ENDC}")
    print(f"    Email: superadmin@taxease.com")
    print(f"    Password: SuperAdmin123!")
    print()
    print(f"  {Colors.BOLD}Admin:{Colors.ENDC}")
    print(f"    Email: admin@taxease.com")
    print(f"    Password: Admin123!")
    print()
    print(f"  {Colors.BOLD}CA:{Colors.ENDC}")
    print(f"    Email: ca@taxease.com")
    print(f"    Password: CA123456!")
    print()
    print_info("Next Steps:")
    print("  1. Start your backend: cd ~/Documents/Projects/CA-final && source backend/venv/bin/activate && export PYTHONPATH=$PWD && uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001")
    print("  2. Access API docs: http://localhost:8001/docs")
    print("  3. Login with admin credentials above")
    print()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Initialize Tax-Ease Database")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm all prompts")
    parser.add_argument("--test-data", "-t", action="store_true", help="Create test users")
    parser.add_argument("--skip-drop", action="store_true", help="Skip dropping existing tables")
    args = parser.parse_args()
    
    # Print banner
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          Tax-Ease Database Initialization Script                  ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    # Get database info
    db_info = get_database_info()
    db_url = get_database_url()
    
    print_info(f"Target Database:")
    print(f"  Host: {db_info['host']}")
    print(f"  Port: {db_info['port']}")
    print(f"  Database: {db_info['database']}")
    print(f"  User: {db_info['user']}")
    print()
    
    # Confirmation
    if not args.yes and not args.skip_drop:
        print_warning("⚠️  WARNING: This will DELETE ALL EXISTING DATA in the database!")
        print_warning("⚠️  This action CANNOT be undone!")
        print()
        response = input(f"{Colors.YELLOW}Are you sure you want to continue? (yes/no): {Colors.ENDC}")
        if response.lower() != "yes":
            print_error("Operation cancelled by user")
            sys.exit(0)
        print()
    
    try:
        # Create engine
        print_info("Connecting to database...")
        engine = create_engine(db_url, echo=False)
        
        # Test connection
        if not test_connection(engine):
            sys.exit(1)
        
        # Drop all tables
        if not args.skip_drop:
            if not drop_all_tables(engine):
                sys.exit(1)
        
        # Create all tables
        if not create_all_tables(engine):
            sys.exit(1)
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create admin users
        create_admin_users(session)
        
        # Create test users if requested
        if args.test_data:
            create_test_users(session)
        
        # Verify setup
        verify_setup(session)
        
        # Close session
        session.close()
        
        # Print summary
        print_summary(db_info)
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All done! Your database is ready.{Colors.ENDC}\n")
        
    except KeyboardInterrupt:
        print()
        print_error("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
