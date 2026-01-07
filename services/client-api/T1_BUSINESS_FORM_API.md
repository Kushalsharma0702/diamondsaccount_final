# T1 Business Form Backend API

This backend API is designed to work with the Flutter mobile app's T1 form structure. It provides endpoints for saving, loading, and managing T1 tax form data in PostgreSQL.

## Overview

The backend matches the Flutter app's data structure exactly:
- `T1FormData` - Main form container
- `T1PersonalInfo` - Personal information with spouse and children
- `T1ForeignProperty` - Foreign property details
- `T1MovingExpense` - Moving expense information
- `T1SelfEmployment` - Self-employment wrapper
  - `T1UberBusiness` - Uber/Skip/DoorDash business details
  - `T1GeneralBusiness` - General business details
  - `T1RentalIncome` - Rental income details

## Database Structure

The database uses normalized tables:
- `t1_forms_main` - Main form table
- `t1_personal_info` - Personal information
- `t1_spouse_info` - Spouse information
- `t1_child_info` - Children information
- `t1_foreign_properties` - Foreign properties (one-to-many)
- `t1_moving_expenses` - Moving expenses
- `t1_self_employment` - Self-employment wrapper
- `t1_uber_business` - Uber business details
- `t1_general_business` - General business details
- `t1_rental_income` - Rental income details

## API Endpoints

### Base URL
```
http://localhost:8001/api/v1/t1-forms-business
```

### 1. Save/Update T1 Form
**POST** `/`

Save or update a T1 form. If the form ID exists, it updates; otherwise, it creates a new form.

**Request Body:**
```json
{
  "formData": {
    "id": "T1_1234567890",
    "status": "draft",
    "personalInfo": {
      "firstName": "John",
      "lastName": "Doe",
      "sin": "123456789",
      "email": "john@example.com",
      "address": "123 Main St",
      "phoneNumber": "1234567890",
      "maritalStatus": "married",
      "spouseInfo": {
        "firstName": "Jane",
        "lastName": "Doe",
        "sin": "987654321"
      },
      "children": [
        {
          "firstName": "Child",
          "lastName": "Doe",
          "sin": "111222333"
        }
      ]
    },
    "hasForeignProperty": false,
    "foreignProperties": [],
    "isSelfEmployed": true,
    "selfEmployment": {
      "businessTypes": ["uber"],
      "uberBusiness": {
        "totalKmForUberSkip": 10000.0,
        "gas": 2000.0
      }
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "T1 form saved successfully",
  "formData": { ... }
}
```

### 2. Get All T1 Forms
**GET** `/`

Get all T1 forms for the authenticated user.

**Response:**
```json
{
  "success": true,
  "forms": [
    {
      "id": "T1_1234567890",
      "status": "draft",
      "personalInfo": { ... },
      ...
    }
  ],
  "total": 1
}
```

### 3. Get T1 Form by ID
**GET** `/{form_id}`

Get a specific T1 form by ID.

**Response:**
```json
{
  "success": true,
  "message": "T1 form retrieved successfully",
  "formData": { ... }
}
```

### 4. Delete T1 Form
**DELETE** `/{form_id}`

Delete a T1 form by ID.

**Response:**
```json
{
  "success": true,
  "message": "T1 form deleted successfully"
}
```

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Database Migration

To create the database tables, run:

```bash
cd services/client-api
alembic upgrade head
```

Or run the specific migration:
```bash
alembic upgrade 20241218_t1_business
```

## Integration with Flutter App

The Flutter app's `T1FormStorageService` can be updated to use these endpoints instead of (or in addition to) local storage:

```dart
// Example API call
final response = await http.post(
  Uri.parse('http://localhost:8001/api/v1/t1-forms-business/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $token',
  },
  body: jsonEncode({
    'formData': formData.toJson(),
  }),
);
```

## Notes

- The API automatically handles relationships (personal info, spouse, children, etc.)
- Form IDs should follow the format: `T1_{timestamp}`
- All dates are stored in UTC
- The API supports both creating new forms and updating existing ones
- Foreign properties are stored as a one-to-many relationship
- Self-employment data (Uber, General Business, Rental) is stored in separate tables

## Future Enhancements

- Complete implementation of moving expenses (individual and spouse)
- Complete implementation of self-employment nested objects
- Form validation
- Tax calculations
- Form submission workflow
- Document upload integration















