# Tax-Ease API Testing Guide

## Base URLs

### Local Development
- **Base URL**: `http://localhost:8001`
- **API Base**: `http://localhost:8001/api/v1`
- **Health Check**: `http://localhost:8001/`

### Production (Future)
- **Base URL**: `https://api.taxease.com`
- **API Base**: `https://api.taxease.com/api/v1`

---

## Authentication

### Client Authentication
- **Base Path**: `/api/v1/auth`
- **Token Type**: JWT Bearer Token
- **Token Header**: `Authorization: Bearer <access_token>`

### Admin Authentication
- **Base Path**: `/api/v1/admin/auth`
- **Token Type**: JWT Bearer Token + Redis Session
- **Token Header**: `Authorization: Bearer <access_token>`

### Universal OTP
- **Static OTP**: `123456` (for all OTP verifications)

---

## 1. Client Authentication Endpoints

### 1.1 Register Client
**POST** `/api/v1/auth/register`

**Request Body:**
```json
{
  "email": "client@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "password": "password123",
  "confirm_password": "password123",
  "accept_terms": true
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "email": "client@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "message": "Account and client record created successfully"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "password": "password123",
    "confirm_password": "password123",
    "accept_terms": true
  }'
```

---

### 1.2 Login Client
**POST** `/api/v1/auth/login`

**Request Body:**
```json
{
  "email": "client@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**cURL:**
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "password123"
  }'
```

---

### 1.3 Request OTP
**POST** `/api/v1/auth/request-otp`

**Request Body:**
```json
{
  "email": "client@example.com",
  "purpose": "email_verification"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP sent to email",
  "otp_code": "123456"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8001/api/v1/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "purpose": "email_verification"
  }'
```

---

### 1.4 Verify OTP
**POST** `/api/v1/auth/verify-otp`

**Request Body:**
```json
{
  "email": "client@example.com",
  "code": "123456",
  "purpose": "email_verification"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP verified successfully",
  "verified": true
}
```

**cURL:**
```bash
curl -X POST http://localhost:8001/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "code": "123456",
    "purpose": "email_verification"
  }'
```

---

## 2. Client Endpoints

### 2.1 Get My Client Info
**GET** `/api/v1/client/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "client@example.com",
  "phone": "+1234567890",
  "filing_year": 2024,
  "status": "documents_pending",
  "payment_status": "pending"
}
```

**cURL:**
```bash
curl -X GET http://localhost:8001/api/v1/client/me \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.2 Add Client (Admin Only)
**POST** `/api/v1/client/add`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newclient@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1234567891",
  "password": "password123"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "Jane Smith",
  "email": "newclient@example.com",
  "phone": "+1234567891",
  "filing_year": 2024,
  "status": "documents_pending",
  "payment_status": "pending"
}
```

---

### 2.3 Delete Client (Admin Only)
**DELETE** `/api/v1/client/{client_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Client deleted successfully"
}
```

---

## 3. Admin Authentication Endpoints

### 3.1 Admin Login
**POST** `/api/v1/admin/auth/login`

**Request Body:**
```json
{
  "email": "admin@taxease.com",
  "password": "Admin123!"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "user_id": "uuid",
    "email": "admin@taxease.com",
    "name": "Admin One",
    "role": "admin",
    "permissions": ["read", "write"]
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "session_id": "uuid"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8001/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@taxease.com",
    "password": "Admin123!"
  }'
```

---

### 3.2 Admin Register (Superadmin Only)
**POST** `/api/v1/admin/auth/register`

**Headers:**
```
Authorization: Bearer <superadmin_access_token>
```

**Request Body:**
```json
{
  "email": "newadmin@taxease.com",
  "name": "New Admin",
  "password": "Admin123!",
  "role": "admin",
  "permissions": ["read", "write"]
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "email": "newadmin@taxease.com",
  "name": "New Admin",
  "role": "admin",
  "is_active": true
}
```

---

### 3.3 Get Current Admin
**GET** `/api/v1/admin/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "user_id": "uuid",
  "email": "admin@taxease.com",
  "name": "Admin One",
  "role": "admin",
  "permissions": ["read", "write"],
  "is_active": true
}
```

---

### 3.4 Admin Logout
**POST** `/api/v1/admin/auth/logout`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

