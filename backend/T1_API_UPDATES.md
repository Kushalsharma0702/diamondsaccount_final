# T1 Forms API Updates

## Summary of Changes

These updates fix critical production issues:
1. **Universal Phone Validation** - Support international phone numbers (not just Canadian)
2. **Explicit T1 Form Creation** - Prevent auto-creation of forms for new users
3. **User T1 Form Management** - New endpoints for listing and deleting T1 forms

---

## 1. Universal Phone Validation ✅

**Issue**: Phone validation was restricted to Canadian format only (10 digits)

**Fix**: Updated validation to accept international phone numbers (10-15 digits)

**File**: `backend/app/services/t1_validation_engine.py` (lines 374-384)

**Before**:
```python
# Canadian format only: (XXX) XXX-XXXX
pattern = r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'
```

**After**:
```python
# Universal format: supports international numbers
# Extract digits only, validate 10-15 digits
# Supports: +1234567890, (123) 456-7890, 123-456-7890, etc.
digits_only = re.sub(r'\D', '', value)
if len(digits_only) < 10 or len(digits_only) > 15:
    return False, "Phone number must contain 10-15 digits"
```

**Supported Formats**:
- `+1 (234) 567-8900` - US/Canada with country code
- `+91 98765 43210` - India
- `+44 20 7946 0958` - UK
- `(234) 567-8900` - US/Canada without country code
- `234-567-8900` - Simple dashes
- `2345678900` - No formatting

---

## 2. Explicit T1 Form Creation ✅

**Issue**: T1 forms were automatically created when users accessed endpoints, causing:
- New users seeing old draft forms
- Users unable to create multiple drafts
- Confusion about form ownership

**Fix**: Removed auto-creation behavior, now requires explicit creation via new endpoint

**File**: `backend/app/routes_v2/t1_forms.py`

### Modified Function: `_get_t1_form_or_create()`

**Before**:
```python
def _get_t1_form_or_create(filing_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> T1Form:
    # Always created form if not found
    t1_form = db.query(T1Form).filter(...).first()
    if not t1_form:
        t1_form = T1Form(filing_id=filing_id, user_id=user_id, status='draft')
        db.add(t1_form)
        db.commit()
    return t1_form
```

**After**:
```python
def _get_t1_form_or_create(filing_id: uuid.UUID, user_id: uuid.UUID, db: Session, 
                           auto_create: bool = False) -> T1Form:
    t1_form = db.query(T1Form).filter(...).first()
    if not t1_form:
        if not auto_create:
            raise HTTPException(status_code=404, detail="T1 form not found")
        # Only create if explicitly requested
        t1_form = T1Form(filing_id=filing_id, user_id=user_id, status='draft')
        db.add(t1_form)
        db.commit()
    return t1_form
```

### Updated Endpoints

All existing endpoints now use `auto_create=False`:

1. **POST /api/v1/t1-forms/{filing_id}/save-draft** - Requires T1 form to exist first
2. **GET /api/v1/t1-forms/{filing_id}/draft** - Returns 404 if form doesn't exist
3. **POST /api/v1/t1-forms/{filing_id}/submit** - Requires T1 form to exist first
4. **GET /api/v1/t1-forms/{filing_id}/required-documents** - Requires T1 form to exist first

---

## 3. New Endpoints for T1 Form Management ✅

### A. List All User T1 Forms

**Endpoint**: `GET /api/v1/t1-forms/user/{user_id}/forms`

**Purpose**: Fetch all T1 forms (drafts and submitted) for authenticated user

**Security**: User can only access their own forms (user_id must match authenticated user)

