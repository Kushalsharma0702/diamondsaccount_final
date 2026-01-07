# PHASE 1 — Backend System Redesign

**Date:** January 5, 2026  
**Status:** AWAITING APPROVAL  
**Scope:** Design only — No code, no database tables

---

## Executive Summary

This document redesigns the TaxEase backend from scratch based on:
- **Email-first communication model** (no in-app chat)
- **Frontend contracts are FINAL** (Flutter client + React admin dashboard)
- **Production-grade architecture** for a 5+ year lifespan
- **Single source of truth** for all data

---

# 1. DOMAIN ENTITIES (REQUIRED BY FRONTEND)

Based on frontend analysis, these are the **only entities** the system needs:

## 1.1 Core Entities

| Entity | Purpose | Owner | Immutable? |
|--------|---------|-------|------------|
| **User** | Client account (auth) | Client | No (email update allowed) |
| **Admin** | Staff account | Superadmin | No |
| **Filing** | Tax return engagement per client per year | System | No |
| **T1FormData** | Complete tax form submission (JSONB) | Client | No (until submitted) |
| **Document** | Uploaded file metadata + encrypted storage | Client | Content immutable; status mutable |
| **Payment** | Payment record | Admin | Yes (append-only) |
| **Notification** | Simple in-app alert pointing to email | System | Yes (append-only) |
| **AuditLog** | Immutable change tracking | System | Yes (append-only) |

## 1.2 Removed Entities (Unnecessary)

| Entity | Why Removed |
|--------|-------------|
| **ChatMessage** | Email-first model — no in-app chat |
| **Client** (separate from Filing) | Merged into Filing — no separate "client profile" entity |
| **TaxReturn + T1ReturnFlat** | Duplicate tables — merged into single T1FormData |
| **TaxSection** | Over-engineered — JSONB handles form sections |
| **CostEstimate** | Part of Payment workflow, not separate entity |
| **Note** | Admin notes go in **email thread** or **AuditLog** |
| **RefreshToken** | Stateless JWT — no token storage needed |
| **OTP** | In-memory with TTL, not persisted |
| **AdminClientMap** | Direct FK on Filing — no junction table needed |

---

# 2. ENTITY DEFINITIONS & OWNERSHIP

## 2.1 User (Client Account)

**Purpose:** Authentication identity for taxpayers

| Attribute | Type | Source | Mutable |
|-----------|------|--------|---------|
| `id` | UUID | System | No |
| `email` | String | Client | Yes (with reverification) |
| `first_name` | String | Client | Yes |
| `last_name` | String | Client | Yes |
| `phone` | String | Client | Yes |
| `password_hash` | String | Client | Yes (reset flow) |
| `email_verified` | Boolean | System | Yes (OTP flow) |
| `is_active` | Boolean | Admin | Yes |
| `created_at` | Timestamp | System | No |
| `updated_at` | Timestamp | System | Auto |

**Ownership Rules:**
- Client creates during registration
- Client updates profile (except `is_active`)
- Admin can deactivate
- System manages verification status

**Lifecycle:**
```
Created → Email Verified → Active → [Deactivated]
```

---

## 2.2 Admin (Staff Account)

**Purpose:** Authentication + authorization for tax professionals

| Attribute | Type | Source | Mutable |
|-----------|------|--------|---------|
| `id` | UUID | System | No |
| `email` | String | Superadmin | Yes |
| `name` | String | Superadmin/Self | Yes |
| `password_hash` | String | Self | Yes |
| `role` | Enum | Superadmin | Yes |
| `permissions` | String[] | Superadmin | Yes |
| `is_active` | Boolean | Superadmin | Yes |
| `last_login_at` | Timestamp | System | Auto |
| `created_at` | Timestamp | System | No |

**Role Values:** `admin`, `superadmin`

**Permission Keys (exactly matching frontend):**
- `add_edit_payment`
- `add_edit_client`
- `request_documents`
- `assign_clients`
- `view_analytics`
- `approve_cost_estimate`
- `update_workflow`

**Ownership Rules:**
- Superadmin creates/deletes admins
- Self updates password and name
- Superadmin manages roles/permissions/activation

---

## 2.3 Filing (Tax Engagement)

**Purpose:** Single source of truth for a client's tax filing in a specific year

