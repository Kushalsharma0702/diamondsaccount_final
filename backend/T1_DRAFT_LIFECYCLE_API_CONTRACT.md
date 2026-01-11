# T1 Draft Lifecycle - API Contract

## Overview

This document defines the **exact API contract** between the Flutter frontend and the backend for the T1 form draft lifecycle.

**Key Principles:**
1. ✅ NO auto-creation of filings or T1 forms
2. ✅ User explicitly creates filing via POST /filings  
3. ✅ First POST to /t1-forms/{filing_id}/answers **implicitly creates** T1 form
4. ✅ Frontend never calls POST /t1-forms/create
5. ✅ All endpoints use `filing_id` (not t1_form_id)

---

## Authentication

All endpoints (except `/t1-forms/structure`) require:

```http
Authorization: Bearer <access_token>
```

Access token obtained from:
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh

---

## Endpoint 1: Get Current User Profile

**Purpose:** Get authenticated user's details, including `user_id` for other API calls.

### Request

```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
Accept: application/json
```

### Response (200 OK)

```json
{
  "id": "1c53efcb-3651-483d-8e09-b178806c9044",
  "email": "john@example.com",
  "phone": "911234567890",
  "first_name": "John",
  "last_name": "Doe",
  "email_verified": true,
  "phone_verified": true,
  "created_at": "2026-01-10T10:00:00Z"
}
```

**Frontend Usage:**
- Store `id` as `user_id` for subsequent calls
- Use for `GET /api/v1/t1-forms/user/{user_id}/forms`

---

## Endpoint 2: List User's T1 Forms

**Purpose:** Get all T1 forms (drafts + submitted) for the authenticated user.

### Request

```http
GET /api/v1/t1-forms/user/{user_id}/forms
Authorization: Bearer <access_token>
Accept: application/json
```

**Path Parameters:**
- `user_id` (string, UUID): User ID from `/users/me`

### Response (200 OK)

```json
{
  "user_id": "1c53efcb-3651-483d-8e09-b178806c9044",
  "total_forms": 2,
  "forms": [
    {
      "id": "a1b2c3d4-...",
      "filing_id": "972ce307-....",
      "filing_year": 2026,
      "status": "draft",
      "is_locked": false,
      "completion_percentage": 45,
      "submitted_at": null,
      "created_at": "2026-01-10T10:00:00Z",
      "updated_at": "2026-01-10T10:30:00Z"
    },
    {
      "id": "e5f6g7h8-...",
      "filing_id": "abc12345-....",
      "filing_year": 2025,
      "status": "submitted",
      "is_locked": true,
      "completion_percentage": 100,
      "submitted_at": "2025-12-20T14:00:00Z",
      "created_at": "2025-12-15T09:00:00Z",
      "updated_at": "2025-12-20T14:00:00Z"
    }
  ]
}
```

**Response Fields:**
- `user_id`: UUID of the user
- `total_forms`: Number of forms returned
- `forms[]`: Array of form summaries
  - `id`: T1 form UUID (internal)
  - `filing_id`: ⭐ **Primary identifier** used in all other endpoints
  - `filing_year`: Tax year (e.g., 2026)
  - `status`: `"draft"` | `"submitted"` | `"documents_pending"` | `"completed"`
  - `is_locked`: Boolean (true if submitted)
  - `completion_percentage`: 0-100 integer
  - `submitted_at`: ISO 8601 timestamp or null
  - `created_at`: ISO 8601 timestamp
  - `updated_at`: ISO 8601 timestamp

**Error Responses:**

```json
// 403 Forbidden - Trying to access another user's forms
{
  "detail": "Access denied: Cannot access other users' forms"
}
```

---

## Endpoint 3: Create New Filing

**Purpose:** User explicitly creates a new tax filing. This is the **starting point** for a new T1 form.

### Request

```http
POST /api/v1/filings
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json

{
  "filing_year": 2026
}
```

**Request Body:**
- `filing_year` (integer, required): Tax year (2020-2030)

