# Flutter Error Message Fix

## Issue
The Flutter frontend was showing generic error messages like "Invalid request. Please check your input and try again." instead of the actual error messages from the FastAPI backend.

## Root Cause
FastAPI returns errors in the format:
```json
{"detail": "Error message here"}
```

But the Flutter error handler (`ui_error.dart`) was only checking for:
```dart
data['message']
```

So it never extracted the actual error message and defaulted to generic messages.

## Fix Applied
Updated all Flutter error handler files to check for both `detail` and `message` fields:

```dart
if (data is Map) {
  // FastAPI returns errors in 'detail' field
  if (data['detail'] != null) {
    backendMessage = data['detail'].toString();
  } 
  // Some APIs may use 'message' field
  else if (data['message'] != null) {
    backendMessage = data['message'].toString();
  }
  // Handle nested error objects
  else if (data['error'] is Map && data['error']['detail'] != null) {
    backendMessage = data['error']['detail'].toString();
  }
}
```

## Files Updated
1. `client_side/tax_ease-main/lib/core/network/ui_error.dart`
2. `mobile-app/lib/core/network/ui_error.dart`
3. `frontend/tax_ease-main (1)/tax_ease-main/lib/core/network/ui_error.dart`

## Result
Now the Flutter app will display actual error messages from the backend, such as:
- "Unable to send verification email. The email address may need to be verified in AWS SES..."
- "Email already registered. Please sign in instead."
- "Password must contain at least one symbol character..."
- etc.

## Next Steps
1. Restart the Flutter app (hot reload should work)
2. Try registering again - you should now see the actual error messages
3. For SES permission errors, you'll need to either:
   - Verify the email in AWS SES console, OR
   - Update the Cognito Lambda role to allow sending to unverified addresses

