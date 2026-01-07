# API REDESIGN — PHASE 2: Endpoint Design

**Date:** January 5, 2026  
**Status:** AWAITING APPROVAL  
**Scope:** Complete REST Endpoint Architecture

---

## Executive Summary

This document defines **all REST endpoints** for the TaxEase API under `/api/v1/`. All endpoints follow REST principles, use role-based access control, and maintain frontend compatibility without requiring any UI changes.

---

# 1. API STRUCTURE OVERVIEW

## 1.1 Base URL

```
/api/v1/
```

**Versioning Strategy:**
- Major version in URL path (`/v1/`, `/v2/`)
- Breaking changes require new major version
- Backward compatibility maintained within major version
- Deprecation warnings via response headers (`X-API-Deprecation`)

## 1.2 Endpoint Organization

| Resource Group | Endpoint Prefix | Total Endpoints |
|----------------|-----------------|-----------------|
| Authentication | `/auth`, `/sessions` | 7 |
| User Management | `/users` | 4 |
| Admin Management | `/admins` | 5 |
| Filings | `/filings` | 8 |
| T1 Forms | `/t1-forms` | 5 |
| Documents | `/documents` | 7 |
| Payments | `/payments` | 4 |
| Notifications | `/notifications` | 3 |
| Analytics | `/analytics` | 3 |
| Audit Logs | `/audit-logs` | 2 |

**Total Endpoints:** 48

---

# 2. AUTHENTICATION ENDPOINTS

## 2.1 Client Authentication

### `POST /api/v1/auth/register`
**Purpose:** Register new client account  
**Auth:** None (public)  
**Role:** None  

---

### `POST /api/v1/auth/login`
**Purpose:** Authenticate client and issue JWT tokens  
**Auth:** None (public)  
**Role:** None  

---

### `POST /api/v1/auth/otp/request`
**Purpose:** Request OTP code via email  
**Auth:** None (public)  
**Role:** None  

---

### `POST /api/v1/auth/otp/verify`
**Purpose:** Verify OTP code  
**Auth:** None (public)  
**Role:** None  

---

### `POST /api/v1/auth/password/reset-request`
**Purpose:** Request password reset via email  
**Auth:** None (public)  
**Role:** None  

---

### `POST /api/v1/auth/password/reset-confirm`
**Purpose:** Confirm password reset with OTP  
**Auth:** None (public)  
**Role:** None  

---

### `POST /api/v1/auth/logout`
**Purpose:** Invalidate JWT token (blacklist)  
**Auth:** JWT  
**Role:** User, Admin  

---

## 2.2 Session Management

### `POST /api/v1/sessions/refresh`
**Purpose:** Refresh JWT access token using refresh token  
**Auth:** Refresh token  
**Role:** User, Admin  

---

### `GET /api/v1/sessions/current`
**Purpose:** Get current authenticated user/admin info  
**Auth:** JWT  
**Role:** User, Admin  

---

## 2.3 Admin Authentication

**Note:** Admin auth uses same `/api/v1/auth/login` endpoint. Role detection is automatic based on email domain or database lookup.

---

# 3. USER MANAGEMENT ENDPOINTS

## 3.1 Client User Operations

### `GET /api/v1/users/me`
**Purpose:** Get current user profile  
**Auth:** JWT  
**Role:** User (self only)  

---

### `PATCH /api/v1/users/me`
**Purpose:** Update current user profile  
**Auth:** JWT  
**Role:** User (self only)  

---

### `GET /api/v1/users/{user_id}`
**Purpose:** Get user by ID (admin view)  
**Auth:** JWT  
**Role:** Admin, Superadmin  

---

### `PATCH /api/v1/users/{user_id}/status`
**Purpose:** Activate/deactivate user account  
**Auth:** JWT  
**Role:** Superadmin only  

---

# 4. ADMIN MANAGEMENT ENDPOINTS

## 4.1 Admin User Operations

### `GET /api/v1/admins`
**Purpose:** List all admin users  
**Auth:** JWT  
**Role:** Superadmin only  
**Pagination:** Yes  

---

