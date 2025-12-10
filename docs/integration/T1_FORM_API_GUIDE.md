# T1 Tax Form API - Complete Guide

## 📋 Overview

Your TaxEase backend now has **TWO sets of T1 endpoints**:

1. **Basic T1 Endpoints** (Simple schema - `main.py` lines 446-600)
   - Location: `/api/v1/tax/t1-personal`
   - Uses: Simple fields (employment_income, sin, marital_status, etc.)
   
2. **Enhanced T1 Endpoints** (Comprehensive schema - `shared/t1_routes.py`)
   - Location: `/api/v1/t1-forms`
   - Uses: Full nested structure matching your T1_Personal_sample.json
   - **✅ This is what you should use for your frontend**

---

## 🎯 Recommended API Endpoint (Enhanced T1 Forms)

### Base URL
```
http://localhost:8000/api/v1/t1-forms
```

### Authentication
All endpoints require JWT Bearer token:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📝 API Endpoints

### 1. Create T1 Form (POST)

**Endpoint:** `POST /api/v1/t1-forms/`

**Description:** Create a comprehensive T1 Personal Tax Form with automatic encryption

**Request Body:** (Matches your T1_Personal_sample.json structure)

```json
{
  "status": "draft",
  "personalInfo": {
    "firstName": "Jane",
    "middleName": "Q",
    "lastName": "Doe",
    "sin": "123456789",
    "dateOfBirth": "1990-05-20",
    "address": "123 Main St, Toronto, ON",
    "phoneNumber": "+14165550123",
    "email": "jane@example.com",
    "isCanadianCitizen": true,
    "maritalStatus": "married",
    "spouseInfo": {
      "firstName": "John",
      "middleName": null,
      "lastName": "Doe",
      "sin": "987654321",
      "dateOfBirth": "1989-09-09"
    },
    "children": [
      {
        "firstName": "Kid",
        "middleName": null,
        "lastName": "Doe",
        "sin": "001122334",
        "dateOfBirth": "2018-03-15"
      }
    ]
  },
  "hasForeignProperty": true,
  "foreignProperties": [
    {
      "investmentDetails": "US ETF",
      "grossIncome": 1200.5,
      "gainLossOnSale": 100.0,
      "maxCostDuringYear": 12000.0,
      "costAmountYearEnd": 11500.0,
      "country": "US"
    }
  ],
  "hasMedicalExpenses": true,
  "hasCharitableDonations": true,
  "hasMovingExpenses": true,
  "movingExpenseForIndividual": true,
  "movingExpenseForSpouse": false,
  "movingExpenseIndividual": {
    "individual": "Jane Doe",
    "oldAddress": "Old Address",
    "newAddress": "New Address",
    "distanceFromOldToNew": "550 km",
    "distanceFromNewToOffice": "12 km",
    "airTicketCost": 350.75,
    "moversAndPackers": 800.0,
    "mealsAndOtherCost": 120.0,
    "anyOtherCost": 0.0,
    "dateOfTravel": "2024-06-01",
    "dateOfJoining": "2024-06-15",
    "companyName": "NewCo Inc.",
    "newEmployerAddress": "456 King St",
    "grossIncomeAfterMoving": 65000.0
  },
  "isSelfEmployed": true,
  "selfEmployment": {
    "businessTypes": ["uber", "general", "rental"],
    "uberBusiness": {
      "uberSkipStatement": "file.pdf",
      "businessHstNumber": "123456789RT0001",
      "hstAccessCode": "XXXX",
      "hstFillingPeriod": "2024-Q4",
      "income": 25000.0,
      "totalKmForUberSkip": 8000.0,
      "totalOfficialKmDriven": 9000.0,
      "totalKmDrivenEntireYear": 20000.0,
      "businessNumberVehicleRegistration": 120.0,
      "meals": 300.0,
      "telephone": 480.0,
      "parkingFees": 200.0,
      "cleaningExpenses": 150.0,
      "safetyInspection": 90.0,
      "winterTireChange": 100.0,
      "oilChangeAndMaintenance": 400.0,
      "depreciation": 0.0,
      "insuranceOnVehicle": 1200.0,
      "gas": 3500.0,
      "financingCostInterest": 0.0,
      "leaseCost": 0.0,
      "otherExpense": 0.0
    },
    "generalBusiness": {
      "clientName": "Jane Doe",
      "businessName": "JD Consulting",
      "salesCommissionsFees": 50000.0,
      "minusHstCollected": 6500.0,
      "grossIncome": 43500.0,
      "advertising": 500.0,
      "mealsEntertainment": 300.0,
      "insurance": 250.0,
      "officeExpenses": 900.0,
      "supplies": 400.0,
      "legalAccountingFees": 700.0,
      "travel": 600.0,
      "telephoneUtilities": 720.0,
      "areaOfHomeForBusiness": "200 sqft",
      "totalAreaOfHome": "1000 sqft",
      "heat": 200.0,
      "electricity": 300.0,
      "houseInsurance": 350.0,
      "homeMaintenance": 150.0,
      "houseRent": 18000.0,
      "kmDrivenForBusiness": 1200.0,
      "totalKmDrivenInYear": 8000.0
    },
    "rentalIncome": {
      "propertyAddress": "789 Queen St",
      "numberOfUnits": 1,
      "grossRentalIncome": 18000.0,
      "anyGovtIncomeRelatingToRental": 0.0,
      "personalUsePortion": "0%",
      "houseInsurance": 600.0,
      "mortgageInterest": 7000.0,
      "propertyTaxes": 3000.0,
      "repairAndMaintenance": 500.0,
      "purchasePrice": 350000.0,
      "purchaseDate": "2020-08-01",
      "additionDeletionAmount": 0.0
    }
  },
  "isFirstHomeBuyer": true,
  "soldPropertyLongTerm": true,
  "soldPropertyShortTerm": true,
  "hasWorkFromHomeExpense": true,
  "wasStudentLastYear": true,
  "isUnionMember": true,
  "hasDaycareExpenses": true,
  "isFirstTimeFiler": true,
  "hasOtherIncome": true,
  "otherIncomeDescription": "Other income details",
  "hasProfessionalDues": true,
  "hasRrspFhsaInvestment": true,
  "hasChildArtSportCredit": true,
  "isProvinceFiler": true
}
```