### 3.5 Refresh Session
**POST** `/api/v1/admin/auth/refresh-session`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Session refreshed",
  "session_id": "uuid"
}
```

---

## 4. Admin Full Endpoints

### 4.1 Get All Clients
**GET** `/api/v1/admin/clients`

**Query Parameters:**
- `status` (optional): Filter by status (e.g., "documents_pending", "under_review")
- `year` (optional): Filter by filing year (e.g., 2024)
- `search` (optional): Search by name, email, or phone

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "name": "John Doe",
    "email": "client@example.com",
    "phone": "+1234567890",
    "filingYear": 2024,
    "status": "documents_pending",
    "paymentStatus": "pending",
    "assignedAdminId": "uuid",
    "assignedAdminName": "Admin One",
    "totalAmount": 500.00,
    "paidAmount": 0.00,
    "createdAt": "2024-01-15T10:30:00",
    "updatedAt": "2024-01-15T10:30:00"
  }
]
```

**cURL:**
```bash
curl -X GET "http://localhost:8001/api/v1/admin/clients?status=documents_pending&year=2024" \
  -H "Authorization: Bearer <admin_access_token>"
```

---

### 4.2 Get Client Detail
**GET** `/api/v1/admin/clients/{client_id}`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "client@example.com",
  "phone": "+1234567890",
  "filingYear": 2024,
  "status": "documents_pending",
  "paymentStatus": "pending",
  "assignedAdminId": "uuid",
  "assignedAdminName": "Admin One",
  "totalAmount": 500.00,
  "paidAmount": 0.00,
  "createdAt": "2024-01-15T10:30:00",
  "updatedAt": "2024-01-15T10:30:00"
}
```

---

### 4.3 Update Client
**PATCH** `/api/v1/admin/clients/{client_id}`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "status": "under_review",
  "paymentStatus": "partial",
  "totalAmount": 500.00,
  "paidAmount": 250.00
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "status": "under_review",
  "paymentStatus": "partial",
  "totalAmount": 500.00,
  "paidAmount": 250.00
}
```

---

### 4.4 Delete Client
**DELETE** `/api/v1/admin/clients/{client_id}`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
{
  "message": "Client deleted successfully"
}
```

---

### 4.5 Get Documents
**GET** `/api/v1/admin/documents`

**Query Parameters:**
- `client_id` (optional): Filter by client ID
- `status` (optional): Filter by status

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "name": "T4 Slip",
    "original_filename": "t4_2024.pdf",
    "file_type": "pdf",
    "file_size": 102400,
    "section_name": "income",
    "status": "pending",
    "encrypted": true,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

### 4.6 Update Document Status
**PATCH** `/api/v1/admin/documents/{document_id}`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "status": "approved"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "status": "approved"
}
```

---

### 4.7 Get Payments
**GET** `/api/v1/admin/payments`

**Query Parameters:**
- `client_id` (optional): Filter by client ID

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "clientId": "uuid",
    "amount": 500.00,
    "method": "E-Transfer",
    "note": "Payment for tax filing",
    "status": "received",
    "isRequest": false,
    "createdAt": "2024-01-15T10:30:00"
  }
]
```

---

### 4.8 Create Payment
**POST** `/api/v1/admin/payments`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "client_id": "uuid",
  "amount": 500.00,
  "method": "E-Transfer",
  "note": "Payment for tax filing",
  "is_request": false
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "clientId": "uuid",
  "amount": 500.00,
  "method": "E-Transfer",
  "status": "received",
  "createdAt": "2024-01-15T10:30:00"
}
```

---

### 4.9 Get Analytics
**GET** `/api/v1/admin/analytics`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
{
  "totalClients": 50,
  "totalAdmins": 5,
  "pendingDocuments": 25,
  "pendingPayments": 10,
  "completedFilings": 15,
  "totalRevenue": 25000.00,
  "monthlyRevenue": [
    {
      "month": "Jan",
      "revenue": 5000.00
    },
    {
      "month": "Feb",
      "revenue": 6000.00
    }
  ],
  "clientsByStatus": [
    {
      "status": "Documents Pending",
      "count": 20
    },
    {
      "status": "Under Review",
      "count": 15
    }
  ],
  "adminWorkload": []
}
```

---

### 4.10 Get Admin Users
**GET** `/api/v1/admin/admin-users`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "email": "admin@taxease.com",
    "name": "Admin One",
    "role": "admin",
    "is_active": true
  }
]
```