| Attribute | Type | Source | Mutable |
|-----------|------|--------|---------|
| `id` | UUID | System | No |
| `user_id` | FK→User | System | No |
| `filing_year` | Integer | Client | No (after creation) |
| `status` | Enum | Admin | Yes |
| `payment_status` | Enum | System | Yes (derived) |
| `assigned_admin_id` | FK→Admin | Superadmin/Admin | Yes |
| `total_fee` | Decimal | Admin | Yes |
| `paid_amount` | Decimal | System | Yes (derived from payments) |
| `email_thread_id` | String | System | No (set once) |
| `created_at` | Timestamp | System | No |
| `updated_at` | Timestamp | System | Auto |

**Status Values (9-step workflow):**
```
draft → submitted → payment_request_sent → payment_received → 
return_in_progress → additional_info_required → 
under_review → approved_for_filing → e_filing_completed
```

**Payment Status (DERIVED):**
- `pending` — paid_amount = 0
- `partial` — 0 < paid_amount < total_fee
- `paid` — paid_amount >= total_fee
- `overdue` — pending AND deadline passed

**Unique Constraint:** `(user_id, filing_year)` — one filing per user per year

**Ownership Rules:**
- System creates when client starts T1 form
- Client cannot directly modify Filing (only via T1FormData)
- Admin updates status, fee, assignment
- System derives payment_status from Payment records

---

## 2.4 T1FormData (Tax Form)

**Purpose:** Complete T1 personal tax form data

| Attribute | Type | Source | Mutable |
|-----------|------|--------|---------|
| `id` | UUID | System | No |
| `filing_id` | FK→Filing | System | No |
| `form_data` | JSONB | Client | Yes (until submitted) |
| `submitted_at` | Timestamp | System | Yes (once) |
| `created_at` | Timestamp | System | No |
| `updated_at` | Timestamp | System | Auto |

**Denormalized Query Columns (extracted from JSONB on save):**
- `first_name`, `last_name`, `sin` (encrypted), `date_of_birth`
- `marital_status`, `spouse_sin` (encrypted)
- Boolean flags: `has_foreign_property`, `has_medical_expenses`, `has_self_employment`, etc.

**JSONB `form_data` Structure (matching Flutter model):**
```json
{
  "personalInfo": {
    "firstName": "",
    "lastName": "",
    "sin": "",
    "dateOfBirth": "YYYY-MM-DD",
    "address": "",
    "phoneNumber": "",
    "email": "",
    "isCanadianCitizen": true,
    "maritalStatus": "single|married|common_law|...",
    "spouseInfo": {...},
    "children": [...]
  },
  "hasForeignProperty": false,
  "foreignProperty": [...],
  "hasMedicalExpenses": false,
  "medicalExpenses": [...],
  "hasWorkFromHomeExpense": false,
  "workFromHomeExpense": {...},
  "selfEmployment": {
    "businessTypes": [],
    "uberBusiness": {...},
    "generalBusiness": {...},
    "rentalIncome": {...}
  },
  "uploadedDocuments": {}
}
```

**Ownership Rules:**
- Client creates/updates while status = `draft`
- Client submits (status → `submitted`, form becomes read-only)
- Admin can view but not edit form_data

**Lifecycle:**
```
Draft (editable) → Submitted (locked) → [Admin processes]
```

---

## 2.5 Document (File Upload)

**Purpose:** Track uploaded files with encryption metadata

| Attribute | Type | Source | Mutable |
|-----------|------|--------|---------|
| `id` | UUID | System | No |
| `filing_id` | FK→Filing | System | No |
| `name` | String | Client/Admin | Yes |
| `original_filename` | String | Client | No |
| `file_type` | String | System | No |
| `file_size` | Integer | System | No |
| `storage_path` | String | System | No |
| `section_key` | String | Client | Yes |
| `document_type` | String | Client/Admin | Yes |
| `status` | Enum | Admin | Yes |
| `notes` | Text | Admin | Yes |
| `uploaded_at` | Timestamp | System | No |
| `requested_at` | Timestamp | Admin | Yes |
| `request_message` | Text | Admin | Yes |

**Status Values:**
- `pending` — uploaded, awaiting review
- `approved` — admin verified
- `reupload_requested` — issues found
- `missing` — admin requested, not yet uploaded

