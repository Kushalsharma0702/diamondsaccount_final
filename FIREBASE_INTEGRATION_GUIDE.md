# Firebase Authentication Integration Guide

## Overview

Firebase Authentication has been integrated into the TaxEase application **ALONGSIDE** the existing AWS Cognito/SES OTP flow. Both authentication methods work independently and can be used simultaneously.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter Mobile App                        │
├─────────────────────────────────────────────────────────────┤
│  Firebase Auth (NEW)          │  Cognito/SES OTP (EXISTING) │
│  • Email/Password              │  • Email/Password            │
│  • Google Sign-In              │  • OTP Verification          │
└──────────────┬────────────────┴──────────────┬──────────────┘
               │                               │
               │ Firebase ID Token             │ Cognito Token
               │                               │
┌──────────────▼───────────────────────────────▼──────────────┐
│                  FastAPI Backend                             │
├─────────────────────────────────────────────────────────────┤
│  Firebase Verification       │  Cognito Verification        │
│  ↓                           │  ↓                           │
│  Backend JWT Tokens          │  Backend JWT Tokens          │
└─────────────────────────────────────────────────────────────┘
```

## What Was Added

### Flutter App (`mobile-app/`)

1. **Dependencies Added** (`pubspec.yaml`):
   - `firebase_core: ^3.6.0`
   - `firebase_auth: ^5.3.1`
   - `google_sign_in: ^6.2.1`
   - `flutterfire_cli: ^0.3.6` (dev dependency)

2. **New Files Created**:
   - `lib/core/firebase/firebase_service.dart` - Firebase authentication service
   - `lib/core/firebase/firebase_options.dart` - Firebase configuration (needs generation)
   - `lib/core/logger/app_logger.dart` - Logging utility

3. **Files Modified**:
   - `lib/main.dart` - Added Firebase initialization
   - `lib/features/auth/data/auth_api.dart` - Added Firebase auth methods
   - `lib/core/constants/api_endpoints.dart` - Added Firebase endpoints

### Backend (`client_side/`)

1. **New Files Created**:
   - `shared/firebase_service.py` - Firebase Admin SDK integration

2. **Files Modified**:
   - `main.py` - Added Firebase auth routes:
     - `POST /api/v1/auth/firebase-register`
     - `POST /api/v1/auth/firebase-login`
     - `POST /api/v1/auth/google-login`
   - `shared/schemas.py` - Added Firebase request schemas

3. **Dependencies**:
   - `firebase-admin==7.0.0` added to `requirements.txt`

## Setup Instructions

### 1. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing: `taxease-ec35f`
3. Enable Authentication:
   - Go to Authentication → Sign-in method
   - Enable "Email/Password"
   - Enable "Google" sign-in provider

### 2. Flutter App Configuration

#### Generate Firebase Configuration

```bash
cd mobile-app

# Install FlutterFire CLI globally (if not already installed)
dart pub global activate flutterfire_cli

# Configure Firebase for your Flutter app
flutterfire configure --project=taxease-ec35f
```

This will:
- Generate `lib/core/firebase/firebase_options.dart` with platform-specific configs
- Add Firebase configuration files to Android/iOS/Web projects

#### Android Configuration

1. Download `google-services.json` from Firebase Console
2. Place it in `mobile-app/android/app/`

#### iOS Configuration

1. Download `GoogleService-Info.plist` from Firebase Console
2. Place it in `mobile-app/ios/Runner/`
3. Add to Xcode project

#### Web Configuration

Firebase configuration is automatically added via `flutterfire configure`.

### 3. Backend Configuration

#### Install Firebase Admin SDK

```bash
cd client_side
source venv/bin/activate  # or your virtual environment
pip install firebase-admin==7.0.0
```

#### Get Firebase Service Account Credentials

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Download the JSON file (e.g., `taxease-firebase-adminsdk.json`)
4. Place it in a secure location (e.g., `client_side/config/`)
5. **IMPORTANT**: Add to `.gitignore` to prevent committing secrets

#### Configure Environment Variables

Add to `client_side/.env`:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=taxease-ec35f
FIREBASE_CREDENTIALS_PATH=config/taxease-firebase-adminsdk.json
```

Alternatively, if running in Google Cloud, Firebase Admin SDK will use default credentials automatically.

### 4. Google Sign-In Setup (Optional)

#### Android

1. Go to Firebase Console → Authentication → Sign-in method → Google
2. Copy the SHA-1 certificate fingerprint:
   ```bash
   cd mobile-app/android
   ./gradlew signingReport
   ```
3. Add SHA-1 to Firebase Console

#### iOS

1. Add your iOS app's Bundle ID to Firebase Console
2. Download updated `GoogleService-Info.plist`

## Usage

### Flutter: Firebase Email/Password Registration

