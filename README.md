# Tax-Ease Backend - PostgreSQL + FastAPI Monolith

A production-ready, low-cost, local-first backend for the Tax-Ease tax filing platform. Supports both client (Flutter) and admin (React) dashboards.

## Architecture Overview

### Design Principles
- **Minimal & Fast**: Optimized for read-heavy admin dashboards
- **Low-Cost**: PostgreSQL only, local filesystem storage (no S3)
- **Flexible**: JSONB for tax form data (handles yearly T1 changes)
- **Monolithic**: Single FastAPI application (no microservices)
- **Production-Ready**: RBAC, JWT auth, proper error handling

### Technology Stack
- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with JSONB
- **Authentication**: JWT tokens (access + refresh)
- **Storage**: Local filesystem (AWS-ready for later migration)
- **ORM**: SQLAlchemy 2.0

## Database Schema

### Core Tables

#### `users`
Client user accounts with email/password authentication.

#### `admins`
Admin and superadmin accounts with role-based permissions.

#### `clients`
Client records linked to users. Denormalized fields for fast queries (name, email, status, payment_status).

#### `admin_client_map`
Many-to-many mapping: Admins assigned to clients.

#### `tax_returns`
Tax return records (T1 forms). Uses **JSONB** for flexible form data structure.

**Key Design Decision**: JSONB `form_data` column stores the entire T1 form structure, allowing:
- Yearly T1 form changes without schema migrations
- Flexible section data (personal_info, foreign_property, moving_expenses, etc.)
- Quick access flags denormalized for filtering

#### `tax_sections`
Tax form sections for organizing documents and data. Also uses JSONB for section-specific data.

#### `documents`
Document files with local filesystem paths. Organized by `section_name`.

#### `payments`
Payment records and payment requests.

#### `notifications`
Notifications for clients and admins.

### Why JSONB?

1. **Flexibility**: T1 forms change yearly. JSONB allows schema evolution without migrations.
2. **Performance**: PostgreSQL JSONB is indexed (GIN indexes) and queryable.
3. **Cost**: No need for separate NoSQL database.
4. **Simplicity**: Single database, single query pattern.

### Indexes

Optimized for common queries:
- Client status + filing year
- Payment status
- Document client + section
- JSONB GIN indexes for form_data queries

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- pip

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taxease
DB_USER=postgres
DB_PASSWORD=postgres

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# File Storage
STORAGE_PATH=./storage/uploads
MAX_FILE_SIZE_MB=10

# OTP Configuration
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6

# Email (optional for OTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@taxease.com
```

### 3. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE taxease;

# Exit
\q
```

### 4. Initialize Schema

```bash
# Option 1: Run schemas.py directly
python database/schemas.py

# Option 2: Schema is auto-created on first startup
# (see main.py startup_event)
```

### 5. Run Backend

```bash
cd backend
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`

## API Endpoints

### Authentication

#### `POST /api/v1/auth/login`
Login user (client or admin). Returns JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### `POST /api/v1/auth/otp/send`
Send OTP for email verification or password reset.

**Request:**
```json
{
  "email": "user@example.com",
  "purpose": "email_verification"
}
```

#### `POST /api/v1/auth/otp/verify`
Verify OTP code.

**Request:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "purpose": "email_verification"
}
```

### Client Routes

#### `POST /api/v1/client/profile`
Update client profile (personal information).

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "personalInfo": {
    "firstName": "John",
    "lastName": "Doe",
    "sin": "123456789",
    "email": "john@example.com",
    "phoneNumber": "123-456-7890",
    "address": "123 Main St",
    "maritalStatus": "single"
  }
}
```

#### `POST /api/v1/client/tax-return`
Create or update tax return (T1 form).

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "formData": {
    "status": "draft",
    "personalInfo": {...},
    "hasForeignProperty": false,
    "hasMedicalExpenses": true,
    "hasCharitableDonations": false,
    "hasMovingExpenses": false,
    "isSelfEmployed": true,
    "selfEmployment": {
      "businessTypes": ["uber"],
      "uberBusiness": {...}
    },
    "uploadedDocuments": {
      "T2202 Form": "t2202_2024.pdf"
    }
  }
}
```

#### `GET /api/v1/client/status`
Get client status (filing status, payment status, etc.).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "status": "under_review",
  "payment_status": "pending",
  "filing_year": 2024,
  "total_amount": 500.0,
  "paid_amount": 0.0,
  "client_id": "uuid-here"
}
```

### Document Routes

#### `POST /api/v1/documents/upload`
Upload a document file.

**Headers:** `Authorization: Bearer <token>`

**Form Data:**
- `file`: File (multipart/form-data)
- `section`: Optional section name
- `document_type`: Type (e.g., "receipt", "form")