**Section Keys (matching T1 form sections):**
- `employment_income`, `investment_income`, `foreign_property`
- `medical_expenses`, `charitable_donations`, `moving_expenses`
- `self_employment`, `rental_income`, `work_from_home`
- `tuition`, `childcare`, `other`

**Ownership Rules:**
- Client uploads (creates with status=`pending`)
- Admin requests documents (creates with status=`missing`)
- Admin updates status/notes
- Files are encrypted at rest, decrypted on download

---

## 2.6 Payment (Append-Only Ledger)

**Purpose:** Immutable record of payments received

| Attribute | Type | Source | Mutable |
|-----------|------|--------|---------|
| `id` | UUID | System | No |
| `filing_id` | FK→Filing | System | No |
| `amount` | Decimal | Admin | No |
| `method` | String | Admin | No |
| `note` | Text | Admin | No |
| `recorded_by_id` | FK→Admin | System | No |
| `recorded_at` | Timestamp | System | No |

**Immutability:** Payments are never edited or deleted. Corrections are made by adding new records (e.g., refunds as negative amounts).

**Ownership Rules:**
- Admin records payment
- System updates Filing.paid_amount (SUM of payments)
- System updates Filing.payment_status

---

## 2.7 Notification (Simple Alert)

**Purpose:** In-app notification that points user to email

| Attribute | Type | Source | Mutable |
|-----------|------|--------|---------|
| `id` | UUID | System | No |
| `user_id` | FK→User | System | No |
| `filing_id` | FK→Filing | System | Yes (nullable) |
| `type` | Enum | System | No |
| `title` | String | System | No |
| `message` | String | System | No |
| `is_read` | Boolean | Client | Yes |
| `created_at` | Timestamp | System | No |

**Type Values:**
- `email_received` — "You have a new message. Check your email."
- `document_requested` — "Documents requested. Check your email."
- `payment_requested` — "Payment requested. Check your email."
- `status_updated` — "Your filing status has been updated."

**Key Design:** Notifications are SIMPLE. They just say "check your email" — all details are in the email thread.

**Ownership Rules:**
- System creates when admin sends email
- Client marks as read
- Never deleted

---

## 2.8 AuditLog (Immutable)

**Purpose:** Compliance-grade change tracking

| Attribute | Type | Source | Mutable |
|-----------|------|--------|---------|
| `id` | UUID | System | No |
| `entity_type` | String | System | No |
| `entity_id` | UUID | System | No |
| `action` | Enum | System | No |
| `changes` | JSONB | System | No |
| `performed_by_id` | UUID | System | No |
| `performed_by_type` | Enum | System | No |
| `ip_address` | String | System | No |
| `user_agent` | String | System | No |
| `timestamp` | Timestamp | System | No |

**Action Values:** `create`, `update`, `delete`, `login`, `logout`, `submit`, `approve`

**Performed By Type:** `user`, `admin`, `system`

**JSONB `changes` Structure:**
```json
{
  "field_name": {
    "old": "previous_value",
    "new": "new_value"
  }
}
```

**Ownership Rules:**
- System-only write
- Superadmin read
- Never modified or deleted

---

# 3. STATE MACHINES & TRANSITIONS

## 3.1 Filing Status State Machine

```
                    ┌──────────────────────────────────────────────┐
                    │                                              │
                    ▼                                              │
┌────────┐    ┌───────────┐    ┌─────────────────────┐    ┌──────────────────┐
│ draft  │───▶│ submitted │───▶│ payment_request_sent│───▶│ payment_received │
└────────┘    └───────────┘    └─────────────────────┘    └──────────────────┘
                                                                   │
                                                                   ▼
┌─────────────────────┐    ┌────────────────────────────┐    ┌──────────────────┐
│ e_filing_completed  │◀───│ approved_for_filing        │◀───│ return_in_progress│
└─────────────────────┘    └────────────────────────────┘    └──────────────────┘
                                      ▲                            │
                                      │                            ▼
                               ┌──────────────┐           ┌──────────────────────┐
                               │ under_review │◀──────────│additional_info_required│
                               └──────────────┘           └──────────────────────┘
                                                                   │
                                                                   └──────────────┐
                                                                                  │
                                                                   (loops back to │
                                                                   return_in_progress)
```

**Valid Transitions:**

