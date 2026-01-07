# API REDESIGN — PHASE 1: Resource Identification

**Date:** January 5, 2026  
**Status:** AWAITING APPROVAL  
**Scope:** API Resource Definition Only

---

## Executive Summary

This document identifies the **PRIMARY API resources** required to serve the existing Flutter client and React admin dashboard. All resources are designed around the email-first communication model and support a 5+ year lifecycle.

---

# 1. PRIMARY API RESOURCES

## 1.1 Resource Inventory

| Resource | Responsibility | Frontend Usage | Mutable | Notes |
|----------|----------------|----------------|---------|-------|
| **User** | Client account & authentication | Flutter | Yes | Self-managed profile |
| **Admin** | Staff account & permissions | React | Yes | Superadmin-managed |
| **Filing** | Tax engagement per user per year | Both | Yes | One per user per year |
| **T1Form** | Tax form data (JSONB) | Flutter (write), React (read) | Yes (until submitted) | Locked after submission |
| **Document** | File metadata + encrypted storage | Both | Status mutable, file immutable | Encryption required |
| **Payment** | Financial transaction record | React | No | Append-only ledger |
| **Notification** | Simple in-app alert | Flutter | Mark-read only | Points to email |
| **Analytics** | Aggregated dashboard stats | React | N/A | Derived, not stored |
| **AuditLog** | Compliance trail | React (superadmin) | No | Append-only |

**Total Primary Resources:** 9

---

# 2. RESOURCE DEFINITIONS

## 2.1 User (Client Account)

**Responsibility:** Client authentication and profile management

**Access Rules:**
- Create: Public (registration)
- Read: Self only
- Update: Self (profile), Admin (activation)
- Delete: Superadmin only

**Mutability:**
- Mutable: `email`, `first_name`, `last_name`, `phone`, `password`
- Immutable: `id`, `created_at`
- System-managed: `email_verified`, `is_active`, `updated_at`