**Response:** `201 Created`

```json
{
  "id": "T1_1730290000000",
  "user_id": "uuid-here",
  "status": "draft",
  "personalInfo": { "...all form data..." },
  "is_encrypted": true,
  "encryption_algorithm": "AES-256-CBC",
  "created_at": "2025-01-10T12:34:56.000Z",
  "updated_at": "2025-01-10T12:34:56.000Z"
}
```

---

### 2. List All T1 Forms (GET)

**Endpoint:** `GET /api/v1/t1-forms/`

**Description:** Get all T1 forms for the current user

**Query Parameters:**
- `offset` (optional): Pagination offset (default: 0)
- `limit` (optional): Number of records (default: 10, max: 100)

**Response:** `200 OK`

```json
{
  "forms": [
    {
      "id": "T1_1730290000000",
      "status": "submitted",
      "personalInfo": { "...form data..." },
      "created_at": "2025-01-10T12:34:56.000Z"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 10
}
```

---

### 3. Get Single T1 Form (GET)

**Endpoint:** `GET /api/v1/t1-forms/{form_id}`

**Description:** Get a specific T1 form by ID (automatically decrypted)

**Response:** `200 OK`

```json
{
  "id": "T1_1730290000000",
  "user_id": "uuid-here",
  "status": "draft",
  "personalInfo": {
    "firstName": "Jane",
    "lastName": "Doe",
    "...complete form data..."
  },
  "is_encrypted": true,
  "created_at": "2025-01-10T12:34:56.000Z"
}
```

---

### 4. Update T1 Form (PUT)

**Endpoint:** `PUT /api/v1/t1-forms/{form_id}`

**Description:** Update an existing T1 form (partial or complete update)

**Request Body:** (Same as create, but all fields optional)

```json
{
  "status": "submitted",
  "personalInfo": {
    "firstName": "Jane",
    "lastName": "Doe Updated"
  },
  "hasCharitableDonations": true
}
```

**Response:** `200 OK`

```json
{
  "id": "T1_1730290000000",
  "status": "submitted",
  "personalInfo": { "...updated data..." },
  "updated_at": "2025-01-10T13:00:00.000Z"
}
```

---

### 5. Delete T1 Form (DELETE)

**Endpoint:** `DELETE /api/v1/t1-forms/{form_id}`

**Description:** Delete a T1 form

**Response:** `200 OK`

```json
{
  "message": "T1 form deleted successfully",
  "form_id": "T1_1730290000000"
}
```

---

## 🔐 Security Features

✅ **Automatic Encryption**: All form data is encrypted using AES-256-CBC + RSA-2048
✅ **Per-User Keys**: Each user has unique encryption keys
✅ **Automatic Decryption**: Forms are decrypted automatically when retrieved
✅ **Audit Logging**: All operations are logged for compliance

---

## ✅ Schema Validation

The API validates the following:

### Personal Info
- ✅ First name and last name (required)
- ✅ SIN (9 digits)
- ✅ Phone number (international format: `+14165550123`)
- ✅ Email (valid email format)
- ✅ Date of birth (YYYY-MM-DD format)

### Spouse Info (if married)
- ✅ Same validation as personal info

### Children (array)
- ✅ Each child validated like personal info

### Foreign Properties (if any)
- ✅ All amounts must be >= 0
- ✅ Country name required

### Moving Expenses
- ✅ All costs must be >= 0
- ✅ Dates in YYYY-MM-DD format

### Self Employment (if applicable)
- ✅ Business types: `"uber"`, `"general"`, `"rental"`
- ✅ All income and expense fields must be >= 0
- ✅ HST number format validation

---

## 🧪 Testing with Postman

### Step 1: Register and Login

1. **Register:**
   ```
   POST http://localhost:8000/api/v1/auth/register
   
   {
     "email": "test@example.com",
     "password": "SecurePass123!",
     "first_name": "Test",
     "last_name": "User",
     "phone": "+14165550100",
     "accept_terms": true
   }
   ```

