# Firebase + AWS SES OTP Authentication Flow Implementation

## Overview

This document describes the complete authentication flow that combines:
1. **Firebase Authentication** - For secure credential verification
2. **AWS SES OTP** - For additional security layer via email verification
3. **Backend JWT** - For session management and API access

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER LOGIN FLOW                          │
└─────────────────────────────────────────────────────────────┘

1. User enters email + password
   ↓
2. Flutter: Firebase Auth verifies credentials
   ↓
3. Flutter: Gets Firebase ID token
   ↓
4. Flutter: Sends Firebase ID token to backend /auth/request-otp
   ↓
5. Backend: Verifies Firebase token
   ↓
6. Backend: Generates 6-digit OTP
   ↓
7. Backend: Sends OTP via AWS SES to user's email
   ↓
8. User: Enters OTP code (6 digits)
   ↓
9. Flutter: Sends OTP + Firebase token to backend /auth/verify-otp
   ↓
10. Backend: Verifies OTP
    ↓
11. Backend: Generates and returns JWT token
    ↓
12. Flutter: Saves JWT to SharedPreferences
    ↓
13. User: Enters app dashboard
```

## Files Created/Modified

### Backend (FastAPI)

#### Modified Files:
1. **`client_side/shared/schemas.py`**
   - Added `firebase_id_token` (optional) to `OTPRequest` schema
   - Added `firebase_id_token` (optional) to `OTPVerify` schema
   - Added `OTPVerifyResponse` schema with `success`, `message`, and `token` fields

2. **`client_side/main.py`**
   - Updated `/auth/request-otp` endpoint:
     - Now accepts optional `firebase_id_token`
     - Verifies Firebase token before generating OTP
     - Validates Firebase email matches requested email
   - Updated `/auth/verify-otp` endpoint:
     - Now accepts optional `firebase_id_token`
     - Returns `OTPVerifyResponse` (includes JWT token)
     - If Firebase token provided:
       - Verifies Firebase token
       - Creates user if doesn't exist
       - Generates backend JWT token
       - Returns JWT token to client

### Flutter Mobile App

#### Created Files:
1. **`mobile-app/lib/features/auth/data/otp_api_service.dart`**
   - New service for Firebase-based OTP flow
   - Methods:
     - `requestOtpWithFirebase()` - Requests OTP with Firebase token
     - `verifyOtpAndGetToken()` - Verifies OTP and gets backend JWT

#### Modified Files:
1. **`mobile-app/lib/features/auth/presentation/pages/login_page.dart`**
   - Updated `_handleLogin()` method:
     - Step 1: Authenticate with Firebase (email/password)
     - Step 2: Get Firebase ID token
     - Step 3: Request OTP from backend with Firebase token
     - Step 4: Navigate to OTP verification screen

2. **`mobile-app/lib/features/auth/presentation/pages/otp_verification_page.dart`**
   - Added `firebaseIdToken` parameter to widget
   - Updated `_handleVerifyOtp()`:
     - Detects Firebase-based flow (if `firebaseIdToken` provided)
     - Calls `OtpApiService.verifyOtpAndGetToken()`
     - Saves backend JWT to SharedPreferences
     - Sets logged-in state
     - Navigates to dashboard
   - Updated `_handleResendCode()`:
     - Supports Firebase-based flow for resending OTP

3. **`mobile-app/lib/core/router/app_router.dart`**
   - Updated OTP verification route to accept `firebase_token` query parameter
   - Enhanced redirect logic to check for JWT token
   - Auto-redirects to home if JWT token exists

4. **`mobile-app/lib/core/theme/theme_controller.dart`**
   - Updated `initialize()` to set `isLoggedIn = true` if JWT token exists
   - Ensures users stay logged in after app restart

## API Endpoints

### POST `/api/v1/auth/request-otp`

**Request Body:**
```json
{
  "email": "user@example.com",
  "purpose": "email_verification",
  "firebase_id_token": "eyJhbGciOiJSUzI1NiIs..." // Optional for Firebase flow
}
```

**Response:**
```json
{
  "message": "OTP sent successfully"
}
```

**Behavior:**
- If `firebase_id_token` provided:
  - Verifies Firebase token
  - Validates email matches Firebase token email
  - Generates OTP
  - Sends OTP via AWS SES
- If `firebase_id_token` not provided:
  - Works as before (traditional flow)
  - Generates OTP
  - Sends OTP via AWS SES

### POST `/api/v1/auth/verify-otp`

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "purpose": "email_verification",
  "firebase_id_token": "eyJhbGciOiJSUzI1NiIs..." // Optional for Firebase flow
}
```