---

## 5. Chat Endpoints

### 5.1 Send Message
**POST** `/api/v1/chat/send`

**Request Body:**
```json
{
  "client_id": "uuid",
  "message": "Hello, I have a question about my tax return.",
  "sender_role": "client"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "sender_role": "client",
  "message": "Hello, I have a question about my tax return.",
  "created_at": "2024-01-15T10:30:00",
  "read_by_client": true,
  "read_by_admin": false
}
```

**cURL:**
```bash
curl -X POST http://localhost:8001/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "uuid",
    "message": "Hello, I have a question about my tax return.",
    "sender_role": "client"
  }'
```

---

### 5.2 Get Messages
**GET** `/api/v1/chat/{client_id}`

**Response (200 OK):**
```json
{
  "messages": [
    {
      "id": "uuid",
      "sender_role": "client",
      "message": "Hello, I have a question about my tax return.",
      "created_at": "2024-01-15T10:30:00",
      "read_by_client": true,
      "read_by_admin": false
    },
    {
      "id": "uuid",
      "sender_role": "admin",
      "message": "Sure, how can I help you?",
      "created_at": "2024-01-15T10:35:00",
      "read_by_client": false,
      "read_by_admin": true
    }
  ],
  "total": 2
}
```

**cURL:**
```bash
curl -X GET http://localhost:8001/api/v1/chat/{client_id}
```

---

### 5.3 Mark Messages as Read
**PUT** `/api/v1/chat/{client_id}/mark-read?role=admin`

**Query Parameters:**
- `role`: "client" or "admin"

**Response (200 OK):**
```json
{
  "message": "Messages marked as read for admin"
}
```

---

### 5.4 Get Unread Count
**GET** `/api/v1/chat/{client_id}/unread-count?role=admin`

**Query Parameters:**
- `role`: "client" or "admin"

**Response (200 OK):**
```json
{
  "unread_count": 3
}
```

---

## 6. Document Endpoints

### 6.1 Upload Document
**POST** `/api/v1/documents/upload`

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: File (PDF, JPG, PNG, etc.)
- `client_id`: Client UUID (required)
- `section`: Section name (optional)
- `document_type`: Document type (default: "receipt")

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "t4_2024.pdf",
  "original_filename": "t4_2024.pdf",
  "file_type": "pdf",
  "file_size": 102400,
  "section_name": "income",
  "status": "pending",
  "encrypted": true,
  "created_at": "2024-01-15T10:30:00"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8001/api/v1/documents/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/document.pdf" \
  -F "client_id=uuid" \
  -F "section=income" \
  -F "document_type=receipt"
```

---

### 6.2 Download Document
**GET** `/api/v1/documents/{document_id}/download`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** Binary file content (decrypted)

**cURL:**
```bash
curl -X GET http://localhost:8001/api/v1/documents/{document_id}/download \
  -H "Authorization: Bearer <access_token>" \
  -o downloaded_file.pdf