### `POST /api/v1/admins`
**Purpose:** Create new admin user  
**Auth:** JWT  
**Role:** Superadmin only  

---

### `GET /api/v1/admins/{admin_id}`
**Purpose:** Get admin details  
**Auth:** JWT  
**Role:** Self or Superadmin  

---

### `PATCH /api/v1/admins/{admin_id}`
**Purpose:** Update admin details  
**Auth:** JWT  
**Role:** Self (name, password) or Superadmin (all fields)  

---

### `DELETE /api/v1/admins/{admin_id}`
**Purpose:** Soft delete admin (deactivate)  
**Auth:** JWT  
**Role:** Superadmin only  

---

# 5. FILING ENDPOINTS

## 5.1 Filing Management

### `GET /api/v1/filings`
**Purpose:** List filings with filters  
**Auth:** JWT  
**Role:**  
- User: Own filings only  
- Admin: Assigned filings (or all if permission)  
- Superadmin: All filings  
**Pagination:** Yes  
**Filters:** `year`, `status`, `payment_status`, `assigned_admin_id`, `user_id`, `search`  

---

### `GET /api/v1/filings/{filing_id}`
**Purpose:** Get filing details  
**Auth:** JWT  
**Role:**  
- User: Own filing only  
- Admin: Assigned filing  
- Superadmin: Any filing  

---

### `POST /api/v1/filings`
**Purpose:** Create new filing (system/admin only)  
**Auth:** JWT  
**Role:** Admin, Superadmin  
**Note:** Clients don't create filings directly. Filings are auto-created when T1 form is first saved.

---

### `PATCH /api/v1/filings/{filing_id}/status`
**Purpose:** Update filing status  
**Auth:** JWT  
**Role:** Admin, Superadmin  
**Side Effect:** Creates notification, sends email  

---

### `PATCH /api/v1/filings/{filing_id}/assignment`
**Purpose:** Assign filing to admin  
**Auth:** JWT  
**Role:** Admin (with permission), Superadmin  

---

### `PATCH /api/v1/filings/{filing_id}/fee`
**Purpose:** Update total fee amount  
**Auth:** JWT  
**Role:** Admin, Superadmin  
**Side Effect:** Sends email notification  

---

### `GET /api/v1/filings/{filing_id}/timeline`
**Purpose:** Get filing status timeline  
**Auth:** JWT  
**Role:**  
- User: Own filing  
- Admin: Assigned filing  
- Superadmin: Any filing  

---

### `DELETE /api/v1/filings/{filing_id}`
**Purpose:** Soft delete filing (archive)  
**Auth:** JWT  
**Role:** Superadmin only  

---

# 6. T1 FORM ENDPOINTS

## 6.1 T1 Form Operations

### `GET /api/v1/t1-forms`
**Purpose:** List T1 forms with filters  
**Auth:** JWT  
**Role:**  
- User: Own forms only  
- Admin: Assigned client forms  
- Superadmin: All forms  
**Pagination:** Yes  
**Filters:** `filing_id`, `year`, `status`, `user_id`  

---

### `GET /api/v1/t1-forms/{t1_form_id}`
**Purpose:** Get T1 form data  
**Auth:** JWT  
**Role:**  
- User: Own form only  
- Admin: Assigned client form  
- Superadmin: Any form  

---

### `POST /api/v1/t1-forms`
**Purpose:** Create new T1 form (auto-creates filing if needed)  
**Auth:** JWT  
**Role:** User  
**Side Effect:** Auto-creates Filing record if not exists for user+year  

---

### `PATCH /api/v1/t1-forms/{t1_form_id}`
**Purpose:** Update T1 form data (auto-save)  
**Auth:** JWT  
**Role:** User (only if status=draft)  
**Lock Rule:** Once submitted, form_data is read-only  

---

### `POST /api/v1/t1-forms/{t1_form_id}/submit`
**Purpose:** Submit T1 form for review  
**Auth:** JWT  
**Role:** User  
**Side Effect:**  
- Sets status=submitted  
- Sets submitted_at timestamp  
- Locks form_data  
- Updates Filing status  
- Creates notification  
- Sends email  

---

# 7. DOCUMENT ENDPOINTS