**Response (Firebase flow):**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "token": "eyJhbGciOiJIUzI1NiIs..." // Backend JWT token
}
```

**Response (Traditional flow):**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "token": null
}
```

**Behavior:**
- If `firebase_id_token` provided:
  - Verifies Firebase token
  - Verifies OTP code
  - Creates user if doesn't exist (from Firebase data)
  - Generates backend JWT token
  - Returns JWT token
- If `firebase_id_token` not provided:
  - Works as before (traditional flow)
  - Verifies OTP
  - Marks user as verified (if applicable)
  - No JWT token returned

## Security Features

1. **Firebase Token Verification**: Backend verifies Firebase ID token before processing OTP
2. **Email Validation**: Ensures Firebase token email matches requested email
3. **OTP Expiry**: OTP codes expire after 5 minutes
4. **OTP Single Use**: Each OTP code can only be used once
5. **JWT Token**: Secure backend-issued JWT for API access
6. **SharedPreferences**: JWT stored securely in Flutter app

## Backward Compatibility

✅ **All existing authentication flows continue to work:**
- Traditional SES OTP flow (without Firebase)
- AWS Cognito authentication
- Existing signup flows

✅ **Both flows can coexist:**
- Firebase-based OTP flow (new)
- Traditional OTP flow (existing)

## Testing

### Test Firebase Login Flow:

1. **Start Backend:**
   ```bash
   cd client_side
   python -m uvicorn main:app --reload --port 8001
   ```

2. **Start Flutter App:**
   ```bash
   cd mobile-app
   flutter run -d chrome
   ```

3. **Test Steps:**
   - Go to login page
   - Enter email and password (must be registered in Firebase)
   - Click "Sign In"
   - Firebase authenticates user
   - OTP is sent to email via AWS SES
   - Enter OTP code
   - Backend returns JWT token
   - User is redirected to dashboard

### Test Traditional Flow:

- The existing OTP flow (without Firebase) continues to work for signup verification
- No breaking changes to existing functionality

## Environment Variables

### Backend:
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase service account JSON
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `AWS_SES_REGION` - AWS SES region
- `DEVELOPER_OTP` - Development OTP bypass code (optional)

### Flutter:
- Firebase configuration is in `firebase_options.dart` (generated by FlutterFire CLI)

## Notes

- Firebase authentication is **optional** - app works without it
- If Firebase initialization fails, app continues with Cognito/SES only
- JWT tokens are stored in SharedPreferences with key `auth_token`
- Router automatically redirects logged-in users to dashboard
- All existing endpoints and logic remain unchanged

## Troubleshooting

### Issue: Firebase token verification fails
- **Solution**: Ensure `FIREBASE_CREDENTIALS_PATH` is set and points to valid service account JSON

### Issue: OTP not received
- **Solution**: Check AWS SES configuration and verify email address in SES sandbox (if in sandbox mode)

### Issue: JWT token not saved
- **Solution**: Check SharedPreferences permissions and ensure `ThemeController.setAuthToken()` is called

### Issue: User redirected to login after app restart
- **Solution**: Ensure `ThemeController.initialize()` is called in `main.dart` before `runApp()`