### Response (201 Created)

```json
{
  "id": "972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b",
  "user_id": "1c53efcb-3651-483d-8e09-b178806c9044",
  "filing_year": 2026,
  "status": "draft",
  "total_fee": 0.0,
  "paid_amount": 0.0,
  "payment_status": "pending",
  "email_thread_id": null,
  "created_at": "2026-01-10T10:00:00Z",
  "updated_at": "2026-01-10T10:00:00Z",
  "assigned_admin": null
}
```

**Response Fields:**
- `id`: ⭐ **This is the filing_id** used in all T1 form endpoints
- `user_id`: Owner of the filing
- `filing_year`: Confirmed tax year
- `status`: Filing status (initially `"draft"`)
- Other fields: Payment and admin assignment (not relevant for T1 form)

**Frontend Workflow After Create:**
1. Extract `filing_id = response.id`
2. Create local T1FormData object with:
   - `id = filing_id`
   - `status = "draft"`
   - `answers = {}`
3. Navigate to T1 form screen with route parameter `formId = filing_id`
4. **NO additional backend call to create T1 form**

**Error Responses:**

```json
// 403 Forbidden - Email not verified
{
  "detail": "Email verification required. Please verify your email before creating a filing."
}
```

---

## Endpoint 4: Save Draft Answers (Auto-Create T1 Form)

**Purpose:** Save user's answers to T1 form. **First call implicitly creates the T1 form record.**

### Request

```http
POST /api/v1/t1-forms/{filing_id}/answers
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json

{
  "answers": {
    "personalInfo.firstName": "John",
    "personalInfo.lastName": "Doe",
    "personalInfo.sin": "123456789",
    "personalInfo.dateOfBirth": "1990-03-15",
    "personalInfo.phoneNumber": "911234567890",
    "personalInfo.email": "john@example.com",
    "questionnaire.hasForeignProperty": true,
    "questionnaire.foreignPropertyDetails": "Rental property in USA",
    "income.employmentIncome": 75000.00,
    "children[0].firstName": "Emma",
    "children[0].dateOfBirth": "2015-06-20",
    "children[0].hasDisability": false
  }
}
```

**Path Parameters:**
- `filing_id` (string, UUID): Filing ID from POST /filings

**Request Body:**
- `answers` (object, required): Flat key-value map of form fields

**Key Format:**
- Dot notation: `personalInfo.firstName`
- Array indexing: `children[0].firstName`, `children[1].dateOfBirth`
- Matches T1Structure.json field paths

**Value Types & Formats:**

| Type | Format | Example |
|------|--------|---------|
| **String** | Plain text | `"John"` |
| **Number** | Numeric (int/float) | `75000.00` |
| **Boolean** | `true` / `false` | `true` |
| **Date** | `yyyy-MM-dd` (no time) | `"1990-03-15"` |
| **Phone** | Digits only (no `+`) | `"911234567890"` (UI shows `+911234567890`) |
| **SIN** | 9 digits only | `"123456789"` (UI shows `123-456-789`) |

**Frontend Normalization:**
- **Dates**: Convert all date inputs to `yyyy-MM-dd` string before sending
- **Phone**: Strip all non-digits (remove `+`, spaces, hyphens)
- **SIN**: Strip all non-digits (remove spaces, hyphens)

### Response (200 OK)

```json
{
  "success": true,
  "message": "Draft saved successfully",
  "completion_percentage": 45,
  "fields_saved": 12
}
```

**Response Fields:**
- `success`: Always `true` on success
- `message`: Human-readable message
- `completion_percentage`: Updated percentage (0-100)
- `fields_saved`: Number of fields saved in this call

### Behavior

