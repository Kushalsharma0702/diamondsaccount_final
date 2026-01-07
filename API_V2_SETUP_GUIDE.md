# API v2 Implementation - Setup and Testing Guide

## Overview

This document describes the core subset implementation (Option B) of the redesigned API. The following endpoints are now available:

- **Authentication** (7 endpoints)
- **User Profile** (2 endpoints)
- **Filings** (4 endpoints)
- **Documents** (6 endpoints)
- **Health Check** (1 endpoint)

**Total: 20 endpoints** ready for testing.

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── auth.py              # JWT + OTP + Redis
│   │   ├── errors.py            # Error handling
│   │   └── database.py          # Updated to use schemas_v2
│   ├── schemas/
│   │   └── api_v2.py            # Pydantic request/response models
│   ├── services/
│   │   ├── filing_service.py    # Filing business logic
│   │   └── document_service.py  # Document + encryption logic
│   ├── routes_v2/
│   │   ├── auth.py              # Auth endpoints
│   │   ├── users.py             # User profile endpoints
│   │   ├── filings.py           # Filing endpoints
│   │   ├── documents.py         # Document endpoints
│   │   └── health.py            # Health check
│   └── main.py                  # Updated with v2 routes
database/
└── schemas_v2.py                # New database schema
```

## Environment Variables

Create/update your `.env` file:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=CA_Project
DB_USER=postgres
DB_PASSWORD=postgres

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRY=3600        # 1 hour
JWT_REFRESH_EXPIRY=2592000    # 30 days

# Redis (for token blacklist + OTP)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=              # Optional

# File Storage
STORAGE_PATH=/var/taxease/storage
ENCRYPTION_KEY=your-32-byte-encryption-key-change-this
```

## Database Setup

### Option 1: Create New Database (Recommended for Testing)

```bash
# Create new database
psql -U postgres -c "CREATE DATABASE taxease_v2;"

# Run migration to create v2 tables
python -c "from backend.app.database import init_db; init_db()"
```

### Option 2: Add Tables to Existing Database

```bash
# Add v2 tables alongside existing tables
python -c "from backend.app.database import init_db; init_db()"
```

> **Note:** The v2 schema uses different table names, so it won't conflict with existing tables. You can run both old and new APIs simultaneously for testing.

## Dependencies

Install missing dependencies:

```bash
cd backend
pip install python-multipart passlib[bcrypt] redis cryptography
```

## Starting the Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "database": "healthy",
  "version": "2.0.0"
}
```

### 2. User Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 3. User Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

### 4. Get User Profile

```bash
TOKEN="your-access-token-here"

curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "test@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "email_verified": false,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 5. Create Filing

```bash
curl -X POST http://localhost:8000/api/v1/filings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filing_year": 2023
  }'
```

**Expected Response:**
```json
{
  "id": "456e4567-e89b-12d3-a456-426614174001",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "filing_year": 2023,
  "status": "not_started",
  "total_fee": 0.0,
  "paid_amount": 0.0,
  "payment_status": "pending",
  "email_thread_id": null,
  "created_at": "2024-01-15T10:35:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "assigned_admin": null
}
```

### 6. List User Filings

```bash
curl http://localhost:8000/api/v1/filings?page=1&page_size=20 \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Upload Document

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "filing_id=456e4567-e89b-12d3-a456-426614174001" \
  -F "category=t4_slip"
```

**Expected Response:**
```json
{
  "id": "789e4567-e89b-12d3-a456-426614174002",
  "filename": "document.pdf",
  "file_size": 12345,
  "file_type": "pdf",
  "created_at": "2024-01-15T10:40:00Z"
}
```

### 8. List Documents

```bash
curl http://localhost:8000/api/v1/documents?filing_id=456e4567-e89b-12d3-a456-426614174001 \
  -H "Authorization: Bearer $TOKEN"
```

### 9. Download Document

