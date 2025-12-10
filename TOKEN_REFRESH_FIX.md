# Token Refresh Fix - Automatic Token Refresh Implementation

## Problem
Users were experiencing "Token expired" errors when trying to upload files after their access token had expired. This required users to manually log in again, which is a poor user experience.

## Solution
Implemented automatic token refresh using a Dio interceptor that:
1. Detects 401 (Unauthorized) errors
2. Automatically refreshes the access token using the refresh token
3. Retries the failed request with the new token
4. Queues multiple requests if token refresh is in progress

## Implementation Details

### Backend Changes

#### 1. Refresh Token Endpoint (`/api/v1/auth/refresh`)
- **Location:** `client_side/main.py`
- **Method:** POST
- **Request Body:** `{ "refresh_token": "..." }`
- **Response:** `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 86400 }`
- Validates refresh token, verifies user is active, generates new tokens, and stores new refresh token in database

#### 2. OTP Verification Response Updated
- **Location:** `client_side/shared/schemas.py` and `client_side/main.py`
- Updated `OTPVerifyResponse` to include `refresh_token` field
- OTP verification endpoint now returns both access and refresh tokens

### Flutter Changes

#### 1. AuthInterceptor (`mobile-app/lib/core/network/auth_interceptor.dart`)
- **New file** - Dio interceptor for automatic token refresh
- Intercepts all HTTP requests/responses
- On 401 error:
  - Checks if refresh token exists
  - Calls `/auth/refresh` endpoint
  - Updates stored tokens
  - Retries original request
  - Queues multiple requests during refresh to avoid race conditions

#### 2. ThemeController Updates (`mobile-app/lib/core/theme/theme_controller.dart`)
- Added `_refreshToken` storage
- Added `setRefreshToken()` method
- Added `refreshToken` getter
- Updated `clearAuth()` to remove refresh token
- Updated `initialize()` to load refresh token from SharedPreferences

#### 3. FilesApi Updates (`mobile-app/lib/features/documents/data/files_api.dart`)
- Updated `_dio()` to use `AuthInterceptor`
- All file upload requests now automatically refresh tokens on expiry

#### 4. Auth Flow Updates
- **Login Page:** Stores refresh token after successful login
- **OTP Verification:** Stores refresh token after OTP verification
- **OTP API Service:** Added `verifyOtpWithFirebase()` method that returns `AuthResult` with refresh token

#### 5. API Endpoints (`mobile-app/lib/core/constants/api_endpoints.dart`)
- Added `REFRESH_TOKEN = '/auth/refresh'` constant

## How It Works

1. **User uploads file** → Request sent with access token
2. **Backend returns 401** → Token expired
3. **AuthInterceptor catches 401** → Checks for refresh token
4. **Calls `/auth/refresh`** → Gets new access token
5. **Updates stored tokens** → Saves new access and refresh tokens
6. **Retries original request** → Upload continues seamlessly
7. **User never notices** → Upload succeeds transparently

## Benefits

- ✅ **Seamless user experience** - No forced re-login
- ✅ **Automatic token refresh** - Handles token expiry transparently
- ✅ **Queue management** - Multiple requests handled correctly during refresh
- ✅ **Production ready** - Proper error handling and edge cases covered

## Testing

1. Log in to the app
2. Wait for access token to expire (or manually expire it)
3. Try to upload a file
4. Upload should succeed automatically without requiring re-login

## Files Changed

### Backend
- `client_side/main.py` - Added refresh endpoint
- `client_side/shared/schemas.py` - Added refresh_token to OTPVerifyResponse

### Flutter
- `mobile-app/lib/core/network/auth_interceptor.dart` - NEW FILE
- `mobile-app/lib/core/theme/theme_controller.dart` - Added refresh token storage
- `mobile-app/lib/features/documents/data/files_api.dart` - Added interceptor
- `mobile-app/lib/features/auth/presentation/pages/login_page.dart` - Store refresh token
- `mobile-app/lib/features/auth/presentation/pages/otp_verification_page.dart` - Store refresh token
- `mobile-app/lib/features/auth/data/otp_api_service.dart` - Added verifyOtpWithFirebase method
- `mobile-app/lib/core/constants/api_endpoints.dart` - Added REFRESH_TOKEN endpoint

## Next Steps

To use this in other API services, simply add the `AuthInterceptor` to your Dio instance:

```dart
static Dio _dio() {
  final dio = Dio(BaseOptions(...));
  dio.interceptors.add(AuthInterceptor());
  return dio;
}
```

All requests using this Dio instance will automatically refresh tokens on expiry!