#### `GET /api/v1/documents/client/{client_id}`
Get all documents for a client.

**Headers:** `Authorization: Bearer <token>`

#### `GET /api/v1/documents/section/{section_name}`
Get documents for a specific section.

**Headers:** `Authorization: Bearer <token>`

### Admin Routes

#### `GET /api/v1/admin/clients`
Get list of clients (filtered by admin role).

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `status_filter`: Filter by status
- `payment_status_filter`: Filter by payment status
- `year_filter`: Filter by filing year
- `skip`: Pagination offset
- `limit`: Pagination limit

**Response:**
```json
{
  "clients": [
    {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "status": "under_review",
      "payment_status": "pending",
      "filing_year": 2024,
      "total_amount": 500.0,
      "paid_amount": 0.0
    }
  ],
  "total": 1
}
```

#### `POST /api/v1/admin/request-documents`
Request documents from a client.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "client_id": "uuid",
  "document_type": "T2202 Form",
  "note": "Please upload your T2202 form for 2024"
}
```

#### `POST /api/v1/admin/update-status`
Update client status or payment status.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "client_id": "uuid",
  "status": "in_preparation",
  "payment_status": "partial"
}
```

## Role-Based Access Control (RBAC)

### Roles

1. **client**: Regular user (can only access own data)
2. **admin**: Admin user (can access assigned clients only)
3. **superadmin**: Superadmin (can access all clients)

### Permissions

- `add_edit_payment`: Add/edit payments
- `add_edit_client`: Add/edit clients
- `request_documents`: Request documents from clients
- `assign_clients`: Assign clients to admins
- `view_analytics`: View analytics
- `approve_cost_estimate`: Approve cost estimates
- `update_workflow`: Update client workflow status

### Permission Checking

Admins have a `permissions` JSON array. Superadmins have all permissions automatically.

## How Admin & Client Flows Connect

### Client Flow

1. **Register/Login** → JWT token
2. **Update Profile** → Creates/updates `clients` record
3. **Fill T1 Form** → POST `/client/tax-return` → Stores in `tax_returns.form_data` (JSONB)
4. **Upload Documents** → POST `/documents/upload` → Stores in `documents` table with `section_name`
5. **Submit Form** → Status changes to "submitted" → Client status → "under_review"

### Admin Flow

1. **Login** → JWT token (admin role)
2. **View Clients** → GET `/admin/clients` → Filtered by admin assignments (or all if superadmin)
3. **Request Documents** → POST `/admin/request-documents` → Creates notification, updates document status
4. **Update Status** → POST `/admin/update-status` → Updates client status, creates notification
5. **Review Tax Return** → Query `tax_returns.form_data` (JSONB) for flexible form data

### Data Flow

```
Client Dashboard (Flutter)
    ↓
POST /client/tax-return
    ↓
tax_returns.form_data (JSONB) ← Flexible structure
    ↓
Admin Dashboard (React)
    ↓
GET /admin/clients → Query with filters
    ↓
Review form_data JSONB
    ↓
Update status → notifications table
```

## Local Filesystem Storage

Documents are stored in `./storage/uploads/` (configurable via `STORAGE_PATH`).

**File naming**: `{uuid}.{extension}`

**Migration to AWS**: Change `file_path` to S3 key, update upload/download logic in `routes/documents.py`.

## Performance Optimizations

1. **Denormalized Fields**: Client name, email, status for fast queries
2. **Indexes**: Status, payment_status, filing_year, JSONB GIN indexes
3. **Connection Pooling**: SQLAlchemy pool_size=10, max_overflow=20
4. **No Deep Joins**: Maximum 2-3 levels (client → tax_return → sections)

## Production Deployment

### Environment Variables

Update `.env` with production values:
- Strong `JWT_SECRET_KEY`
- Production database credentials
- SMTP configuration for emails
- Appropriate `STORAGE_PATH` (or migrate to S3)

### Database

1. Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
2. Enable connection pooling (PgBouncer)
3. Set up automated backups
4. Monitor query performance

### Security

1. Use HTTPS (TLS)
2. Set CORS origins appropriately
3. Rate limiting (add middleware)
4. Input validation (Pydantic models)
5. SQL injection protection (SQLAlchemy ORM)

### Scaling

- **Horizontal**: Multiple FastAPI instances behind load balancer
- **Database**: Read replicas for admin dashboard queries
- **Storage**: Migrate to S3 for document storage

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql -h localhost -U postgres -d taxease
```

### Schema Not Created

```bash
# Manually create
python database/schemas.py
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend
python -m pip install -r requirements.txt
```

## License

Proprietary - Tax-Ease Platform







