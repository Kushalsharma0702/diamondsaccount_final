# TaxEase Backend - Python Project Structure

## Overview
This is a **Python-only** backend system built with FastAPI for Canadian tax filing applications.

---

## Technology Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy (Async)
- **Authentication:** JWT (JSON Web Tokens)
- **Encryption:** AES-256-CBC + RSA-2048
- **API Documentation:** OpenAPI/Swagger (auto-generated)
- **Testing:** pytest
- **Deployment:** Docker, Uvicorn

---

## Project Structure

```
taxease_backend/
│
├── main.py                          # Main FastAPI application (unified server)
│
├── shared/                          # Shared modules across all services
│   ├── __init__.py                  # Package initialization
│   ├── auth.py                      # JWT authentication & authorization
│   ├── database.py                  # Database connection & session management
│   ├── models.py                    # SQLAlchemy database models
│   ├── schemas.py                   # Pydantic schemas for validation
│   ├── utils.py                     # Utility functions (OTP, email, S3, tax calc)
│   ├── encryption.py                # End-to-end encryption service
│   ├── encrypted_file_service.py    # Encrypted file operations
│   ├── t1_routes.py                 # Enhanced T1 tax form routes
│   ├── t1_enhanced_schemas.py       # Enhanced T1 form schemas
│   ├── t1_models.py                 # (empty placeholder)
│   ├── t1_schemas.py                # (empty placeholder)
│   └── t1_tax_models.py             # (empty placeholder)
│
├── services/                        # Individual microservices (Python)
│   ├── auth/
│   │   └── main.py                  # Authentication service
│   ├── tax/
│   │   └── main.py                  # Tax form service
│   ├── file/
│   │   └── main.py                  # File management service
│   ├── report/
│   │   └── main.py                  # Report generation service
│   └── gateway/
│       └── main.py                  # API gateway service
│
├── alembic/                         # Database migrations
│   ├── versions/                    # Migration files
│   ├── env.py                       # Alembic environment configuration
│   └── script.py.mako               # Migration template
│
├── docker/                          # Docker configuration
│   ├── Dockerfile                   # Main Dockerfile
│   └── postgres/
│       └── init.sql                 # PostgreSQL initialization script
│
├── aws/                             # AWS infrastructure templates
│   ├── infrastructure.yml           # CloudFormation infrastructure
│   └── ecs-tasks.yml                # ECS task definitions
│
├── public/                          # Static files for testing
│   └── index.html                   # Test dashboard HTML
│
├── dashboard.html                   # Encrypted file dashboard
├── alembic.ini                      # Alembic configuration
├── .env                             # Environment variables
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore rules
├── requirements.txt                 # Python dependencies
├── API_DOCUMENTATION.md             # Comprehensive API documentation
├── ARCHITECTURE.md                  # System architecture
├── PROJECT_STRUCTURE.md             # This file
└── README.md                        # Project README

```

---

## Core Files Explanation

### Main Application

#### `main.py`
The unified FastAPI application that combines all microservices into a single deployable unit.

**Key Features:**
- Unified FastAPI app with all routes
- CORS middleware configuration
- Database initialization
- JWT authentication
- Health check endpoints
- Automatic API documentation
- Includes all service routes (auth, tax, files, reports, encrypted files)

**Endpoints:**
- `/` - Root endpoint
- `/health` - Health check
- `/docs` - Interactive API documentation (Swagger UI)
- `/redoc` - Alternative API documentation
- `/api/v1/auth/*` - Authentication endpoints
- `/api/v1/tax/*` - Tax form endpoints
- `/api/v1/t1-forms/*` - Enhanced encrypted T1 forms
- `/api/v1/files/*` - File management endpoints
- `/api/v1/reports/*` - Report generation endpoints
- `/api/v1/encrypted-files/*` - Encrypted file operations

---

### Shared Modules

#### `shared/auth.py`
JWT authentication and authorization utilities.