```bash
curl http://localhost:8000/api/v1/documents/789e4567-e89b-12d3-a456-426614174002/download \
  -H "Authorization: Bearer $TOKEN" \
  -o downloaded.pdf
```

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": null,
    "trace_id": "abc123"
  }
}
```

### Common Error Codes

- `AUTH_INVALID_CREDENTIALS` - Wrong email/password
- `AUTH_TOKEN_EXPIRED` - JWT token expired
- `AUTH_TOKEN_INVALID` - Malformed JWT
- `AUTH_ACCOUNT_INACTIVE` - User account deactivated
- `AUTHZ_NOT_RESOURCE_OWNER` - User doesn't own the resource
- `AUTHZ_NOT_ASSIGNED` - Admin not assigned to filing
- `RESOURCE_NOT_FOUND` - Resource doesn't exist
- `RESOURCE_ALREADY_EXISTS` - Duplicate resource (e.g., filing for same year)
- `VALIDATION_INVALID_EMAIL` - Email format invalid
- `VALIDATION_WEAK_PASSWORD` - Password doesn't meet requirements
- `FILE_TOO_LARGE` - File exceeds 10MB limit
- `FILE_INVALID_TYPE` - File type not allowed

## What's Implemented

### ✅ Core Infrastructure
- [x] Database schema v2 (schemas_v2.py)
- [x] Error handling system (40+ error codes)
- [x] JWT authentication with Redis blacklist
- [x] OTP system with Redis storage
- [x] Pydantic v2 request/response models
- [x] Service layer (Filing + Document)
- [x] Route handlers (Auth + Users + Filings + Documents)
- [x] Exception handlers registered in main.py

### ✅ Authentication Features
- [x] User registration with password validation
- [x] Login with JWT tokens
- [x] Token blacklist on logout
- [x] OTP request/verify
- [x] Password reset flow
- [x] Email verification (OTP generated, email sending TODO)

### ✅ User Profile
- [x] Get current user profile
- [x] Update profile (first_name, last_name, phone)

### ✅ Filing Features
- [x] List user's own filings (paginated)
- [x] Get filing details with derived fields (paid_amount, payment_status)
- [x] Create filing with duplicate check
- [x] Filing timeline tracking
- [x] Admin assignment model (database ready)

### ✅ Document Features
- [x] List documents with filters
- [x] Upload with AES-256 encryption
- [x] Download with decryption
- [x] Update metadata
- [x] Delete document (file + DB record)
- [x] File type validation (pdf, jpg, jpeg, png, doc, docx)
- [x] File size limit (10MB)

## What's NOT Implemented Yet

### ⏳ Missing from Core Subset
- [ ] T1 Form endpoints (CRUD for T1 forms)
- [ ] Payment endpoints (record payments, calculate balance)
- [ ] Notification endpoints (list, mark read, get unread count)
- [ ] Admin endpoints (status updates, fee setting, assignment)
- [ ] Superadmin endpoints (admin management)

### ⏳ Additional Features
- [ ] Email sending (SMTP integration)
- [ ] File type virus scanning
- [ ] Rate limiting middleware
- [ ] Request logging middleware
- [ ] OpenAPI documentation enhancements
- [ ] Unit tests for services
- [ ] Integration tests for endpoints

## Testing with Postman

Import this collection to Postman:

1. Create new collection "Tax-Ease API v2"
2. Add environment variables:
   - `base_url`: http://localhost:8000
   - `access_token`: (will be set after login)
3. Add requests:
   - POST /api/v1/auth/register
   - POST /api/v1/auth/login
   - GET /api/v1/users/me
   - POST /api/v1/filings
   - GET /api/v1/filings
   - POST /api/v1/documents/upload
   - GET /api/v1/documents

4. Set Authorization header for protected endpoints:
   ```
   Authorization: Bearer {{access_token}}
   ```

## Next Steps

1. **Test Core Functionality**
   - Register user → Login → Create filing → Upload document
   - Verify encryption works (check storage path)
   - Test error responses (invalid token, duplicate filing, etc.)

2. **Implement Missing Pieces**
   - T1Form service + endpoints
   - Payment endpoints
   - Admin-specific endpoints (status updates, assignments)
   - Notification endpoints

3. **Production Readiness**
   - Add rate limiting
   - Implement email sending
   - Add request logging
   - Write tests
   - Deploy to staging

## Troubleshooting

### Redis Connection Error
```
⚠️ Redis not available - token blacklist disabled
```
**Solution:** Start Redis with `redis-server` or update REDIS_HOST in .env

### Database Connection Error
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Solution:** Check PostgreSQL is running and DB credentials in .env

### Import Error
```
ModuleNotFoundError: No module named 'passlib'
```
**Solution:** Install missing dependencies with `pip install passlib[bcrypt] redis cryptography python-multipart`

### File Upload Error
```
FILE_TOO_LARGE: File exceeds maximum size limit
```
**Solution:** Files must be under 10MB. Split large files or compress.

## Support

For issues or questions, refer to:
- Phase 1-5 API design documentation
- Error code definitions in `backend/app/core/errors.py`
- Service layer logic in `backend/app/services/`

---

**Implementation Date:** January 2024  
**API Version:** 2.0.0  
**Status:** Core subset ready for testing
