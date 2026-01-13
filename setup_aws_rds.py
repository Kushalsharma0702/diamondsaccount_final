
#!/usr/bin/env python3
"""
AWS RDS Database Setup Script
This script:
1. Tests connection to AWS RDS
2. Creates all necessary schemas
3. Optionally migrates data from local database
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# AWS RDS Connection
RDS_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', '5432')
}

# Local Database Connection (for migration)
LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'CA_Project',
    'user': 'postgres',
    'password': 'Kushal07',
    'port': '5432'
}


def test_connection(config, name):
    """Test database connection"""
    print(f"\n{'='*60}")
    print(f"Testing {name} Connection")
    print(f"{'='*60}")
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Port: {config['port']}")
    
    try:
        conn = psycopg2.connect(**config, connect_timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        cur.close()
        conn.close()
        
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {version[0][:50]}...")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def create_schemas(config):
    """Create all necessary database schemas"""
    print(f"\n{'='*60}")
    print("Creating Database Schemas")
    print(f"{'='*60}")
    
    try:
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Read schema files
        schema_files = [
            'database/schemas.py',
            'database/schemas_v2.py',
            'backend/database_constraints.sql'
        ]
        
        # First, let's create the core tables
        print("\n📝 Creating core tables...")
        
        core_schema = """
        -- Drop existing tables if they exist (CASCADE will drop dependent objects)
        DROP TABLE IF EXISTS t1_form_data CASCADE;
        DROP TABLE IF EXISTS tax_documents CASCADE;
        DROP TABLE IF EXISTS admin_chat_messages CASCADE;
        DROP TABLE IF EXISTS otp_codes CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS admins CASCADE;
        
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone_number VARCHAR(20) UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        
        -- Admins table
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            role VARCHAR(50) DEFAULT 'admin',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        
        -- OTP codes table
        CREATE TABLE IF NOT EXISTS otp_codes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            email VARCHAR(255),
            phone_number VARCHAR(20),
            otp_code VARCHAR(10) NOT NULL,
            purpose VARCHAR(50) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            is_used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Tax documents table
        CREATE TABLE IF NOT EXISTS tax_documents (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            document_type VARCHAR(100) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size INTEGER,
            mime_type VARCHAR(100),
            encrypted BOOLEAN DEFAULT FALSE,
            tax_year INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Admin chat messages table
        CREATE TABLE IF NOT EXISTS admin_chat_messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            admin_id INTEGER,
            message TEXT NOT NULL,
            sender_type VARCHAR(20) NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE SET NULL
        );
        
        -- T1 Form Data table
        CREATE TABLE IF NOT EXISTS t1_form_data (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            tax_year INTEGER NOT NULL,
            form_data JSONB NOT NULL,
            filing_status VARCHAR(50) DEFAULT 'draft',
            last_saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, tax_year)
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
        CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);
        CREATE INDEX IF NOT EXISTS idx_otp_email ON otp_codes(email);
        CREATE INDEX IF NOT EXISTS idx_otp_phone ON otp_codes(phone_number);
        CREATE INDEX IF NOT EXISTS idx_otp_expires ON otp_codes(expires_at);
        CREATE INDEX IF NOT EXISTS idx_tax_docs_user ON tax_documents(user_id);
        CREATE INDEX IF NOT EXISTS idx_tax_docs_year ON tax_documents(tax_year);
        CREATE INDEX IF NOT EXISTS idx_chat_user ON admin_chat_messages(user_id);
        CREATE INDEX IF NOT EXISTS idx_chat_admin ON admin_chat_messages(admin_id);
        CREATE INDEX IF NOT EXISTS idx_t1_user_year ON t1_form_data(user_id, tax_year);
        
        -- Create updated_at trigger function
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        -- Add triggers for updated_at
        DROP TRIGGER IF EXISTS update_users_updated_at ON users;
        CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        
        DROP TRIGGER IF EXISTS update_admins_updated_at ON admins;
        CREATE TRIGGER update_admins_updated_at
            BEFORE UPDATE ON admins
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        
        DROP TRIGGER IF EXISTS update_tax_documents_updated_at ON tax_documents;
        CREATE TRIGGER update_tax_documents_updated_at
            BEFORE UPDATE ON tax_documents
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        
        DROP TRIGGER IF EXISTS update_t1_form_data_updated_at ON t1_form_data;
        CREATE TRIGGER update_t1_form_data_updated_at
            BEFORE UPDATE ON t1_form_data
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        
        # Execute core schema
        cur.execute(core_schema)
        print("✅ Core tables created successfully")
        
        # Verify tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print(f"\n📊 Total tables created: {len(tables)}")
        for table in tables:
            print(f"  • {table[0]}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Schema creation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def migrate_data(source_config, target_config):
    """Migrate data from local database to AWS RDS"""
    print(f"\n{'='*60}")
    print("Migrating Data from Local to AWS RDS")
    print(f"{'='*60}")
    
    try:
        # Connect to both databases
        print("📡 Connecting to source database...")
        source_conn = psycopg2.connect(**source_config)
        source_cur = source_conn.cursor()
        
        print("📡 Connecting to target database...")
        target_conn = psycopg2.connect(**target_config)
        target_conn.autocommit = False
        target_cur = target_conn.cursor()
        
        # Tables to migrate (in order of dependencies)
        tables = ['users', 'admins', 'otp_codes', 'tax_documents', 'admin_chat_messages', 't1_form_data']
        
        total_migrated = 0
        
        for table in tables:
            try:
                # Check if table exists in source
                source_cur.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """)
                
                if not source_cur.fetchone()[0]:
                    print(f"⚠️  Table '{table}' not found in source database, skipping...")
                    continue
                
                # Get column names
                source_cur.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    ORDER BY ordinal_position;
                """)
                columns = [row[0] for row in source_cur.fetchall()]
                
                # Fetch all data from source
                source_cur.execute(f'SELECT * FROM {table}')
                rows = source_cur.fetchall()
                
                if not rows:
                    print(f"⚠️  No data in '{table}' table")
                    continue
                
                # Clear target table
                target_cur.execute(f'TRUNCATE TABLE {table} RESTART IDENTITY CASCADE')
                
                # Insert data into target
                columns_str = ', '.join(columns)
                placeholders = ', '.join(['%s'] * len(columns))
                insert_query = f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders})'
                
                target_cur.executemany(insert_query, rows)
                target_conn.commit()
                
                print(f"✅ Migrated {len(rows)} rows from '{table}'")
                total_migrated += len(rows)
                
            except Exception as e:
                print(f"❌ Error migrating table '{table}': {e}")
                target_conn.rollback()
                continue
        
        # Reset sequences
        print("\n🔄 Resetting sequences...")
        for table in tables:
            try:
                target_cur.execute(f"""
                    SELECT setval(pg_get_serial_sequence('{table}', 'id'), 
                    COALESCE((SELECT MAX(id) FROM {table}), 1), false);
                """)
                target_conn.commit()
            except Exception as e:
                print(f"⚠️  Could not reset sequence for '{table}': {e}")
        
        source_cur.close()
        source_conn.close()
        target_cur.close()
        target_conn.close()
        
        print(f"\n✅ Migration completed! Total rows migrated: {total_migrated}")
        return True
        
    except Exception as e:
        print(f"❌ Data migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='AWS RDS Database Setup')
    parser.add_argument('--test-only', action='store_true', help='Only test connections')
    parser.add_argument('--create-schema', action='store_true', help='Create schemas')
    parser.add_argument('--migrate', action='store_true', help='Migrate data from local to RDS')
    parser.add_argument('--all', action='store_true', help='Run all steps')
    
    args = parser.parse_args()
    
    if not any([args.test_only, args.create_schema, args.migrate, args.all]):
        args.all = True
    
    print("\n" + "="*60)
    print("AWS RDS Database Setup Tool")
    print("="*60)
    
    # Step 1: Test AWS RDS connection
    if args.all or args.test_only or args.create_schema or args.migrate:
        if not test_connection(RDS_CONFIG, "AWS RDS"):
            print("\n❌ Cannot connect to AWS RDS. Please check your configuration.")
            sys.exit(1)
    
    # Step 2: Test local connection (if migrating)
    if args.all or args.migrate:
        print("\n⚠️  Testing local database connection for migration...")
        if not test_connection(LOCAL_CONFIG, "Local PostgreSQL"):
            print("\n⚠️  Cannot connect to local database. Migration will be skipped.")
            args.migrate = False
    
    if args.test_only:
        print("\n✅ Connection tests completed!")
        return
    
    # Step 3: Create schemas
    if args.all or args.create_schema:
        if not create_schemas(RDS_CONFIG):
            print("\n❌ Schema creation failed!")
            sys.exit(1)
    
    # Step 4: Migrate data
    if args.all or args.migrate:
        response = input("\n⚠️  This will OVERWRITE all data in AWS RDS. Continue? (yes/no): ")
        if response.lower() == 'yes':
            if not migrate_data(LOCAL_CONFIG, RDS_CONFIG):
                print("\n❌ Data migration failed!")
                sys.exit(1)
        else:
            print("\n❌ Migration cancelled by user")
    
    print("\n" + "="*60)
    print("✅ AWS RDS Setup Completed Successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Test your application with the new database")
    print("2. Update any hardcoded connection strings")
    print("3. Run ./deploy_ec2.sh to deploy with AWS RDS")
    print("")


if __name__ == '__main__':
    main()
