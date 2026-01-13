# Database Initialization Script - Quick Reference

## 📋 Overview

The `init_database.py` script is a comprehensive database initialization tool that:
- ✅ Drops all existing tables (clean slate)
- ✅ Creates fresh schemas from `database/schemas_v2.py`
- ✅ Creates default admin and superadmin users
- ✅ Optionally creates test user accounts
- ✅ Verifies the setup

## 🚀 Quick Start

### Basic Usage (Interactive Mode)
```bash
cd ~/Documents/Projects/CA-final
python3 init_database.py
```

### Auto-Confirm Mode (No Prompts)
```bash
python3 init_database.py --yes
```

### With Test Users
```bash
python3 init_database.py --yes --test-data
```

### Skip Dropping Tables (Only Create)
```bash
python3 init_database.py --skip-drop
```

## 📊 What Gets Created

### Tables Created (13 tables):
1. **users** - Client user accounts
2. **admins** - Admin user accounts
3. **filings** - Tax filing records
4. **admin_filing_assignments** - Admin-to-filing assignments
5. **documents** - Document uploads
6. **payments** - Payment records
7. **notifications** - User notifications
8. **filing_timeline** - Filing event timeline
9. **audit_logs** - Audit trail for sensitive operations
10. **t1_forms** - T1 personal tax forms
11. **t1_answers** - T1 form answers (normalized)
12. **t1_sections_progress** - Section completion tracking
13. **email_threads** & **email_messages** - Email communication

### Admin Accounts Created:

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| **Superadmin** | superadmin@taxease.com | SuperAdmin123! | All (*) |
| **Admin** | admin@taxease.com | Admin123! | Standard admin |
| **CA** | ca@taxease.com | CA123456! | CA-specific |

### Test Users (with --test-data flag):

| Email | Password | Name |
|-------|----------|------|
| john.doe@example.com | User123! | John Doe |
| jane.smith@example.com | User123! | Jane Smith |
| test@taxease.com | Test123! | Test User |

## 🎯 Usage Examples

### Full Clean Install
```bash
# Drop everything and recreate with test data
python3 init_database.py --yes --test-data
```

### Production Setup
```bash
# Only admin accounts, no test users
python3 init_database.py --yes
```

### Development/Testing
```bash
# Interactive mode with test data
python3 init_database.py --test-data
```

## ⚠️ Important Notes

### ⚠️ WARNING
- This script will **DELETE ALL DATA** in your database
- This action **CANNOT BE UNDONE**
- Always backup important data before running
- Use `--skip-drop` flag to preserve existing data

### Requirements
- Python 3.8+
- PostgreSQL database
- Required packages: `sqlalchemy`, `passlib`, `python-dotenv`, `bcrypt`
- Valid `.env` file with database credentials

### Environment Variables Required
```bash
# In your .env file:
DATABASE_URL=postgresql://user:pass@host:port/database
# OR individual components:
DB_HOST=database-1.ct2g4wqam4oi.ca-central-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
```

## 🔍 Verification

The script automatically verifies the setup by:
1. Counting created tables
2. Listing all admin accounts
3. Listing all user accounts (if created)
4. Displaying summary with credentials

## 📝 Script Output

### Successful Run:
```
╔════════════════════════════════════════════════════════════════════╗
║          Tax-Ease Database Initialization Script                  ║
╚════════════════════════════════════════════════════════════════════╝

ℹ Target Database:
  Host: database-1.ct2g4wqam4oi.ca-central-1.rds.amazonaws.com
  Port: 5432
  Database: postgres
  User: postgres

==================================================
Step 1: Cleaning Database
==================================================

⚠ Found 13 tables to drop:
  • users
  • admins
  • filings
  ... (etc)

✓ All tables dropped successfully!

==================================================
Step 2: Creating Database Schema
==================================================

ℹ Creating tables from schemas_v2.py...
✓ Created 13 tables:
  • admin_filing_assignments
  • admins
  • audit_logs
  ... (etc)

==================================================
Step 3: Creating Admin Users
==================================================

✓ Created superadmin: superadmin@taxease.com
ℹ   Name: Super Admin
ℹ   Password: SuperAdmin123!
ℹ   ID: 12345678-1234-1234-1234-123456789012

✓ Created admin: admin@taxease.com
... (etc)

==================================================
Verification
==================================================

ℹ Total Admins: 3
  • superadmin@taxease.com (superadmin) - Super Admin
  • admin@taxease.com (admin) - Admin User
  • ca@taxease.com (admin) - CA Administrator

ℹ Total Users: 0

==================================================
Summary
==================================================

✓ Database initialization completed successfully!
```

## 🛠️ Troubleshooting

### Connection Issues
```bash
# Test connection first
python3 -c "from init_database import *; engine = create_engine(get_database_url()); test_connection(engine)"
```

### Module Not Found
```bash
# Make sure you're in project root and have activated venv
cd ~/Documents/Projects/CA-final
source backend/venv/bin/activate
```

### Permission Errors
```bash
# Check database user has proper permissions
# Or use superuser credentials in .env
```

## 🔗 Next Steps After Running

1. **Start Backend:**
   ```bash
   cd ~/Documents/Projects/CA-final
   source backend/venv/bin/activate
   export PYTHONPATH=$PWD
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Access API Documentation:**
   - Swagger UI: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc

3. **Test Admin Login:**
   - Use credentials from summary output
   - Email: superadmin@taxease.com
   - Password: SuperAdmin123!

4. **Verify Database:**
   ```bash
   # Using psql
   psql -h database-1.ct2g4wqam4oi.ca-central-1.rds.amazonaws.com -U postgres -d postgres
   
   # Check tables
   \dt
   
   # Check admin users
   SELECT id, email, name, role FROM admins;
   ```

## 📚 Related Files

- **Schema Definition:** `database/schemas_v2.py`
- **Environment Config:** `.env`
- **Backend Main:** `backend/app/main.py`
- **Setup Guide:** `AWS_RDS_DEPLOYMENT_GUIDE.md`

## 💡 Tips

1. **Development:** Use `--test-data` flag for quick testing
2. **Production:** Never use default passwords in production
3. **Backup:** Always backup before running in production
4. **Testing:** Run with `--skip-drop` to preserve existing data while adding new records
5. **Automation:** Add to CI/CD pipeline for automated testing environments

## 🆘 Getting Help

If you encounter issues:
1. Check `.env` file configuration
2. Verify database connectivity
3. Check PostgreSQL logs
4. Review script output for specific error messages
5. Ensure all Python dependencies are installed