**First Call (T1 Form Doesn't Exist):**
1. Backend creates new T1Form record with `filing_id`
2. Saves all answers to T1Answer table
3. Calculates completion percentage
4. Returns success response

**Subsequent Calls (T1 Form Exists):**
1. Updates existing T1Form record
2. Upserts answers (creates new or updates existing)
3. Recalculates completion percentage
4. Returns success response

**Idempotent:** Safe to call multiple times with same or different data.

**Validation:** Partial validation only (draft mode):
- Required fields NOT enforced
- Format validation applied (e.g., SIN must be 9 digits)
- Type validation applied (e.g., date must be valid date)

**Error Responses:**

```json
// 400 Bad Request - Validation failed
{
  "detail": {
    "message": "Validation failed",
    "errors": {
      "personalInfo.sin": "SIN must be exactly 9 digits",
      "personalInfo.dateOfBirth": "Invalid date format. Use yyyy-MM-dd"
    }
  }
}

// 403 Forbidden - Form already submitted
{
  "detail": "Cannot modify submitted T1 form. Contact admin to request unlock."
}

// 404 Not Found - Filing doesn't exist
{
  "detail": "Filing 972ce307-.... not found or access denied"
}
```

---

## Endpoint 5: Get T1 Form Draft

**Purpose:** Fetch T1 form with all saved answers.

### Request

```http
GET /api/v1/t1-forms/{filing_id}
Authorization: Bearer <access_token>
Accept: application/json
```

**Path Parameters:**
- `filing_id` (string, UUID): Filing ID

### Response (200 OK) - With Saved Answers

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filing_id": "972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b",
  "form_version": "2024",
  "status": "draft",
  "is_locked": false,
  "completion_percentage": 45,
  "submitted_at": null,
  "answers": {
    "personalInfo.firstName": "John",
    "personalInfo.lastName": "Doe",
    "personalInfo.sin": "123456789",
    "personalInfo.dateOfBirth": "1990-03-15",
    "personalInfo.phoneNumber": "911234567890",
    "personalInfo.email": "john@example.com",
    "questionnaire.hasForeignProperty": true,
    "income.employmentIncome": 75000.00
  },
  "created_at": "2026-01-10T10:00:00Z",
  "updated_at": "2026-01-10T10:30:00Z"
}
```

### Response (200 OK) - No Answers Yet (Virtual Draft)

If T1 form doesn't exist (user created filing but hasn't saved any answers):

```json
{
  "id": "972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b",
  "filing_id": "972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b",
  "form_version": "2024",
  "status": "draft",
  "is_locked": false,
  "completion_percentage": 0,
  "submitted_at": null,
  "answers": {},
  "created_at": "2026-01-10T10:00:00Z",
  "updated_at": "2026-01-10T10:00:00Z"
}
```

**Response Fields:**
- `id`: T1 form UUID (same as filing_id if no T1 form created yet)
- `filing_id`: Filing UUID
- `form_version`: T1 form version (e.g., "2024")
- `status`: `"draft"` | `"submitted"`
- `is_locked`: Boolean (true if submitted)
- `completion_percentage`: 0-100
- `submitted_at`: ISO 8601 timestamp or null
- `answers`: ⭐ Flat key-value map (same format as POST request)
- `created_at`: ISO 8601 timestamp
- `updated_at`: ISO 8601 timestamp

**Frontend Usage:**
1. Call this endpoint when reopening a form from "Your Forms" page
2. Unflatten `answers` map back into structured T1FormData model
3. Populate form UI with saved values

**Error Responses:**

```json
// 404 Not Found - Filing doesn't exist
{
  "detail": "Filing 972ce307-.... not found or access denied"
}
```

---

## Endpoint 6: Submit T1 Form

**Purpose:** Submit T1 form for review (one-way lock with complete validation).

### Request

```http
POST /api/v1/t1-forms/{filing_id}/submit
Authorization: Bearer <access_token>
Accept: application/json
```

**Path Parameters:**
- `filing_id` (string, UUID): Filing ID

**Request Body:** None

### Response (200 OK)

```json
{
  "success": true,
  "message": "T1 form submitted successfully. Your filing is now under review.",
  "t1_form_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "submitted_at": "2026-01-10T11:00:00Z"
}
```

**Response Fields:**
- `success`: Always `true` on success
- `message`: Confirmation message
- `t1_form_id`: T1 form UUID
- `submitted_at`: ISO 8601 timestamp of submission

**Behavior:**
1. **Complete validation** applied (all required fields must be filled)
2. **One-way lock**: Form cannot be edited after submission
3. **State change**: `status` → `"submitted"`, `is_locked` → `true`
4. **Audit log**: Submission action recorded
5. **Completion**: `completion_percentage` → `100`

**Error Responses:**

```json
// 400 Bad Request - Form incomplete
{
  "detail": {
    "message": "T1 form is incomplete or contains errors",
    "errors": {
      "personalInfo.sin": "SIN is required",
      "income.employmentIncome": "Employment income must be provided"
    },
    "completion_percentage": 45
  }
}