**Classes:**
- `JWTManager` - JWT token creation and verification
- `get_current_user()` - Dependency for protected routes

**Features:**
- Access token generation (15 minutes expiry)
- Refresh token generation (7 days expiry)
- Password hashing with bcrypt
- Token validation and user extraction

#### `shared/database.py`
Database connection and session management.

**Components:**
- Async SQLAlchemy engine
- AsyncSession factory
- Base model class
- Database initialization
- Connection pooling

**Key Functions:**
- `get_db()` - FastAPI dependency for database sessions
- `Database.init()` - Initialize database tables
- `Database.check_connection()` - Health check

#### `shared/models.py`
SQLAlchemy ORM models for database tables.

**Models:**
1. **User** - User accounts
   - id, email, password_hash
   - first_name, last_name, phone
   - email_verified, is_active
   - public_key, private_key (for encryption)
   - Relationships: forms, files, reports

2. **RefreshToken** - JWT refresh tokens
   - id, user_id, token
   - expires_at, revoked

3. **OTP** - One-Time Passwords for verification
   - id, email, code, purpose
   - expires_at, used

4. **T1PersonalForm** - Tax forms (basic + encrypted)
   - id, user_id, tax_year
   - Personal info fields
   - Income and deduction fields
   - Calculated tax fields
   - encrypted_form_data (LargeBinary)
   - encryption_metadata (JSON)
   - status (draft, submitted, reviewed, approved, rejected)

5. **File** - File uploads
   - id, user_id, filename
   - file_size, mime_type
   - s3_key, s3_url
   - encrypted_data, encryption_metadata
   - is_encrypted

6. **Report** - Generated PDF reports
   - id, user_id, form_id
   - report_type, filename
   - s3_key, s3_url
   - status (pending, completed, failed)

7. **EncryptedDocument** - Encrypted document metadata
   - id, user_id, file_id
   - encryption_algorithm
   - key_checksum, iv

8. **AuditLog** - System audit trail
   - id, user_id, action
   - resource_type, resource_id
   - metadata, timestamp

#### `shared/schemas.py`
Pydantic schemas for request/response validation.

**Base Schemas:**
- UserCreate, UserResponse, UserLogin
- Token, TokenRefresh
- OTPRequest, OTPVerify
- T1PersonalFormCreate, T1PersonalFormUpdate, T1PersonalFormResponse
- FileUploadResponse, FileListResponse
- ReportResponse, ReportRequest
- MessageResponse, HealthResponse

**Features:**
- Automatic validation
- Type conversion
- Documentation generation
- Error messages

#### `shared/utils.py`
Utility functions and helpers.

**Functions:**
- `generate_otp()` - Generate random OTP codes
- `generate_filename()` - Generate unique filenames
- `validate_file_type()` - Check file extensions
- `calculate_tax()` - Canadian tax calculations
- `log_user_action()` - Audit logging

**Classes:**
- `S3Manager` - AWS S3 file operations
- `EmailService` - Email sending (OTP, notifications)

**Development Mode:**
- `DEVELOPMENT_MODE` - Skip email verification
- `DEVELOPER_OTP` - Fixed OTP for testing (123456)
- `SKIP_EMAIL_VERIFICATION` - Auto-verify emails

#### `shared/encryption.py`
End-to-end encryption service for documents.

**Classes:**
1. **DocumentEncryption** - Main encryption service
   - `generate_rsa_keypair()` - Generate RSA-2048 keys
   - `generate_aes_key()` - Generate AES-256 keys
   - `encrypt_file()` - Encrypt file with AES-256-CBC
   - `decrypt_file()` - Decrypt file with AES-256-CBC
   - `create_encrypted_document()` - Encrypt JSON data
   - `decrypt_encrypted_document()` - Decrypt JSON data

2. **SecureDocumentManager** - Document management
   - `store_encrypted_document()` - Store encrypted document
   - `retrieve_encrypted_document()` - Retrieve and decrypt
   - `rotate_encryption_keys()` - Key rotation