```

---

### 6.3 Get Client Documents
**GET** `/api/v1/documents/client/{client_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "documents": [
    {
      "id": "uuid",
      "name": "T4 Slip",
      "original_filename": "t4_2024.pdf",
      "file_type": "pdf",
      "file_size": 102400,
      "section_name": "income",
      "status": "pending",
      "encrypted": true,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

---

### 6.4 Delete Document
**DELETE** `/api/v1/documents/{document_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Document deleted successfully"
}
```

---

## 7. T1 Tax Form Endpoints

### 7.1 Submit T1 Form
**POST** `/api/v1/t1/tax-return`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "client_id": "uuid",
  "filing_year": 2024,
  "formData": {
    "personalInfo": {
      "firstName": "John",
      "lastName": "Doe",
      "sin": "123456789",
      "dateOfBirth": "1990-01-15",
      "maritalStatus": "single"
    },
    "income": {
      "employmentIncome": 50000.00,
      "otherIncome": 0.00
    },
    "deductions": {
      "rrspContributions": 5000.00
    }
  }
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "filing_year": 2024,
  "status": "submitted",
  "message": "T1 form submitted successfully"
}
```

---

### 7.2 Get Client T1 Form
**GET** `/api/v1/t1/tax-return?client_id={client_id}&filing_year=2024`

**Query Parameters:**
- `client_id`: Client UUID (required)
- `filing_year`: Filing year (optional, defaults to current year)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "filing_year": 2024,
  "status": "submitted",
  "form_data": {
    "personalInfo": {
      "firstName": "John",
      "lastName": "Doe",
      "sin": "123456789"
    }
  },
  "first_name": "John",
  "last_name": "Doe",
  "sin": "123456789",
  "marital_status": "single"
}
```

---

## 8. Filing Status Endpoints

### 8.1 Get Client Filing Status
**GET** `/api/v1/filing-status/client/{client_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "client_id": "uuid",
  "filing_year": 2024,
  "current_status": "under_review",
  "timeline": [
    {
      "step": 1,
      "name": "Documents Submitted",
      "status": "completed",
      "completed_at": "2024-01-15T10:00:00"
    },
    {
      "step": 2,
      "name": "Under Review",
      "status": "in_progress",
      "completed_at": null
    },
    {
      "step": 3,
      "name": "Awaiting Payment",
      "status": "pending",
      "completed_at": null
    }
  ]
}
```

---

### 8.2 Update Filing Status (Admin)
**PUT** `/api/v1/filing-status/admin/{return_id}/status`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "status": "awaiting_payment",
  "notes": "Review completed, ready for payment"
}
```

**Response (200 OK):**
```json
{
  "return_id": "uuid",
  "status": "awaiting_payment",
  "message": "Status updated successfully"
}
```

---

### 8.3 Get All Returns (Admin)
**GET** `/api/v1/filing-status/admin/returns`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "client_id": "uuid",
    "client_name": "John Doe",
    "filing_year": 2024,
    "status": "under_review",
    "payment_status": "pending"
  }
]
```

---

## 9. Health Check

### 9.1 Root Endpoint
**GET** `/`

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

**cURL:**
```bash
curl http://localhost:8001/
```

---

## Testing Tools

### Using cURL
All endpoints can be tested using cURL commands provided above.

### Using Postman
1. Import the collection (create from examples above)
2. Set base URL: `http://localhost:8001`
3. Set environment variables:
   - `base_url`: `http://localhost:8001`
   - `api_base`: `http://localhost:8001/api/v1`
   - `access_token`: (set after login)
   - `client_id`: (set after registration)

### Using Python Requests
```python
import requests

BASE_URL = "http://localhost:8001/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "client@example.com", "password": "password123"}
)
token = response.json()["access_token"]

# Get client info
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/client/me", headers=headers)
print(response.json())
```

### Using JavaScript/Fetch
```javascript
const BASE_URL = "http://localhost:8001/api/v1";

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "client@example.com",
    password: "password123"
  })
});

const { access_token } = await loginResponse.json();

// Get client info
const clientResponse = await fetch(`${BASE_URL}/client/me`, {
  headers: { "Authorization": `Bearer ${access_token}` }
});

const clientData = await clientResponse.json();
console.log(clientData);
```

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request:**
```json
{
  "detail": "Error message here"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid or expired token"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Demo Credentials

### Client
- **Email**: `client@example.com`
- **Password**: `password123`
- **OTP**: `123456`

### Admin
- **Email**: `admin@taxease.com`
- **Password**: `Admin123!`

### Superadmin
- **Email**: `superadmin@taxease.com`
- **Password**: `Super123!`

---

## Notes

1. **Static OTP**: All OTP verifications use `123456`
2. **Token Expiry**: Access tokens expire in 30 minutes (1800 seconds)
3. **File Encryption**: All uploaded documents are encrypted before storage
4. **Session Management**: Admin sessions use Redis for token revocation
5. **CORS**: Backend allows all origins for development
6. **Database**: PostgreSQL database with JSONB support for flexible data storage

---

## Quick Start Testing

1. **Start Backend:**
   ```bash
   cd /home/cyberdude/Documents/Projects/CA-final
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Test Health:**
   ```bash
   curl http://localhost:8001/
   ```

3. **Register Client:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","first_name":"Test","last_name":"User","password":"test123"}'
   ```

4. **Login:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123"}'
   ```

---

**Last Updated**: 2024-01-15
**Backend Version**: 1.0.0





