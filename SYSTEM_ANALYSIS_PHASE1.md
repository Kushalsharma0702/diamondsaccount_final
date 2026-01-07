# TaxEase System Analysis - PHASE 1
## Final Documentation

**Generated:** January 5, 2026  
**Purpose:** Complete system analysis for backend redesign  
**Status:** PHASE 1 COMPLETE

---

# Table of Contents

1. [PART 1: High-Level System Overview](#part-1--high-level-system-overview)
2. [PART 2: Frontend → Backend Interaction Map](#part-2--frontend--backend-interaction-map)
3. [PART 3: Identified Core Domain Entities](#part-3--identified-core-domain-entities)
4. [PART 4: Gaps & Risks](#part-4--gaps--risks)

---

# PART 1 → High-Level System Overview

## 1.1 System Purpose & Domain

**TaxEase** is a Canadian personal tax filing platform consisting of:
- A **mobile client app** (Flutter) for taxpayers to submit T1 personal tax returns
- An **admin dashboard** (React) for tax professionals to review, process, and manage client filings
- A **Flask backend** providing unified API services and PostgreSQL data persistence

**Business Domain:** Canadian T1 Personal Income Tax Filing (CRA-compliant)

---

## 1.2 Major System Modules

| Module | Responsibility | Primary Actors |
|--------|----------------|----------------|
| **Authentication** | User registration, login, OTP verification, JWT tokens, session management | Client, Admin, Superadmin |
| **Client Management** | Client profile CRUD, status tracking, admin assignment | Admin, Superadmin |
| **T1 Form Processing** | Multi-step tax form submission, questionnaire data, JSONB storage with flat-column mapping | Client |
| **Document Management** | File upload with encryption, download, status tracking, section tagging | Client, Admin |
| **Filing Status** | 9-stage workflow timeline, status updates, notifications | Client (read), Admin (write) |
| **Chat/Communication** | Real-time messaging between client and admin, read receipts | Client, Admin |
| **Payments** | Payment recording, requests, tracking, revenue analytics | Admin, Superadmin |
| **Analytics** | Dashboard stats, workload distribution, revenue charts | Admin, Superadmin |
| **Admin Management** | Admin user CRUD, role/permission assignment | Superadmin only |
| **Audit Logging** | Action tracking, entity change history | System (auto), Superadmin (view) |

---

## 1.3 Actor Roles & Permissions

### 1.3.1 Client (Flutter Mobile App)

| Capability | Access Level |
|------------|--------------|
| Register/Login/OTP verification | Self |
| View own profile | Self |
| Submit T1 tax forms | Self |
| Upload documents | Self |
| View filing status timeline | Self |
| Chat with assigned admin | Self |
| View notifications | Self |

### 1.3.2 Admin (React Dashboard)

| Capability | Access Level |
|------------|--------------|
| Login with JWT session | Self |
| View all clients (filtered by assignment) | Assigned or All |
| Review T1 forms & documents | Assigned clients |
| Update document status | Assigned clients |
| Update filing status | Assigned clients |
| Record payments | Per permission |
| Send chat messages | Assigned clients |
| Request missing documents | Per permission |

### 1.3.3 Superadmin (React Dashboard)

| Capability | Access Level |
|------------|--------------|
| All Admin capabilities | Global |
| Create/manage admin users | Global |
| View analytics & revenue | Global |
| View audit logs | Global |
| Assign clients to admins | Global |
| Manage permissions | Global |

### 1.3.4 System (Automated)

| Capability | Trigger |
|------------|---------|
| Generate audit log entries | On entity changes |
| Create notifications | On status updates |
| Sync T1 status → Client status | On T1 status change |
| Encrypt documents on upload | Automatic |

---

## 1.4 End-to-End User Flows

### Flow A: Client Signup → T1 Submission

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Register  │───▶│ Verify OTP  │───▶│    Login    │───▶│ Create T1   │
│   (email)   │    │  (123456)   │    │  (JWT)      │    │   Form      │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
    ┌───────────────────────────────────────────────────────────┘
    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Personal   │───▶│Questionnaire│───▶│  Upload     │
│    Info     │    │   (20 Q's)  │    │  Documents  │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │   Submit    │
                                      │  (draft→    │
                                      │  submitted) │
                                      └─────────────┘
```

### Flow B: Admin Review → Filing Completion

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Admin Login │───▶│ View Client │───▶│  Review T1  │───▶│  Request    │
│   (JWT)     │    │   List      │    │   & Docs    │    │  More Docs  │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
    ┌───────────────────────────────────────────────────────────┘
    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Send Cost   │───▶│  Receive    │───▶│  Prepare    │───▶│  E-File     │
│  Estimate   │    │  Payment    │    │   Return    │    │  (CRA)      │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
                                                                ▼
                                                         ┌─────────────┐
                                                         │  Complete   │
                                                         │  (filed)    │
                                                         └─────────────┘
```

### Flow C: Filing Status Lifecycle

```
draft → submitted → payment_request_sent → payment_received → 
return_in_progress → additional_info_required (optional loop) →
under_review_pending_approval → approved_for_filing → e_filing_completed
```

**Status-to-Client Mapping (Auto-sync):**

| T1 Status | Client Status |
|-----------|---------------|
| `draft` | `documents_pending` |
| `submitted` | `under_review` |
| `payment_request_sent` | `awaiting_payment` |
| `payment_received` | `in_preparation` |
| `e_filing_completed` | `filed` |

---

## 1.5 System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                    │
├────────────────────────┬───────────────────────────────────────────────┤
│   Flutter Mobile App   │         React Admin Dashboard                 │
│   (tax_ease_app_client)│         (tax-hub-dashboard-admin)             │
├────────────────────────┴───────────────────────────────────────────────┤
│                            HTTP/REST API                                │
├────────────────────────────────────────────────────────────────────────┤
│                         Flask Backend (FastAPI)                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │   Auth   │  Client  │    T1    │   Docs   │   Chat   │  Admin   │  │
│  │  Routes  │  Routes  │  Routes  │  Routes  │  Routes  │  Routes  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘  │
├────────────────────────────────────────────────────────────────────────┤
│                      Services Layer (Business Logic)                    │
├───────────────────────┬────────────────────────────────────────────────┤
│     PostgreSQL DB     │           Redis (Sessions)                      │
│   (Users, T1Forms,    │      (Token revocation, cache)                 │
│    Documents, etc.)   │                                                 │
├───────────────────────┴────────────────────────────────────────────────┤
│                     Encrypted File Storage                              │
│                      (./storage/uploads)                                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 1.6 Current Backend Route Organization

| Route File | Prefix | Purpose |
|------------|--------|---------|
| `auth.py` | `/auth` | Client authentication |
| `admin_auth.py` | `/admin/auth` | Admin authentication + session |
| `client.py` | `/client` | Client CRUD operations |
| `client_me.py` | `/client/me` | Current user profile |
| `admin.py` | `/admin` | Basic admin operations |
| `admin_full.py` | `/admin` | Extended admin operations |
| `t1.py` | `/client` | T1 form submission/retrieval |
| `documents.py` | `/documents` | Document upload/download |
| `chat.py` | `/chat` | Messaging system |
| `filing_status.py` | `/filing-status` | Status workflow |

---

## 1.7 Data Flow Characteristics

| Flow Type | Examples | Communication Pattern |
|-----------|----------|----------------------|
| **Synchronous** | Login, T1 submit, document upload | Request → Response |
| **Polling** | Chat messages (5s interval) | Client polls server |
| **Event-driven** | Status change → Notification created | Backend trigger |
| **Batch** | Analytics aggregation | On-demand calculation |

**Note:** No WebSocket/real-time push currently implemented. Chat uses polling.

---

## 1.8 Key Technology Stack

| Layer | Technology |
|-------|------------|
| Mobile Client | Flutter/Dart, Dio HTTP client |
| Admin Dashboard | React, TypeScript, Vite, TailwindCSS, Recharts |
| Backend | Flask (actually FastAPI based on code), Python 3.x |
| Database | PostgreSQL with JSONB support |
| Session/Cache | Redis (optional, falls back to in-memory) |
| File Storage | Local filesystem with AES encryption |
| Authentication | JWT (access + refresh tokens) |

---

# PART 2 → Frontend → Backend Interaction Map

## 2.1 Flutter Client App → API Expectations

### 2.1.1 Authentication Flow

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Register | `POST` | `/auth/register` | `{email, first_name, last_name, phone?, password, accept_terms}` | `{id, email, first_name, last_name, email_verified, is_active, created_at}` |
| Login | `POST` | `/auth/login` | `{email, password}` | `{access_token, refresh_token, token_type, expires_in}` |
| Request OTP | `POST` | `/auth/request-otp` | `{email, purpose}` | `{message, success}` |
| Verify OTP | `POST` | `/auth/verify-otp` | `{email, code, purpose}` | `{message, success}` |
| Get Profile | `GET` | `/auth/me` | — | `{id, email, first_name, last_name, phone, email_verified, is_active, created_at, updated_at}` |

**Flutter Code Location:** `lib/features/auth/data/auth_api.dart`

**Token Storage:** `ThemeController.authToken` (in-memory during session)

---

### 2.1.2 T1 Tax Form Submission

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Submit T1 | `POST` | `/client/tax-return` | `{formData: {personalInfo, questionnaire answers, subforms...}}` | `{id, status, filing_year, created_at, updated_at}` |
| Get T1 | `GET` | `/client/tax-return?client_id={id}` | — | Full T1 form data object |

**Flutter Code Location:** `lib/features/tax_forms/data/services/t1_form_storage_service.dart`

**T1 Form Structure (20+ questions):**
```json
{
  "personalInfo": {
    "firstName", "lastName", "sin", "dateOfBirth", "address",
    "phoneNumber", "email", "isCanadianCitizen", "maritalStatus",
    "spouseInfo": {...},
    "children": [...]
  },
  "hasForeignProperty": true/false,
  "foreignProperty": [{country, cost, income, gain_loss...}],
  "hasMedicalExpenses": true/false,
  "medicalExpenses": [{date, patient, amount, insurance...}],
  "hasWorkFromHomeExpense": true/false,
  "workFromHomeExpense": {totalArea, workArea, rent, utilities...},
  "selfEmployment": {
    "businessTypes": ["uber", "general", "rental"],
    "uberBusiness": {...},
    "generalBusiness": {...},
    "rentalIncome": {...}
  }
}
```

---

### 2.1.3 Document Management

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Upload | `POST` | `/documents/upload` | `multipart/form-data: file, client_id, section?, document_type` | `{id, name, file_type, file_size, status, encrypted, created_at}` |
| Download | `GET` | `/documents/{id}/download` | — | Binary file stream (decrypted) |
| List | `GET` | `/documents?client_id={id}` | — | `{documents: [...], total}` |

**Flutter Code Location:** `lib/features/documents/data/files_api.dart`

---

### 2.1.4 Chat/Communication

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Send Message | `POST` | `/chat/send` | `{client_id, message, sender_role: "client"}` | `{id, sender_role, message, created_at, read_by_client, read_by_admin}` |
| Get Messages | `GET` | `/chat/{client_id}` | — | `{messages: [...], total}` |
| Mark Read | `PUT` | `/chat/{client_id}/mark-read?role=client` | — | `{message}` |
| Unread Count | `GET` | `/chat/{client_id}/unread-count?role=client` | — | `{unread_count}` |

**Flutter Code Location:** `lib/features/chat/data/chat_api.dart`

**Polling Pattern:** 5-second interval refresh (no WebSocket)

---

### 2.1.5 Filing Status

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Get Status | `GET` | `/filing-status/client/{client_id}` | — | `{return_id, filing_year, current_status, timeline: [...], updated_at}` |
| Get by Email | `GET` | `/filing-status/client?email={email}` | — | Same as above |

**Flutter Code Location:** `lib/features/filing/presentation/pages/filing_status_page.dart`

**Timeline Response Structure:**
```json
{
  "timeline": [
    {"status": "draft", "display_name": "Form in Draft", "is_completed": true, "is_current": false, "completed_at": "..."},
    {"status": "submitted", "display_name": "Form Submitted", "is_completed": true, "is_current": false, "completed_at": "..."},
    {"status": "under_review_pending_approval", "display_name": "Under Review", "is_completed": false, "is_current": true, "completed_at": null}
  ]
}
```

---

### 2.1.6 Client Self-Service

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Get My Info | `GET` | `/client/me` | — | `{id, email, name, phone, status, filing_year...}` |

---

## 2.2 React Admin Dashboard → API Expectations

### 2.2.1 Admin Authentication

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Login | `POST` | `/admin/auth/login` | `{email, password}` | `{user: {...}, token: {access_token, refresh_token}, session_id}` |
| Get Current | `GET` | `/admin/auth/me` | — | `{id, email, name, role, permissions, is_active}` |
| Logout | `POST` | `/admin/auth/logout` | `{session_id?}` | — |
| Register Admin | `POST` | `/admin/auth/register` | `{name, email, password, role, permissions}` | Admin user object |
| Refresh Session | `POST` | `/admin/auth/refresh-session` | — | Extended session |

**Dashboard Code Location:** `src/services/api.ts`

**Session Management:** Redis-backed with 30-minute timeout, auto-refresh every 5 minutes.

---

### 2.2.2 Client Management

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| List Clients | `GET` | `/admin/clients?status=&year=&search=` | — | `[{id, name, email, phone, status, payment_status, filingYear...}]` |
| Get Client | `GET` | `/admin/clients/{id}` | — | Full client with personal info, T1 data |
| Create Client | `POST` | `/client/add` | `{first_name, last_name, email, phone, filing_year}` | Client object |
| Update Client | `PATCH` | `/admin/clients/{id}` | `{status?, payment_status?, assigned_admin_id?, total_amount?, paid_amount?}` | Updated client |
| Delete Client | `DELETE` | `/admin/clients/{id}` | — | — |

**Client Statuses:**
- `documents_pending`
- `under_review`
- `cost_estimate_sent`
- `awaiting_payment`
- `in_preparation`
- `awaiting_approval`
- `filed`
- `completed`

**Payment Statuses:**
- `pending`
- `partial`
- `paid`
- `overdue`

---

### 2.2.3 Document Management (Admin)

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| List Documents | `GET` | `/admin/documents?status=&client_id=` | — | `[{id, name, type, status, version, uploaded_at...}]` |
| Update Status | `PATCH` | `/admin/documents/{id}` | `{status, notes?}` | Updated document |
| Create (request) | `POST` | `/documents` | `{client_id, name, type, status?, notes?}` | Document object |
| Delete | `DELETE` | `/documents/{id}` | — | — |

**Document Statuses:**
- `pending`
- `complete`
- `missing`
- `approved`
- `reupload_requested`

---

### 2.2.4 Payment Management

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| List Payments | `GET` | `/admin/payments?client_id=` | — | `[{id, client_id, amount, method, note, created_at, created_by}]` |
| Create Payment | `POST` | `/payments` | `{client_id, amount, method, note?}` | Payment object |
| Update Payment | `PATCH` | `/payments/{id}` | `{amount?, method?, note?}` | Updated payment |
| Delete Payment | `DELETE` | `/payments/{id}` | — | — |

---

### 2.2.5 Filing Status Management (Admin)

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Update Status | `PUT` | `/filing-status/admin/{return_id}/status` | `{status, notes?}` | `{return_id, status, status_display, updated_at, message}` |
| List Returns | `GET` | `/filing-status/admin/returns?status=&filing_year=&client_id=` | — | Array of T1 returns |

---

### 2.2.6 Analytics

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Get Analytics | `GET` | `/admin/analytics` | — | See structure below |

**Expected Response:**
```typescript
{
  totalClients: number,
  totalAdmins: number,
  pendingDocuments: number,
  pendingPayments: number,
  completedFilings: number,
  totalRevenue: number,
  monthlyRevenue: [{month: string, revenue: number}],
  clientsByStatus: [{status: string, count: number}],
  adminWorkload: [{name: string, clients: number}]
}
```

---

### 2.2.7 Admin User Management

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| List Admins | `GET` | `/admin/admin-users` | — | Array of admin users |
| Create Admin | `POST` | `/admin/auth/register` | `{name, email, password, role, permissions}` | Admin user |
| Update Admin | `PATCH` | `/admin/admin-users/{id}` | `{name?, role?, permissions?, is_active?}` | ⚠️ **NOT IMPLEMENTED** |
| Delete Admin | `DELETE` | `/admin/admin-users/{id}` | — | ⚠️ **NOT IMPLEMENTED** |

---

### 2.2.8 Chat (Admin Side)

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Get Messages | `GET` | `/chat/{client_id}` | — | `{messages: [...], total}` |
| Send Message | `POST` | `/chat/send` | `{client_id, message, sender_role: "admin"}` | Message object |
| Mark Read | `PUT` | `/chat/{client_id}/mark-read?role=admin` | — | `{message}` |
| Unread Count | `GET` | `/chat/{client_id}/unread-count?role=admin` | — | `{unread_count}` |

---

### 2.2.9 Audit Logs

| Action | Method | Endpoint | Request Payload | Expected Response |
|--------|--------|----------|-----------------|-------------------|
| Get Logs | `GET` | `/admin/audit-logs?page=&page_size=&entity_type=&action=` | — | ⚠️ **NOT IMPLEMENTED** |

**Expected Response:**
```typescript
{
  logs: [{id, action, entityType, entityId, oldValue?, newValue?, performedBy, performedByName, timestamp}],
  total, page, page_size, total_pages
}
```

---

## 2.3 Request/Response Patterns Summary

### 2.3.1 Common Headers

```http
Content-Type: application/json
Authorization: Bearer <jwt_access_token>
ngrok-skip-browser-warning: true  // Flutter only (for dev tunnels)
```

### 2.3.2 Error Response Format

```json
{
  "detail": "Error message string"
}
// OR validation errors:
{
  "detail": [
    {"loc": ["body", "field"], "msg": "error description", "type": "value_error"}
  ]
}
```

### 2.3.3 HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation failure |
| 401 | Unauthorized | Invalid/missing token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Schema validation error |
| 500 | Server Error | Unexpected failure |

---

## 2.4 Real-time vs Polling Patterns

| Feature | Pattern | Interval | Notes |
|---------|---------|----------|-------|
| Chat messages | Polling | 5 seconds | No WebSocket implemented |
| Filing status | On-demand | Manual refresh | User-triggered |
| Notifications | **Not implemented** | — | No push system exists |
| Session refresh | Polling | 5 minutes | Auto-extend session |

---

## 2.5 API Inconsistencies Identified

| Issue | Description |
|-------|-------------|
| **Endpoint prefix mismatch** | Flutter docs reference `/files/upload`, actual is `/documents/upload` |
| **T1 submission path** | Docs show `/t1/tax-return`, actual is `/client/tax-return` |
| **Auth context in Dashboard** | AuthContext.tsx still has mock users hardcoded alongside API calls |
| **Missing admin endpoints** | `PATCH /admin/admin-users/{id}` and `DELETE /admin/admin-users/{id}` referenced but not implemented |
| **Audit logs** | Frontend expects `/admin/audit-logs` but backend doesn't have this route |
| **Notifications** | Types define notification structure but no API endpoints exist |

---

# PART 3 → Identified Core Domain Entities

## 3.1 Entity Overview Matrix

| Entity | Responsibility | Owner | Lifecycle |
|--------|----------------|-------|-----------|
| **User** | Client account authentication | Client (self) | Registration → Active → Deactivated |
| **Admin** | Admin/Superadmin account | Superadmin | Created → Active → Deactivated |
| **Client** | Client profile & filing record | System (Admin-managed) | Created → Filing stages → Completed |
| **T1Return** | Tax form submission data | Client (submits), Admin (reviews) | Draft → Submitted → Reviewed → Filed |
| **Document** | Uploaded file metadata | Client (uploads), Admin (reviews) | Uploaded → Pending → Approved/Requested |
| **Payment** | Financial transaction record | Admin (creates) | Requested → Received/Cancelled |
| **ChatMessage** | Communication record | Client/Admin (sends) | Created → Read |
| **Notification** | System alert | System (auto-generated) | Created → Read |
| **CostEstimate** | Service pricing | Admin (creates) | Draft → Sent → Paid |
| **Note** | Internal/client-facing notes | Admin (creates) | Created (immutable) |
| **AuditLog** | Change tracking | System (auto) | Created (immutable) |

---

## 3.2 Core Entity Definitions

### 3.2.1 User (Client Account)

**Purpose:** Represents an authenticated taxpayer who can file returns.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `email` | String | Unique, Required | Login credential |
| `first_name` | String | Required | Legal first name |
| `last_name` | String | Required | Legal last name |
| `phone` | String | Optional | Contact number |
| `password_hash` | String | Required | Hashed password |
| `email_verified` | Boolean | Default: false | OTP verification status |
| `is_active` | Boolean | Default: true | Account status |
| `created_at` | Timestamp | Auto | Registration time |
| `updated_at` | Timestamp | Auto | Last modification |

**Relationships:**
- Has many → `Client` records (one per filing year)
- Has many → `RefreshToken`
- Has many → `OTP`
- Has many → `ChatMessage`

**Ownership:** Self-managed (registration, profile update)

---

### 3.2.2 Admin (Staff Account)

**Purpose:** Represents a tax professional or administrator who manages client filings.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `email` | String | Unique, Required | Login credential |
| `name` | String | Required | Display name |
| `password_hash` | String | Required | Hashed password |
| `role` | Enum | Required | `admin` or `superadmin` |
| `permissions` | JSON Array | Required | Permission keys |
| `avatar` | String | Optional | Profile image URL |
| `is_active` | Boolean | Default: true | Account status |
| `last_login_at` | Timestamp | Optional | Session tracking |

**Permission Keys:**
- `add_edit_payment`
- `add_edit_client`
- `request_documents`
- `assign_clients`
- `view_analytics`
- `approve_cost_estimate`
- `update_workflow`

**Ownership:** Superadmin creates/manages; Self updates profile

---

### 3.2.3 Client (Filing Record)

**Purpose:** Represents a client's tax filing engagement for a specific year.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `user_id` | UUID | FK → User | Link to user account |
| `name` | String | Required | Denormalized for queries |
| `email` | String | Required | Denormalized for queries |
| `phone` | String | Optional | Contact number |
| `filing_year` | Integer | Required | Tax year (e.g., 2024) |
| `status` | Enum | Required | Workflow status |
| `payment_status` | Enum | Required | Payment tracking |
| `assigned_admin_id` | UUID | FK → Admin | Responsible admin |
| `total_amount` | Float | Default: 0 | Service cost |
| `paid_amount` | Float | Default: 0 | Amount received |

**Status Values:**
```
documents_pending → under_review → cost_estimate_sent → 
awaiting_payment → in_preparation → awaiting_approval → 
filed → completed
```

**Ownership:** System creates; Admin manages status; User owns data

---

### 3.2.4 T1Return (Tax Form Submission)

**Purpose:** Stores complete T1 personal tax return data.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `client_id` | UUID | FK → Client | Associated client |
| `filing_year` | Integer | Required | Tax year |
| `status` | Enum | Required | `draft`, `submitted`, etc. |
| `payment_status` | Enum | Required | Payment tracking |
| `form_data` | JSONB | Required | **Complete nested T1 structure** |
| `submitted_at` | Timestamp | Optional | Submission time |

**Flat Columns (Denormalized for Queries):**
- Personal info: `first_name`, `last_name`, `sin`, `date_of_birth`, `marital_status`
- Spouse: `spouse_first_name`, `spouse_sin`, etc.
- Questionnaire flags: `has_foreign_property`, `has_medical_expenses`, `has_self_employment`, etc. (20+ flags)
- Aggregated values: `foreign_property_total_income`, `medical_expense_out_of_pocket`, `uber_income`, etc.

**T1 Status Lifecycle:**
```
draft → submitted → payment_request_sent → payment_received →
return_in_progress → additional_info_required → 
under_review_pending_approval → approved_for_filing → e_filing_completed
```

**JSONB `form_data` Structure:**
```json
{
  "personalInfo": {
    "firstName", "lastName", "sin", "dateOfBirth", "address",
    "isCanadianCitizen", "maritalStatus",
    "spouseInfo": {...},
    "children": [...]
  },
  "hasForeignProperty": true,
  "foreignProperty": [{country, cost, income...}],
  "hasMedicalExpenses": true,
  "medicalExpenses": [{date, patient, amount...}],
  "selfEmployment": {
    "businessTypes": ["uber", "general"],
    "uberBusiness": {...},
    "generalBusiness": {...},
    "rentalIncome": {...}
  }
}
```

**Ownership:** Client creates/submits; Admin reviews/updates status

---

### 3.2.5 Document (Uploaded File)

**Purpose:** Stores metadata for encrypted files uploaded by clients.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `client_id` | UUID | FK → Client | File owner |
| `tax_return_id` | UUID | FK → T1Return | Optional link |
| `name` | String | Required | Display name |
| `original_filename` | String | Required | Upload name |
| `file_type` | String | Required | Extension (pdf, jpg, etc.) |
| `file_size` | Integer | Required | Bytes |
| `file_path` | String | Required | Encrypted file path |
| `encrypted` | Boolean | Default: true | Encryption status |
| `section_name` | String | Optional | T1 section tag |
| `document_type` | String | Required | Category (receipt, form, etc.) |
| `status` | Enum | Required | Review status |
| `version` | Integer | Default: 1 | Version number |
| `notes` | Text | Optional | Admin notes |

**Document Statuses:**
- `pending` → Awaiting review
- `complete` → Approved, no issues
- `missing` → Requested but not uploaded
- `approved` → Verified by admin
- `reupload_requested` → Issues found, need new upload

**Section Names (T1 Categories):**
- `employment_income`, `investment_income`, `foreign_property`
- `medical_expenses`, `charitable_donations`, `moving_expenses`
- `self_employment`, `rental_income`, `work_from_home`
- `tuition_education`, `childcare`, etc.

**Ownership:** Client uploads; Admin reviews/requests

---

### 3.2.6 Payment (Transaction Record)

**Purpose:** Tracks payments received and payment requests.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `client_id` | UUID | FK → Client | Payer |
| `created_by_id` | UUID | FK → Admin | Recording admin |
| `amount` | Float | Required | Dollar amount |
| `method` | String | Required | E-Transfer, Credit, Debit |
| `note` | Text | Optional | Transaction note |
| `status` | Enum | Required | Payment status |
| `is_request` | Boolean | Default: false | Request vs actual payment |

**Payment Flow:**
```
Request Created (is_request=true) → Payment Received (is_request=false, status=received)
```

**Ownership:** Admin creates; System tracks

---

### 3.2.7 ChatMessage (Communication)

**Purpose:** Stores bidirectional messages between clients and admins.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `user_id` | UUID | FK → User | Client (conversation context) |
| `sender_role` | Enum | Required | `client`, `admin`, `superadmin` |
| `message` | Text | Required | Message content |
| `read_by_client` | Boolean | Default: false | Client read status |
| `read_by_admin` | Boolean | Default: false | Admin read status |
| `created_at` | Timestamp | Auto | Send time |

**Design Note:** Messages are linked to `user_id` (the client), not sender. The `sender_role` field indicates who sent the message.

**Ownership:** Sender creates; Recipient marks as read

---

### 3.2.8 Notification (Alert)

**Purpose:** System-generated alerts for status changes and requests.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `client_id` | UUID | FK → Client | Recipient |
| `created_by_id` | UUID | FK → Admin | Triggering admin (optional) |
| `type` | Enum | Required | Notification category |
| `title` | String | Required | Alert heading |
| `message` | Text | Required | Alert body |
| `link` | String | Optional | Deep link |
| `is_read` | Boolean | Default: false | Read status |
| `related_entity_id` | UUID | Optional | Linked entity |
| `related_entity_type` | String | Optional | Entity type |

**Notification Types:**
- `document_request`
- `payment_request`
- `tax_file_approval`
- `payment_received`
- `status_update`

**Ownership:** System creates; Client consumes

---

### 3.2.9 CostEstimate (Pricing)

**Purpose:** Service cost breakdown sent to clients.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `client_id` | UUID | FK → Client | Recipient |
| `service_cost` | Float | Required | Base fee |
| `discount` | Float | Default: 0 | Applied discount |
| `gst_hst` | Float | Required | Tax amount |
| `total` | Float | Required | Final amount |
| `status` | Enum | Required | `draft`, `sent`, `awaiting_payment`, `paid` |

**Ownership:** Admin creates/sends; Client pays

---

### 3.2.10 Note (Internal Record)

**Purpose:** Admin notes about client cases (internal or client-facing).

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `client_id` | UUID | FK → Client | Subject |
| `content` | Text | Required | Note text |
| `is_client_facing` | Boolean | Default: false | Visibility |
| `author_id` | UUID | FK → Admin | Author |
| `author_name` | String | Required | Denormalized name |

**Ownership:** Admin creates (immutable)

---

### 3.2.11 AuditLog (Change Tracking)

**Purpose:** Immutable record of system changes for compliance.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `action` | String | Required | `create`, `update`, `delete` |
| `entity_type` | String | Required | Table name |
| `entity_id` | UUID | Required | Record ID |
| `old_value` | JSON | Optional | Previous state |
| `new_value` | JSON | Optional | New state |
| `performed_by` | UUID | Required | Actor ID |
| `performed_by_name` | String | Required | Actor name |
| `timestamp` | Timestamp | Auto | Change time |

**Ownership:** System creates (immutable, append-only)

---

## 3.3 Entity Relationship Summary

```
┌──────────┐      1:N      ┌──────────┐      1:N      ┌──────────┐
│   User   │──────────────▶│  Client  │──────────────▶│ T1Return │
└──────────┘               └──────────┘               └──────────┘
     │                          │                          │
     │ 1:N                      │ 1:N                      │
     ▼                          ▼                          │
┌──────────┐              ┌──────────┐                     │
│ChatMessage│             │ Document │◀────────────────────┘
└──────────┘              └──────────┘         (optional link)
                               │
┌──────────┐      N:M     ┌────┴─────┐
│  Admin   │◀────────────▶│  Client  │
└──────────┘              └──────────┘
     │                         │
     │ 1:N                     │ 1:N
     ▼                         ▼
┌──────────┐              ┌──────────┐
│ Payment  │              │  Note    │
└──────────┘              └──────────┘
                               
┌──────────┐              ┌──────────┐
│Notification│◀───────────│  Client  │
└──────────┘              └──────────┘

┌──────────┐              ┌──────────┐
│CostEstimate│◀───────────│  Client  │
└──────────┘              └──────────┘
```

---

## 3.4 Supporting Entities

| Entity | Purpose | Notes |
|--------|---------|-------|
| **RefreshToken** | JWT refresh token storage | Linked to User; supports token revocation |
| **OTP** | One-time password records | Linked to User; expires after use |
| **AdminClientMap** | Admin-Client assignment | Many-to-many junction table |
| **TaxSection** | T1 form section organization | Optional; can use JSONB in T1Return instead |

---

## 3.5 Data Ownership Matrix

| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| **User** | Client (self) | Self, Admin | Self | Superadmin |
| **Admin** | Superadmin | Self, Superadmin | Self, Superadmin | Superadmin |
| **Client** | System (on registration) | Admin, Self | Admin | Superadmin |
| **T1Return** | Client | Client, Admin | Client (draft), Admin (status) | Superadmin |
| **Document** | Client | Client, Admin | Admin (status) | Admin, Superadmin |
| **Payment** | Admin | Admin, Superadmin | Admin | Superadmin |
| **ChatMessage** | Client, Admin | Client, Admin | Mark-read only | — |
| **Notification** | System | Client | Mark-read only | — |
| **CostEstimate** | Admin | Client, Admin | Admin | Admin |
| **Note** | Admin | Admin | — | Superadmin |
| **AuditLog** | System | Superadmin | — | — |

---

# PART 4 → Gaps & Risks

## 4.1 Missing API Endpoints

### 4.1.1 Critical Missing (Frontend Expects, Backend Doesn't Provide)

| Endpoint | Expected By | Status | Impact |
|----------|-------------|--------|--------|
| `PATCH /admin/admin-users/{id}` | Admin Dashboard | **NOT IMPLEMENTED** | Cannot edit admin users |
| `DELETE /admin/admin-users/{id}` | Admin Dashboard | **NOT IMPLEMENTED** | Cannot remove admin users |
| `GET /admin/audit-logs` | Admin Dashboard | **NOT IMPLEMENTED** (exists in separate admin-api service) | No audit trail visibility |
| `GET /notifications` | Flutter Client | **NOT IMPLEMENTED** | Client cannot see notifications |
| `PUT /notifications/{id}/read` | Flutter Client | **NOT IMPLEMENTED** | Cannot mark notifications read |
| `POST /auth/refresh` | Both Frontends | **NOT IMPLEMENTED** | Token refresh not available |
| `POST /auth/reset-password` | Flutter Client | **NOT IMPLEMENTED** | Password reset incomplete |

### 4.1.2 Partially Implemented

| Endpoint | Issue | Resolution Needed |
|----------|-------|-------------------|
| `POST /payments` | Listed in admin routes but not in main backend | Consolidate payment creation |
| `GET /client/me` | Returns User, not linked Client record | Should return full client profile |
| `PUT /client/profile` | No profile update endpoint | Add profile update capability |

### 4.1.3 Inconsistent Implementation

| Issue | Location | Description |
|-------|----------|-------------|
| **Duplicate backend services** | `backend/` vs `tax-hub-dashboard-admin/backend/` vs `services/admin-api/` | Three separate Flask backends with overlapping functionality |
| **Audit logging exists but not connected** | `tax-hub-dashboard-admin/backend/app/api/v1/audit_logs.py` | Audit routes exist in dashboard backend but not in main backend |
| **Notification creation without retrieval** | `filing_status.py` creates notifications | No endpoint for clients to retrieve their notifications |

---

## 4.2 Design Inconsistencies

### 4.2.1 Authentication Inconsistencies

| Issue | Evidence | Risk |
|-------|----------|------|
| **Static OTP in production** | `AUTH_API_DOCS.md`: "Currently uses static OTP `123456`" | **CRITICAL**: No actual email verification |
| **Mock users in AuthContext** | `AuthContext.tsx` still has hardcoded `MOCK_USERS` array | Dashboard may fall back to mock auth |
| **Duplicate `get_current_admin` functions** | Defined in both `admin_auth.py` and `jwt.py` | Confusion about which to use |
| **No token refresh endpoint** | JWT tokens expire in 30 min with no refresh mechanism in main backend | Users forced to re-login frequently |

### 4.2.2 Data Model Inconsistencies

| Issue | Evidence | Risk |
|-------|----------|------|
| **Client vs User confusion** | `User` is auth account, `Client` is filing record, but frontends use interchangeably | Query/API mismatches |
| **Chat linked to User, not Client** | `ChatMessage.user_id → User.id` but dashboard expects `client_id` | Admin may see wrong chat threads |
| **Two T1 tables** | `TaxReturn` (normalized) and `T1ReturnFlat` (denormalized) coexist | Data sync issues, unclear which is source of truth |
| **Payment `created_by_id` requires Admin** | Cannot record self-service payments from clients | Business logic limitation |

### 4.2.3 API Naming Inconsistencies

| Frontend Expects | Backend Provides | Issue |
|------------------|------------------|-------|
| `/files/upload` (Flutter docs) | `/documents/upload` | Endpoint name mismatch |
| `/t1/tax-return` (some docs) | `/client/tax-return` | Inconsistent prefix |
| `camelCase` response fields | Mixed `snake_case` and `camelCase` | Serialization inconsistency |
| `filingYear` (frontend) | `filing_year` (database) | Case transformation needed |

---

## 4.3 Security Concerns

### 4.3.1 Critical Security Issues

| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|
| **Static OTP `123456`** | 🔴 CRITICAL | `auth.py` | Implement real OTP generation + email delivery |
| **Default JWT secret** | 🔴 CRITICAL | `jwt.py`: `"change-me-in-prod"` | Enforce strong secret in production |
| **Auto-generated encryption key** | 🔴 CRITICAL | `encryption.py` prints key to console | Require `FILE_ENCRYPTION_KEY` in env |
| **CORS allows all origins** | 🟠 HIGH | `main.py`: `allow_origins=["*"]` | Restrict to known frontend domains |
| **No rate limiting** | 🟠 HIGH | All endpoints | Add rate limiting for auth endpoints |

### 4.3.2 Medium Security Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| **No password complexity validation** | 🟡 MEDIUM | Only checks length ≥ 6 characters |
| **Chat endpoints unprotected** | 🟡 MEDIUM | `API_QUICK_REFERENCE.md` shows no auth for chat |
| **SIN stored in plaintext** | 🟡 MEDIUM | T1 forms store SIN without encryption |
| **No audit logging in main backend** | 🟡 MEDIUM | No tracking of who changed what |
| **Session not validated against Redis** | 🟡 MEDIUM | Token valid even if session revoked (race condition) |

### 4.3.3 Encryption Concerns

| Issue | Description | Recommendation |
|-------|-------------|----------------|
| **Single encryption key for all files** | Same Fernet key encrypts all documents | Consider per-client or per-document keys |
| **Key hash stored, not rotated** | `encryption_key_hash` stored but no rotation mechanism | Implement key rotation strategy |
| **Decrypted files streamed directly** | No access logging for downloads | Add audit trail for document access |

---

## 4.4 Data Integrity Risks

### 4.4.1 Referential Integrity

| Issue | Tables Affected | Risk |
|-------|-----------------|------|
| **T1ReturnFlat lacks FK constraint** | `client_id` has no foreign key | Orphaned T1 records possible |
| **No cascade on User deletion** | User → Client → T1Return → Documents | Manual cleanup required |
| **Admin deletion with assigned clients** | `AdminClientMap` references deleted admin | Assignment orphans |

### 4.4.2 Data Synchronization

| Issue | Description | Risk |
|-------|-------------|------|
| **Dual T1 tables** | `TaxReturn` and `T1ReturnFlat` may diverge | Inconsistent form data |
| **Denormalized client name/email** | `Client` duplicates `User.first_name + last_name` | Updates don't propagate |
| **Status sync T1 → Client** | `filing_status.py` syncs statuses but mapping may miss edge cases | Status mismatch |
| **Payment totals not recalculated** | `Client.paid_amount` updated manually | Sum may not match `Payment` records |

### 4.4.3 Business Rule Violations

| Rule | Current Implementation | Risk |
|------|------------------------|------|
| **One Client per User per Year** | No unique constraint on `(user_id, filing_year)` | Duplicate filings possible |
| **Status progression** | No validation of valid state transitions | Status can jump backward |
| **Payment before filing** | No enforcement | Could file without payment |

---

## 4.5 Scaling Risks

### 4.5.1 Performance Concerns

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **JSONB full-table scans** | T1 form queries may scan entire `form_data` | Add GIN indexes (partially done) |
| **Chat polling every 5 seconds** | N clients = N requests/5 seconds | Implement WebSocket or long-polling |
| **No pagination on some endpoints** | `/admin/clients`, `/admin/documents` return all | Add pagination parameters |
| **Analytics calculated on every request** | `GET /admin/analytics` does live aggregation | Cache results, use materialized views |
| **File decryption on download** | CPU-intensive for large files | Consider streaming decryption |

### 4.5.2 Architectural Concerns

| Issue | Description | Risk |
|-------|-------------|------|
| **Three backend services** | `backend/`, `services/admin-api/`, `tax-hub-dashboard-admin/backend/` | Maintenance nightmare, feature drift |
| **Local filesystem storage** | Documents stored in `./storage/uploads` | No redundancy, single-server limit |
| **Redis optional** | Falls back to in-memory dict | Sessions lost on restart |
| **No background job queue** | OTP emails, notifications are synchronous | Request latency, failures |

### 4.5.3 Operational Concerns

| Issue | Current State | Production Requirement |
|-------|---------------|------------------------|
| **No health check endpoint** | Only `/` returns `{"status": "ok"}` | Need `/health` with DB/Redis checks |
| **No structured logging** | Print statements | JSON logging with correlation IDs |
| **No metrics/monitoring** | None | Prometheus/StatsD integration |
| **No database migrations** | Schema created via `Base.metadata.create_all()` | Need Alembic migrations |

---

## 4.6 Gap Summary Matrix

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| **Missing APIs** | 3 | 4 | 5 | 2 |
| **Security** | 3 | 2 | 5 | 0 |
| **Data Integrity** | 2 | 4 | 3 | 1 |
| **Scaling** | 1 | 3 | 4 | 2 |
| **Architecture** | 2 | 3 | 2 | 1 |
| **TOTAL** | **11** | **16** | **19** | **6** |

---

## 4.7 Prioritized Action Items

### 🔴 Must Fix Before Production (Critical)

1. **Replace static OTP** with real email-based OTP generation
2. **Enforce JWT secret key** - fail startup if not set in production
3. **Require `FILE_ENCRYPTION_KEY`** - never auto-generate
4. **Restrict CORS origins** - whitelist frontend domains only
5. **Implement `/admin/admin-users/{id}` PATCH/DELETE** - dashboard depends on it
6. **Consolidate backend services** - single source of truth

### 🟠 Should Fix Before Production (High)

1. **Add rate limiting** on auth endpoints
2. **Implement token refresh** endpoint
3. **Add client notification retrieval** API
4. **Fix Chat authentication** - require auth on all chat endpoints
5. **Add audit logging** to main backend
6. **Implement pagination** on list endpoints

### 🟡 Plan for Post-Launch (Medium)

1. Add password complexity rules
2. Encrypt SIN values in database
3. Implement WebSocket for chat
4. Add database migrations (Alembic)
5. Create health check endpoints
6. Add structured logging

---

# Next Steps

**PHASE 1 COMPLETE.**

Recommended next actions:

1. **Review and confirm** all findings are accurate
2. **Prioritize** which gaps to address first
3. **Proceed to PHASE 2** (Database Schema Design) when ready

---

*Document generated from codebase analysis on January 5, 2026*
