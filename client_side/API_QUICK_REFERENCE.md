# TaxEase API - Quick Reference Guide

**Base URL:** `http://localhost:8000`

---

## 🔐 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login and get JWT token | No |
| GET | `/api/v1/auth/me` | Get current user profile | Yes |
| POST | `/api/v1/auth/request-otp` | Request OTP for verification | No |
| POST | `/api/v1/auth/verify-otp` | Verify OTP code | No |

---

## 📋 Basic T1 Tax Forms

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/tax/t1-personal` | Create basic T1 form | Yes |
| GET | `/api/v1/tax/t1-personal` | List all T1 forms | Yes |
| GET | `/api/v1/tax/t1-personal/{id}` | Get specific T1 form | Yes |
| PUT | `/api/v1/tax/t1-personal/{id}` | Update T1 form | Yes |
| POST | `/api/v1/tax/t1-personal/{id}/submit` | Submit T1 form | Yes |
| DELETE | `/api/v1/tax/t1-personal/{id}` | Delete T1 form | Yes |

---

## 🔒 Enhanced T1 Forms (Encrypted)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/t1-forms/` | Create encrypted T1 form | Yes |
| GET | `/api/v1/t1-forms/` | List T1 forms (metadata) | Yes |
| GET | `/api/v1/t1-forms/{id}` | Get T1 form (decrypted) | Yes |
| PUT | `/api/v1/t1-forms/{id}` | Update T1 form (re-encrypted) | Yes |
| DELETE | `/api/v1/t1-forms/{id}` | Delete T1 form | Yes |

---

## 📁 File Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/files/upload` | Upload file | Yes |
| GET | `/api/v1/files` | List all files | Yes |
| GET | `/api/v1/files/{id}` | Get file details | Yes |
| GET | `/api/v1/files/{id}/download` | Download file | Yes |
| DELETE | `/api/v1/files/{id}` | Delete file | Yes |

---

## 📊 Reports

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/reports/generate` | Generate PDF report | Yes |
| GET | `/api/v1/reports` | List all reports | Yes |
| GET | `/api/v1/reports/{id}` | Get report details | Yes |
| GET | `/api/v1/reports/{id}/download` | Download report | Yes |
| DELETE | `/api/v1/reports/{id}` | Delete report | Yes |

---

## 🔐 Encrypted File Operations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/encrypted-files/setup` | Setup user encryption | Yes |
| POST | `/api/v1/encrypted-files/upload` | Upload encrypted file | Yes |
| GET | `/api/v1/encrypted-files` | List encrypted files | Yes |
| GET | `/api/v1/encrypted-files/{id}` | Get file metadata | Yes |
| POST | `/api/v1/encrypted-files/{id}/decrypt` | Decrypt and download | Yes |
| DELETE | `/api/v1/encrypted-files/{id}` | Delete encrypted file | Yes |

---

## 🏥 Health & Status

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API welcome message | No |
| GET | `/health` | Health check | No |
| GET | `/dev/otps/{email}` | Get OTP (dev mode only) | No |
| GET | `/docs` | Swagger UI documentation | No |
| GET | `/redoc` | ReDoc documentation | No |

---

## 📝 Common Request Examples

### Register User
```json
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+14161234567"
}
```

### Login
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### Create T1 Form (Basic)
```json
POST /api/v1/tax/t1-personal
Headers: Authorization: Bearer {token}
{
  "tax_year": 2024,
  "first_name": "John",
  "last_name": "Doe",
  "sin": "123456789",
  "date_of_birth": "1990-01-15",
  "marital_status": "single",
  "address": "123 Main St, Toronto, ON",
  "phone_number": "+14161234567",
  "email": "john@example.com",
  "employment_income": 75000.00,
  "rrsp_contributions": 5000.00
}
```

