# T1 Personal Tax Form API Documentation

## Overview

This document provides comprehensive documentation for all T1 Personal Tax Form endpoints in the Tax-Ease Backend API v2. The T1 form system enables users to:

- Save draft answers progressively
- Submit complete tax forms
- Track completion percentage
- Get dynamic document requirements
- Communicate with admins via email threads

**Base URL:** `http://localhost:8000`

**Authentication:** All endpoints require JWT Bearer token (except structure endpoint which is public)

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Endpoints](#user-endpoints)
   - [Get T1 Form Structure](#get-t1-form-structure)
   - [Save Draft Answers](#save-draft-answers)
   - [Fetch Draft](#fetch-draft)
   - [Submit T1 Form](#submit-t1-form)
   - [Get Required Documents](#get-required-documents)
3. [Admin Endpoints](#admin-endpoints)
   - [View Full T1 Form](#view-full-t1-form)
   - [Unlock T1 for Corrections](#unlock-t1-for-corrections)
   - [Request Additional Documents](#request-additional-documents)
   - [Mark Section Reviewed](#mark-section-reviewed)
   - [Get Audit Trail](#get-audit-trail)
   - [Dashboard Overview](#dashboard-overview)
   - [Detailed T1 View](#detailed-t1-view)
4. [Data Models](#data-models)
5. [Testing Guide](#testing-guide)
6. [Error Handling](#error-handling)

---

## Authentication

### Register User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass@123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+14161234567"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": false
  }
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass@123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Note:** After registration, email verification is required before accessing T1 endpoints.

---

### Email Verification (OTP)

#### Request OTP

Send a 6-digit OTP code to user's email for verification.

```http
POST /api/v1/auth/otp/request
Content-Type: application/json

{
  "email": "user@example.com",
  "purpose": "email_verification"
}
```

**Purpose Options:**
- `email_verification` - Verify email after registration
- `password_reset` - Reset forgotten password

**Response (200 OK):**
```json
{
  "message": "OTP sent successfully to your email",
  "expires_in": 600
}
```

**Note:** OTP is valid for 10 minutes. Check server logs for OTP code in development (no email service configured).

#### Verify OTP

Verify the 6-digit OTP code received via email.

```http
POST /api/v1/auth/otp/verify
Content-Type: application/json

{
  "email": "user@example.com",
  "code": "123456",
  "purpose": "email_verification"
}
```

**Request Fields:**
- `email` (string, required): User's email address
- `code` (string, required): 6-digit OTP code (must be exactly 6 characters)
- `purpose` (string, required): Must be either `email_verification` or `password_reset`

**Response (200 OK):**
```json
{
  "message": "OTP verified successfully"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "OTP_INVALID",
    "message": "Invalid or expired OTP code"
  }
}
```

**Error Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "purpose"],
      "msg": "string does not match regex \"^(email_verification|password_reset)$\"",
      "type": "value_error.str.regex"
    }
  ]
}
```

---

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass@123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "email_verified": true
  }
}
```

**Note:** Email verification must be completed before accessing T1 endpoints.

### Create Filing

Before working with T1 forms, create a filing:

```http
POST /api/v1/filings
Authorization: Bearer <token>
Content-Type: application/json

{
  "tax_year": 2024,
  "filing_type": "personal"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "tax_year": 2024,
  "filing_type": "personal",
  "status": "documents_pending",
  "created_at": "2026-01-06T10:00:00Z"
}
```

---

## User Endpoints

### Get T1 Form Structure

**GET** `/api/v1/t1-forms/structure`

Returns the complete T1 form structure from `T1Structure.json` for frontend rendering.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "formType": "T1",
  "formName": "T1 Personal Tax Form",
  "generatedAtUtc": "2025-12-20T08:04:32Z",
  "steps": [
    {
      "id": "personal_info",
      "title": "Personal Information",
      "sections": [
        {
          "id": "individual_information",
          "title": "Individual Information",
          "fields": [
            {
              "key": "personalInfo.firstName",
              "label": "First Name",
              "type": "text",
              "required": true
            },
            ...
          ]
        }
      ]
    },
    {
      "id": "questionnaire",
      "title": "Questionnaire",
      "questions": [...]
    }
  ],
  "documentRequirements": [...]
}
```

**Use Case:** Frontend loads this structure once at startup to render the T1 form dynamically.

---

### Save Draft Answers

**POST** `/api/v1/t1-forms/{filing_id}/answers`

Save partial or complete T1 form answers. Idempotent - can be called multiple times with partial data.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `filing_id` (UUID): Filing ID created earlier

**Request Body:**
```json
{
  "answers": {
    "personalInfo.firstName": "John",
    "personalInfo.lastName": "Taxpayer",
    "personalInfo.sin": "123456789",
    "personalInfo.dateOfBirth": "1990-01-15",
    "personalInfo.address": "123 Main St, Toronto, ON M5V 2T6",
    "personalInfo.phoneNumber": "+14161234567",
    "personalInfo.email": "user@example.com",
    "personalInfo.isCanadianCitizen": true,
    "personalInfo.maritalStatus": "single",
    "hasForeignProperty": false,
    "hasMedicalExpenses": true,
    "selfEmployment.businessTypes": ["uber", "general"]
  }
}
```

**Field Value Types:**
- **Boolean fields:** `true` or `false`
- **Text fields:** `"string value"`
- **Number fields:** `123.45` or `"123.45"`
- **Date fields:** `"YYYY-MM-DD"` format
- **Select fields:** Must match one of the options from structure
- **Array fields:** `["value1", "value2"]` for repeatable sections

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Draft saved successfully",
  "t1_form_id": "uuid",
  "filing_id": "uuid",
  "status": "draft",
  "is_locked": false,
  "completion_percentage": 65,
  "answers": {
    "personalInfo.firstName": "John",
    "personalInfo.lastName": "Taxpayer",
    ...
  },
  "validation_errors": []
}
```

**Validation:**
- **Draft validation:** Type checking only (lenient)
- **Not checked:** Required fields, completeness
- **Immutability:** Cannot modify after submission (is_locked=true)

**Error Response (400 Bad Request):**
```json
{
  "detail": "Validation failed",
  "validation_errors": [
    "Field 'personalInfo.email': Invalid email format",
    "Field 'personalInfo.maritalStatus': invalid option 'divorced'. Must be one of ['single', 'married', 'common-law', 'separated', 'divorced', 'widowed']"
  ]
}
```

---

### Fetch Draft

**GET** `/api/v1/t1-forms/{filing_id}`

Fetch the current T1 form draft with all saved answers.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `filing_id` (UUID): Filing ID

**Response (200 OK):**
```json
{
  "t1_form_id": "uuid",
  "filing_id": "uuid",
  "status": "draft",
  "is_locked": false,
  "completion_percentage": 65,
  "submitted_at": null,
  "created_at": "2026-01-06T10:00:00Z",
  "updated_at": "2026-01-06T11:30:00Z",
  "answers": {
    "personalInfo.firstName": "John",
    "personalInfo.lastName": "Taxpayer",
    "personalInfo.sin": "123456789",
    ...
  }
}
```

**Use Case:** Load saved draft when user returns to form, auto-save recovery.

---

### Submit T1 Form

**POST** `/api/v1/t1-forms/{filing_id}/submit`

Submit the T1 form for admin review. This is a **one-way operation** - form becomes immutable after submission.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `filing_id` (UUID): Filing ID

**Request Body:** (empty)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "T1 form submitted successfully",
  "t1_form_id": "uuid",
  "filing_id": "uuid",
  "status": "submitted",
  "is_locked": true,
  "completion_percentage": 100,
  "submitted_at": "2026-01-06T12:00:00Z",
  "answers": {...}
}
```

**Validation:**
- **All required fields** must be filled
- **All conditional sections** must be complete (if triggered)
- **Type validation** must pass
- **Form must not be already locked**

**Error Response (400 Bad Request):**
```json
{
  "detail": "Form validation failed",
  "validation_errors": [
    "Required field missing: 'First Name' (personalInfo.firstName)",
    "Required field missing: 'Last Name' (personalInfo.lastName)",
    "Conditional field missing: 'Spouse First Name' (personalInfo.spouseInfo.firstName) - required because maritalStatus='married'"
  ]
}
```

**Error Response (409 Conflict):**
```json
{
  "detail": "T1 form is already locked and cannot be modified"
}
```

---

### Get Required Documents

**GET** `/api/v1/t1-forms/{filing_id}/required-documents`

Get dynamically computed list of required documents based on user answers.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `filing_id` (UUID): Filing ID

**Response (200 OK):**
```json
{
  "filing_id": "uuid",
  "required_documents": [
    {
      "label": "T2202 Form",
      "reason": "Required because 'wasStudentLastYear' is answered Yes",
      "question_key": "wasStudentLastYear"
    },
    {
      "label": "Day Care Expense Receipts",
      "reason": "Required because 'hasDaycareExpenses' is answered Yes",
      "question_key": "hasDaycareExpenses"
    },
    {
      "label": "RRSP/FHSA T-slips",
      "reason": "Required because 'hasRrspFhsaInvestment' is answered Yes",
      "question_key": "hasRrspFhsaInvestment"
    }
  ]
}
```

**Use Case:** Show document checklist to user before submission.

---

## Admin Endpoints

All admin endpoints require `role: admin` or `role: superadmin` in JWT token.

### View Full T1 Form

**GET** `/api/v1/admin/t1-forms/{t1_form_id}`

View complete T1 form organized by steps and sections.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `t1_form_id` (UUID): T1 Form ID

**Response (200 OK):**
```json
{
  "t1_form_id": "uuid",
  "filing_id": "uuid",
  "user_info": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Taxpayer"
  },
  "status": "submitted",
  "is_locked": true,
  "completion_percentage": 100,
  "submitted_at": "2026-01-06T12:00:00Z",
  "sections": [
    {
      "step_id": "personal_info",
      "step_title": "Personal Information",
      "sections": [
        {
          "section_id": "individual_information",
          "section_title": "Individual Information",
          "answers": [
            {
              "field_key": "personalInfo.firstName",
              "field_label": "First Name",
              "value": "John"
            },
            ...
          ]
        }
      ]
    }
  ],
  "created_at": "2026-01-06T10:00:00Z",
  "updated_at": "2026-01-06T12:00:00Z"
}
```

---

### Unlock T1 for Corrections

**POST** `/api/v1/admin/t1-forms/{t1_form_id}/unlock`

Unlock a submitted T1 form to allow user corrections. Creates audit log entry.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `t1_form_id` (UUID): T1 Form ID

**Request Body:**
```json
{
  "reason": "Incorrect SIN number - needs correction"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "T1 form unlocked successfully",
  "t1_form_id": "uuid",
  "status": "draft",
  "is_locked": false,
  "unlocked_by": "admin_uuid",
  "unlock_reason": "Incorrect SIN number - needs correction"
}
```

---

### Request Additional Documents

**POST** `/api/v1/admin/t1-forms/{t1_form_id}/request-documents`

Request additional documents from user via email thread.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `t1_form_id` (UUID): T1 Form ID

**Request Body:**
```json
{
  "document_names": [
    "T4 slips for all employers",
    "Property tax statement",
    "RRSP contribution receipt"
  ],
  "message": "Please upload the following documents to complete your tax return."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Document request sent",
  "email_thread_id": "uuid",
  "documents_requested": 3
}
```

---

### Mark Section Reviewed

**POST** `/api/v1/admin/t1-forms/{t1_form_id}/sections/{step_id}/{section_id}/review`

Mark a specific section as reviewed.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `t1_form_id` (UUID): T1 Form ID
- `step_id` (string): Step ID (e.g., "personal_info")
- `section_id` (string): Section ID (e.g., "individual_information")

**Request Body:**
```json
{
  "review_notes": "All information verified against supporting documents"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Section marked as reviewed",
  "section_id": "individual_information",
  "is_reviewed": true,
  "reviewed_by": "admin_uuid",
  "reviewed_at": "2026-01-06T14:00:00Z"
}
```

---

### Get Audit Trail

**GET** `/api/v1/admin/t1-forms/{t1_form_id}/audit`

Get complete audit trail of all actions on T1 form.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `t1_form_id` (UUID): T1 Form ID

**Response (200 OK):**
```json
{
  "t1_form_id": "uuid",
  "audit_trail": [
    {
      "timestamp": "2026-01-06T10:00:00Z",
      "action": "created",
      "actor": "user_uuid",
      "actor_name": "John Taxpayer",
      "details": "T1 form created"
    },
    {
      "timestamp": "2026-01-06T12:00:00Z",
      "action": "submitted",
      "actor": "user_uuid",
      "actor_name": "John Taxpayer",
      "details": "Form submitted for review"
    },
    {
      "timestamp": "2026-01-06T14:00:00Z",
      "action": "reviewed",
      "actor": "admin_uuid",
      "actor_name": "Admin Smith",
      "details": "Section 'personal_info' reviewed"
    }
  ]
}
```

---

### Dashboard Overview

**GET** `/api/v1/admin/dashboard/t1-filings`

Get overview of all T1 filings with counts and filters.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `status` (optional): Filter by status (draft/submitted/under_review)
- `tax_year` (optional): Filter by tax year
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50)

**Response (200 OK):**
```json
{
  "total": 245,
  "status_counts": {
    "draft": 89,
    "submitted": 120,
    "under_review": 36
  },
  "filings": [
    {
      "t1_form_id": "uuid",
      "filing_id": "uuid",
      "user_email": "user@example.com",
      "user_name": "John Taxpayer",
      "tax_year": 2024,
      "status": "submitted",
      "completion_percentage": 100,
      "submitted_at": "2026-01-06T12:00:00Z",
      "days_pending": 2
    },
    ...
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_pages": 5
  }
}
```

---

### Detailed T1 View

**GET** `/api/v1/admin/t1-forms/{t1_form_id}/detailed`

Get detailed T1 view with UI rendering hints for admin dashboard.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `t1_form_id` (UUID): T1 Form ID

**Response (200 OK):**
```json
{
  "t1_form_id": "uuid",
  "filing_info": {...},
  "user_info": {...},
  "form_status": "submitted",
  "sections": [...],
  "required_documents": [...],
  "email_threads": [...],
  "review_progress": {
    "total_sections": 15,
    "reviewed_sections": 10,
    "percentage": 67
  }
}
```

---

## Data Models

### T1 Form Status States

```
draft → submitted → under_review → approved/rejected
```

- **draft**: User is filling the form
- **submitted**: User submitted, waiting for admin review
- **under_review**: Admin actively reviewing
- **approved**: Tax return approved
- **rejected**: Rejected with feedback

### Field Key Naming Convention

Field keys follow dot notation matching T1Structure.json:

- `personalInfo.firstName`
- `personalInfo.spouseInfo.lastName`
- `selfEmployment.uberBusiness.income`
- `hasMedicalExpenses` (questionnaire boolean)

### Polymorphic Value Storage

Answers are stored in normalized table with 5 value columns:
- `value_boolean`: For true/false fields
- `value_text`: For text/email/phone/select fields
- `value_numeric`: For number fields
- `value_date`: For date fields (YYYY-MM-DD)
- `value_array`: For repeatable sections (JSONB)

---

## Testing Guide

### Using cURL

#### 1. Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1234567890"
  }'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

#### 2. Create Filing
```bash
FILING_ID=$(curl -X POST http://localhost:8000/api/v1/filings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tax_year": 2024,
    "filing_type": "personal"
  }' | jq -r '.id')

echo "Filing ID: $FILING_ID"
```

#### 3. Save Draft
```bash
curl -X POST "http://localhost:8000/api/v1/t1-forms/$FILING_ID/answers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "personalInfo.firstName": "John",
      "personalInfo.lastName": "Taxpayer",
      "personalInfo.sin": "123456789"
    }
  }' | jq '.'
```

#### 4. Fetch Draft
```bash
curl -X GET "http://localhost:8000/api/v1/t1-forms/$FILING_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### Using Python Test Script

Run the included test script:

```bash
cd /home/cyberdude/Documents/Projects/CA-final
python backend/test_t1_endpoints.py
```

This tests all endpoints sequentially with colored output.

### Using Swagger UI

Open your browser to:
```
http://localhost:8000/docs
```

Interactive API documentation with try-it-now functionality.

---

## Error Handling

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Validation failed, malformed request
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions (not admin)
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource state conflict (e.g., form already locked)
- **422 Unprocessable Entity**: Semantic validation failed
- **500 Internal Server Error**: Server error (check logs)

### Common Error Responses

**Email Not Verified:**
```json
{
  "detail": "Email verification required. Please verify your email before accessing this endpoint."
}
```

**Form Already Locked:**
```json
{
  "detail": "T1 form is already locked and cannot be modified"
}
```

**Invalid Field Type:**
```json
{
  "detail": "Validation failed",
  "validation_errors": [
    "Field 'personalInfo.sin': Expected number, got str"
  ]
}
```

**Admin Access Required:**
```json
{
  "detail": "Admin access required"
}
```

---

## Performance Notes

- **Draft saves**: ~200ms (idempotent, can be called frequently)
- **Submission**: ~500ms (includes full validation)
- **Structure fetch**: ~50ms (can be cached by frontend)
- **Admin views**: ~300ms (joins multiple tables)

---

## Security

- **Authentication**: JWT Bearer tokens with 60-minute expiration
- **Rate Limiting**: 100 requests per minute per IP
- **Email Verification**: Required before T1 form access
- **Immutability**: Submitted forms cannot be modified without admin unlock
- **Audit Logging**: All admin actions logged with timestamps and reasons
- **Database Triggers**: Prevent modification of locked forms at DB level

---

## Support

For issues or questions:
- **API Logs**: `/tmp/taxease-api.log`
- **Health Check**: `GET /health`
- **OpenAPI Spec**: `GET /openapi.json`
- **Swagger UI**: `http://localhost:8000/docs`

---

## Changelog

### v2.0.0 (2026-01-06)
- Complete database redesign with normalized schema
- T1ValidationEngine implementation (dynamic validation)
- All 13 endpoints tested and documented
- Immutability guarantees at DB and application level
- Email threading for admin-user communication
- Comprehensive audit logging

---

**End of Documentation**
