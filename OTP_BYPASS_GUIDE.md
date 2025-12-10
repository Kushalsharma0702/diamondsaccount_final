# OTP Bypass Guide

## Overview

The authentication system includes bypass OTP codes for testing and development purposes. These codes allow you to skip the actual email OTP verification while still completing the authentication flow.

## Bypass OTP Codes

### Universal Bypass Code: `698745`
- **Always works** in all authentication flows
- Works with Firebase-based authentication
- Works with traditional authentication
- Works in both development and production environments
- Can be used for any OTP verification (login, signup, password reset)

### Developer OTP: `123456` (Legacy)
- Also always works
- Maintained for backward compatibility
- Same functionality as universal bypass

## How to Use

### During Login Flow:

1. **User logs in with email/password:**
   - Firebase authenticates the user
   - Backend generates OTP and sends via email

2. **User is redirected to OTP verification screen**

3. **Instead of checking email, user enters bypass code:**
   - Enter: `698745`
   - Click "Verify & Continue"

4. **Backend validates bypass code:**
   - ✅ Bypass code is accepted
   - ✅ Firebase token is verified (if provided)
   - ✅ User is authenticated
   - ✅ Backend JWT token is returned
   - ✅ User is redirected to dashboard

### During Signup Flow:

1. **User signs up**
2. **OTP verification screen appears**
3. **Enter bypass code:** `698745`
4. **Verification succeeds → User can proceed**

## Configuration

The bypass OTP code is configurable via environment variable:

```bash
# In .env file
BYPASS_OTP=698745  # Default value
```

To disable the bypass (not recommended for development), you can:
- Remove the bypass code check from the code (requires code changes)
- Or set a random string that won't be guessed

## Security Notes

⚠️ **Important Security Considerations:**

1. **Development/Testing Only:**
   - Bypass codes should primarily be used in development/testing
   - For production, consider disabling or restricting access

2. **Firebase Authentication Still Required:**
   - The bypass code does NOT skip Firebase authentication
   - User must still authenticate with Firebase first
   - Bypass code only skips the email OTP verification step

3. **Email Still Sent:**
   - Even when using bypass code, the actual OTP email is still sent
   - This ensures the email delivery system is working

## Code Flow

### Without Bypass (Normal Flow):
```
User Login → Firebase Auth → OTP Generated → Email Sent → 
User Enters Real OTP → Verified → JWT Token → Dashboard
```

### With Bypass (Testing Flow):
```
User Login → Firebase Auth → OTP Generated → Email Sent → 
User Enters Bypass Code (698745) → Bypass Accepted → 
JWT Token → Dashboard
```

## Testing

### Test Bypass Code:
1. Start the application
2. Go to login page
3. Enter email/password
4. On OTP screen, enter: `698745`
5. Should immediately authenticate and redirect to dashboard

### Verify It Works:
- Check logs for: `✅ Bypass OTP matched!`
- User should be authenticated successfully
- JWT token should be returned
- Dashboard should be accessible

## Error Messages

If you see an error when using the bypass code:
- **"Invalid or expired OTP"** → Code entered incorrectly (check for spaces, typos)
- **"Firebase token email does not match"** → Email mismatch issue (bypass works, but Firebase validation failed)

## Troubleshooting

### Bypass Code Not Working:

1. **Check Code Format:**
   - Must be exactly: `698745`
   - No spaces before/after
   - All digits

2. **Check Logs:**
   ```bash
   # Look for bypass OTP log messages
   grep "Bypass OTP" logs/application.log
   ```

3. **Verify Environment Variable:**
   ```bash
   # Check if BYPASS_OTP is set correctly
   echo $BYPASS_OTP
   ```

4. **Check Code Implementation:**
   - Ensure bypass check is in `verify_otp` endpoint
   - Verify `BYPASS_OTP` constant is imported correctly

## Production Considerations

For production deployment:

1. **Keep Bypass Enabled:** (Recommended for support/troubleshooting)
   - Useful for customer support scenarios
   - Can help with account recovery
   - Only bypasses OTP, not Firebase authentication

2. **Restrict Bypass Access:** (More secure)
   - Only allow from specific IPs
   - Require admin/support role
   - Log all bypass usage for audit

3. **Disable Bypass:** (Most secure)
   - Remove bypass code checks
   - Require real OTP verification
   - Ensure email delivery is 100% reliable

## Summary

- **Bypass Code:** `698745`
- **Always Works:** Yes
- **Skips Email Check:** Yes
- **Requires Firebase Auth:** Yes
- **Production Ready:** Yes (with considerations above)

Use this bypass code whenever you need to test the authentication flow without waiting for emails!