**Request**:
```bash
curl -X GET http://localhost:8000/api/v1/t1-forms/user/USER_ID/forms \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response** (200 OK):
```json
{
  "forms": [
    {
      "id": "uuid",
      "filing_id": "uuid",
      "status": "draft",
      "is_locked": false,
      "completion_percentage": 45,
      "submitted_at": null,
      "created_at": "2024-01-11T03:00:00Z",
      "updated_at": "2024-01-11T03:15:00Z"
    },
    {
      "id": "uuid",
      "filing_id": "uuid",
      "status": "submitted",
      "is_locked": true,
      "completion_percentage": 100,
      "submitted_at": "2024-01-10T10:00:00Z",
      "created_at": "2024-01-08T12:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z"
    }
  ],
  "total_count": 2
}
```

**Notes**:
- Does NOT include detailed answers (use `GET /api/v1/t1-forms/{id}` for that)
- Useful for displaying a list of all user's T1 forms
- Shows both draft and submitted forms

---

### B. Create T1 Form

**Endpoint**: `POST /api/v1/t1-forms/create`

**Purpose**: Explicitly create a new T1 form for a filing

**Security**: 
- User must own the filing
- Cannot create duplicate forms for the same filing

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/t1-forms/create \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filing_id": "FILING_UUID"
  }'
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "filing_id": "uuid",
  "status": "draft",
  "is_locked": false,
  "completion_percentage": 0,
  "submitted_at": null,
  "created_at": "2024-01-11T03:30:00Z",
  "updated_at": "2024-01-11T03:30:00Z"
}
```

**Error Responses**:
- `403 Forbidden` - User doesn't own the filing
- `404 Not Found` - Filing doesn't exist
- `409 Conflict` - T1 form already exists for this filing

**Workflow**:
```
1. User creates filing: POST /api/v1/filings
2. User creates T1 form: POST /api/v1/t1-forms/create {"filing_id": "..."}
3. User saves answers: POST /api/v1/t1-forms/{filing_id}/save-draft
4. User submits form: POST /api/v1/t1-forms/{filing_id}/submit
```

---

### C. Delete T1 Form

**Endpoint**: `DELETE /api/v1/t1-forms/{t1_form_id}`

**Purpose**: Delete a T1 form (drafts only, not submitted forms)

**Security**: 
- User must own the T1 form
- Cannot delete submitted or locked forms

**Request**:
```bash
curl -X DELETE http://localhost:8000/api/v1/t1-forms/FORM_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response** (200 OK):
```json
{
  "message": "T1 form deleted successfully",
  "deleted_form_id": "uuid"
}
```

**Error Responses**:
- `403 Forbidden` - Form is submitted/locked or user doesn't own it
- `404 Not Found` - T1 form doesn't exist

**Notes**:
- Cascade deletes all answers associated with the form
- Cascade deletes progress tracking data
- Filing remains intact (only T1 form is deleted)

---

## Migration Guide for Frontend

### Old Workflow (Auto-Creation)
```javascript
// Step 1: Save answers (form auto-created)
POST /api/v1/t1-forms/{filing_id}/save-draft
{
  "answers": {"name": "John Doe"}
}
```

### New Workflow (Explicit Creation) ⚠️ BREAKING CHANGE
```javascript
// Step 1: Create T1 form explicitly
POST /api/v1/t1-forms/create
{
  "filing_id": "uuid"
}

// Step 2: Save answers (form must exist)
POST /api/v1/t1-forms/{filing_id}/save-draft
{
  "answers": {"name": "John Doe"}
}
```

### User Dashboard - List Forms
```javascript
// Fetch all user's T1 forms
GET /api/v1/t1-forms/user/{user_id}/forms

// Display list with:
// - Filing ID
// - Status (draft/submitted)
// - Completion %
// - Created date
// - Actions: View, Edit (if draft), Delete (if draft)
```

### Delete Form Flow
```javascript
// User clicks "Delete" on draft form
if (form.status === 'draft' && !form.is_locked) {
  DELETE /api/v1/t1-forms/{form_id}
  // Refresh list after successful delete
}
```

---

## Testing the Updates

### 1. Test Phone Validation

```bash
# Test various phone formats
curl -X POST http://localhost:8000/api/v1/t1-forms/FILING_ID/save-draft \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "phone": "+1 (234) 567-8900"
    }
  }'

