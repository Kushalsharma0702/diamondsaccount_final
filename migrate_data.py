#!/usr/bin/env python3
"""
Smart Data Migration Script
Handles schema differences between local and AWS RDS databases
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# AWS RDS Connection
RDS_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', '5432')
}

# Local Database Connection
LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'CA_Project',
    'user': 'postgres',
    'password': 'Kushal07',
    'port': '5432'
}


def get_table_columns(conn, table_name):
    """Get columns for a table"""
    cur = conn.cursor()
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        ORDER BY ordinal_position;
    """)
    columns = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    return columns


def migrate_table_smart(source_conn, target_conn, table_name, column_mapping=None):
    """Migrate a table with smart column mapping"""
    source_cur = source_conn.cursor(cursor_factory=RealDictCursor)
    target_cur = target_conn.cursor()
    
    try:
        # Get columns from both databases
        source_columns = get_table_columns(source_conn, table_name)
        target_columns = get_table_columns(target_conn, table_name)
        
        if not source_columns:
            print(f"⚠️  Table '{table_name}' not found in source database")
            return 0
        
        if not target_columns:
            print(f"⚠️  Table '{table_name}' not found in target database")
            return 0
        
        # Find common columns
        common_columns = set(source_columns.keys()) & set(target_columns.keys())
        
        # Apply custom column mapping
        if column_mapping:
            for source_col, target_col in column_mapping.items():
                if source_col in source_columns and target_col in target_columns:
                    common_columns.discard(source_col)
                    common_columns.add(source_col)
        
        if not common_columns and not column_mapping:
            print(f"⚠️  No common columns found for table '{table_name}'")
            return 0
        
        # Fetch data from source
        source_cur.execute(f'SELECT * FROM {table_name}')
        rows = source_cur.fetchall()
        
        if not rows:
            print(f"⚠️  No data in '{table_name}' table")
            return 0
        
        # Clear target table
        target_cur.execute(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE')
        
        migrated = 0
        for row in rows:
            # Build insert statement with mapped columns
            if column_mapping:
                target_cols = []
                values = []
                
                for source_col in common_columns:
                    target_col = column_mapping.get(source_col, source_col)
                    if target_col in target_columns and source_col in row:
                        target_cols.append(target_col)
                        values.append(row[source_col])
                
                # Add custom mappings
                for source_col, target_col in column_mapping.items():
                    if source_col not in common_columns and source_col in row and target_col in target_columns:
                        target_cols.append(target_col)
                        values.append(row[source_col])
            else:
                target_cols = list(common_columns)
                values = [row[col] for col in target_cols]
            
            if target_cols:
                cols_str = ', '.join(target_cols)
                placeholders = ', '.join(['%s'] * len(values))
                insert_query = f'INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})'
                
                try:
                    target_cur.execute(insert_query, values)
                    migrated += 1
                except Exception as e:
                    print(f"  ⚠️  Error inserting row: {e}")
                    continue
        
        target_conn.commit()
        print(f"✅ Migrated {migrated} rows to '{table_name}'")
        return migrated
        
    except Exception as e:
        print(f"❌ Error migrating table '{table_name}': {e}")
        target_conn.rollback()
        return 0
    finally:
        source_cur.close()
        target_cur.close()


def main():
    print("\n" + "="*60)
    print("Smart Data Migration Tool")
    print("="*60)
    
    # Connect to databases
    print("\n📡 Connecting to databases...")
    try:
        source_conn = psycopg2.connect(**LOCAL_CONFIG)
        print("✅ Connected to local database")
    except Exception as e:
        print(f"❌ Cannot connect to local database: {e}")
        sys.exit(1)
    
    try:
        target_conn = psycopg2.connect(**RDS_CONFIG)
        target_conn.autocommit = False
        print("✅ Connected to AWS RDS database")
    except Exception as e:
        print(f"❌ Cannot connect to AWS RDS: {e}")
        sys.exit(1)
    
    # Define column mappings for tables with different schemas
    table_mappings = {
        'users': {
            'phone': 'phone_number',  # Map 'phone' to 'phone_number'
        },
        'admins': {
            'name': 'first_name',  # Map 'name' to 'first_name'
        }
    }
    
    # Tables to migrate (in order of dependencies)
    tables_to_migrate = [
        'users',
        'admins',
        'otp_codes',
        'tax_documents',
        'admin_chat_messages',
        't1_form_data',
        'documents',
        'filings',
        'notifications',
        'payments',
        'email_threads',
        'email_messages'
    ]
    
    total_migrated = 0
    
    print("\n📦 Starting data migration...")
    print("="*60)
    
    for table in tables_to_migrate:
        mapping = table_mappings.get(table, None)
        count = migrate_table_smart(source_conn, target_conn, table, mapping)
        total_migrated += count
    
    # Reset sequences
    print("\n🔄 Resetting sequences...")
    target_cur = target_conn.cursor()
    for table in tables_to_migrate:
        try:
            target_cur.execute(f"""
                SELECT setval(pg_get_serial_sequence('{table}', 'id'), 
                COALESCE((SELECT MAX(id) FROM {table}), 1), false);
            """)
            target_conn.commit()
        except Exception as e:
            pass  # Table might not have a sequence
    target_cur.close()
    
    source_conn.close()
    target_conn.close()
    
    print("\n" + "="*60)
    print(f"✅ Migration Completed Successfully!")
    print(f"📊 Total rows migrated: {total_migrated}")
    print("="*60)
    print("\nYour AWS RDS database is now ready!")
    print("You can now run: ./deploy_ec2.sh")


if __name__ == '__main__':
    response = input("\n⚠️  This will OVERWRITE data in AWS RDS. Continue? (yes/no): ")
    if response.lower() == 'yes':
        main()
    else:
        print("\n❌ Migration cancelled")
