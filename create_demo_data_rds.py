#!/usr/bin/env python3
"""
Create demo users and admin accounts in AWS RDS
"""

import os
import sys
from passlib.context import CryptContext
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AWS RDS Connection
RDS_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', '5432')
}


def create_admin_users(conn):
    """Create admin users"""
    print("\n" + "="*60)
    print("Creating Admin Users")
    print("="*60)
    
    cur = conn.cursor()
    
    admin_users = [
        {
            'email': 'admin@taxease.com',
            'password': 'Admin123!',
            'first_name': 'Super',
            'last_name': 'Admin',
            'role': 'superadmin'
        },
        {
            'email': 'ca@taxease.com',
            'password': 'CA123456!',
            'first_name': 'CA',
            'last_name': 'Administrator',
            'role': 'admin'
        }
    ]
    
    for admin in admin_users:
        password_hash = pwd_context.hash(admin['password'])
        
        try:
            cur.execute("""
                INSERT INTO admins (email, password_hash, first_name, last_name, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE 
                SET password_hash = EXCLUDED.password_hash,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    role = EXCLUDED.role
                RETURNING id;
            """, (
                admin['email'],
                password_hash,
                admin['first_name'],
                admin['last_name'],
                admin['role'],
                True,
                datetime.now()
            ))
            
            admin_id = cur.fetchone()[0]
            conn.commit()
            
            print(f"✅ Created admin: {admin['email']}")
            print(f"   Password: {admin['password']}")
            print(f"   ID: {admin_id}")
            
        except Exception as e:
            print(f"❌ Error creating admin {admin['email']}: {e}")
            conn.rollback()
    
    cur.close()


def create_demo_users(conn):
    """Create demo client users"""
    print("\n" + "="*60)
    print("Creating Demo Client Users")
    print("="*60)
    
    cur = conn.cursor()
    
    demo_users = [
        {
            'email': 'john.doe@example.com',
            'password': 'User123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+14165551234'
        },
        {
            'email': 'jane.smith@example.com',
            'password': 'User123!',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone_number': '+14165555678'
        },
        {
            'email': 'test@taxease.com',
            'password': 'Test123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+14165559999'
        }
    ]
    
    for user in demo_users:
        password_hash = pwd_context.hash(user['password'])
        
        try:
            cur.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name, phone_number, 
                                  is_active, is_verified, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE 
                SET password_hash = EXCLUDED.password_hash,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    phone_number = EXCLUDED.phone_number
                RETURNING id;
            """, (
                user['email'],
                password_hash,
                user['first_name'],
                user['last_name'],
                user['phone_number'],
                True,
                True,
                datetime.now()
            ))
            
            user_id = cur.fetchone()[0]
            conn.commit()
            
            print(f"✅ Created user: {user['email']}")
            print(f"   Password: {user['password']}")
            print(f"   ID: {user_id}")
            
        except Exception as e:
            print(f"❌ Error creating user {user['email']}: {e}")
            conn.rollback()
    
    cur.close()


def verify_data(conn):
    """Verify created data"""
    print("\n" + "="*60)
    print("Verifying Created Data")
    print("="*60)
    
    cur = conn.cursor()
    
    # Count admins
    cur.execute("SELECT COUNT(*) FROM admins;")
    admin_count = cur.fetchone()[0]
    print(f"\n📊 Total Admins: {admin_count}")
    
    # Count users
    cur.execute("SELECT COUNT(*) FROM users;")
    user_count = cur.fetchone()[0]
    print(f"📊 Total Users: {user_count}")
    
    # List admins
    cur.execute("SELECT id, email, first_name, last_name, role FROM admins ORDER BY id;")
    admins = cur.fetchall()
    print(f"\n👥 Admins:")
    for admin in admins:
        print(f"   ID {admin[0]}: {admin[1]} ({admin[2]} {admin[3]}) - {admin[4]}")
    
    # List users
    cur.execute("SELECT id, email, first_name, last_name FROM users ORDER BY id;")
    users = cur.fetchall()
    print(f"\n👤 Users:")
    for user in users:
        print(f"   ID {user[0]}: {user[1]} ({user[2]} {user[3]})")
    
    cur.close()


def main():
    print("\n" + "="*60)
    print("AWS RDS Demo Data Setup")
    print("="*60)
    
    # Connect to AWS RDS
    print("\n📡 Connecting to AWS RDS...")
    try:
        conn = psycopg2.connect(**RDS_CONFIG)
        print("✅ Connected to AWS RDS")
    except Exception as e:
        print(f"❌ Cannot connect to AWS RDS: {e}")
        sys.exit(1)
    
    # Create users
    create_admin_users(conn)
    create_demo_users(conn)
    verify_data(conn)
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Demo Data Setup Complete!")
    print("="*60)
    print("\n🔐 Admin Credentials:")
    print("   Email: admin@taxease.com")
    print("   Password: Admin123!")
    print("")
    print("   Email: ca@taxease.com")
    print("   Password: CA123456!")
    print("\n👤 Test User Credentials:")
    print("   Email: test@taxease.com")
    print("   Password: Test123!")
    print("\n🚀 Your AWS RDS is ready for deployment!")
    print("   Run: ./deploy_ec2.sh")
    print("")


if __name__ == '__main__':
    main()