| From | To | Triggered By |
|------|----|--------------|
| `draft` | `submitted` | Client submits T1 form |
| `submitted` | `payment_request_sent` | Admin sends cost estimate email |
| `payment_request_sent` | `payment_received` | Admin records payment |
| `payment_received` | `return_in_progress` | Admin begins preparation |
| `return_in_progress` | `additional_info_required` | Admin requests more docs |
| `additional_info_required` | `return_in_progress` | Client uploads docs |
| `return_in_progress` | `under_review` | Admin completes preparation |
| `under_review` | `approved_for_filing` | Client approves return |
| `approved_for_filing` | `e_filing_completed` | Admin files with CRA |

**Invalid Transitions (backend must reject):**
- Skipping steps (e.g., `draft` → `e_filing_completed`)
- Going backward (except `additional_info_required` loop)

---

## 3.2 Document Status State Machine

```
┌─────────┐         ┌──────────┐
│ missing │────────▶│ pending  │
└─────────┘         └──────────┘
     ▲                   │
     │                   ├───────────────────┐
     │                   ▼                   ▼
     │             ┌──────────┐        ┌──────────────────┐
     └─────────────│ approved │        │reupload_requested│
                   └──────────┘        └──────────────────┘
                                              │
                                              └──────▶ (back to pending)
```

---

# 4. WHAT MUST BE STORED vs DERIVED vs IMMUTABLE

## 4.1 Stored (Persisted in DB)

| Data | Entity | Why |
|------|--------|-----|
| User credentials | User | Authentication |
| Admin credentials | Admin | Authentication |
| Filing metadata | Filing | Workflow tracking |
| T1 form data | T1FormData | Legal document |
| Document metadata | Document | File tracking |
| Payment records | Payment | Financial audit |
| Audit trail | AuditLog | Compliance |

## 4.2 Derived (Calculated on Read)

| Data | Source | Formula |
|------|--------|---------|
| `Filing.payment_status` | Payment | Based on paid_amount vs total_fee |
| `Filing.paid_amount` | Payment | SUM(Payment.amount) WHERE filing_id = X |
| `User.full_name` | User | `first_name + ' ' + last_name` |
| Analytics totals | All entities | Aggregated on request |
| Unread notification count | Notification | COUNT WHERE is_read = false |

## 4.3 Immutable (Never Changed After Creation)

| Data | Why |
|------|-----|
| Payment records | Financial audit trail |
| AuditLog entries | Compliance requirement |
| Document file content | Legal evidence |
| T1FormData after submission | Tax record integrity |
| Timestamps | Audit trail |

---

# 5. EMAIL-FIRST COMMUNICATION MODEL

## 5.1 Core Principle

**ALL substantive communication happens via EMAIL.** In-app notifications are simple alerts that say "Check your email."

## 5.2 Email Thread Per Filing

Each Filing gets ONE email thread ID. All communications for that filing year go in the same thread.

**Thread ID Format:** `filing-{filing_id}@taxease.com`

**Email Types:**
1. **Welcome email** — When client creates account
2. **Document request** — Admin requests specific documents
3. **Cost estimate** — Admin sends fee breakdown
4. **Payment confirmation** — After payment recorded
5. **Status update** — Major filing status changes
6. **Return ready for review** — Client approval request
7. **Filing complete** — Final acknowledgment

## 5.3 Admin Dashboard Real-Time View

Admin sees:
- All filings with current status
- Document upload notifications (real-time via polling/SSE)
- Payment status
- Recent activity feed

Admin actions:
- Send email (opens email composer with thread)
- Request documents (sends email + creates Document with status=`missing`)
- Update status (sends status update email)
- Record payment (sends confirmation email)

## 5.4 Client In-App Experience

Client sees:
- Filing status (9-step timeline)
- Notifications page (simple alerts)
- Document upload interface
- T1 form editor

Client does NOT see:
- Chat interface
- Message history
- Detailed communication log

---

# 6. CLEAN BACKEND ARCHITECTURE

## 6.1 Module Structure

