# API REDESIGN — PHASE 4: Error & Authorization Model

**Date:** January 5, 2026  
**Status:** AWAITING APPROVAL  
**Scope:** Complete Authentication, Authorization, and Error Handling Standards

---

## Executive Summary

This document defines the **complete security and error handling model** for the TaxEase API. All endpoints follow consistent authentication, authorization, and error response patterns.

---

# 1. AUTHENTICATION MODEL

## 1.1 JWT Token Structure

### Access Token
```
Payload:
{
  "sub": "uuid",           // User/Admin ID
  "email": "user@example.com",
  "role": "user",          // user, admin, superadmin
  "type": "access",
  "iat": 1704499200,       // Issued at
  "exp": 1704502800        // Expires (1 hour)
}

Header:
Authorization: Bearer <access_token>
```

### Refresh Token
```
Payload:
{
  "sub": "uuid",
  "type": "refresh",
  "iat": 1704499200,
  "exp": 1709683200        // Expires (30 days)
}
```

## 1.2 Token Lifecycle

| Action | Endpoint | Access Token | Refresh Token |
|--------|----------|--------------|---------------|
| Login | `POST /auth/login` | Generated | Generated |
| API Call | Any protected endpoint | Required | Not used |
| Refresh | `POST /sessions/refresh` | Not required | Required |
| Logout | `POST /auth/logout` | Optional | Optional (to revoke) |

## 1.3 Token Storage

**Client-Side:**
- Access token: Memory only (not localStorage/sessionStorage)
- Refresh token: HttpOnly cookie (secure, SameSite=Strict)

**Server-Side:**
- No token storage (stateless JWT)
- Blacklist only for logout (Redis, TTL = token expiry)

## 1.4 Token Security

| Feature | Implementation |
|---------|----------------|
| Algorithm | HS256 (HMAC-SHA256) |
| Secret | Environment variable (min 32 chars) |
| Rotation | Refresh token rotates on each refresh |
| Blacklist | Redis set with TTL |
| Rate Limiting | 5 login attempts per 15 min per IP |

---

# 2. AUTHORIZATION MODEL

## 2.1 Role Hierarchy

```
┌─────────────────┐
│   Superadmin    │  Full system access
└────────┬────────┘
         │
┌────────▼────────┐
│      Admin      │  Assigned filings + permissions
└────────┬────────┘
         │
┌────────▼────────┐
│      User       │  Self-service only
└─────────────────┘
```

## 2.2 Permission Keys

| Permission | Description | Default Role |
|------------|-------------|--------------|
| `add_edit_payment` | Record and modify payments | Admin |
| `add_edit_client` | Create and modify filing records | Admin |
| `request_documents` | Request missing documents from clients | Admin |
| `assign_clients` | Assign filings to admins | Admin |
| `view_analytics` | Access analytics dashboard | Admin |
| `approve_cost_estimate` | Set filing fees | Admin |
| `update_workflow` | Change filing status | Admin |
| `manage_admins` | CRUD admin users | Superadmin |
| `view_audit_logs` | Access audit trail | Superadmin |

**Note:** Superadmin has all permissions by default (no need to specify)

## 2.3 Endpoint Authorization Matrix

