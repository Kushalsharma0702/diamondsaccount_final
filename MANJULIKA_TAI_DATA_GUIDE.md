# 🎭 Manjulika Tai - Test Data Creation Guide

## Overview

This guide helps you insert comprehensive T1 form test data for user "Manjulika Tai" directly into your AWS RDS database.

---

## 📁 Files Created

1. **Python Script:** `create_manjulika_tai_data.py` - Can be run from EC2 with RDS access
2. **SQL Script:** `insert_manjulika_tai_data.sql` - Direct SQL for RDS (Recommended)

---

## 🚀 Method 1: Run SQL Script on AWS RDS (RECOMMENDED)

### Option A: Using AWS RDS Query Editor

1. Open AWS Console → RDS → Query Editor
2. Select your database: `database-1.ct2g4wqam4oi.ca-central-1.rds.amazonaws.com`
3. Connect with credentials:
   - Username: `postgres`
   - Password: `Diamondaccount321`
   - Database: `postgres`
4. Copy and paste the contents of `insert_manjulika_tai_data.sql`
5. Click "Run"

### Option B: Using psql from EC2

```bash
# SSH into your EC2 instance that has RDS access
ssh -i your-key.pem ec2-user@your-ec2-ip

# Copy the SQL file to EC2
scp -i your-key.pem insert_manjulika_tai_data.sql ec2-user@your-ec2-ip:~/

# On EC2, run the SQL script
psql -h database-1.ct2g4wqam4oi.ca-central-1.rds.amazonaws.com \
     -U postgres \
     -d postgres \
     -f ~/insert_manjulika_tai_data.sql
```

### Option C: Using DBeaver/pgAdmin

1. Connect to your RDS instance
2. Open SQL Editor
3. Paste contents of `insert_manjulika_tai_data.sql`
4. Execute

---

## 🚀 Method 2: Run Python Script from EC2

```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Copy script to EC2
scp -i your-key.pem create_manjulika_tai_data.py ec2-user@your-ec2-ip:~/
scp -i your-key.pem .env ec2-user@your-ec2-ip:~/

# On EC2, install dependencies
pip3 install sqlalchemy psycopg2-binary passlib bcrypt python-dotenv

# Run the script
python3 create_manjulika_tai_data.py
```

---

## 📊 What Gets Created

### 👤 User Account
- **Email:** manjulika.tai@example.com
- **Password:** ManjulikaTai@2024!
- **Name:** Manjulika Devi Tai
- **Phone:** +1-416-555-9876
- **SIN:** 987654321
- **DOB:** August 15, 1985
- **Address:** 123 Haunted Mansion Drive, Apt 666, Toronto, ON M5H 2N2
- **Marital Status:** Married
- **Canadian Citizen:** Yes

### 💑 Spouse Information
- **Name:** Vikram Singh Rathore
- **SIN:** 876543210
- **DOB:** March 20, 1983

### 👶 Children (2)
1. **Chotu Ram Rathore** - Born June 10, 2015 (SIN: 765432109)
2. **Pinky Kumari Rathore** - Born September 25, 2018 (SIN: 654321098)

### 📄 Filing Details
- **Tax Year:** 2024
- **Status:** In Preparation
- **Assessment Fee:** $299.99
- **Payment Status:** Pending

### 📋 T1 Form - Comprehensive Data

#### 1. Foreign Property (2 Properties)
- Real Estate in Mumbai, India - $500,000
- US Stocks (Apple Inc.) - $133,200

#### 2. Medical Expenses (3 Entries)
- Dental Surgery - $1,700 total
- Pediatric Eye Surgery - $2,800 total  
- Physiotherapy - $1,500 total

#### 3. Work From Home Expenses
- Total House Area: 1,800 sq.ft.
- Work Area: 200 sq.ft.
- Rent: $24,000/year
- Utilities: $5,760/year
- Insurance: $1,200/year