// 400 Bad Request - No answers saved
{
  "detail": "Cannot submit T1 form: No answers have been saved yet. Please save answers first."
}

// 400 Bad Request - Already submitted
{
  "detail": "T1 form already submitted. Contact admin to request changes."
}

// 404 Not Found - Filing doesn't exist
{
  "detail": "Filing 972ce307-.... not found or access denied"
}
```

---

## Endpoint 7: Get Required Documents

**Purpose:** Get list of required documents based on questionnaire answers.

### Request

```http
GET /api/v1/t1-forms/{filing_id}/required-documents
Authorization: Bearer <access_token>
Accept: application/json
```

**Path Parameters:**
- `filing_id` (string, UUID): Filing ID

### Response (200 OK)

```json
{
  "filing_id": "972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b",
  "t1_form_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "required_documents": [
    {
      "label": "T4 - Employment Income",
      "question_key": "income.hasEmploymentIncome",
      "description": "Required because: income.hasEmploymentIncome"
    },
    {
      "label": "T5 - Investment Income",
      "question_key": "income.hasInvestmentIncome",
      "description": "Required because: income.hasInvestmentIncome"
    },
    {
      "label": "Proof of Foreign Property Ownership",
      "question_key": "questionnaire.hasForeignProperty",
      "description": "Required because: questionnaire.hasForeignProperty"
    }
  ]
}
```

**Response Fields:**
- `filing_id`: Filing UUID
- `t1_form_id`: T1 form UUID
- `required_documents[]`: Array of required documents
  - `label`: Human-readable document name
  - `question_key`: Questionnaire key that triggered this requirement (optional)
  - `description`: Explanation of why document is required

**Behavior:**
- Dynamically computed based on user's answers
- Returns base required documents if no answers saved yet
- Updates in real-time as user answers questionnaire

**Error Responses:**

```json
// 404 Not Found
{
  "detail": "Filing 972ce307-.... not found or access denied"
}
```

---

## Endpoint 8: Delete T1 Form Draft

**Purpose:** Delete a T1 form draft (only drafts, not submitted forms).

### Request

```http
DELETE /api/v1/t1-forms/{t1_form_id}
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `t1_form_id` (string, UUID): ⚠️ **T1 Form UUID** (not filing_id)

**Note:** This endpoint uses `t1_form_id` (from `GET /user/{user_id}/forms` response), not `filing_id`.

### Response (200 OK)

```json
{
  "success": true,
  "message": "T1 form deleted successfully",
  "t1_form_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Behavior:**
- Deletes T1Form record
- Cascade deletes all T1Answer records
- Cascade deletes all T1SectionProgress records
- Filing record remains (user can create new T1 form for same filing)

**Error Responses:**

```json
// 403 Forbidden - Form is submitted
{
  "detail": "Cannot delete submitted T1 form. Only draft forms can be deleted."
}

// 404 Not Found
{
  "detail": "T1 form not found or access denied"
}