2. **Login:**
   ```
   POST http://localhost:8000/api/v1/auth/login
   
   {
     "email": "test@example.com",
     "password": "SecurePass123!"
   }
   ```

3. **Save the access_token** from response

---

### Step 2: Setup Encryption (First Time Only)

```
POST http://localhost:8000/api/v1/encrypted-files/setup
Authorization: Bearer <your_token>

{
  "password": "T1TestPassword123!"
}
```

---

### Step 3: Create T1 Form

```
POST http://localhost:8000/api/v1/t1-forms/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "status": "draft",
  "personalInfo": {
    "firstName": "Jane",
    "lastName": "Doe",
    "sin": "123456789",
    "dateOfBirth": "1990-05-20",
    "address": "123 Main St, Toronto, ON",
    "phoneNumber": "+14165550123",
    "email": "jane@example.com",
    "isCanadianCitizen": true,
    "maritalStatus": "single"
  },
  "hasForeignProperty": false,
  "hasMedicalExpenses": true,
  "hasCharitableDonations": true,
  "isSelfEmployed": false,
  "isFirstHomeBuyer": false,
  "isFirstTimeFiler": true
}
```

---

### Step 4: List Your Forms

```
GET http://localhost:8000/api/v1/t1-forms/
Authorization: Bearer <your_token>
```

---

### Step 5: Get Specific Form

```
GET http://localhost:8000/api/v1/t1-forms/{form_id}
Authorization: Bearer <your_token>
```

---

## 🐛 Common Errors

### 400 Bad Request - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "personalInfo", "sin"],
      "msg": "string does not match regex '^\\d{9}$'",
      "type": "value_error.str.regex"
    }
  ]
}
```

**Solution:** Check that SIN is exactly 9 digits

---

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

**Solution:** Include valid JWT token in Authorization header

---

### 400 Bad Request - Encryption Not Setup
```json
{
  "detail": "User encryption not set up. Please set up encryption first."
}
```

**Solution:** Call the encryption setup endpoint first

---

## 📊 Database Schema

The T1 form data is stored in the `t1_personal_forms` table:

```sql
- id (string, PK): Format "T1_{timestamp}"
- user_id (UUID, FK): Reference to users table
- tax_year (integer): Tax year
- status (string): "draft", "submitted", "processed"
- encrypted_form_data (binary): AES-256 encrypted JSON
- encryption_metadata (text): Encryption details
- is_encrypted (boolean): Always true
- first_name, last_name, email: Unencrypted for indexing
- has_foreign_property, has_medical_expenses, etc.: Boolean flags
- created_at, updated_at: Timestamps
```

---

## 🎨 Frontend Integration Example (React/Flutter)

### React Example

```javascript
// Create T1 Form
const createT1Form = async (formData) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/t1-forms/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('Validation error:', error.detail);
      return;
    }
    
    const result = await response.json();
    console.log('Form created:', result.id);
    return result;
  } catch (error) {
    console.error('Error:', error);
  }
};

// Usage
const formData = {
  status: "draft",
  personalInfo: {
    firstName: "Jane",
    lastName: "Doe",
    sin: "123456789",
    // ... other fields
  },
  // ... other sections
};

createT1Form(formData);
```

---

### Flutter/Dart Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> createT1Form(Map<String, dynamic> formData) async {
  final token = await getStoredToken(); // Your auth token storage
  
  final response = await http.post(
    Uri.parse('http://localhost:8000/api/v1/t1-forms/'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    },
    body: jsonEncode(formData),
  );
  
  if (response.statusCode == 201) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to create T1 form: ${response.body}');
  }
}

// Usage
final formData = {
  'status': 'draft',
  'personalInfo': {
    'firstName': 'Jane',
    'lastName': 'Doe',
    'sin': '123456789',
    // ... other fields
  },
  // ... other sections
};

final result = await createT1Form(formData);
print('Form ID: ${result['id']}');
```

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc (ReDoc)
- **Sample JSON:** See `T1_Personal_sample.json` in project root
- **Schema File:** `shared/t1_enhanced_schemas.py`
- **Routes File:** `shared/t1_routes.py`

---

## ✅ Checklist for Frontend Developers

- [ ] Use `/api/v1/t1-forms/` endpoints (NOT `/api/v1/tax/t1-personal`)
- [ ] Include JWT token in all requests
- [ ] Setup encryption for new users first
- [ ] Validate SIN format (9 digits)
- [ ] Validate phone format (+14165550123)
- [ ] Use ISO date format (YYYY-MM-DD)
- [ ] Handle validation errors properly
- [ ] Test with the provided sample JSON
- [ ] Check API docs at http://localhost:8000/docs

---

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   cd /home/cyberdude/Documents/Projects/taxease_backend
   python main.py
   ```

2. **Open API docs:**
   ```
   http://localhost:8000/docs
   ```

3. **Test endpoints in Swagger UI**

4. **Integrate with your frontend**

---

**Status:** ✅ API is ready for frontend integration!
