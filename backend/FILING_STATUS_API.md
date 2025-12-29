# Filing Status API Documentation

## Overview

The Filing Status API allows admins to update T1 return statuses and clients to view their filing status with a timeline. Status updates are automatically reflected in the client dashboard.

## Status Workflow

The filing process follows this workflow:

1. **Form in Draft** (`draft`)
2. **Form Submitted** (`submitted`)
3. **Payment Request Sent** (`payment_request_sent`)
4. **Payment Received** (`payment_received`)
5. **Return in Progress** (`return_in_progress`)
6. **Additional Information Required** (`additional_info_required`)
7. **Under Review / Pending Approval** (`under_review_pending_approval`)
8. **Approved for Filing** (`approved_for_filing`)
9. **E-Filing Completed** (`e_filing_completed`)

## API Endpoints

### 1. Get Client Filing Status

**GET** `/api/v1/filing-status/client/{client_id}`

Get filing status with timeline for a specific client.

**Query Parameters:**
- `filing_year` (optional) - Filter by filing year (defaults to latest)

**Response:**
```json
{
  "return_id": "uuid",
  "filing_year": 2024,
  "current_status": "under_review_pending_approval",
  "current_status_display": "Under Review / Pending Approval",
  "payment_status": "paid",
  "timeline": [
    {
      "status": "draft",
      "display_name": "Form in Draft",
      "is_completed": true,
      "is_current": false,
      "completed_at": "2025-12-24T08:00:00"
    },
    {
      "status": "submitted",
      "display_name": "Form Submitted",
      "is_completed": true,
      "is_current": false,
      "completed_at": "2025-12-24T08:05:00"
    },
    {
      "status": "under_review_pending_approval",
      "display_name": "Under Review / Pending Approval",
      "is_completed": false,
      "is_current": true,
      "completed_at": null
    }
    // ... more timeline items
  ],
  "updated_at": "2025-12-24T08:06:48",
  "submitted_at": "2025-12-24T08:05:00"
}
```

**Alternative:** Get by email

**GET** `/api/v1/filing-status/client?email={email}`

Same response format, but finds client by email instead of ID.

### 2. Update Filing Status (Admin)

**PUT** `/api/v1/filing-status/admin/{return_id}/status`

Admin endpoint to update T1 return filing status. Automatically creates a notification for the client.

**Request Body:**
```json
{
  "status": "under_review_pending_approval",
  "notes": "Reviewing documents submitted"
}
```

**Response:**
```json
{
  "return_id": "uuid",
  "status": "under_review_pending_approval",
  "status_display": "Under Review / Pending Approval",
  "updated_at": "2025-12-24T08:06:48",
  "message": "Status updated successfully"
}
```

**Valid Status Values:**
- `draft`
- `submitted`
- `payment_request_sent`
- `payment_received`
- `return_in_progress`
- `additional_info_required`
- `under_review_pending_approval`
- `approved_for_filing`
- `e_filing_completed`

### 3. List All Returns (Admin)

**GET** `/api/v1/filing-status/admin/returns`

List all T1 returns with filtering options.

**Query Parameters:**
- `status` (optional) - Filter by status
- `filing_year` (optional) - Filter by filing year
- `client_id` (optional) - Filter by client ID

**Response:**
```json
[
  {
    "id": "uuid",
    "client_id": "uuid",
    "filing_year": 2024,
    "status": "under_review_pending_approval",
    "status_display": "Under Review / Pending Approval",
    "payment_status": "paid",
    "updated_at": "2025-12-24T08:06:48",
    "submitted_at": "2025-12-24T08:05:00"
  }
]
```

## Features

### Automatic Notifications

When an admin updates a filing status, a notification is automatically created for the client:

- **Type:** `status_update`
- **Title:** "Filing Status Updated"
- **Message:** Includes old and new status, plus any admin notes
- **Read Status:** Unread by default

### Client Status Sync

When a T1 return status is updated, the corresponding `Client` record status is also updated:

| T1 Status | Client Status |
|-----------|---------------|
| `draft` | `documents_pending` |
| `submitted` | `under_review` |
| `payment_request_sent` | `awaiting_payment` |
| `payment_received` | `in_preparation` |
| `return_in_progress` | `in_preparation` |
| `additional_info_required` | `under_review` |
| `under_review_pending_approval` | `awaiting_approval` |
| `approved_for_filing` | `awaiting_approval` |
| `e_filing_completed` | `filed` |

### Timeline Generation

The timeline is automatically generated based on:
- Current status position in the workflow
- Completed steps (before current status)
- Current step (matching current status)
- Pending steps (after current status)

## Usage Examples

### Client View (Frontend)

```javascript
// Get filing status for logged-in client
const response = await fetch(`/api/v1/filing-status/client/${clientId}`);
const status = await response.json();

// Display timeline
status.timeline.forEach(item => {
  if (item.is_current) {
    // Highlight current step
  } else if (item.is_completed) {
    // Show completed checkmark
  } else {
    // Show pending/greyed out
  }
});
```

### Admin Update (Frontend)

```javascript
// Update status from admin panel
const response = await fetch(`/api/v1/filing-status/admin/${returnId}/status`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    status: 'under_review_pending_approval',
    notes: 'Documents reviewed, pending approval'
  })
});

const result = await response.json();
// Status updated, notification sent to client
```

## Testing

Run the test script:

```bash
python3 backend/test_filing_status.py
```

This tests:
1. Client login
2. Getting filing status
3. Admin status update
4. Status change reflection
5. Listing all returns

## Database Schema

The filing status is stored in the `t1_returns_flat` table:

- `status` (VARCHAR(30)) - Current status
- `payment_status` (VARCHAR(20)) - Payment status
- `updated_at` (TIMESTAMP) - Last update time
- `submitted_at` (TIMESTAMP) - Submission time

## Error Handling

- **404 Not Found:** Client or T1 return not found
- **400 Bad Request:** Invalid status value
- **500 Internal Server Error:** Database or server error

## Notes

- Status updates are immediate and reflected in real-time
- Timeline is calculated dynamically based on current status
- Notifications are created automatically on status change
- Client status is synced automatically with T1 return status