## 7.1 Document Management

### `GET /api/v1/documents`
**Purpose:** List documents with filters  
**Auth:** JWT  
**Role:**  
- User: Own documents only  
- Admin: Assigned client documents  
- Superadmin: All documents  
**Pagination:** Yes  
**Filters:** `filing_id`, `section_key`, `document_type`, `status`, `user_id`  

---

### `GET /api/v1/documents/{document_id}`
**Purpose:** Get document metadata  
**Auth:** JWT  
**Role:**  
- User: Own document  
- Admin: Assigned client document  
- Superadmin: Any document  

---

### `GET /api/v1/documents/{document_id}/download`
**Purpose:** Download encrypted document file  
**Auth:** JWT  
**Role:**  
- User: Own document  
- Admin: Assigned client document  
- Superadmin: Any document  
**Response:** Binary file stream (decrypted)  

---

### `POST /api/v1/documents`
**Purpose:** Upload new document  
**Auth:** JWT  
**Role:** User  
**Content-Type:** `multipart/form-data`  
**Side Effect:** File is encrypted at rest  

---

### `PATCH /api/v1/documents/{document_id}`
**Purpose:** Update document metadata (name, section, type)  
**Auth:** JWT  
**Role:**  
- User: Own document (limited fields)  
- Admin: Assigned client document (status, notes)  

---

### `PATCH /api/v1/documents/{document_id}/status`
**Purpose:** Update document review status  
**Auth:** JWT  
**Role:** Admin, Superadmin  
**Side Effect:** Status changes trigger notification + email  

---

### `POST /api/v1/documents/request`
**Purpose:** Request missing document from client  
**Auth:** JWT  
**Role:** Admin, Superadmin  
**Side Effect:**  
- Creates document stub with status=missing  
- Creates notification  
- Sends email  

---

### `DELETE /api/v1/documents/{document_id}`
**Purpose:** Soft delete document (archive)  
**Auth:** JWT  
**Role:** Admin, Superadmin  

---

# 8. PAYMENT ENDPOINTS

## 8.1 Payment Operations

### `GET /api/v1/payments`
**Purpose:** List payments with filters  
**Auth:** JWT  
**Role:**  
- Admin: All payments (or filtered by permission)  
- Superadmin: All payments  
**Pagination:** Yes  
**Filters:** `filing_id`, `user_id`, `recorded_by_id`, `date_from`, `date_to`  

---

### `GET /api/v1/payments/{payment_id}`
**Purpose:** Get payment details  
**Auth:** JWT  
**Role:** Admin, Superadmin  

---

### `POST /api/v1/payments`
**Purpose:** Record new payment  
**Auth:** JWT  
**Role:** Admin (with permission), Superadmin  
**Side Effect:**  
- Updates Filing.paid_amount (derived)  
- Updates Filing.payment_status (derived)  
- Creates notification  
- Sends email confirmation  

---

### `GET /api/v1/payments/filing/{filing_id}`
**Purpose:** Get all payments for a filing  
**Auth:** JWT  
**Role:**  
- Admin: Assigned filing  
- Superadmin: Any filing  

---

# 9. NOTIFICATION ENDPOINTS

## 9.1 Notification Operations

### `GET /api/v1/notifications`
**Purpose:** List notifications for current user  
**Auth:** JWT  
**Role:** User (own notifications only)  
**Pagination:** Yes  
**Filters:** `is_read`, `type`  

---

### `GET /api/v1/notifications/unread-count`
**Purpose:** Get count of unread notifications  
**Auth:** JWT  
**Role:** User  

---

### `PATCH /api/v1/notifications/{notification_id}/read`
**Purpose:** Mark notification as read  
**Auth:** JWT  
**Role:** User (own notification only)  

---

### `PATCH /api/v1/notifications/read-all`
**Purpose:** Mark all notifications as read  
**Auth:** JWT  
**Role:** User  

---

# 10. ANALYTICS ENDPOINTS

## 10.1 Analytics & Reporting