### Public Endpoints (No Auth Required)
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/otp/request
POST /api/v1/auth/otp/verify
POST /api/v1/auth/password/reset-request
POST /api/v1/auth/password/reset-confirm
```

### User Endpoints (JWT Required, Role = User)
```
GET  /api/v1/users/me                    // Self only
PATCH /api/v1/users/me                   // Self only
GET  /api/v1/filings                     // Own filings only
GET  /api/v1/filings/{id}                // Own filing only
GET  /api/v1/filings/{id}/timeline       // Own filing only
GET  /api/v1/t1-forms                    // Own forms only
GET  /api/v1/t1-forms/{id}               // Own form only
POST /api/v1/t1-forms                    // Create own form
PATCH /api/v1/t1-forms/{id}              // Own form, status=draft
POST /api/v1/t1-forms/{id}/submit        // Own form
GET  /api/v1/documents                   // Own documents only
GET  /api/v1/documents/{id}              // Own document only
GET  /api/v1/documents/{id}/download     // Own document only
POST /api/v1/documents                   // Upload own document
PATCH /api/v1/documents/{id}             // Own document (limited fields)
GET  /api/v1/notifications               // Own notifications only
GET  /api/v1/notifications/unread-count  // Own count
PATCH /api/v1/notifications/{id}/read    // Own notification
PATCH /api/v1/notifications/read-all     // Own notifications
```

### Admin Endpoints (JWT Required, Role = Admin)
```
GET  /api/v1/users/{id}                  // View user
GET  /api/v1/admins                      // List all (superadmin) or self
GET  /api/v1/admins/{id}                 // Self or superadmin
PATCH /api/v1/admins/{id}                // Self (limited) or superadmin (all)
GET  /api/v1/filings                     // Assigned filings (or all if permission)
GET  /api/v1/filings/{id}                // Assigned filing
POST /api/v1/filings                     // Create filing
PATCH /api/v1/filings/{id}/status        // Assigned filing + permission
PATCH /api/v1/filings/{id}/assignment    // Permission: assign_clients
PATCH /api/v1/filings/{id}/fee           // Assigned filing + permission
GET  /api/v1/filings/{id}/timeline       // Assigned filing
GET  /api/v1/t1-forms                    // Assigned client forms
GET  /api/v1/t1-forms/{id}               // Assigned client form
GET  /api/v1/documents                   // Assigned client documents
GET  /api/v1/documents/{id}              // Assigned client document
GET  /api/v1/documents/{id}/download     // Assigned client document
PATCH /api/v1/documents/{id}             // Assigned client document
PATCH /api/v1/documents/{id}/status      // Assigned client document + permission
POST /api/v1/documents/request           // Permission: request_documents
DELETE /api/v1/documents/{id}            // Assigned client document
GET  /api/v1/payments                    // All payments (filtered by permission)
GET  /api/v1/payments/{id}               // Any payment
POST /api/v1/payments                    // Permission: add_edit_payment
GET  /api/v1/payments/filing/{id}        // Assigned filing
GET  /api/v1/analytics/dashboard         // Permission: view_analytics
GET  /api/v1/analytics/revenue           // Permission: view_analytics
```

### Superadmin Endpoints (JWT Required, Role = Superadmin)
```
PATCH /api/v1/users/{id}/status          // Activate/deactivate user
POST /api/v1/admins                      // Create admin
DELETE /api/v1/admins/{id}               // Delete admin
DELETE /api/v1/filings/{id}              // Delete filing
GET  /api/v1/analytics/workload          // View all admin workload
GET  /api/v1/audit-logs                  // View audit trail
GET  /api/v1/audit-logs/{id}             // View audit entry
```

## 2.4 Ownership Validation

### Resource Ownership Rules

| Resource | Owner Check | Implementation |
|----------|-------------|----------------|
| User profile | `user_id == jwt.sub` | Middleware |
| Filing | `filing.user_id == jwt.sub` OR `filing.assigned_admin_id == jwt.sub` | Service layer |
| T1 Form | `t1form.filing.user_id == jwt.sub` OR assigned admin | Service layer |
| Document | `document.filing.user_id == jwt.sub` OR assigned admin | Service layer |
| Notification | `notification.user_id == jwt.sub` | Service layer |

### Assignment Check (Admin)

For admin operations, check if filing is assigned to admin:

```python
def is_admin_assigned(filing_id: str, admin_id: str) -> bool:
    """Check if admin is assigned to filing"""
    return db.query(AdminClientMap).filter(
        AdminClientMap.filing_id == filing_id,
        AdminClientMap.admin_id == admin_id
    ).exists()