```
backend/
├── main.py                 # FastAPI app entry
├── config.py               # Environment configuration
├── database.py             # SQLAlchemy setup
│
├── core/                   # Shared infrastructure
│   ├── security.py         # JWT, password hashing
│   ├── email.py            # Email service (SES/SMTP)
│   ├── storage.py          # File encryption + storage
│   └── audit.py            # Audit logging service
│
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── admin.py
│   ├── filing.py
│   ├── t1_form.py
│   ├── document.py
│   ├── payment.py
│   ├── notification.py
│   └── audit_log.py
│
├── schemas/                # Pydantic request/response schemas
│   ├── auth.py
│   ├── user.py
│   ├── admin.py
│   ├── filing.py
│   ├── t1_form.py
│   ├── document.py
│   ├── payment.py
│   └── notification.py
│
├── services/               # Business logic
│   ├── auth_service.py
│   ├── filing_service.py
│   ├── t1_form_service.py
│   ├── document_service.py
│   ├── payment_service.py
│   ├── notification_service.py
│   └── analytics_service.py
│
├── api/                    # Route handlers
│   ├── deps.py             # Dependencies (auth, db session)
│   ├── v1/
│   │   ├── auth.py         # Client auth endpoints
│   │   ├── user.py         # Client profile endpoints
│   │   ├── filing.py       # Client filing endpoints
│   │   ├── t1_form.py      # T1 form endpoints
│   │   ├── documents.py    # Document upload/download
│   │   ├── notifications.py# Client notifications
│   │   │
│   │   └── admin/
│   │       ├── auth.py     # Admin auth endpoints
│   │       ├── users.py    # Admin user management
│   │       ├── clients.py  # Client list/detail (admin view)
│   │       ├── filings.py  # Filing management
│   │       ├── documents.py# Document review
│   │       ├── payments.py # Payment recording
│   │       ├── analytics.py# Dashboard stats
│   │       └── audit.py    # Audit log viewing
│
└── migrations/             # Alembic migrations
```

## 6.2 Data Flow

### Client T1 Form Submission
```
Flutter App                Backend                    Database
    │                         │                          │
    │  POST /t1-form         │                          │
    │ ─────────────────────▶ │                          │
    │                         │  Validate form           │
    │                         │  Extract denorm fields   │
    │                         │                          │
    │                         │  INSERT/UPDATE T1FormData│
    │                         │ ─────────────────────────▶│
    │                         │                          │
    │                         │  UPDATE Filing.status    │
    │                         │ ─────────────────────────▶│
    │                         │                          │
    │                         │  INSERT AuditLog         │
    │                         │ ─────────────────────────▶│
    │                         │                          │
    │  200 OK                │                          │
    │ ◀───────────────────── │                          │
```

### Admin Document Request
```
Admin Dashboard            Backend                    Database          Email Service
    │                         │                          │                   │
    │ POST /admin/documents   │                          │                   │
    │ (status=missing)        │                          │                   │
    │ ─────────────────────▶ │                          │                   │
    │                         │  INSERT Document         │                   │
    │                         │ ─────────────────────────▶│                   │
    │                         │                          │                   │
    │                         │  INSERT Notification     │                   │
    │                         │ ─────────────────────────▶│                   │
    │                         │                          │                   │
    │                         │  Send email              │                   │
    │                         │ ───────────────────────────────────────────▶│
    │                         │                          │                   │
    │                         │  INSERT AuditLog         │                   │
    │                         │ ─────────────────────────▶│                   │
    │                         │                          │                   │
    │  200 OK                │                          │                   │
    │ ◀───────────────────── │                          │                   │
```

## 6.3 Authentication Strategy

### Client Auth
- **Registration:** Email + password → OTP verification email → Account active
- **Login:** Email + password → JWT access token (30min) + refresh token (30 days)
- **OTP:** In-memory with 5-minute TTL, 6-digit code, max 3 attempts
- **Token refresh:** Stateless — verify refresh token signature, issue new access token

### Admin Auth
- **Login:** Email + password → JWT with role/permissions embedded
- **Session:** Optional Redis session for "remember me" (30 days)
- **Permissions:** Checked on every request via JWT claims

### Security Rules
- **No static OTP** — Real random codes sent via email
- **Strong JWT secret** — Required, fail startup if not set
- **Password requirements** — Min 8 chars, mixed case, number
- **Rate limiting** — 5 attempts per minute per IP for auth endpoints
- **CORS restricted** — Only frontend domains allowed

---

# 7. REMOVED BOTTLENECKS & FLAWS

## 7.1 Eliminated Problems