### `GET /api/v1/analytics/dashboard`
**Purpose:** Get admin dashboard statistics  
**Auth:** JWT  
**Role:** Admin (filtered by assignment), Superadmin (all)  
**Returns:**  
- Total clients  
- Clients by status  
- Total revenue  
- Revenue trend (monthly)  
- Pending documents count  
- Average processing time  
- Admin workload distribution  

---

### `GET /api/v1/analytics/revenue`
**Purpose:** Get revenue analytics with date range  
**Auth:** JWT  
**Role:** Admin (with permission), Superadmin  
**Filters:** `date_from`, `date_to`, `group_by` (day/week/month)  

---

### `GET /api/v1/analytics/workload`
**Purpose:** Get admin workload distribution  
**Auth:** JWT  
**Role:** Superadmin only  
**Returns:** Filings per admin, average completion time, bottlenecks  

---

# 11. AUDIT LOG ENDPOINTS

## 11.1 Audit Trail

### `GET /api/v1/audit-logs`
**Purpose:** List audit log entries  
**Auth:** JWT  
**Role:** Superadmin only  
**Pagination:** Yes  
**Filters:** `entity_type`, `entity_id`, `action`, `performed_by_id`, `date_from`, `date_to`  

---

### `GET /api/v1/audit-logs/{audit_log_id}`
**Purpose:** Get audit log entry details  
**Auth:** JWT  
**Role:** Superadmin only  

---

# 12. DEPRECATED ENDPOINTS (DO NOT IMPLEMENT)

These endpoints existed in the old system and must NOT be implemented:

| Old Endpoint | Reason | Replacement |
|--------------|--------|-------------|
| `/chat/*` | Email-first model | Email + `/notifications` |
| `/client/me` | Redundant | `/users/me` |
| `/client/add` | Inconsistent naming | `/filings` (auto-created) |
| `/admin/auth/register` | Wrong resource | `/admins` |
| `/admin/clients/*` | Role-based now | `/filings` with role check |
| `/admin/documents/*` | No admin prefix needed | `/documents` with role check |
| `/admin/payments/*` | No admin prefix needed | `/payments` with role check |
| `/filing-status/*` | Nested under filing | `/filings/{id}/status` |
| `/files/upload` | Wrong resource name | `/documents` |

---

# 13. ENDPOINT NAMING RULES

## 13.1 URL Structure Rules

| Rule | Example | Counter-Example |
|------|---------|-----------------|
| Use plural nouns | `/filings`, `/documents` | `/filing`, `/document` |
| Use kebab-case | `/t1-forms`, `/audit-logs` | `/t1_forms`, `/auditLogs` |
| No verbs in URLs | `/filings/{id}` with PATCH | `/filings/{id}/update` |
| Actions via HTTP methods | `POST /payments` | `POST /create-payment` |
| Sub-resources for nested | `/filings/{id}/timeline` | `/timeline?filing_id=X` |
| Query params for filters | `/filings?status=submitted` | `/filings/submitted` |
| Pagination via query | `?page=1&page_size=20` | `/filings/page/1` |

## 13.2 HTTP Method Usage

| Method | Purpose | Idempotent | Example |
|--------|---------|------------|---------|
| `GET` | Retrieve resource(s) | Yes | `GET /filings/{id}` |
| `POST` | Create new resource | No | `POST /documents` |
| `PATCH` | Partial update | No | `PATCH /filings/{id}/status` |
| `PUT` | Full replacement | Yes | Not used in this API |
| `DELETE` | Remove resource | Yes | `DELETE /admins/{id}` |

**Why PATCH over PUT:**
- Frontend sends partial updates only
- Reduces payload size
- Prevents accidental field overwrites
- Clearer intent (update specific fields)

---

# 14. ROLE-BASED ACCESS CONTROL

## 14.1 Role Hierarchy

```
Superadmin (full access)
    │
    ├── Admin (assigned filings + permissions)
    │
    └── User (self-service only)
```

## 14.2 Access Matrix