```

## 2.5 Permission Check Decorator

```python
from functools import wraps
from fastapi import HTTPException, status

def require_permission(permission: str):
    """Decorator to check if user has required permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = get_current_user()
            
            # Superadmin bypasses permission check
            if current_user.role == "superadmin":
                return await func(*args, **kwargs)
            
            # Check if admin has permission
            if current_user.role == "admin":
                if permission in current_user.permissions:
                    return await func(*args, **kwargs)
            
            # User role cannot have permissions
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return wrapper
    return decorator
```

---

# 3. ERROR RESPONSE MODEL

## 3.1 Standard Error Format

All error responses follow this structure:

```typescript
{
  "error": {
    "code": string,           // Machine-readable error code
    "message": string,        // Human-readable message
    "details"?: object,       // Optional additional context
    "trace_id"?: string       // Optional request trace ID
  }
}
```

## 3.2 HTTP Status Codes

| Code | Name | Usage |
|------|------|-------|
| 200 | OK | Successful GET, PATCH, PUT |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Malformed request, invalid syntax |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (duplicate, state violation) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 501 | Not Implemented | Chat endpoints (email redirect) |
| 503 | Service Unavailable | Temporary unavailability |

## 3.3 Error Code Registry

### Authentication Errors (AUTH_*)

| Code | HTTP | Message |
|------|------|---------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Invalid email or password |
| `AUTH_EMAIL_NOT_VERIFIED` | 403 | Email address not verified |
| `AUTH_ACCOUNT_INACTIVE` | 403 | Account has been deactivated |
| `AUTH_TOKEN_EXPIRED` | 401 | Access token has expired |
| `AUTH_TOKEN_INVALID` | 401 | Invalid or malformed token |
| `AUTH_TOKEN_REVOKED` | 401 | Token has been revoked |
| `AUTH_REFRESH_TOKEN_INVALID` | 401 | Invalid refresh token |

### Authorization Errors (AUTHZ_*)

| Code | HTTP | Message |
|------|------|---------|
| `AUTHZ_INSUFFICIENT_PERMISSIONS` | 403 | Insufficient permissions for this action |
| `AUTHZ_NOT_RESOURCE_OWNER` | 403 | You do not own this resource |
| `AUTHZ_NOT_ASSIGNED` | 403 | You are not assigned to this filing |
| `AUTHZ_ROLE_REQUIRED` | 403 | This action requires a specific role |

### Validation Errors (VALIDATION_*)

| Code | HTTP | Message |
|------|------|---------|
| `VALIDATION_REQUIRED_FIELD` | 422 | Required field missing |
| `VALIDATION_INVALID_FORMAT` | 422 | Field format is invalid |
| `VALIDATION_OUT_OF_RANGE` | 422 | Value out of acceptable range |
| `VALIDATION_TOO_LONG` | 422 | Value exceeds maximum length |
| `VALIDATION_TOO_SHORT` | 422 | Value below minimum length |
| `VALIDATION_INVALID_EMAIL` | 422 | Invalid email format |
| `VALIDATION_INVALID_PHONE` | 422 | Invalid phone format |
| `VALIDATION_INVALID_UUID` | 422 | Invalid UUID format |
| `VALIDATION_WEAK_PASSWORD` | 422 | Password does not meet requirements |

### Resource Errors (RESOURCE_*)

| Code | HTTP | Message |
|------|------|---------|
| `RESOURCE_NOT_FOUND` | 404 | Resource not found |
| `RESOURCE_ALREADY_EXISTS` | 409 | Resource already exists |
| `RESOURCE_CONFLICT` | 409 | Resource state conflict |
| `RESOURCE_LOCKED` | 409 | Resource is locked (e.g., T1 submitted) |
| `RESOURCE_DELETED` | 410 | Resource has been deleted |

### Business Logic Errors (BUSINESS_*)

| Code | HTTP | Message |
|------|------|---------|
| `BUSINESS_DUPLICATE_FILING` | 409 | Filing already exists for this user and year |
| `BUSINESS_T1_ALREADY_SUBMITTED` | 409 | T1 form has already been submitted |
| `BUSINESS_INVALID_STATUS_TRANSITION` | 422 | Invalid status transition |
| `BUSINESS_PAYMENT_EXCEEDS_FEE` | 422 | Payment amount exceeds total fee |
| `BUSINESS_OTP_EXPIRED` | 422 | OTP code has expired |
| `BUSINESS_OTP_INVALID` | 422 | Invalid OTP code |
| `BUSINESS_OTP_ALREADY_USED` | 422 | OTP code has already been used |

### File Errors (FILE_*)

| Code | HTTP | Message |
|------|------|---------|
| `FILE_TOO_LARGE` | 413 | File exceeds maximum size (10MB) |
| `FILE_INVALID_TYPE` | 422 | File type not allowed |
| `FILE_UPLOAD_FAILED` | 500 | File upload failed |
| `FILE_ENCRYPTION_FAILED` | 500 | File encryption failed |
| `FILE_DECRYPTION_FAILED` | 500 | File decryption failed |

### Rate Limiting Errors (RATE_*)

| Code | HTTP | Message |
|------|------|---------|
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests. Try again later. |

### Server Errors (SERVER_*)

| Code | HTTP | Message |
|------|------|---------|
| `SERVER_INTERNAL_ERROR` | 500 | An unexpected error occurred |
| `SERVER_DATABASE_ERROR` | 500 | Database operation failed |
| `SERVER_EXTERNAL_SERVICE_ERROR` | 503 | External service unavailable |

## 3.4 Error Response Examples

### Validation Error (422)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "code": "VALIDATION_INVALID_EMAIL",
        "message": "Invalid email format"
      },
      {
        "field": "password",
        "code": "VALIDATION_WEAK_PASSWORD",
        "message": "Password must be at least 8 characters and contain uppercase, lowercase, and number"
      }
    ]
  }
}
```

### Authentication Error (401)
```json
{
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

### Authorization Error (403)
```json
{
  "error": {
    "code": "AUTHZ_INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to perform this action",
    "details": {
      "required_permission": "add_edit_payment",
      "user_permissions": ["request_documents", "view_analytics"]
    }
  }
}
```

### Resource Not Found (404)
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Filing not found",
    "details": {
      "resource_type": "Filing",
      "resource_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

### Business Logic Error (409)
```json
{
  "error": {
    "code": "BUSINESS_T1_ALREADY_SUBMITTED",
    "message": "This T1 form has already been submitted and cannot be modified",
    "details": {
      "t1_form_id": "550e8400-e29b-41d4-a716-446655440000",
      "submitted_at": "2026-01-05T11:00:00Z"
    }
  }
}
```

### Rate Limit Error (429)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Try again in 45 seconds.",
    "details": {
      "retry_after": 45,
      "limit": 5,
      "window": "15 minutes"
    }
  }
}
```

### Server Error (500)
```json
{
  "error": {
    "code": "SERVER_INTERNAL_ERROR",
    "message": "An unexpected error occurred. Please try again later.",
    "trace_id": "abc123-def456-ghi789"
  }
}
```

**Note:** Never expose internal details (stack traces, database errors) in production

---

# 4. CORS CONFIGURATION

## 4.1 Allowed Origins

### Development
```
http://localhost:3000      # React admin dev
http://localhost:5173      # Vite dev server
http://localhost:8080      # Flutter web dev
http://127.0.0.1:*         # Alternative localhost
```

### Production
```
https://admin.taxease.ca   # Admin dashboard
https://app.taxease.ca     # Client web app
https://taxease.ca         # Marketing site (if needed)
```

## 4.2 CORS Headers

```
Access-Control-Allow-Origin: <origin>
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, Idempotency-Key
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
Access-Control-Expose-Headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
```

## 4.3 Preflight Handling

```
OPTIONS /api/v1/*
Response: 204 No Content
Headers: CORS headers as above
```

---

# 5. SECURITY HEADERS

## 5.1 Required Headers

All API responses include:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

## 5.2 Rate Limiting Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704499200
```

## 5.3 Trace Headers

For debugging (not exposed in production error messages):

```
X-Request-ID: uuid-v4
X-Trace-ID: uuid-v4
```

---

# 6. OTP VERIFICATION FLOW

## 6.1 OTP Generation

```python
import secrets
import string

def generate_otp(length: int = 6) -> str:
    """Generate random numeric OTP"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))