# Should accept:
# +91 98765 43210 (India)
# +44 20 7946 0958 (UK)
# (234) 567-8900 (US/Canada)
# 234-567-8900
```

### 2. Test T1 Form Creation

```bash
# Step 1: Create T1 form
T1_FORM=$(curl -s -X POST http://localhost:8000/api/v1/t1-forms/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filing_id":"FILING_UUID"}' | jq -r '.id')

# Step 2: List user forms
curl -X GET http://localhost:8000/api/v1/t1-forms/user/USER_ID/forms \
  -H "Authorization: Bearer $TOKEN"

# Step 3: Save draft answers
curl -X POST http://localhost:8000/api/v1/t1-forms/FILING_ID/save-draft \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answers": {"name": "Test User"}}'

# Step 4: Delete form (if needed)
curl -X DELETE http://localhost:8000/api/v1/t1-forms/$T1_FORM \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test Error Cases

```bash
# Try to save draft without creating form first (should fail with 404)
curl -X POST http://localhost:8000/api/v1/t1-forms/FILING_ID/save-draft \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answers": {"name": "Test"}}'

# Expected: 404 Not Found - "T1 form not found. Create it first using POST /api/v1/t1-forms/create"

# Try to delete submitted form (should fail with 403)
curl -X DELETE http://localhost:8000/api/v1/t1-forms/SUBMITTED_FORM_ID \
  -H "Authorization: Bearer $TOKEN"

# Expected: 403 Forbidden - "Cannot delete submitted or locked T1 forms"

# Try to create duplicate T1 form (should fail with 409)
curl -X POST http://localhost:8000/api/v1/t1-forms/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filing_id":"EXISTING_FILING_UUID"}'

# Expected: 409 Conflict - "T1 form already exists for this filing"
```

---

## Production Deployment Checklist

- [x] Phone validation updated to universal format
- [x] All `_get_t1_form_or_create` calls updated with `auto_create=False`
- [x] New endpoint: `GET /api/v1/t1-forms/user/{user_id}/forms`
- [x] New endpoint: `POST /api/v1/t1-forms/create`
- [x] New endpoint: `DELETE /api/v1/t1-forms/{t1_form_id}`
- [x] Master backend restarted (port 8000)
- [ ] Frontend updated to use new workflow
- [ ] API documentation updated
- [ ] User notification about workflow change
- [ ] Production testing with real user accounts
- [ ] Monitor logs for 404 errors (users trying old workflow)

---

## API Endpoint Summary

| Method | Endpoint | Purpose | Auth | Notes |
|--------|----------|---------|------|-------|
| **POST** | `/api/v1/t1-forms/create` | Create new T1 form | ✅ | **NEW** - Must be called first |
| **GET** | `/api/v1/t1-forms/user/{user_id}/forms` | List all user T1 forms | ✅ | **NEW** - Returns summary only |
| **DELETE** | `/api/v1/t1-forms/{t1_form_id}` | Delete draft T1 form | ✅ | **NEW** - Drafts only |
| POST | `/api/v1/t1-forms/{filing_id}/save-draft` | Save draft answers | ✅ | **UPDATED** - Requires T1 form to exist |
| GET | `/api/v1/t1-forms/{filing_id}/draft` | Get draft answers | ✅ | **UPDATED** - Returns 404 if not found |
| POST | `/api/v1/t1-forms/{filing_id}/submit` | Submit T1 form | ✅ | **UPDATED** - Requires T1 form to exist |
| GET | `/api/v1/t1-forms/{filing_id}/required-documents` | Get required documents | ✅ | **UPDATED** - Requires T1 form to exist |

---

## Contact & Support

For issues or questions:
- Check logs: `tail -f logs/master-backend-8000.log`
- Health check: `curl http://localhost:8000/health`
- Report issues via admin dashboard

**Last Updated**: 2024-01-11
**Backend Version**: 2.0.0
**API Version**: v1