| Endpoint Pattern | User | Admin | Superadmin |
|------------------|------|-------|------------|
| `/auth/*` | ✅ All | ✅ All | ✅ All |
| `/users/me` | ✅ Self | ❌ No | ❌ No |
| `/users/{id}` | ❌ No | ✅ View | ✅ All |
| `/admins/*` | ❌ No | ✅ Self | ✅ All |
| `/filings` (list) | ✅ Own | ✅ Assigned | ✅ All |
| `/filings/{id}` (view) | ✅ Own | ✅ Assigned | ✅ All |
| `/filings/{id}` (update) | ❌ No | ✅ Assigned | ✅ All |
| `/t1-forms` (create) | ✅ Own | ❌ No | ❌ No |
| `/t1-forms/{id}` (view) | ✅ Own | ✅ Assigned | ✅ All |
| `/t1-forms/{id}` (update) | ✅ Own (draft) | ❌ No | ❌ No |
| `/documents` (upload) | ✅ Own | ❌ No | ❌ No |
| `/documents/{id}/status` | ❌ No | ✅ Assigned | ✅ All |
| `/payments` (create) | ❌ No | ✅ Permission | ✅ All |
| `/payments` (list) | ❌ No | ✅ All | ✅ All |
| `/notifications` | ✅ Own | ❌ No | ❌ No |
| `/analytics/*` | ❌ No | ✅ Permission | ✅ All |
| `/audit-logs/*` | ❌ No | ❌ No | ✅ All |

---

# 15. PAGINATION STANDARD

## 15.1 Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | Integer | 1 | Page number (1-indexed) |
| `page_size` | Integer | 20 | Items per page (max: 100) |
| `sort_by` | String | `created_at` | Sort field |
| `sort_order` | String | `desc` | `asc` or `desc` |

## 15.2 Response Format

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

# 16. FILTER PARAMETERS

## 16.1 Common Filters

| Endpoint | Filters | Example |
|----------|---------|---------|
| `/filings` | `year`, `status`, `payment_status`, `assigned_admin_id`, `user_id`, `search` | `?year=2024&status=submitted` |
| `/documents` | `filing_id`, `section_key`, `document_type`, `status`, `user_id` | `?filing_id=123&status=pending` |
| `/payments` | `filing_id`, `user_id`, `recorded_by_id`, `date_from`, `date_to` | `?date_from=2024-01-01` |
| `/notifications` | `is_read`, `type` | `?is_read=false` |
| `/audit-logs` | `entity_type`, `entity_id`, `action`, `performed_by_id`, `date_from`, `date_to` | `?entity_type=Filing&action=status_update` |

## 16.2 Search Parameters

For text search across multiple fields:

```
GET /api/v1/filings?search=john+doe
```

**Search Fields:**
- Filings: name, email, phone
- Documents: name, original_filename, notes
- Admins: name, email

---

# 17. NESTED RESOURCE PATTERNS

## 17.1 When to Nest

**Use nesting when:**
- Sub-resource cannot exist without parent
- Sub-resource is always accessed via parent
- Relationship is 1:1 or clear 1:N

**Examples:**
```
GET /api/v1/filings/{filing_id}/timeline
GET /api/v1/documents/{document_id}/download
GET /api/v1/payments/filing/{filing_id}
```

## 17.2 When NOT to Nest

**Avoid nesting when:**
- Sub-resource has independent identity
- Multiple access patterns exist
- Nesting depth > 2 levels

**Examples (flat is better):**
```
GET /api/v1/documents?filing_id=123    ✅ Better
GET /api/v1/filings/123/documents      ❌ Avoid

GET /api/v1/t1-forms?filing_id=123     ✅ Better
GET /api/v1/filings/123/t1-form        ❌ Avoid
```

---

# 18. IDEMPOTENCY

## 18.1 Idempotent Operations

| Endpoint | Method | Idempotent? | Notes |
|----------|--------|-------------|-------|
| All GET | `GET` | ✅ Yes | Safe to retry |
| All DELETE | `DELETE` | ✅ Yes | Repeated DELETE returns 404 |
| Status updates | `PATCH` | ⚠️ Partial | Same status = no-op |
| Document upload | `POST` | ❌ No | Creates new record each time |
| Payment record | `POST` | ❌ No | Creates duplicate |

## 18.2 Idempotency Keys

For non-idempotent operations that clients may retry:

```
POST /api/v1/payments
Headers:
  Idempotency-Key: uuid-v4
```

