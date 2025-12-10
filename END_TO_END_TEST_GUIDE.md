# End-to-End Testing Guide

## Quick Test - Complete Authentication Flow

### Prerequisites
- Backend running on `localhost:8001`
- Flutter app running in Chrome
- Firebase configured (optional - OTP flow works without it)

### Test Flow 1: Email/Password Login with OTP

1. **Go to Login Page:**
   - URL: `http://localhost:40743/#/login`

2. **Enter Credentials:**
   - Email: `kushalsharmacse@gmail.com` (or any Firebase-registered email)
   - Password: Your Firebase password

3. **Click "Sign In":**
   - Firebase authenticates user
   - Backend generates OTP
   - OTP email sent via AWS SES
   - User redirected to OTP verification screen

4. **Enter OTP:**
   - **Option A:** Check email for real OTP code
   - **Option B:** Use bypass code `698745` (always works)
   - Click "Verify & Continue"

5. **Expected Result:**
   - ✅ JWT token received
   - ✅ User redirected to dashboard (`/home`)
   - ✅ User logged in successfully

### Test Flow 2: Google Sign-In with OTP

1. **Go to Login Page**

2. **Click "Continue with Google" or "Login with Google (Test)"**

3. **Select Google Account:**
   - Google Sign-In popup appears
   - Select account (e.g., `kushalsharmacse@gmail.com`)

4. **If Firebase Admin SDK is configured:**
   - Backend verifies Firebase token
   - Returns JWT directly
   - User logged in

5. **If Firebase Admin SDK is NOT configured:**
   - Backend requests OTP
   - OTP email sent via AWS SES
   - User redirected to OTP verification screen
   - Enter bypass code `698745`
   - User logged in

### Test Flow 3: Signup with OTP

1. **Go to Signup Page:**
   - URL: `http://localhost:40743/#/signup`

2. **Fill Form:**
   - First Name: `Kushal`
   - Last Name: `Sharma`
   - Email: `kushalsharmacse@gmail.com`
   - Phone: `7983394461`
   - Password: Your password
   - Confirm Password: Same password
   - Accept Terms: ✓

3. **Click "Create Account":**
   - User registered in Firebase
   - OTP email sent
   - Redirected to OTP verification

4. **Enter OTP:**
   - Use bypass code: `698745`
   - Click "Verify & Continue"

5. **Expected Result:**
   - ✅ Account created
   - ✅ Email verified
   - ✅ Redirected to login

### Test Flow 4: Forgot Password

1. **Go to Forgot Password Page:**
   - URL: `http://localhost:40743/#/forgot-password`

2. **Enter Email:**
   - Email: `kushalsharmacse@gmail.com`
   - (Email validation should now work correctly)

3. **Click "Send Reset Link":**
   - Password reset OTP sent via email
   - Success message shown

## Bypass OTP Code

**Universal Bypass:** `698745`
- Always works
- No expiry
- Works for login, signup, password reset
- Works with Firebase-based flows

## Troubleshooting

### Issue: "Unable to connect to the server"
**Fix:** 
- Check backend is running: `ps aux | grep uvicorn`
- Verify API endpoint: `http://localhost:8001/api/v1`
- Hot restart Flutter app: Press `R` in terminal

### Issue: "Please enter a valid email"
**Fix:** 
- Email validation regex fixed
- Hot restart Flutter app: Press `R`

### Issue: "Firebase authentication is not configured"
**Fix:**
- This is OK - OTP flow will work instead
- Or set up Firebase Admin SDK:
  ```bash
  cd client_side
  ./setup_firebase.sh
  # Follow instructions to download service account JSON
  # Set FIREBASE_CREDENTIALS_PATH in .env
  ```

### Issue: AWS SES Email Not Received
**Fix:**
- Check AWS credentials in `.env`
- Verify sender email in SES console
- Use bypass code `698745` for testing

### Issue: OTP Verification Fails
**Fix:**
- Use bypass code `698745` (always works)
- Or check email for real OTP code
- Verify OTP hasn't expired (5 minutes)

## Complete Test Checklist

- [ ] Backend running on port 8001
- [ ] Flutter app running in Chrome
- [ ] Email validation works (no false errors)
- [ ] Login with email/password → OTP screen appears
- [ ] OTP email sent (or use bypass code)
- [ ] Bypass code `698745` works
- [ ] User logged in → Dashboard accessible
- [ ] Google Sign-In works (with or without Firebase Admin SDK)
- [ ] Signup flow works
- [ ] Forgot password works

## Quick Commands

```bash
# Start Backend
cd client_side
python -m uvicorn main:app --reload --port 8001

# Start Flutter App
cd mobile-app
flutter run -d chrome

# Test Email Delivery
cd client_side
python test_otp_email.py

# Check Backend Health
curl http://localhost:8001/api/v1/health
```

## Success Indicators

✅ No "Unable to connect" errors
✅ Email validation passes
✅ OTP screen appears after login
✅ Bypass code `698745` works
✅ User reaches dashboard
✅ JWT token stored in SharedPreferences