// 400 Bad Request - Invalid UUID
{
  "detail": "Invalid T1 form ID format"
}
```

---

## Endpoint 9: Get T1 Form Structure (Public)

**Purpose:** Fetch T1Structure.json for frontend form rendering.

### Request

```http
GET /api/v1/t1-forms/structure
Accept: application/json
```

**Authentication:** Not required (public endpoint)

### Response (200 OK)

```json
{
  "version": "2024",
  "sections": [
    {
      "id": "personal-info",
      "label": "Personal Information",
      "fields": [
        {
          "key": "personalInfo.firstName",
          "label": "First Name",
          "type": "text",
          "required": true,
          "validation": {
            "min_length": 1,
            "max_length": 50
          }
        },
        {
          "key": "personalInfo.sin",
          "label": "Social Insurance Number (SIN)",
          "type": "text",
          "required": true,
          "validation": {
            "pattern": "^[0-9]{9}$",
            "message": "SIN must be exactly 9 digits"
          }
        }
      ]
    },
    {
      "id": "questionnaire",
      "label": "Tax Questionnaire",
      "fields": [
        {
          "key": "questionnaire.hasForeignProperty",
          "label": "Do you own foreign property worth over $100,000 CAD?",
          "type": "boolean",
          "required": true
        }
      ]
    }
  ],
  "conditional_documents": [
    {
      "label": "T4 - Employment Income",
      "condition": {
        "field": "income.hasEmploymentIncome",
        "value": true
      }
    }
  ]
}
```

**Response:** Complete T1Structure.json file

**Frontend Usage:**
- Fetch once on app start
- Cache locally
- Use for:
  - Rendering form fields
  - Client-side validation
  - Calculating required documents

---

## Complete Workflow Example

### Step 1: User Navigates to "Your Forms"

```http
GET /api/v1/t1-forms/user/1c53efcb-3651-483d-8e09-b178806c9044/forms
Authorization: Bearer <token>
```

**Response:**

```json
{
  "user_id": "1c53efcb-3651-483d-8e09-b178806c9044",
  "total_forms": 0,
  "forms": []
}
```

**Frontend:** Shows empty state with "+ New Filing" button.

---

### Step 2: User Taps "+ New Filing"

```http
POST /api/v1/filings
Authorization: Bearer <token>
Content-Type: application/json

{
  "filing_year": 2026
}
```

**Response:**

```json
{
  "id": "972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b",
  "user_id": "1c53efcb-3651-483d-8e09-b178806c9044",
  "filing_year": 2026,
  "status": "draft",
  "created_at": "2026-01-10T10:00:00Z",
  ...
}
```

**Frontend:**
- Extracts `filing_id = "972ce307-...."`
- Creates local T1FormData with `id = filing_id`, `answers = {}`
- Navigates to `/tax-forms/personal?formId=972ce307-....`

---

### Step 3: User Fills Personal Info, App Autosaves

```http
POST /api/v1/t1-forms/972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b/answers
Authorization: Bearer <token>
Content-Type: application/json

