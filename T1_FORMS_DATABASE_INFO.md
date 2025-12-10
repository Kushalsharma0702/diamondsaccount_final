# T1 Forms Database Information

## 📊 Database & Table Details

### Database
- **Name:** `taxease_db`
- **Type:** PostgreSQL
- **Location:** `localhost:5432`
- **Connection:** Both client backend and admin dashboard use the same database

### Table
- **Table Name:** `t1_personal_forms`
- **Schema:** Public schema
- **Primary Key:** `id` (String, format: `T1_{timestamp}`)

## 📋 Table Structure

```sql
CREATE TABLE t1_personal_forms (
    id VARCHAR(50) PRIMARY KEY,           -- Format: T1_{timestamp}
    user_id UUID NOT NULL,                -- Foreign key to users.id
    tax_year INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',   -- draft, in_progress, review, submitted, processed
    
    -- Encrypted form data
    encrypted_form_data BYTEA,
    encryption_metadata TEXT,
    is_encrypted BOOLEAN DEFAULT TRUE,
    
    -- Basic info (unencrypted for indexing)
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    sin_encrypted BOOLEAN DEFAULT TRUE,
    
    -- Form completion flags
    has_foreign_property BOOLEAN DEFAULT FALSE,
    has_medical_expenses BOOLEAN DEFAULT FALSE,
    has_charitable_donations BOOLEAN DEFAULT FALSE,
    has_moving_expenses BOOLEAN DEFAULT FALSE,
    is_self_employed BOOLEAN DEFAULT FALSE,
    is_first_home_buyer BOOLEAN DEFAULT FALSE,
    is_first_time_filer BOOLEAN DEFAULT FALSE,
    
    -- Income fields (calculated from encrypted data)
    employment_income FLOAT DEFAULT 0.0,
    self_employment_income FLOAT DEFAULT 0.0,
    investment_income FLOAT DEFAULT 0.0,
    other_income FLOAT DEFAULT 0.0,
    total_income FLOAT DEFAULT 0.0,
    
    -- Deductions
    rrsp_contributions FLOAT DEFAULT 0.0,
    charitable_donations FLOAT DEFAULT 0.0,
    
    -- Tax calculations
    federal_tax FLOAT DEFAULT 0.0,
    provincial_tax FLOAT DEFAULT 0.0,
    total_tax FLOAT DEFAULT 0.0,
    refund_or_owing FLOAT DEFAULT 0.0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE
);
```

## 📊 Current Data

**Total Forms:** 3

### Recent Forms:
1. **ID:** `T1_1762995957365`
   - **User:** `a8fb8ab8-4ba4-4b9e-b709-3d66ce1f1476`
   - **Tax Year:** 2025
   - **Status:** `draft`
   - **Name:** John Doe
   - **Email:** john.test@example.com
   - **Created:** 2025-11-13 06:35:57

2. **ID:** `T1_1762445908993`
   - **User:** `d94d33e2-015f-44bb-9b9e-ac40c0099387`
   - **Tax Year:** 2025
   - **Status:** `submitted`
   - **Name:** Updated John Doe
   - **Email:** john.doe@example.com
   - **Created:** 2025-11-06 21:48:28

3. **ID:** `T1_1762445820513`
   - **User:** `d94d33e2-015f-44bb-9b9e-ac40c0099387`
   - **Tax Year:** 2025
   - **Status:** `submitted`
   - **Name:** Updated John Doe
   - **Email:** john.doe@example.com
   - **Created:** 2025-11-06 21:47:00

## 🔗 Relationships

- **Foreign Key:** `user_id` → `users.id`
- **Join:** `LEFT JOIN users ON t1_personal_forms.user_id = users.id`

## 📡 Admin Dashboard Access

### Backend Endpoint
- **URL:** `http://localhost:8002/api/v1/t1-forms`
- **Method:** `GET`
- **Authentication:** Required (Bearer token)
- **Query Parameters:**
  - `client_id` (optional): Filter by user ID
  - `client_email` (optional): Filter by email
  - `status_filter` (optional): Filter by status
  - `limit` (default: 20): Number of results
  - `offset` (default: 0): Pagination offset

### Example Query
```bash
# Get all forms
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/api/v1/t1-forms

# Filter by status
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8002/api/v1/t1-forms?status_filter=submitted"

# Filter by email
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8002/api/v1/t1-forms?client_email=john.doe@example.com"
```

## 🚀 Admin Dashboard URLs

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8002/api/v1
- **API Docs:** http://localhost:8002/docs
- **T1 Forms Endpoint:** http://localhost:8002/api/v1/t1-forms

## 🔍 Direct Database Query

To query directly from PostgreSQL:
```sql
-- Count forms
SELECT COUNT(*) FROM t1_personal_forms;

-- View all forms
SELECT 
    id, 
    user_id, 
    tax_year, 
    status, 
    first_name, 
    last_name, 
    email,
    created_at
FROM t1_personal_forms
ORDER BY created_at DESC;

-- Join with users table
SELECT 
    t1.id,
    t1.tax_year,
    t1.status,
    t1.first_name,
    t1.last_name,
    COALESCE(t1.email, u.email) as client_email,
    t1.created_at
FROM t1_personal_forms t1
LEFT JOIN users u ON t1.user_id = u.id
ORDER BY t1.created_at DESC;
```

## ✅ Status

- ✅ Database: `taxease_db` exists
- ✅ Table: `t1_personal_forms` exists
- ✅ Data: 3 forms found
- ✅ Admin Backend: Running on port 8002
- ✅ Admin Frontend: Running on port 5173
- ✅ T1 Forms Endpoint: Configured and ready

## 📝 Next Steps

1. Login to admin dashboard: http://localhost:5173
2. Navigate to T1 Forms (may need to add to sidebar)
3. View forms in admin panel
4. Filter by client, status, or email