```

## 6.2 OTP Storage (In-Memory)

```python
# Redis structure
otp_key = f"otp:{email}:{purpose}"
otp_data = {
    "code": "123456",
    "expires_at": "2026-01-05T10:40:00Z",
    "attempts": 0
}
# TTL = 10 minutes
redis.setex(otp_key, 600, json.dumps(otp_data))
```

## 6.3 OTP Verification Rules

| Rule | Value |
|------|-------|
| Code length | 6 digits |
| Expiry | 10 minutes |
| Max attempts | 5 |
| Lockout after 5 failed | 30 minutes |
| Rate limit | 3 OTP requests per 5 min per email |

## 6.4 OTP Error Responses

```json
// Expired
{
  "error": {
    "code": "BUSINESS_OTP_EXPIRED",
    "message": "OTP code has expired. Please request a new one."
  }
}

// Invalid
{
  "error": {
    "code": "BUSINESS_OTP_INVALID",
    "message": "Invalid OTP code. 3 attempts remaining."
  }
}

// Locked out
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many failed attempts. Try again in 30 minutes.",
    "details": {
      "retry_after": 1800
    }
  }
}
```

---

# 7. PASSWORD REQUIREMENTS

## 7.1 Password Policy

| Rule | Requirement |
|------|-------------|
| Minimum length | 8 characters |
| Maximum length | 128 characters |
| Uppercase | At least 1 |
| Lowercase | At least 1 |
| Digit | At least 1 |
| Special char | Optional (recommended) |
| No common passwords | Check against OWASP list |

## 7.2 Password Hashing

```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
```

## 7.3 Password Validation Error

```json
{
  "error": {
    "code": "VALIDATION_WEAK_PASSWORD",
    "message": "Password does not meet requirements",
    "details": {
      "requirements": [
        "At least 8 characters",
        "At least one uppercase letter",
        "At least one lowercase letter",
        "At least one digit"
      ],
      "violations": [
        "Missing uppercase letter",
        "Too short (6 characters, minimum 8)"
      ]
    }
  }
}
```

---

# 8. MIDDLEWARE STACK

## 8.1 Request Processing Order

```
1. CORS Middleware (preflight, origin check)
2. Security Headers Middleware
3. Request ID Middleware (generate trace ID)
4. Rate Limiting Middleware
5. Authentication Middleware (JWT validation)
6. Authorization Middleware (role/permission check)
7. Route Handler
8. Error Handler Middleware
9. Response Middleware (format, headers)
```

## 8.2 Authentication Middleware

```python
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError

