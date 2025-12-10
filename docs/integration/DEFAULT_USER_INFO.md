# Default Developer User

## ✅ User Created Successfully!

A default developer user has been created in the database for easy testing.

## Login Credentials

- **Email:** `Developer@aurocode.app`
- **Password:** `Developer@123`

## User Details

- **Name:** Developer User
- **Email Verified:** ✅ Yes
- **Account Status:** ✅ Active
- **Can Login:** ✅ Yes

## How to Use

### In Flutter App:
1. Open the login screen
2. Enter email: `Developer@aurocode.app`
3. Enter password: `Developer@123`
4. Tap "Login"
5. ✅ You'll be logged in immediately!

### Via API:
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "Developer@aurocode.app",
    "password": "Developer@123"
  }'
```

## Recreate User (if needed)

If you need to recreate the user (e.g., after database reset):

```bash
cd client_side
python3 create_default_user.py
```

The script will:
- Check if the user already exists
- Create the user if it doesn't exist
- Update the user if it exists (ensures password is correct)

## Notes

- The email is stored in lowercase in the database: `developer@aurocode.app`
- Login works with both: `Developer@aurocode.app` or `developer@aurocode.app`
- The password is securely hashed using bcrypt
- This user is automatically verified (no OTP needed for login)

---

**This user is intended for development/testing purposes only.**




