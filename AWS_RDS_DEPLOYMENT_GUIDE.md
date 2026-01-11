# AWS RDS Deployment - Quick Start Guide

## ✅ Completed Setup Steps

### 1. Database Configuration
- ✅ AWS RDS PostgreSQL database configured
- ✅ Connection string updated in `.env` file
- ✅ Database schemas created successfully (22 tables)
- ✅ Connection tested and verified

### 2. Database Details
```
Host: database-1.ct2g4wqam4oi.ca-central-1.rds.amazonaws.com
Database: postgres
Port: 5432
User: postgres
Status: ✅ CONNECTED (PostgreSQL 15.10)
```

### 3. Database Schema
The following tables have been created:
- users, admins, otp_codes
- tax_documents, t1_form_data
- admin_chat_messages
- documents, filings, notifications, payments
- email_threads, email_messages
- And 11 more supporting tables

## 🚀 Deployment Instructions

### Option 1: Fix Virtual Environment Permission Issue (Recommended)

Run these commands to fix the permission issue and deploy:

```bash
# Remove the problematic venv with sudo
cd /home/cyberdude/Documents/Projects/CA-final
sudo rm -rf backend/venv

# Create fresh virtual environment
python3 -m venv backend/venv

# Now run the deployment script
./deploy_ec2.sh
```

### Option 2: Manual Deployment (If script fails)

If the automated script continues to have issues, deploy manually:

```bash
cd /home/cyberdude/Documents/Projects/CA-final

# 1. Activate virtual environment  
source backend/venv/bin/activate

# 2. Install dependencies
pip install --no-cache-dir -r backend/requirements.txt

# 3. Create demo admin user
python3 create_demo_data_rds.py

# 4. Start the backend services
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔐 Test Credentials (To be created)

Once deployment is complete, you'll be able to create these accounts:

### Admin Account
```
Email: admin@taxease.com
Password: Admin123!
```

### Test User Account  
```
Email: test@taxease.com
Password: Test123!
```

## 📝 Create Demo Users

After fixing the venv issue, run this to create demo users:

```bash
python3 create_demo_data_rds.py
```

This will create:
- 2 admin accounts (superadmin and CA)
- 3 test user accounts

## 🔍 Verify Deployment

### Check Database Connection
```bash
python3 setup_aws_rds.py --test-only
```

### Check Tables
```bash
python3 << 'EOF'
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT', '5432')
)

cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
tables = cur.fetchall()

print(f"\n✅ Total tables: {len(tables)}")
for table in tables:
    print(f"  • {table[0]}")

cur.close()
conn.close()
EOF
```

## 🐛 Troubleshooting

### Issue: Permission Denied on venv files
**Solution:**
```bash
sudo rm -rf backend/venv
python3 -m venv backend/venv
```

### Issue: Cannot connect to AWS RDS
**Solution:**
1. Check security group allows your IP on port 5432
2. Verify DATABASE_URL in `.env` is correct
3. Test connection: `python3 setup_aws_rds.py --test-only`

### Issue: Missing dependencies
**Solution:**
```bash
source backend/venv/bin/activate
pip install --no-cache-dir -r backend/requirements.txt
```

## 📊 Current Status

| Component | Status |
|-----------|--------|
| AWS RDS Database | ✅ Connected |
| Database Schemas | ✅ Created (22 tables) |
| .env Configuration | ✅ Updated |
| Demo Users | ⏳ Pending (run create_demo_data_rds.py) |
| Backend Deployment | ⏳ Pending (fix venv issue first) |

## 🎯 Next Steps

1. **Fix Virtual Environment:**
   ```bash
   sudo rm -rf backend/venv
   python3 -m venv backend/venv
   ```

2. **Create Demo Users:**
   ```bash
   python3 create_demo_data_rds.py
   ```

3. **Run Deployment:**
   ```bash
   ./deploy_ec2.sh
   ```

4. **Verify Services:**
   - Backend API: http://localhost:8000/docs
   - Admin API: http://localhost:8001/docs
   - Client API: http://localhost:8002/docs

## 📁 Important Files

- `.env` - Database configuration (AWS RDS connection string)
- `setup_aws_rds.py` - Database setup and testing tool
- `create_demo_data_rds.py` - Creates demo users and admins
- `deploy_ec2.sh` - Automated deployment script
- `migrate_data.py` - Data migration tool (if needed)

## 🔗 AWS RDS Connection String

Your current DATABASE_URL (already configured in `.env`):
```
postgresql+asyncpg://postgres:Diamondaccount321@database-1.ct2g4wqam4oi.ca-central-1.rds.amazonaws.com:5432/postgres
```

✅ This is already set up and working!