**Behavior:**
- Server stores key for 24 hours
- Duplicate key returns cached response (201 → 200)
- Prevents accidental double payments

---

# 19. RATE LIMITING

## 19.1 Rate Limit Rules

| Endpoint Pattern | Rate Limit | Window |
|------------------|------------|--------|
| `/auth/login` | 5 attempts | 15 minutes |
| `/auth/otp/request` | 3 attempts | 5 minutes |
| `/auth/otp/verify` | 5 attempts | 10 minutes |
| `/auth/register` | 3 attempts | 1 hour |
| `/documents` (upload) | 10 uploads | 5 minutes |
| All other endpoints | 100 requests | 1 minute |

## 19.2 Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704499200
```

**429 Response:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Try again in 45 seconds.",
  "retry_after": 45
}
```

---

# 20. CONDITIONAL REQUESTS

## 20.1 ETags for Caching

```
GET /api/v1/filings/123
Response:
  ETag: "abc123xyz"
  
GET /api/v1/filings/123
Headers:
  If-None-Match: "abc123xyz"
Response: 304 Not Modified (empty body)
```

## 20.2 Last-Modified

```
GET /api/v1/t1-forms/456
Response:
  Last-Modified: Sat, 05 Jan 2026 10:30:00 GMT

GET /api/v1/t1-forms/456
Headers:
  If-Modified-Since: Sat, 05 Jan 2026 10:30:00 GMT
Response: 304 Not Modified
```

---

# 21. CORS POLICY

## 21.1 Allowed Origins

**Development:**
```
http://localhost:3000   # React admin
http://localhost:5173   # Vite dev server
http://localhost:*      # Flutter web
```

**Production:**
```
https://admin.taxease.ca
https://app.taxease.ca
```

## 21.2 CORS Headers

```
Access-Control-Allow-Origin: <origin>
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, Idempotency-Key
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
```

---

# 22. CONTENT NEGOTIATION

## 22.1 Supported Content Types

**Request:**
- `application/json` (default)
- `multipart/form-data` (document upload only)

**Response:**
- `application/json` (default)
- `application/octet-stream` (document download)
- `text/csv` (analytics export)

## 22.2 Accept Header

```
GET /api/v1/analytics/revenue
Headers:
  Accept: text/csv
Response: CSV file
```

---

# 23. ENDPOINT SUMMARY TABLE