### Create Enhanced T1 Form (Encrypted)
```json
POST /api/v1/t1-forms/
Headers: Authorization: Bearer {token}
{
  "taxYear": 2024,
  "status": "draft",
  "personalInfo": {
    "firstName": "John",
    "lastName": "Doe",
    "sin": "123456789",
    "email": "john@example.com",
    "phoneNumber": "+14161234567"
  },
  "employmentIncome": 75000.00,
  "rrspContributions": 5000.00
}
```

### Upload File
```
POST /api/v1/files/upload
Headers: Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- file: [select file]
- description: "Tax receipt"
- category: "tax_document"
```

### Generate Report
```json
POST /api/v1/reports/generate
Headers: Authorization: Bearer {token}
{
  "form_id": "uuid-of-form",
  "report_type": "tax_summary"
}
```

---

## 🔑 Authentication Flow

1. **Register** → `POST /api/v1/auth/register`
2. **Login** → `POST /api/v1/auth/login` → Receive `access_token`
3. **Use Token** → Add header: `Authorization: Bearer {access_token}`
4. **Make Requests** → All protected endpoints require this header

---

## ⚠️ Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## 📊 Response Formats

### Success Response
```json
{
  "id": "uuid-here",
  "created_at": "2025-11-13T10:30:00Z",
  "data": { ... }
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🧪 Testing with Postman

### Environment Setup
```
base_url = http://localhost:8000
access_token = (set after login)
user_email = test@example.com
user_password = TestPassword123!
```

### Collection Variables
- `{{base_url}}` - API base URL
- `{{access_token}}` - JWT access token

### Authorization Tab
- Type: Bearer Token
- Token: `{{access_token}}`

---

## 🔍 Query Parameters

### List T1 Forms
```
GET /api/v1/t1-forms/?tax_year=2024&status=draft
```

### List Files
```
GET /api/v1/files?category=tax_document&limit=50&offset=0
```

### List Reports
```
GET /api/v1/reports?status=completed&report_type=tax_summary
```

---

## 📦 Response Fields

### User Object
- `id` - UUID
- `email` - Email address
- `first_name` - First name
- `last_name` - Last name
- `phone` - Phone number
- `email_verified` - Boolean
- `is_active` - Boolean
- `created_at` - ISO timestamp
- `updated_at` - ISO timestamp

### T1 Form Object (Enhanced)
- `id` - Form ID (T1_timestamp)
- `user_id` - User UUID
- `tax_year` - Integer (2024)
- `status` - Enum (draft, submitted, etc.)
- `personalInfo` - Object with personal details
- `employmentIncome` - Decimal
- `totalIncome` - Calculated decimal
- `taxableIncome` - Calculated decimal
- `totalTax` - Calculated decimal
- `is_encrypted` - Boolean
- `created_at` - ISO timestamp
- `updated_at` - ISO timestamp

### File Object
- `id` - UUID
- `user_id` - User UUID
- `filename` - String
- `file_size` - Bytes
- `mime_type` - MIME type
- `category` - String
- `s3_url` - S3 URL (if applicable)
- `is_encrypted` - Boolean
- `created_at` - ISO timestamp

---

## 🚀 Quick Start Commands

```bash
# Start server
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Check database status
alembic current
```

---

## 📚 Documentation Links

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Full API Docs:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Project Structure:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **README:** [README.md](README.md)

---

## 💡 Development Tips

1. **Always use Bearer token** for authenticated endpoints
2. **Check `/docs`** for interactive API testing
3. **Use development mode** for testing (OTP = 123456)
4. **Check `/health`** to verify server status
5. **Review error responses** for debugging
6. **Use query parameters** for filtering lists
7. **Upload files** using multipart/form-data
8. **Store access_token** after login for subsequent requests

---

## 🔒 Security Notes

- **Never share JWT tokens** - they provide full access
- **Tokens expire** - Access tokens expire in 15 minutes
- **Use HTTPS in production** - Never send tokens over HTTP
- **Validate inputs** - All inputs are validated by Pydantic
- **Encrypted data** - T1 forms are automatically encrypted per user
- **Audit logging** - All actions are logged for compliance

---

**Last Updated:** November 13, 2025
**API Version:** 1.0.0