#### 4. Daycare Expenses (2 Providers)
- Little Angels Daycare - $8,500 (48 weeks)
- After School Program - $3,200 (40 weeks)

#### 5. Province Filer Details (Ontario)
- Rent at current address
- 12 months residence

#### 6. Employment Income
- Employer: Haunted Spirits Inc.
- Income: $85,000
- Deductions: CPP, EI, RPP, Union Dues

#### 7. Investment Income
- Interest: $1,250
- Dividends: $3,400

#### 8. Contributions
- RRSP: $15,000
- TFSA: $6,500
- Charitable Donations: $2,500

---

## ✅ Verification Steps

After running the script, verify the data:

### SQL Verification

```sql
-- Check user
SELECT * FROM users WHERE email = 'manjulika.tai@example.com';

-- Check filing
SELECT f.*, u.email 
FROM filings f
JOIN users u ON f.user_id = u.id
WHERE u.email = 'manjulika.tai@example.com';

-- Check T1 form and answers count
SELECT 
    t.id,
    t.status,
    t.completion_percentage,
    COUNT(a.id) as total_answers
FROM t1_forms t
JOIN users u ON t.user_id = u.id
LEFT JOIN t1_answers a ON t.id = a.t1_form_id
WHERE u.email = 'manjulika.tai@example.com'
GROUP BY t.id, t.status, t.completion_percentage;

-- View sample answers
SELECT field_key, value_text, value_numeric, value_boolean
FROM t1_answers
WHERE t1_form_id IN (
    SELECT id FROM t1_forms 
    WHERE user_id = (
        SELECT id FROM users WHERE email = 'manjulika.tai@example.com'
    )
)
LIMIT 20;
```

### API Verification

```bash
# Login
curl -X POST http://your-api/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manjulika.tai@example.com",
    "password": "ManjulikaTai@2024!"
  }'

# Get user's filings
curl -X GET http://your-api/api/v1/filings \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎯 Test Scenarios

Once data is inserted, you can test:

1. ✅ **User Login** - Login with Manjulika's credentials
2. ✅ **View T1 Form** - See all filled sections
3. ✅ **Edit Sections** - Modify any subform
4. ✅ **View Subforms** - Check all complex data (arrays, nested objects)
5. ✅ **Progress Tracking** - See 85% completion
6. ✅ **Submit Form** - Change status from draft to submitted
7. ✅ **Admin Review** - View as admin user
8. ✅ **Documents** - Attach required documents
9. ✅ **Payment** - Process assessment fee payment

---

## 🐛 Troubleshooting

### Issue: Connection timeout
**Solution:** Run from EC2 instance with VPC access to RDS

### Issue: User already exists
**Solution:** Delete existing user first:
```sql
DELETE FROM users WHERE email = 'manjulika.tai@example.com';
```

### Issue: Foreign key constraint error
**Solution:** Ensure `users` and `filings` tables exist and schema is correct

### Issue: UUID generation error
**Solution:** Use PostgreSQL 13+ or install `uuid-ossp` extension:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 📈 Data Statistics

- **Total Tables Affected:** 4 (users, filings, t1_forms, t1_answers, t1_section_progress)
- **Total Records Created:** ~60+ records
- **T1 Fields Populated:** ~50+ fields
- **Completion Level:** 85%
- **Subforms with Data:** 6 (Foreign Property, Medical, WFH, Daycare, Province, Employment)

---

## 🔐 Login Credentials

```
Email:    manjulika.tai@example.com
Password: ManjulikaTai@2024!
```

**Important:** Change password after first login in production!

---

## 📝 Notes

- All monetary values are in CAD
- All dates follow ISO format (YYYY-MM-DD)
- Arrays and complex data stored as JSONB
- Form status is "draft" - ready for editing/submission
- No admin review yet - ready for admin assignment

---

**Status:** ✅ Ready to Run  
**Last Updated:** January 22, 2026