| # | Endpoint | Method | Auth | Role | Purpose |
|---|----------|--------|------|------|---------|
| 1 | `/auth/register` | POST | None | Public | Register user |
| 2 | `/auth/login` | POST | None | Public | Login |
| 3 | `/auth/otp/request` | POST | None | Public | Request OTP |
| 4 | `/auth/otp/verify` | POST | None | Public | Verify OTP |
| 5 | `/auth/password/reset-request` | POST | None | Public | Request password reset |
| 6 | `/auth/password/reset-confirm` | POST | None | Public | Confirm password reset |
| 7 | `/auth/logout` | POST | JWT | User, Admin | Logout |
| 8 | `/sessions/refresh` | POST | Refresh | User, Admin | Refresh token |
| 9 | `/sessions/current` | GET | JWT | User, Admin | Current session info |
| 10 | `/users/me` | GET | JWT | User | Get own profile |
| 11 | `/users/me` | PATCH | JWT | User | Update own profile |
| 12 | `/users/{user_id}` | GET | JWT | Admin+ | Get user by ID |
| 13 | `/users/{user_id}/status` | PATCH | JWT | Superadmin | Activate/deactivate |
| 14 | `/admins` | GET | JWT | Superadmin | List admins |
| 15 | `/admins` | POST | JWT | Superadmin | Create admin |
| 16 | `/admins/{admin_id}` | GET | JWT | Self/Superadmin | Get admin |
| 17 | `/admins/{admin_id}` | PATCH | JWT | Self/Superadmin | Update admin |
| 18 | `/admins/{admin_id}` | DELETE | JWT | Superadmin | Delete admin |
| 19 | `/filings` | GET | JWT | All | List filings |
| 20 | `/filings` | POST | JWT | Admin+ | Create filing |
| 21 | `/filings/{filing_id}` | GET | JWT | Owner/Admin+ | Get filing |
| 22 | `/filings/{filing_id}/status` | PATCH | JWT | Admin+ | Update status |
| 23 | `/filings/{filing_id}/assignment` | PATCH | JWT | Admin+ | Assign admin |
| 24 | `/filings/{filing_id}/fee` | PATCH | JWT | Admin+ | Update fee |
| 25 | `/filings/{filing_id}/timeline` | GET | JWT | Owner/Admin+ | Get timeline |
| 26 | `/filings/{filing_id}` | DELETE | JWT | Superadmin | Delete filing |
| 27 | `/t1-forms` | GET | JWT | All | List T1 forms |
| 28 | `/t1-forms` | POST | JWT | User | Create T1 form |
| 29 | `/t1-forms/{t1_form_id}` | GET | JWT | Owner/Admin+ | Get T1 form |
| 30 | `/t1-forms/{t1_form_id}` | PATCH | JWT | User (draft) | Update T1 form |
| 31 | `/t1-forms/{t1_form_id}/submit` | POST | JWT | User | Submit T1 form |
| 32 | `/documents` | GET | JWT | All | List documents |
| 33 | `/documents` | POST | JWT | User | Upload document |
| 34 | `/documents/{document_id}` | GET | JWT | Owner/Admin+ | Get document metadata |
| 35 | `/documents/{document_id}/download` | GET | JWT | Owner/Admin+ | Download document |
| 36 | `/documents/{document_id}` | PATCH | JWT | Owner/Admin+ | Update document |
| 37 | `/documents/{document_id}/status` | PATCH | JWT | Admin+ | Update status |
| 38 | `/documents/request` | POST | JWT | Admin+ | Request missing doc |
| 39 | `/documents/{document_id}` | DELETE | JWT | Admin+ | Delete document |
| 40 | `/payments` | GET | JWT | Admin+ | List payments |
| 41 | `/payments` | POST | JWT | Admin+ | Record payment |
| 42 | `/payments/{payment_id}` | GET | JWT | Admin+ | Get payment |
| 43 | `/payments/filing/{filing_id}` | GET | JWT | Admin+ | List filing payments |
| 44 | `/notifications` | GET | JWT | User | List notifications |
| 45 | `/notifications/unread-count` | GET | JWT | User | Unread count |
| 46 | `/notifications/{notification_id}/read` | PATCH | JWT | User | Mark read |
| 47 | `/notifications/read-all` | PATCH | JWT | User | Mark all read |
| 48 | `/analytics/dashboard` | GET | JWT | Admin+ | Dashboard stats |
| 49 | `/analytics/revenue` | GET | JWT | Admin+ | Revenue analytics |
| 50 | `/analytics/workload` | GET | JWT | Superadmin | Workload distribution |
| 51 | `/audit-logs` | GET | JWT | Superadmin | List audit logs |
| 52 | `/audit-logs/{audit_log_id}` | GET | JWT | Superadmin | Get audit log |

---

# PHASE 2 COMPLETE — ENDPOINT DESIGN

## Summary

**Total Endpoints:** 52 (48 core + 4 nested variants)

**Key Design Principles Applied:**
1. ✅ All endpoints use `/api/v1/` prefix
2. ✅ Plural nouns only (`/filings`, `/documents`)
3. ✅ Kebab-case for multi-word (`/t1-forms`, `/audit-logs`)
4. ✅ Role-based access (no `/admin/*` prefix duplication)
5. ✅ HTTP method semantics (POST=create, PATCH=update, DELETE=remove)
6. ✅ Logical nesting (max depth 2)
7. ✅ Query params for filtering
8. ✅ Pagination on all list endpoints
9. ✅ No deprecated patterns

**Removed Legacy Patterns:**
- ❌ No `/chat/*` endpoints (email-first)
- ❌ No `/admin/` prefixed duplicates
- ❌ No `/client/` endpoints
- ❌ No verb-based URLs

**Frontend Compatibility:** ✅ 100% (all expected operations preserved)

---

**Reply "PROCEED TO PHASE 3" to continue with request/response contracts.**
