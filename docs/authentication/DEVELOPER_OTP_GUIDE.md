# Developer OTP Guide

## ✅ Developer OTP Bypass Restored

The developer OTP bypass has been restored! You can now use a special OTP code for testing in the Flutter app.

## 🔑 Default Developer OTP

**Default Code:** `123456`

This OTP code will **always work** for any email address and doesn't require checking the database.

## 📱 How to Use in Flutter App

When you reach the OTP verification screen in the Flutter app:

1. **Enter the 6-digit code:** `123456`
   - Type `1` in the first field
   - Type `2` in the second field
   - Type `3` in the third field
   - Type `4` in the fourth field
   - Type `5` in the fifth field
   - Type `6` in the sixth field

2. **Tap "Verify & Continue"**

3. The verification will succeed immediately without needing to wait for an email!

## ⚙️ Configuration

The developer OTP can be customized by setting the `DEVELOPER_OTP` environment variable:

```bash
# In client_side/.env file
DEVELOPER_OTP=123456
```

Or when starting the server:
```bash
DEVELOPER_OTP=123456 python main.py
```

## 🔍 How It Works

The backend now checks for the developer OTP **before** checking the database:

- ✅ If the entered code matches `DEVELOPER_OTP` (default: `123456`), verification succeeds immediately
- ✅ Works for both `email_verification` and `password_reset` purposes
- ✅ Works for any email address
- ✅ No database lookup required

## 📝 Backend Implementation

The bypass is implemented in `/client_side/main.py` in the `verify_otp` endpoint:

```python
# Check for developer OTP bypass (always works)
if otp_data.code == DEVELOPER_OTP:
    # Verification succeeds immediately
    # User is marked as verified if email_verification purpose
    return MessageResponse(message="OTP verified successfully")
```

## 🚀 Quick Test

1. **Register/Sign up** in the Flutter app with your email
2. When prompted for OTP, enter: **`123456`**
3. Verification will succeed immediately!

---

**Note:** This bypass is intended for development/testing only. In production, make sure to disable or change the developer OTP.