**Frontend Dependencies:**
- Flutter: Registration, login, profile editing
- React: None (admins don't manage user accounts directly)

---

## 2.2 Admin (Staff Account)

**Responsibility:** Staff authentication, authorization, and role management

**Access Rules:**
- Create: Superadmin only
- Read: Self (own data), Superadmin (all admins)
- Update: Self (name, password), Superadmin (role, permissions, activation)
- Delete: Superadmin only

**Mutability:**
- Mutable: `name`, `email`, `password`, `role`, `permissions`, `is_active`
- Immutable: `id`, `created_at`
- System-managed: `last_login_at`, `updated_at`

**Frontend Dependencies:**
- React: Admin login, profile, user management dashboard

---

## 2.3 Filing (Tax Engagement)

**Responsibility:** Represents a client's tax filing engagement for a specific year. Single source of truth for filing workflow.

**Access Rules:**
- Create: System (when client starts T1 form)
- Read: Client (own filings), Admin (assigned or all)
- Update: Admin (status, fee, assignment), System (payment calculations)
- Delete: Superadmin only (soft delete)

**Mutability:**
- Mutable: `status`, `assigned_admin_id`, `total_fee`, `email_thread_id`
- Immutable: `id`, `user_id`, `filing_year`, `created_at`
- Derived: `paid_amount`, `payment_status` (calculated from Payment records)

**Unique Constraint:** One filing per user per year

**Frontend Dependencies:**
- Flutter: Filing status timeline, progress tracking
- React: Client list, filing management, status updates

**State Machine:** 9-step workflow (draft → submitted → payment_request_sent → ... → e_filing_completed)

---

## 2.4 T1Form (Tax Form Data)

**Responsibility:** Complete T1 personal tax form submission data in JSONB format

**Access Rules:**
- Create: Client (when starting form)
- Read: Client (own forms), Admin (assigned clients)
- Update: Client (while status=draft), Admin (status updates only)
- Delete: Superadmin only (audit trail)

**Mutability:**
- Mutable: `form_data` (only while status=draft), `status`
- Immutable: `id`, `filing_id`, `created_at`, `submitted_at`
- System-managed: `updated_at`

**Frontend Dependencies:**
- Flutter: Multi-step form editor, auto-save, submission
- React: Form data viewing (read-only)

**Lock Rule:** After submission, `form_data` becomes read-only

---

## 2.5 Document (File Upload)

**Responsibility:** Track uploaded files with encryption, metadata, and review status

**Access Rules:**
- Create: Client (upload), Admin (request missing doc)
- Read: Client (own docs), Admin (assigned client docs)
- Update: Admin (status, notes), System (encryption metadata)
- Delete: Admin (soft delete - archive)

**Mutability:**
- Mutable: `name`, `section_key`, `document_type`, `status`, `notes`, `requested_at`, `request_message`
- Immutable: `id`, `filing_id`, `original_filename`, `file_type`, `file_size`, `storage_path`, `uploaded_at`
- System-managed: `created_at`, `updated_at`

**File Immutability:** File content never changes; new uploads create new document records

**Frontend Dependencies:**
- Flutter: Document upload, section tagging, status view
- React: Document review, status updates, request missing docs

---

## 2.6 Payment (Transaction Record)

**Responsibility:** Append-only ledger of payments received

**Access Rules:**
- Create: Admin only
- Read: Admin (all), Superadmin (all)
- Update: Never (corrections done via new records)
- Delete: Never (audit requirement)

**Mutability:**
- Mutable: None (append-only)
- Immutable: All fields
- System-managed: `recorded_at`

**Frontend Dependencies:**
- React: Payment recording, payment history, revenue analytics

**Design Note:** Payments trigger Filing.paid_amount recalculation and email notification

---

## 2.7 Notification (In-App Alert)

**Responsibility:** Simple notification that directs user to check email

**Access Rules:**
- Create: System only (triggered by admin actions)
- Read: Client (own notifications)
- Update: Client (mark as read only)
- Delete: Never

**Mutability:**
- Mutable: `is_read`
- Immutable: All other fields
- System-managed: `created_at`

**Frontend Dependencies:**
- Flutter: Notification list, unread count, mark as read

**Design Note:** Notifications are NOT detailed messages. They say "Check your email for [action]."

---

## 2.8 Analytics (Derived Data)

**Responsibility:** Aggregated statistics for admin dashboard

**Access Rules:**
- Create: N/A (calculated on demand)
- Read: Admin (based on permissions), Superadmin (all)
- Update: N/A
- Delete: N/A

**Mutability:**
- N/A (not stored, calculated from other resources)

**Frontend Dependencies:**
- React: Dashboard charts, statistics, revenue tracking, workload distribution

**Data Sources:** Aggregations from Filing, Payment, Document, Admin

---

## 2.9 AuditLog (Compliance Trail)

**Responsibility:** Immutable record of all system changes for compliance

**Access Rules:**
- Create: System only (automatic)
- Read: Superadmin only
- Update: Never
- Delete: Never

**Mutability:**
- Mutable: None
- Immutable: All fields
- System-managed: All fields

**Frontend Dependencies:**
- React: Audit log viewer (superadmin only)

**Audit Triggers:** User changes, Filing status changes, Document uploads, Payment recording, Admin actions

---

# 3. REMOVED / CONSOLIDATED RESOURCES

## 3.1 Resources Removed from Old System

| Old Resource | Reason for Removal | Replacement |
|--------------|-------------------|-------------|
| **Chat / ChatMessage** | Email-first model | Email + Notification |
| **Client** (separate from Filing) | Confusion between User and Client | Filing (one per year) |
| **TaxReturn + T1ReturnFlat** | Duplicate tables | Single T1Form resource |
| **TaxSection** | Over-engineered | JSONB in T1Form |
| **CostEstimate** | Not a separate entity | Part of Filing workflow |
| **Note** | Not needed | Email thread + AuditLog |
| **RefreshToken** | Stateless JWT preferred | Token refresh via endpoint |
| **OTP** | Not persisted | In-memory with TTL |
| **AdminClientMap** | Junction table | Direct FK on Filing |

---

# 4. ACCESS PATTERN ANALYSIS

## 4.1 Client (Flutter) Access Patterns

| Resource | Operations | Frequency | Notes |
|----------|-----------|-----------|-------|
| User | GET (profile), PATCH (profile) | Low | Once per session |
| Filing | GET (own status) | Medium | Manual refresh |
| T1Form | POST/PATCH (form data), GET | High | Auto-save every 2 min |
| Document | POST (upload), GET (list) | Medium | Per section upload |
| Notification | GET (list), PATCH (mark read) | Medium | On app open |

**Key Pattern:** Client NEVER creates Filing directly. Filing is created automatically when T1Form is first saved.

## 4.2 Admin (React) Access Patterns

| Resource | Operations | Frequency | Notes |
|----------|-----------|-----------|-------|
| Admin | GET (self), GET (list), POST, PATCH | Low | User management |
| Filing | GET (list), GET (detail), PATCH (status/assignment) | High | Main workflow |
| T1Form | GET (read-only) | Medium | Review submissions |
| Document | GET (list), PATCH (status), POST (request) | High | Document review |
| Payment | POST (record), GET (list) | Medium | Payment recording |
| Analytics | GET | Medium | Dashboard load |
| AuditLog | GET (list) | Low | Superadmin only |

**Key Pattern:** Admin actions trigger emails and notifications automatically.

---

# 5. DERIVED vs STORED DATA

## 5.1 Derived Data (Calculated, Not Stored)

| Data | Calculation Source | When Calculated |
|------|-------------------|-----------------|
| `Filing.paid_amount` | SUM(Payment.amount WHERE filing_id = X) | On read |
| `Filing.payment_status` | Based on paid_amount vs total_fee | On read |
| `User.full_name` | first_name + ' ' + last_name | On read |
| Analytics totals | Aggregation queries | On demand |
| Notification unread count | COUNT WHERE is_read = false | On read |

## 5.2 Stored Data (Persisted)

| Data | Why Stored |
|------|-----------|
| User credentials | Authentication |
| Filing metadata | Workflow state |
| T1Form.form_data | Legal document |
| Document metadata | File tracking |
| Payment records | Financial audit |
| AuditLog entries | Compliance |

---

# 6. RESOURCE RELATIONSHIP MATRIX

```
User (1) ──────▶ Filing (N)
                    │
                    ├──────▶ T1Form (1)
                    │
                    ├──────▶ Document (N)
                    │
                    ├──────▶ Payment (N)
                    │
                    └──────▶ Notification (N)

Admin (1) ────────▶ Filing (N)  [assigned_admin_id]
      │
      └───────────▶ Payment (N)  [recorded_by_id]

AuditLog ─────────▶ All entities [polymorphic]
```

**Key Relationships:**
- User : Filing = 1 : Many (one per year)
- Filing : T1Form = 1 : 1 (one form per filing)
- Filing : Document = 1 : Many
- Filing : Payment = 1 : Many
- Admin : Filing = 1 : Many (assignment)

---

# 7. RESOURCE OWNERSHIP RULES

## 7.1 Client Ownership

| Resource | Can Create | Can Read | Can Update | Can Delete |
|----------|-----------|----------|------------|-----------|
| User | Self (registration) | Self | Self (profile) | Never |
| Filing | System (auto) | Self | Never | Never |
| T1Form | Self | Self | Self (draft) | Never |
| Document | Self | Self | Never | Never |
| Payment | Never | Never | Never | Never |
| Notification | Never | Self | Self (mark read) | Never |

**Client Cannot:**
- Create Filing directly
- Update Filing status
- Delete anything
- Access other clients' data

## 7.2 Admin Ownership

| Resource | Can Create | Can Read | Can Update | Can Delete |
|----------|-----------|----------|------------|-----------|
| User | Never | List only | Activation only | Never |
| Admin | Superadmin | Self + Superadmin | Self/Superadmin | Superadmin |
| Filing | System | Assigned/All | Status/Assignment | Superadmin |
| T1Form | Never | Assigned clients | Status only | Never |
| Document | Request missing | Assigned clients | Status/Notes | Soft delete |
| Payment | Yes | All | Never | Never |
| Notification | Never (system) | Never | Never | Never |
| Analytics | Never | Based on permissions | Never | Never |
| AuditLog | Never (system) | Superadmin | Never | Never |

**Admin Cannot:**
- Create or modify User accounts
- Edit T1Form.form_data
- Delete payments
- Modify audit logs

---

# 8. RESOURCE NAMING CONVENTIONS

## 8.1 Naming Rules

| Rule | Rationale |
|------|-----------|
| Use **plural nouns** | `/filings`, `/documents` (standard REST) |
| Use **kebab-case** for multi-word | `/audit-logs`, `/t1-forms` |
| No verbs in resource names | `/filings/{id}/submit` → `/filings/{id}` with status change |
| No redundant nesting | `/filings/{id}/documents` not `/users/{id}/filings/{id}/documents` |
| Use query params for filters | `/filings?year=2024&status=submitted` |

## 8.2 Resource Naming Table

| Resource | URL Segment | Notes |
|----------|-------------|-------|
| User | `/users` | Client accounts |
| Admin | `/admins` | Staff accounts |
| Filing | `/filings` | Tax engagements |
| T1Form | `/t1-forms` | Tax form data |
| Document | `/documents` | File uploads |
| Payment | `/payments` | Transaction records |
| Notification | `/notifications` | In-app alerts |
| Analytics | `/analytics` | Aggregated stats |
| AuditLog | `/audit-logs` | Compliance trail |

---

# 9. SPECIAL RESOURCE CONSIDERATIONS

## 9.1 Authentication Pseudo-Resources

Not stored as resources, but need endpoints:

| Pseudo-Resource | Purpose | Endpoints Needed |
|----------------|---------|------------------|
| **Session** | JWT lifecycle | login, logout, refresh |
| **OTP** | Email verification | request, verify |
| **Password** | Password management | reset-request, reset-confirm |

These are **actions**, not resources, so they get special endpoint treatment.

## 9.2 Bulk Operations

Some endpoints need bulk operations:

| Operation | Resource | Use Case |
|-----------|----------|----------|
| Bulk status update | Document | Approve multiple docs at once |
| Batch notification | Notification | System-generated alerts |

---

# 10. FRONTEND COMPATIBILITY CHECK

## 10.1 Flutter Client Requirements

| Frontend Need | Resource | Compatible? |
|--------------|----------|-------------|
| User registration | User | ✅ Yes |
| Login | User (session) | ✅ Yes |
| OTP verification | OTP | ✅ Yes |
| Profile management | User | ✅ Yes |
| T1 form editor | T1Form | ✅ Yes |
| Document upload | Document | ✅ Yes |
| Filing status | Filing | ✅ Yes |
| Notifications | Notification | ✅ Yes |
| Chat | ~~ChatMessage~~ | ⚠️ Removed (email-first) |

**Chat Removal:** Chat endpoints will return `501 Not Implemented` with message directing to email.

## 10.2 React Admin Requirements

| Frontend Need | Resource | Compatible? |
|--------------|----------|-------------|
| Admin login | Admin (session) | ✅ Yes |
| Client list | Filing | ✅ Yes |
| Client detail | Filing + T1Form | ✅ Yes |
| Document review | Document | ✅ Yes |
| Payment recording | Payment | ✅ Yes |
| Analytics dashboard | Analytics | ✅ Yes |
| Admin user management | Admin | ✅ Yes |
| Audit logs | AuditLog | ✅ Yes |
| Chat | ~~ChatMessage~~ | ⚠️ Removed (email-first) |

---

# 11. RESOURCE LIFECYCLE SUMMARY

## 11.1 Lifecycle Stages

| Resource | Creation | Active Use | Archival/Deletion |
|----------|----------|------------|-------------------|
| User | Registration | Login, profile edits | Soft delete (deactivate) |
| Admin | Superadmin creates | Daily operations | Soft delete |
| Filing | T1Form auto-creates | Status workflow | Archived after completion |
| T1Form | Client starts form | Edits until submit | Locked after submission |
| Document | Client uploads | Review cycle | Archived with filing |
| Payment | Admin records | Immutable | Never deleted |
| Notification | System creates | Read once | Never deleted |
| AuditLog | System creates | Compliance queries | Never deleted |

---

# PHASE 1 COMPLETE — RESOURCE IDENTIFICATION

## Summary

**Total Resources:** 9 primary + 3 pseudo-resources (Session, OTP, Password)

**Removed Resources:** 9 legacy resources consolidated or eliminated

**Key Decisions:**
1. Email-first model (no Chat resource)
2. Filing is central resource (not Client)
3. Single T1Form resource (no duplication)
4. Payment is append-only
5. Notification is simple (points to email)
6. Analytics is derived (not stored)
7. AuditLog is append-only

**Frontend Compatibility:** ✅ 100% (except chat → email redirect)

---

**Reply "PROCEED TO PHASE 2" to continue with endpoint design.**
