# 📘 API Documentation

## **Base URL**
```
https://ee736495b330.ngrok-free.app//api/v1
```

---

## **Authentication**

### 🔹 POST `/auth/register`
#### **Register User**
Creates a new user account with email verification.  
An OTP will be sent to the provided email address for verification.

#### **Request Body**
```json
{
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "phone": "string",
  "password": "string",
  "accept_terms": true
}
```

| Field | Type | Required | Description |
|--------|--------|-----------|-------------|
| `email` | string | ✅ | Valid email address (must be unique) |
| `first_name` | string | ✅ | User's first name |
| `last_name` | string | ✅ | User's last name |
| `password` | string | ✅ | Strong password (minimum 8 characters) |
| `phone` | string | ❌ | Optional phone number |
| `accept_terms` | boolean | ✅ | Must be true to register |

#### **Responses**
**201 – Successful Response**
```json
{
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "phone": "string",
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email_verified": true,
  "is_active": true,
  "created_at": "2025-11-05T21:56:34.371Z",
  "updated_at": "2025-11-05T21:56:34.371Z"
}
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 🔹 POST `/auth/login`
#### **Login User**
Authenticate a user and return access tokens.

Validates credentials and returns JWT tokens.

| Field | Type | Required | Description |
|--------|--------|-----------|-------------|
| `email` | string | ✅ | Registered email address |
| `password` | string | ✅ | User password |

#### **Request Body**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

#### **Responses**
**200 – Successful Response**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "string",
  "expires_in": 0
}
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 🔹 POST `/auth/request-otp`
#### **Request OTP**
Request OTP for email verification or password reset.

| Field | Type | Required | Description |
|--------|--------|-----------|-------------|
| `email` | string | ✅ | Email to send OTP to |
| `purpose` | string | ✅ | Either `"email_verification"` or `"password_reset"` |

#### **Request Body**
```json
{
  "email": "user@example.com",
  "purpose": "string"
}
```

#### **Responses**
**200 – Successful Response**
```json
{
  "message": "string",
  "success": true
}
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 🔹 POST `/auth/verify-otp`
#### **Verify OTP**
Verifies the OTP code sent to the user’s email and performs the requested action.

| Field | Type | Required | Description |
|--------|--------|-----------|-------------|
| `email` | string | ✅ | Email that received the OTP |
| `code` | string | ✅ | 6-digit OTP code |
| `purpose` | string | ✅ | Purpose of verification |

#### **Request Body**
```json
{
  "email": "user@example.com",
  "code": "string",
  "purpose": "string"
}
```

#### **Responses**
**200 – Successful Response**
```json
{
  "message": "string",
  "success": true
}
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 🔹 GET `/auth/me`
#### **Get Current User Info**
Returns the profile information of the currently authenticated user.  
Requires a valid **JWT access token** in the `Authorization` header.

#### **Headers**
| Header | Type | Required | Description |
|--------|--------|-----------|-------------|
| `Authorization` | string | ✅ | Bearer token |

#### **Responses**
**200 – Successful Response**
```json
{
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "phone": "string",
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email_verified": true,
  "is_active": true,
  "created_at": "2025-11-05T21:56:34.385Z",
  "updated_at": "2025-11-05T21:56:34.385Z"
}
```

## **File Management**

### 🔹 POST `/files/upload`
#### **Upload File**
Uploads a document file to AWS S3 and stores metadata in the database.  
Supported file types: **PDF, JPG, PNG, DOC, DOCX, XLS, XLSX.**  
Max file size: **10MB**

#### **Request Body**
**multipart/form-data**
| Field | Type | Required | Description |
|--------|--------|-----------|-------------|
| `file` | binary | ✅ | File to upload |

#### **Responses**
**201 – Successful Response**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "filename": "string",
  "original_filename": "string",
  "file_type": "string",
  "file_size": 0,
  "upload_status": "string",
  "created_at": "2025-11-06T18:07:39.608Z"
}
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 🔹 GET `/files`
#### **List User Files**
Get a paginated list of files uploaded by the current user.

#### **Query Parameters**
| Name | Type | Default | Description |
|------|------|----------|--------------|
| `skip` | integer | 0 | Number of records to skip |
| `limit` | integer | 50 | Max number of records (max 100) |

#### **Responses**
**200 – Successful Response**
```json
{
  "files": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "filename": "string",
      "original_filename": "string",
      "file_type": "string",
      "file_size": 0,
      "upload_status": "string",
      "created_at": "2025-11-06T18:07:39.614Z"
    }
  ],
  "total": 0
}
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 🔹 GET `/files/{file_id}`
#### **Get File Metadata**
Returns metadata information about a specific uploaded file.

| Parameter | Type | Location | Required | Description |
|------------|--------|-----------|-----------|-------------|
| `file_id` | string | path | ✅ | UUID of the file |

#### **Responses**
**200 – Successful Response**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "filename": "string",
  "original_filename": "string",
  "file_type": "string",
  "file_size": 0,
  "upload_status": "string",
  "created_at": "2025-11-06T18:07:39.619Z"
}
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 🔹 DELETE `/files/{file_id}`
#### **Delete File**
Permanently deletes a file from both cloud storage and the database.

| Parameter | Type | Location | Required | Description |
|------------|--------|-----------|-----------|-------------|
| `file_id` | string | path | ✅ | UUID of the file to delete |

#### **Responses**
**200 – Successful Response**
```json
{
  "message": "string",
  "success": true
}
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---

### 🔹 GET `/files/{file_id}/download`
#### **Download File**
Generates a presigned URL for downloading the file from cloud storage.

| Parameter | Type | Location | Required | Description |
|------------|--------|-----------|-----------|-------------|
| `file_id` | string | path | ✅ | UUID of the file to download |

#### **Responses**
**200 – Successful Response**
```json
"string"
```

**422 – Validation Error**
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```