3. **KeyManager** - Encryption key management
   - `derive_key_from_password()` - PBKDF2 key derivation
   - `validate_password_strength()` - Password validation

**Features:**
- AES-256-CBC encryption
- RSA-2048 key pairs
- PBKDF2 key derivation
- Compression before encryption
- Integrity verification

#### `shared/t1_routes.py`
Enhanced T1 tax form routes with automatic encryption.

**Endpoints:**
- `POST /api/v1/t1-forms/` - Create encrypted T1 form
- `GET /api/v1/t1-forms/` - List T1 forms (metadata only)
- `GET /api/v1/t1-forms/{id}` - Get T1 form (decrypted)
- `PUT /api/v1/t1-forms/{id}` - Update T1 form (re-encrypted)
- `DELETE /api/v1/t1-forms/{id}` - Delete T1 form

**Features:**
- Automatic per-user encryption
- AES-256-CBC + RSA-2048 hybrid encryption
- Audit logging for all operations
- Form validation with nested objects
- Automatic tax calculations

#### `shared/t1_enhanced_schemas.py`
Comprehensive T1 form schemas with nested validation.

**Main Schemas:**
- `T1PersonalFormCreate` - Create new T1 form
- `T1PersonalFormUpdate` - Update existing form
- `T1PersonalFormResponse` - API response format
- `T1PersonalFormListResponse` - List response

**Nested Schemas:**
- `T1PersonalInfo` - Personal information
- `T1SpouseInfo` - Spouse details
- `T1ChildInfo` - Child information
- `T1ForeignProperty` - Foreign property details
- `T1MovingExpense` - Moving expense details
- `T1UberBusiness` - Uber/rideshare business
- `T1GeneralBusiness` - General business details
- `T1RentalIncome` - Rental property income
- `T1SelfEmployment` - Self-employment details

**Validation:**
- SIN format (^\d{9}$)
- Phone number regex (^\+?[1-9]\d{1,14}$)
- Email validation
- Postal code format
- Enum constraints (marital status, business type, etc.)
- Required field validation
- Range validation for numeric fields

---

## Database Migrations

### Alembic Setup

**Configuration:**
- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Environment setup
- `alembic/versions/` - Migration files

**Commands:**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

**Migration Files:**
1. `20251106_0151_39854d26cbdd_initial_database_schema.py`
   - Initial database setup
   - Users, OTPs, RefreshTokens, T1Forms, Files, Reports

2. `20251106_0318_f9b923eed535_add_encryption_support_for_files_and_.py`
   - Added encryption fields to Files table
   - Added public_key, private_key to Users table

3. `20251107_0036_68aa2ca60ef1_add_comprehensive_t1_tax_form_models.py`
   - Enhanced T1PersonalForm table
   - Added encrypted_form_data (LargeBinary)
   - Added encryption_metadata (JSON)
   - Added indexable fields

---

## Environment Configuration

### `.env` File

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/taxease_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taxease_db
DB_USER=postgres
DB_PASSWORD=password

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_REFRESH_SECRET=your-super-secret-refresh-key-change-this-in-production
JWT_ACCESS_EXPIRATION=15m
JWT_REFRESH_EXPIRATION=7d

# AWS (optional - for S3 file storage)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=taxease-files

# Development Mode
DEVELOPMENT_MODE=True
DEVELOPER_OTP=123456
SKIP_EMAIL_VERIFICATION=True

# Email (optional - for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@taxease.com
```

---

## Python Dependencies

### `requirements.txt`

```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-decouple==3.8
pydantic[email]==2.5.3

# Encryption
cryptography==41.0.7

# AWS
boto3==1.34.20
botocore==1.34.20

# Email
python-email-validator==2.1.0

# PDF Generation
reportlab==4.0.9

# Utilities
python-dotenv==1.0.0
pydantic-settings==2.1.0
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