async def authenticate_request(request: Request):
    """Validate JWT token and attach user to request"""
    
    # Skip auth for public endpoints
    if is_public_endpoint(request.url.path):
        return
    
    # Extract token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_TOKEN_INVALID", "message": "Missing or invalid authorization header"}
        )
    
    token = auth_header.split(" ")[1]
    
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_TOKEN_REVOKED", "message": "Token has been revoked"}
        )
    
    # Decode and validate token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.state.user = payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_TOKEN_INVALID", "message": str(e)}
        )
```

## 8.3 Authorization Middleware

```python
async def authorize_request(request: Request):
    """Check if user has permission for endpoint"""
    
    user = request.state.user
    endpoint_config = get_endpoint_config(request.url.path, request.method)
    
    # Check role requirement
    if endpoint_config.required_role:
        if user.role not in endpoint_config.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "AUTHZ_ROLE_REQUIRED",
                    "message": f"This action requires {endpoint_config.required_role} role"
                }
            )
    
    # Check permission requirement
    if endpoint_config.required_permission:
        if user.role != "superadmin":  # Superadmin bypasses permission check
            if endpoint_config.required_permission not in user.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "AUTHZ_INSUFFICIENT_PERMISSIONS",
                        "message": "Insufficient permissions for this action"
                    }
                )