```dart
import 'package:tax_ease/core/firebase/firebase_service.dart';
import 'package:tax_ease/features/auth/data/auth_api.dart';

// Step 1: Create user in Firebase
final firebaseResult = await FirebaseService.createUserWithEmailAndPassword(
  email: 'user@example.com',
  password: 'SecurePassword123!',
);

// Step 2: Exchange Firebase ID token for backend JWT
final authResult = await AuthApi.registerWithFirebase(
  email: 'user@example.com',
  firstName: 'John',
  lastName: 'Doe',
  password: 'SecurePassword123!',
  acceptTerms: true,
);

// Firebase automatically sends verification email
// User can verify via Firebase or continue with SES OTP flow
```

### Flutter: Firebase Login

```dart
// Step 1: Sign in with Firebase
final firebaseResult = await FirebaseService.signInWithEmailAndPassword(
  email: 'user@example.com',
  password: 'SecurePassword123!',
);

// Step 2: Get ID token and exchange for backend JWT
final idToken = await FirebaseService.getIdToken();
final authResult = await AuthApi.loginWithFirebase(
  firebaseIdToken: idToken!,
);
```

### Flutter: Google Sign-In

```dart
// Step 1: Sign in with Google (via Firebase)
final firebaseResult = await FirebaseService.signInWithGoogle();

// Step 2: Exchange Firebase ID token for backend JWT
final idToken = firebaseResult.idToken;
final authResult = await AuthApi.loginWithGoogle(
  firebaseIdToken: idToken!,
);
```

### Backend: Token Verification

The backend automatically verifies Firebase ID tokens using Firebase Admin SDK:

```python
from shared.firebase_service import get_firebase_service

firebase_service = get_firebase_service()
decoded_token = firebase_service.verify_id_token(firebase_id_token)

# Returns:
# {
#   'uid': 'firebase-user-id',
#   'email': 'user@example.com',
#   'email_verified': True,
#   'name': 'John Doe',
#   ...
# }
```

## API Endpoints

### POST `/api/v1/auth/firebase-register`

Register user with Firebase Email/Password.

**Request:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePassword123!",
  "phone": "+1234567890",
  "accept_terms": true,
  "firebase_id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "id_token": null
}
```

### POST `/api/v1/auth/firebase-login`

Login with Firebase ID token.

**Request:**
```json
{
  "firebase_id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

**Response:** Same as above.

### POST `/api/v1/auth/google-login`

Login with Google Sign-In (Firebase).

**Request:**
```json
{
  "firebase_id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

**Response:** Same as above.

## Existing Authentication (Untouched)

All existing authentication methods continue to work:

- `POST /api/v1/auth/register` - Cognito registration
- `POST /api/v1/auth/login` - Cognito login
- `POST /api/v1/auth/request-otp` - SES OTP request
- `POST /api/v1/auth/verify-otp` - SES OTP verification

## Dual Authentication Flow

Users can now choose between:

1. **Firebase Authentication**:
   - Email/Password (Firebase handles verification emails)
   - Google Sign-In
   - Fast, modern authentication

2. **Cognito/SES OTP**:
   - Email/Password (backend handles authentication)
   - OTP verification via AWS SES
   - Full control over authentication flow

Both methods result in backend JWT tokens that work with all existing API endpoints.

## Security Considerations

1. **Firebase Admin SDK**: Keep service account credentials secure
2. **ID Token Verification**: Always verify Firebase ID tokens on backend
3. **User Records**: Backend creates user records for both methods
4. **Email Verification**: Firebase handles its own, SES OTP still works independently

## Troubleshooting

### Firebase Not Initialized

**Error**: `Firebase not initialized`

**Solution**: 
- Run `flutterfire configure --project=taxease-ec35f`
- Ensure `firebase_options.dart` is generated correctly

### Firebase Admin SDK Not Available

**Error**: `Firebase authentication is not configured`

**Solution**:
- Install: `pip install firebase-admin`
- Configure `FIREBASE_CREDENTIALS_PATH` in `.env`
- Ensure service account JSON file exists

### Google Sign-In Fails

**Error**: `Google Sign-In failed`

**Solution**:
- Verify SHA-1 certificate in Firebase Console (Android)
- Ensure Bundle ID matches (iOS)
- Check Google Sign-In is enabled in Firebase Console

## Next Steps

1. ✅ Run `flutterfire configure` to generate Firebase config
2. ✅ Download Firebase service account credentials
3. ✅ Update `.env` with Firebase configuration
4. ✅ Install `firebase-admin` in backend
5. ✅ Test Firebase authentication flow
6. ✅ Test Google Sign-In
7. ✅ Verify existing Cognito/SES flow still works

## Notes

- Firebase and Cognito/SES can coexist without conflicts
- Users registered via Firebase can also use SES OTP (if backend supports it)
- Backend JWT tokens work identically regardless of authentication method
- All existing API endpoints remain unchanged

