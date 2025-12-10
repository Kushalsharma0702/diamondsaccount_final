# AWS Cognito Authentication Setup Guide

## Current Configuration

- **User Pool ID**: `ca-central-1_FP2WE41eW`
- **User Pool Name**: `caxmb4`
- **App Client Name**: `TaxEaseApp`
- **Client ID**: `504mgtvq1h97vlml90c3iibnt0`

## Required Authentication Flows

For the backend FastAPI application to work with Cognito, the following authentication flows **MUST** be enabled:

### ✅ Required: ALLOW_USER_PASSWORD_AUTH
- **What it is**: Allows server-side authentication with username and password
- **Why needed**: Our FastAPI backend uses `initiate_auth` with `USER_PASSWORD_AUTH` flow
- **Status**: Check the console to ensure this is enabled

### Other Flows (Optional but Recommended)
- `ALLOW_USER_SRP_AUTH` - For client-side SRP authentication
- `ALLOW_REFRESH_TOKEN_AUTH` - For token refresh (usually enabled by default)
- `ALLOW_ADMIN_USER_PASSWORD_AUTH` - For admin operations (optional)

## How to Enable USER_PASSWORD_AUTH

1. **Go to AWS Cognito Console**
   - Navigate to: https://console.aws.amazon.com/cognito/v2/idp/user-pools
   - Select region: **Canada (Central) - ca-central-1**

2. **Select Your User Pool**
   - Click on: **caxmb4** (User pool - caxmb4)

3. **Go to App Clients**
   - In the left sidebar, click **App clients**
   - Click on: **TaxEaseApp**

4. **Edit App Client**
   - Click the **Edit** button (or "Edit app client information")

5. **Enable Authentication Flow**
   - Under **Authentication flows** section
   - ✅ Check: **"Sign in with username and password: ALLOW_USER_PASSWORD_AUTH"**
   - Make sure this checkbox is checked/enabled

6. **Save Changes**
   - Click **Save changes** at the bottom

## Verify Configuration

After enabling, you can verify by:

1. **Check the App Client Info page**
   - Under "Authentication flows", you should see: **Username and password**

2. **Run the test script**
   ```bash
   python3 scripts/testing/verify_cognito_config.py
   ```

3. **Test login**
   ```bash
   python3 scripts/testing/test_auth_automated.py
   ```

## Current Token Settings

Based on your console:
- **Authentication flow session duration**: 3 minutes
- **Refresh token expiration**: 5 days
- **Access token expiration**: 60 minutes
- **ID token expiration**: 60 minutes

These settings are fine for production use.

## Troubleshooting

### Error: "USER_PASSWORD_AUTH flow not enabled"
- **Solution**: Follow steps 1-6 above to enable `ALLOW_USER_PASSWORD_AUTH`

### Error: "InvalidSignatureException"
- **Cause**: AWS credentials not configured properly
- **Solution**: Ensure `.env` has valid `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### Error: "UserNotConfirmedException" during login
- **Cause**: User email not verified
- **Solution**: User must verify email via OTP before login

### Error: "NotAuthorizedException" during login
- **Cause**: Incorrect email or password
- **Solution**: Verify credentials, or reset password if needed

## Test Commands

```bash
# Send OTP to specific email
python3 scripts/testing/send_otp_to_email.py

# Full automated test
python3 scripts/testing/test_auth_automated.py

# Interactive test suite
python3 scripts/testing/test_cognito_auth.py

# Verify Cognito configuration
python3 scripts/testing/verify_cognito_config.py
```

## Notes

- The app client must have `ALLOW_USER_PASSWORD_AUTH` enabled for server-side authentication
- OTP verification uses Cognito's `confirm_sign_up` which works independently
- Once enabled, restart the backend to ensure changes take effect