### Development Mode

```bash
# Start the main application
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points

- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Dashboard:** http://localhost:8080 (if running)

### Production Mode

```bash
# Use Gunicorn with Uvicorn workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## API Testing

### Using Postman

1. Import the API documentation
2. Create environment with:
   - `base_url`: http://localhost:8000
   - `access_token`: (set after login)
   - `user_email`: user@example.com
   - `user_password`: SecurePassword123!

3. Test workflow:
   - Register user
   - Login (save token)
   - Create T1 form
   - Upload file
   - Generate report

### Using cURL

```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# Create T1 form (with token)
curl -X POST http://localhost:8000/api/v1/t1-forms/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "taxYear": 2024,
    "personalInfo": {
      "firstName": "John",
      "lastName": "Doe",
      "sin": "123456789",
      "email": "john@example.com"
    },
    "employmentIncome": 75000
  }'
```

---

## Security Features

### Authentication
- JWT-based authentication
- Access tokens (15 minutes)
- Refresh tokens (7 days)
- Password hashing with bcrypt
- Token blacklisting support

### Encryption
- AES-256-CBC for document encryption
- RSA-2048 for key exchange
- Per-user encryption keys
- Automatic encryption for T1 forms
- Secure key storage

### Validation
- Pydantic schema validation
- Input sanitization
- File type validation
- Size limits
- Rate limiting (planned)

### Audit Logging
- All user actions logged
- Resource access tracking
- Compliance ready
- Tamper-proof logs

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    public_key TEXT,
    private_key TEXT,
    key_salt VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### T1 Personal Forms Table
```sql
CREATE TABLE t1_personal_forms (
    id VARCHAR(50) PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    tax_year INTEGER NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    sin VARCHAR(20),
    encrypted_form_data BYTEA,
    encryption_metadata TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    has_foreign_property BOOLEAN,
    has_moving_expenses BOOLEAN,
    has_uber_business BOOLEAN,
    has_general_business BOOLEAN,
    has_rental_income BOOLEAN,
    is_self_employed BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Files Table
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_size BIGINT,
    mime_type VARCHAR(100),
    description TEXT,
    category VARCHAR(50),
    s3_key TEXT,
    s3_url TEXT,
    encrypted_data BYTEA,
    encrypted_key TEXT,
    encryption_metadata TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t taxease-backend .

# Run container
docker run -d \
  --name taxease-api \
  -p 8000:8000 \
  --env-file .env \
  taxease-backend
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/taxease_db
    depends_on:
      - db
  
  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=taxease_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Monitoring & Logging

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Checks

- `/health` - Application health
- `/health/db` - Database connectivity
- `/health/services` - Microservices status

---

## Best Practices

1. **Always use environment variables** for sensitive data
2. **Validate all inputs** using Pydantic schemas
3. **Log user actions** for audit trails
4. **Use async/await** for database operations
5. **Handle exceptions** with try-except blocks
6. **Test endpoints** before deployment
7. **Keep secrets secure** - never commit .env
8. **Use migrations** for database changes
9. **Document API changes** in API_DOCUMENTATION.md
10. **Review logs** regularly for errors

---

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL is running
   - Verify credentials

2. **JWT Token Invalid**
   - Check JWT_SECRET in .env
   - Verify token expiration
   - Re-login to get new token

3. **File Upload Fails**
   - Check file size limits
   - Verify AWS credentials
   - Check S3 bucket permissions

4. **Encryption Errors**
   - Ensure user has set up encryption
   - Verify encryption password
   - Check public/private keys exist

---

## Support & Documentation

- **API Docs:** http://localhost:8000/docs
- **Architecture:** ARCHITECTURE.md
- **API Reference:** API_DOCUMENTATION.md
- **This Guide:** PROJECT_STRUCTURE.md

---

**Last Updated:** November 13, 2025
**Version:** 1.0.0
**Language:** Python 3.11+
**Framework:** FastAPI