```

---

# 9. AUDIT LOGGING

## 9.1 Audit Log Triggers

All destructive or sensitive operations are logged:

| Action | Logged Data |
|--------|-------------|
| User registration | Email, timestamp |
| Login attempt | Email, IP, success/failure |
| Password change | User ID, timestamp |
| Filing status change | Filing ID, old status, new status, admin ID |
| Document upload | Document ID, filing ID, user ID |
| Document status change | Document ID, old status, new status, admin ID |
| Payment recorded | Payment ID, amount, filing ID, admin ID |
| Admin created | New admin ID, creator ID |
| Admin deleted | Deleted admin ID, deleter ID |
| Permission changed | Admin ID, old permissions, new permissions |

## 9.2 Audit Log Format

```typescript
{
  "id": "uuid",
  "action": "status_update",           // Action type
  "entity_type": "Filing",             // Resource type
  "entity_id": "uuid",                 // Resource ID
  "old_value": "submitted",            // Before change (JSON string)
  "new_value": "payment_request_sent", // After change (JSON string)
  "performed_by_id": "uuid",           // User/Admin ID
  "performed_by_name": "Jane Smith",   // Cached for display
  "performed_by_email": "jane@example.com",
  "ip_address": "192.168.1.100",       // Request IP
  "user_agent": "Mozilla/5.0...",      // Client info
  "timestamp": "2026-01-05T11:00:00Z"
}
```

## 9.3 Audit Log Retention

| Environment | Retention |
|-------------|-----------|
| Development | 30 days |
| Staging | 90 days |
| Production | 7 years (compliance) |

---

# 10. IDEMPOTENCY IMPLEMENTATION

## 10.1 Idempotency Key Storage

```python
# Redis structure
idempotency_key = f"idempotency:{key}"
idempotency_data = {
    "request_hash": "sha256_of_payload",
    "response_status": 201,
    "response_body": {...},
    "created_at": "2026-01-05T11:00:00Z"
}
# TTL = 24 hours
redis.setex(idempotency_key, 86400, json.dumps(idempotency_data))
```

## 10.2 Idempotency Check Flow

```python
from hashlib import sha256

async def check_idempotency(request: Request):
    """Check if request is duplicate based on idempotency key"""
    
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return None  # No idempotency check requested
    
    # Retrieve cached response
    cached = redis.get(f"idempotency:{idempotency_key}")
    if not cached:
        return None  # First request with this key
    
    cached_data = json.loads(cached)
    
    # Hash current request payload
    request_body = await request.body()
    request_hash = sha256(request_body).hexdigest()
    
    # Check if payload matches
    if request_hash != cached_data["request_hash"]:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "IDEMPOTENCY_CONFLICT",
                "message": "Request with this idempotency key has different payload"
            }
        )
    
    # Return cached response
    return Response(
        status_code=200,  # Change 201 to 200 for cached response
        content=json.dumps(cached_data["response_body"]),
        media_type="application/json"
    )