{
  "answers": {
    "personalInfo.firstName": "John",
    "personalInfo.lastName": "Doe",
    "personalInfo.sin": "123456789",
    "personalInfo.dateOfBirth": "1990-03-15",
    "personalInfo.phoneNumber": "911234567890",
    "personalInfo.email": "john@example.com"
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Draft saved successfully",
  "completion_percentage": 25,
  "fields_saved": 6
}
```

**Backend Behavior:**
- ✅ T1Form record created (first call)
- ✅ 6 T1Answer records created
- ✅ Completion percentage calculated

---

### Step 4: User Continues Filling, Multiple Autosaves

Each change triggers:

```http
POST /api/v1/t1-forms/972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b/answers
Authorization: Bearer <token>
Content-Type: application/json

{
  "answers": {
    "questionnaire.hasForeignProperty": true,
    "questionnaire.foreignPropertyDetails": "Rental in USA",
    "income.employmentIncome": 75000.00
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Draft saved successfully",
  "completion_percentage": 45,
  "fields_saved": 3
}
```

**Backend Behavior:**
- ✅ T1Form record updated
- ✅ 3 T1Answer records upserted (updated if exist, created if new)

---

### Step 5: User Closes App, Returns Later

**User navigates back to "Your Forms":**

```http
GET /api/v1/t1-forms/user/1c53efcb-3651-483d-8e09-b178806c9044/forms
Authorization: Bearer <token>
```

**Response:**

```json
{
  "user_id": "1c53efcb-3651-483d-8e09-b178806c9044",
  "total_forms": 1,
  "forms": [
    {
      "id": "a1b2c3d4-...",
      "filing_id": "972ce307-....",
      "filing_year": 2026,
      "status": "draft",
      "completion_percentage": 45,
      "updated_at": "2026-01-10T10:30:00Z",
      ...
    }
  ]
}
```

**Frontend:** Shows card for the draft form.

---

### Step 6: User Taps Card to Reopen Form

**Frontend checks local cache first. If not found:**

```http
GET /api/v1/t1-forms/972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b
Authorization: Bearer <token>
```

**Response:**

```json
{
  "id": "a1b2c3d4-...",
  "filing_id": "972ce307-....",
  "status": "draft",
  "completion_percentage": 45,
  "answers": {
    "personalInfo.firstName": "John",
    "personalInfo.lastName": "Doe",
    "personalInfo.sin": "123456789",
    "personalInfo.dateOfBirth": "1990-03-15",
    "personalInfo.phoneNumber": "911234567890",
    "personalInfo.email": "john@example.com",
    "questionnaire.hasForeignProperty": true,
    "questionnaire.foreignPropertyDetails": "Rental in USA",
    "income.employmentIncome": 75000.00
  },
  ...
}
```

**Frontend:**
- Unflattens `answers` map into T1FormData model
- Populates form UI with saved values
- User continues editing

---

### Step 7: User Completes Form and Submits

```http
POST /api/v1/t1-forms/972ce307-5d8e-4f3a-9b2a-1c8f7e6d5a4b/submit
Authorization: Bearer <token>
```

**Response:**

```json
{
  "success": true,
  "message": "T1 form submitted successfully. Your filing is now under review.",
  "t1_form_id": "a1b2c3d4-...",
  "submitted_at": "2026-01-10T11:00:00Z"
}
```

**Backend Behavior:**
- ✅ Complete validation applied
- ✅ Form locked (`is_locked = true`)
- ✅ Status changed to `"submitted"`
- ✅ Audit log created

---

## Error Handling

### Common Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Error message" 
}
```

Or for validation errors:

```json
{
  "detail": {
    "message": "Validation failed",
    "errors": {
      "field.key": "Error message for this field",
      "another.field": "Another error message"
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful GET, POST (update), DELETE |
| `201` | Created | Successful POST (create) |
| `400` | Bad Request | Validation failed, invalid input, form incomplete |
| `401` | Unauthorized | Missing or invalid access token |
| `403` | Forbidden | Email not verified, form locked, access denied |
| `404` | Not Found | Filing or T1 form not found, user mismatch |
| `409` | Conflict | T1 form already exists (if using POST /create) |

---

## Data Normalization Rules

### Frontend → Backend

| Field Type | Frontend Format | Backend Expected | Example |
|------------|-----------------|------------------|---------|
| **Date** | `DateTime` or string | `yyyy-MM-dd` | `"1990-03-15"` |
| **Phone** | `+911234567890` (with +) | `911234567890` (digits only) | `"911234567890"` |
| **SIN** | `123-456-789` (UI formatting) | `123456789` (9 digits) | `"123456789"` |
| **Boolean** | `true` / `false` | `true` / `false` | `true` |
| **Number** | Numeric | Numeric (int/float) | `75000.00` |
| **String** | Text | Text | `"John"` |

### Backend → Frontend

| Field Type | Backend Format | Frontend Expected | Transformation |
|------------|----------------|-------------------|----------------|
| **Date** | `yyyy-MM-dd` | `DateTime` | Parse to DateTime |
| **Phone** | `911234567890` | `+911234567890` | Prepend `+` |
| **SIN** | `123456789` | `123-456-789` (UI only) | Format with hyphens |
| **Timestamp** | `2026-01-10T10:00:00Z` | `DateTime` | Parse ISO 8601 |

---

## Security & Authorization

### Email Verification Required

All endpoints except:
- `POST /auth/login`
- `POST /auth/register`
- `GET /t1-forms/structure`

Require email to be verified (`email_verified = true`).

**Error if not verified:**

```json
{
  "detail": "Email verification required. Please verify your email before accessing this resource."
}
```

### User Isolation

- Users can ONLY access their own filings and T1 forms
- `user_id` from JWT token is enforced on all queries
- Attempting to access another user's data returns `403 Forbidden`

### Form Locking

- Submitted forms are **locked** (`is_locked = true`)
- Cannot save answers to locked forms
- Cannot delete locked forms
- Admin intervention required to unlock

---

## Performance & Caching

### Frontend Caching Strategy

1. **Local-first approach:**
   - Store T1FormData in on-device storage (Hive, SharedPreferences, etc.)
   - Check local cache before calling `GET /t1-forms/{filing_id}`
   - Update local cache after every autosave

2. **Sync strategy:**
   - Autosave to backend every 1.5 seconds (debounced)
   - Fetch from backend only on:
     - Form reopening (if not in cache)
     - Manual refresh
     - App restart

3. **Cache invalidation:**
   - Clear cache when user logs out
   - Update cache timestamp after successful autosave

### Backend Performance

- Autosave endpoint optimized for frequent calls
- Upsert operations prevent duplicate records
- Indexes on `filing_id`, `user_id`, `t1_form_id` for fast queries

---

## Testing Checklist

### Happy Path

- ✅ Create filing via POST /filings
- ✅ Save answers via POST /t1-forms/{filing_id}/answers (multiple times)
- ✅ List forms via GET /t1-forms/user/{user_id}/forms
- ✅ Get form via GET /t1-forms/{filing_id}
- ✅ Submit form via POST /t1-forms/{filing_id}/submit
- ✅ Delete draft via DELETE /t1-forms/{t1_form_id}

### Edge Cases

- ✅ GET form before any answers saved (should return empty answers)
- ✅ Submit form with incomplete data (should fail with validation errors)
- ✅ Try to save answers to submitted form (should fail with 403)
- ✅ Try to delete submitted form (should fail with 403)
- ✅ Access another user's form (should fail with 403)
- ✅ Invalid UUID format (should fail with 400)

### Data Integrity

- ✅ Phone number normalization (strip +)
- ✅ SIN normalization (strip hyphens)
- ✅ Date format validation (yyyy-MM-dd)
- ✅ Completion percentage calculation
- ✅ Idempotent autosave (multiple calls with same data)

---

## API Changes Summary

### What Changed from Original Implementation

**Before:**
- ❌ T1 forms auto-created on GET/POST
- ❌ Required explicit POST /t1-forms/create before saving answers
- ❌ Frontend needed to track separate t1_form_id

**After:**
- ✅ NO auto-creation
- ✅ First POST /t1-forms/{filing_id}/answers implicitly creates T1 form
- ✅ Frontend only tracks filing_id (simpler)
- ✅ GET /t1-forms/{filing_id} returns virtual draft if no answers yet

### Migration Path for Frontend

1. **Remove calls to POST /t1-forms/create**
   - Delete any code that calls this endpoint
   - Filing creation via POST /filings is sufficient

2. **Update autosave logic**
   - First autosave will now create T1 form automatically
   - No need to check if T1 form exists before saving

3. **Update cache keys**
   - Use `filing_id` as primary cache key (not t1_form_id)
   - Simplifies cache management

4. **Handle virtual drafts**
   - GET /t1-forms/{filing_id} may return empty `answers` map
   - Handle gracefully (populate form with empty values)

---

## Contact & Support

**Backend Developer:** Refer to this document for exact API contract  
**Frontend Developer:** Use this as the source of truth for API integration  
**QA:** Use testing checklist to validate end-to-end flow

**Last Updated:** 2026-01-11  
**API Version:** v1  
**Status:** ✅ Production-Ready
