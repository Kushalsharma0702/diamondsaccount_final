# Authentication API Documentation

## Endpoints

### 1. Register (Sign Up)

**POST** `/api/v1/auth/register`

Creates a new user account matching the signup form fields.

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-555-123-4567",  // Optional
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"  // Must match password
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-555-123-4567",
  "message": "Account created successfully"
}
```

**Validation:**
- Password must be at least 6 characters
- `confirm_password` must match `password`
- Email must be unique (not already registered)

**Error Responses:**
- `400`: Passwords don't match, password too short, or email already exists

---

### 2. Login (Sign In)

**POST** `/api/v1/auth/login`

Signs in with email and password, matching the signin form fields.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "jwt-token-here",
  "refresh_token": "refresh-token-here",
  "token_type": "bearer",
  "expires_in": 1800  // 30 minutes in seconds
}
```

**Error Responses:**
- `401`: Invalid email or password, or account is deactivated

---

### 3. Request OTP

**POST** `/api/v1/auth/request-otp`

Requests a one-time password for email verification.

**Request Body:**
```json
{
  "email": "user@example.com",
  "purpose": "email_verification"  // or "password_reset"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP sent (static)",
  "success": true
}
```

**Note:** Currently uses static OTP `123456` for testing.

---

### 4. Verify OTP

**POST** `/api/v1/auth/verify-otp`

Verifies the OTP code and marks email as verified.

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "purpose": "email_verification"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP verified",
  "success": true
}
```

---

## Form Field Mapping

### Signup Form → API
- ✅ **First Name** → `first_name`
- ✅ **Last Name** → `last_name`
- ✅ **Email Address** → `email`
- ✅ **Phone Number** → `phone` (optional)
- ✅ **Password** → `password`
- ✅ **Confirm Password** → `confirm_password`
- ℹ️ **Terms & Conditions** → Not stored (frontend validation only)

### Signin Form → API
- ✅ **Email Address** → `email`
- ✅ **Password** → `password`

---

## Example Usage

### Complete Signup Flow

```bash
# 1. Register
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-123-4567",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'

# 2. Request OTP
curl -X POST http://localhost:8001/api/v1/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "purpose": "email_verification"
  }'

# 3. Verify OTP
curl -X POST http://localhost:8001/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "code": "123456",
    "purpose": "email_verification"
  }'
```

### Signin Flow

```bash
# Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# Use the access_token in subsequent requests:
curl -X GET http://localhost:8001/api/v1/client/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Security Notes

- Passwords are hashed using `bcrypt` before storage
- JWT tokens expire after 30 minutes
- Static OTP `123456` is used for development/testing only
- In production, implement proper OTP generation and email delivery







