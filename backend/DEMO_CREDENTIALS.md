# Demo Login Credentials

## For Development & Testing

These credentials are pre-created in the database for easy testing during development.

### Client Accounts

#### Demo User
- **Email:** `demo@taxease.com`
- **Password:** `Demo123!`
- **Role:** Client
- **Status:** Active, Email Verified

#### Test User
- **Email:** `test@taxease.com`
- **Password:** `Test123!`
- **Role:** Client
- **Status:** Active, Email Verified

### Admin Account

#### Admin User
- **Email:** `admin@taxease.com`
- **Password:** `Admin123!`
- **Role:** Admin
- **Status:** Active, Email Verified

## Usage

### Login via API

```bash
# Client login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@taxease.com",
    "password": "Demo123!"
  }'
```

### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Creating/Updating Demo Users

Run the script to create or update demo users:

```bash
python3 backend/create_demo_user.py
```

This will:
- Create new demo users if they don't exist
- Update existing demo users with correct passwords
- Create client records for client users

## Notes

- All demo users have `email_verified=True` and `is_active=True`
- Passwords are hashed using bcrypt
- Client users automatically get a client record created
- You can modify the credentials in `backend/create_demo_user.py`

## Security

⚠️ **These are for development only!**

- Never use these credentials in production
- Change passwords before deploying to production
- Consider removing demo users in production environments