```

## 10.3 Endpoints Using Idempotency

| Endpoint | Required? | Use Case |
|----------|-----------|----------|
| `POST /api/v1/payments` | Recommended | Prevent duplicate payment recording |
| `POST /api/v1/t1-forms/{id}/submit` | Recommended | Prevent duplicate submission |
| `POST /api/v1/documents` | Optional | Each upload is unique file |
| `POST /api/v1/filings` | Optional | Unique constraint handles duplicates |

---

# 11. CHAT ENDPOINT DEPRECATION

## 11.1 Chat Endpoint Responses

All chat endpoints return `501 Not Implemented`:

```
GET  /chat/*
POST /chat/*
PUT  /chat/*
```

**Response (501):**
```json
{
  "error": {
    "code": "FEATURE_NOT_IMPLEMENTED",
    "message": "Chat feature is not available. Please check your email for communications.",
    "details": {
      "reason": "Communication is email-first",
      "alternative": "All communications are sent to your registered email address"
    }
  }
}
```

## 11.2 Frontend Handling

**Flutter:**
```dart
if (response.statusCode == 501) {
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      title: Text('Check Your Email'),
      content: Text('All communications are sent via email. Please check your inbox.'),
    ),
  );
}
```

**React:**
```typescript
if (response.status === 501) {
  notification.info({
    message: 'Check Your Email',
    description: 'All communications are sent via email. Please check your inbox.',
  });
}
```

---

# 12. SECURITY CHECKLIST

## 12.1 Production Security Requirements

- [x] JWT secret is strong (min 32 chars) and stored in environment variable
- [x] HTTPS only (redirect HTTP to HTTPS)
- [x] CORS restricted to production domains
- [x] Rate limiting enabled on all endpoints
- [x] Password hashing with bcrypt (rounds=12)
- [x] OTP codes are cryptographically random
- [x] Tokens stored in httpOnly cookies (refresh) or memory (access)
- [x] SQL injection prevention (parameterized queries)
- [x] XSS prevention (input sanitization, CSP headers)
- [x] File upload size limits (10MB)
- [x] File type validation
- [x] File encryption at rest (AES-256)
- [x] Audit logging for sensitive operations
- [x] No sensitive data in error messages
- [x] No stack traces in production
- [x] Database credentials in environment variables
- [x] API versioning (/v1/)
- [x] Deprecation headers for old versions

## 12.2 Common Vulnerabilities Prevented

| Vulnerability | Prevention |
|---------------|------------|
| SQL Injection | ORM with parameterized queries |
| XSS | Input sanitization, CSP headers |
| CSRF | SameSite cookies, CORS |
| JWT Attacks | Strong secret, short expiry, blacklist |
| Brute Force | Rate limiting, account lockout |
| Session Fixation | Token rotation on refresh |
| Mass Assignment | Explicit field validation |
| Path Traversal | UUID-based file names, validation |
| File Upload Attacks | Type validation, size limits, encryption |

---

# PHASE 4 COMPLETE — ERROR & AUTHORIZATION MODEL

## Summary

**Complete Security Model Defined:**
1. ✅ JWT-based authentication with access + refresh tokens
2. ✅ Role-based authorization (User, Admin, Superadmin)
3. ✅ Permission-based access control (7 permissions)
4. ✅ Ownership validation for all resources
5. ✅ Complete error response format with 40+ error codes
6. ✅ HTTP status code usage standards
7. ✅ OTP verification flow (email-only, 10-minute expiry)
8. ✅ Password policy (min 8 chars, complexity rules)
9. ✅ Rate limiting rules per endpoint
10. ✅ CORS configuration (dev + production)
11. ✅ Security headers (HSTS, CSP, XSS protection)
12. ✅ Audit logging for sensitive operations
13. ✅ Idempotency key implementation
14. ✅ Chat endpoint deprecation (501 response)
15. ✅ Production security checklist

**Key Security Features:**
- Stateless JWT with 1-hour access token expiry
- Refresh token rotation on each refresh
- Token blacklist for logout
- 5 login attempts per 15 min rate limit
- bcrypt password hashing (rounds=12)
- AES-256 file encryption
- Email-only OTP (no SMS)
- Audit trail with 7-year retention

**Frontend Impact:** Zero (all security handled server-side)

---

**Reply "PROCEED TO PHASE 5" to continue with cleanup & final notes.**