| Problem | Old System | New System |
|---------|-----------|------------|
| **Duplicate T1 tables** | `TaxReturn` + `T1ReturnFlat` | Single `T1FormData` |
| **Client vs User confusion** | Separate entities with unclear relation | `User` for auth, `Filing` for engagement |
| **Chat polling** | 5-second polling for messages | Email-first (no chat) |
| **Static OTP** | Hardcoded `123456` | Real OTP via email |
| **Three backends** | `backend/`, `admin-api/`, `dashboard-backend/` | Single unified backend |
| **No audit trail** | Ad-hoc logging | Comprehensive `AuditLog` |
| **CORS wildcard** | `allow_origins=["*"]` | Restricted to frontend domains |
| **Duplicate auth code** | Multiple `get_current_admin` functions | Single auth dependency |
| **Missing APIs** | Frontend expects, backend doesn't have | Complete API coverage |

## 7.2 Simplified Architecture

**Before:**
```
Flutter ──▶ client-api ──▶ PostgreSQL
React ──▶ admin-api ──▶ PostgreSQL (same or different?)
React ──▶ dashboard-backend ──▶ PostgreSQL
```

**After:**
```
Flutter ─┐
         ├──▶ Single Backend ──▶ PostgreSQL
React ───┘
```

---

# 8. FRONTEND COMPATIBILITY MATRIX

## 8.1 Flutter Client (No Changes Needed)

| Feature | Current API Call | New API Call | Compatible? |
|---------|-----------------|--------------|-------------|
| Register | `POST /auth/register` | Same | ✅ |
| Login | `POST /auth/login` | Same | ✅ |
| OTP | `POST /auth/request-otp`, `/verify-otp` | Same | ✅ |
| Profile | `GET /auth/me` | Same | ✅ |
| T1 Submit | `POST /client/tax-return` | Same | ✅ |
| Documents | `POST /documents/upload` | Same | ✅ |
| Filing Status | `GET /filing-status/client/{id}` | Same | ✅ |
| Notifications | `GET /notifications` | **NEW** (was missing) | ✅ |
| Chat | `POST /chat/send` | **REMOVED** | ⚠️ See note |

**Chat Removal Note:** The Flutter app has a `CommunicationPage` that uses chat APIs. This page should:
1. Be repurposed as a "Contact Support" page with email link, OR
2. Show notification history only

Since frontend is FINAL, the chat endpoints will return `501 Not Implemented` with a message directing users to email.

## 8.2 React Admin Dashboard (No Changes Needed)

| Feature | Current API Call | New API Call | Compatible? |
|---------|-----------------|--------------|-------------|
| Login | `POST /admin/auth/login` | Same | ✅ |
| Logout | `POST /admin/auth/logout` | Same | ✅ |
| Get Clients | `GET /admin/clients` | Same | ✅ |
| Client Detail | `GET /admin/clients/{id}` | Same | ✅ |
| Update Client | `PATCH /admin/clients/{id}` | Same | ✅ |
| Documents | `GET /admin/documents` | Same | ✅ |
| Payments | `POST /payments` | Same | ✅ |
| Analytics | `GET /admin/analytics` | Same | ✅ |
| Admin Users | `GET /admin/admin-users` | **Fixed** (was partial) | ✅ |
| Audit Logs | `GET /admin/audit-logs` | **NEW** (was missing) | ✅ |
| Chat | `POST /chat/send` | **REMOVED** | ⚠️ See note |

---

# 9. DECISION SUMMARY

## 9.1 What MUST Be Stored
- User accounts and credentials
- Admin accounts with roles/permissions
- Filing records (one per user per year)
- T1 form data (JSONB + denormalized columns)
- Document metadata (encrypted files in storage)
- Payment ledger (append-only)
- Audit log (append-only)

## 9.2 What MUST Be Derived
- Payment status (from payment sum)
- Analytics aggregations
- Notification counts

## 9.3 What MUST Be Immutable
- Payment records
- Audit log entries
- Submitted T1 forms
- Document file content

## 9.4 What MUST Be Removed
- In-app chat system
- Duplicate backend services
- Duplicate T1 tables
- Static OTP
- CORS wildcard
- Unnecessary junction tables

---

# 10. NEXT STEPS

**PHASE 1 COMPLETE — AWAITING APPROVAL**

Upon your confirmation, I will proceed to:

**PHASE 2 — Database Schema Design**
- PostgreSQL tables with proper constraints
- UUID primary keys
- Referential integrity
- JSONB for form_data
- Indexing strategy
- Migration-ready (Alembic)

---

**Reply "PROCEED TO PHASE 2" to continue.**
