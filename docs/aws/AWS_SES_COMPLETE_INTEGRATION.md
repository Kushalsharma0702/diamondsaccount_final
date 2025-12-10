# AWS SES OTP Integration - Complete Production Guide

## ✅ Step-by-Step AWS SES Setup Instructions

### Step 1: Verify Sender Email in AWS SES

1. **Login to AWS Console:**
   - Go to: https://console.aws.amazon.com/ses
   - Select region: **ca-central-1** (Canada Central)

2. **Verify Sender Email:**
   - Navigate to: **SES → Verified identities → Create identity**
   - Select **"Email address"**
   - Enter: `diamondacc.project@gmail.com`
   - Click **"Create identity"**
   - Check your email inbox and click the verification link

3. **Request Production Access (Optional but Recommended):**
   - If in sandbox mode, request production access:
     - Go to: **SES → Account dashboard → Request production access**
     - Fill out the form with your use case
   - **Note:** Sandbox mode only allows sending to verified emails

### Step 2: Verify IAM Permissions

Your AWS credentials already have SES permissions. Ensure they have:
- `ses:SendEmail`
- `ses:SendRawEmail`
- `ses:GetSendQuota`

---

## ✅ Step 2: Environment Configuration

Add these to your `.env` file in `client_side/` directory:

```env
# AWS SES Configuration
AWS_ACCESS_KEY_ID=AKIA3BMJ25BIYDGPA47X
AWS_SECRET_ACCESS_KEY=BDSPNqu7MlgZ38C1yPMEOZ2X43DgvpJYOMc4ddVA1CJl
AWS_REGION=ca-central-1
AWS_SES_FROM_EMAIL=diamondacc.project@gmail.com

# OTP Configuration
OTP_EXPIRY_MINUTES=5
OTP_LENGTH=6

# Development Mode (set to false for production)
DEVELOPMENT_MODE=false
DEVELOPER_OTP=123456
SKIP_EMAIL_VERIFICATION=false
```

---

## ✅ Step 3: Python Dependencies

Ensure these packages are installed in your `requirements.txt`:

```txt
boto3>=1.28.0
botocore>=1.31.0
python-decouple>=3.8
```

Install dependencies:
```bash
cd client_side
pip install -r requirements.txt
```

---

## ✅ Step 4: Code Files Created/Updated

### Files Created:
1. **`client_side/shared/aws_ses_service.py`** - AWS SES email service implementation
2. **`AWS_SES_COMPLETE_INTEGRATION.md`** - This documentation

### Files Updated:
1. **`client_side/shared/utils.py`** - Updated `EmailService` to use AWS SES
2. **`client_side/main.py`** - Updated OTP expiry to 5 minutes

---

## ✅ Step 5: OTP Generation & Storage

### OTP Generation Function
- **Location:** `client_side/shared/utils.py`
- **Function:** `generate_otp(length=6)`
- **Details:**
  - Exactly 6 digits, numeric only
  - Uses `secrets.choice()` for cryptographically strong randomness
  - Random and unpredictable

### OTP Storage
- **Location:** Database table `otps`
- **Expiry:** 5 minutes (configurable via `OTP_EXPIRY_MINUTES`)
- **Fields:** email, code, purpose, expires_at, used

---

## ✅ Step 6: AWS SES Email Sending Function

### Implementation Details:
- **File:** `client_side/shared/aws_ses_service.py`
- **Class:** `AWSEmailService`
- **Method:** `send_otp_email(email, otp_code, purpose)`

### Email Template:
- **Subject:** "Your TaxEase Login OTP"
- **Body:** Professional HTML email with:
  - Branded header
  - Large, readable OTP code display
  - 5-minute expiry notice
  - Security disclaimer
  - Plain text fallback

### Error Handling:
- Invalid AWS credentials
- SES service errors
- Network failures
- Sandbox mode restrictions
- Account sending paused

---

## ✅ Step 7: Integration Points

### Signup Flow:
```python
# In register_user endpoint:
1. User registers → creates account
2. Calls send_verification_otp() → generates 6-digit OTP
3. Stores OTP in DB with 5-minute expiry
4. Calls email_service.send_otp_email() → sends via AWS SES
5. User receives email with OTP
```

### Login Flow:
```python
# Currently login doesn't require OTP by default
# To add OTP on login, modify login_user endpoint
```

### Email Verification:
```python
# In verify_otp endpoint:
1. User submits OTP code
2. System verifies OTP (checks DB, expiry, used status)
3. Marks OTP as used
4. Marks user email as verified
```

---

## ✅ Step 8: Verification API Endpoint

### Existing Endpoint:
```
POST /api/v1/auth/verify-otp
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "purpose": "email_verification"
}
```

**Response:**
```json
{
  "message": "OTP verified successfully"
}
```

**Error Responses:**
- `400`: Invalid or expired OTP
- `401`: Invalid token (if authentication required)

---

## ✅ Step 9: Testing the Integration

### Test OTP Sending:
```bash
# 1. Start your backend
cd client_side
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001

# 2. Register a new user (OTP will be sent)
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456",
    "first_name": "Test",
    "last_name": "User",
    "accept_terms": true
  }'

# 3. Check email inbox for OTP

# 4. Verify OTP
curl -X POST http://localhost:8001/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "purpose": "email_verification"
  }'
```

### Development Mode Testing:
```env
DEVELOPMENT_MODE=true
```
When enabled, OTP is logged to console instead of being sent via email.

---

## ✅ Step 10: Production Checklist

- [ ] AWS SES sender email verified
- [ ] Production access requested (if needed)
- [ ] Environment variables configured
- [ ] `DEVELOPMENT_MODE=false` in production
- [ ] AWS credentials secured (use AWS Secrets Manager or environment variables)
- [ ] Error monitoring set up for SES failures
- [ ] OTP expiry set to 5 minutes
- [ ] Rate limiting implemented (optional but recommended)

---

## 🔒 Security Best Practices

1. **Never commit AWS credentials to Git**
   - Use environment variables
   - Use AWS Secrets Manager in production

2. **OTP Security:**
   - 6 digits, numeric only
   - 5-minute expiry
   - Single use (marked as used after verification)
   - Cryptographically random generation

3. **Rate Limiting:**
   - Limit OTP requests per email/IP
   - Prevent OTP brute force attacks

4. **Error Handling:**
   - Don't reveal if email exists
   - Generic error messages for invalid OTP
   - Log detailed errors server-side only

---

## 🐛 Troubleshooting

### OTP Email Not Received:
1. **Check AWS SES Console:**
   - Verify sender email is verified
   - Check if account is in sandbox mode
   - View sending statistics

2. **Check Backend Logs:**
   ```bash
   # Look for AWS SES errors
   grep -i "ses\|otp\|email" client_side/server.log
   ```

3. **Common Issues:**
   - **Sandbox Mode:** Can only send to verified emails
   - **Unverified Sender:** Sender email must be verified
   - **Invalid Credentials:** Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   - **Wrong Region:** Ensure AWS_REGION matches SES region

### Error Messages:
- `MessageRejected`: Email not verified in sandbox mode
- `MailFromDomainNotVerified`: Sender email/domain not verified
- `AccountSendingPausedException`: Account sending is paused

---

## 📝 Summary

✅ **AWS SES Integration Complete:**
- OTP generation (6 digits, cryptographically random)
- OTP storage (5-minute expiry in database)
- AWS SES email sending (production-ready)
- Professional email template
- Error handling and logging
- Development mode support
- Existing authentication logic preserved

✅ **No Breaking Changes:**
- Existing API endpoints unchanged
- Existing authentication flow intact
- Developer OTP bypass still works
- All existing features preserved

---

## 🚀 Next Steps

1. **Configure Environment Variables:** Add AWS credentials to `.env`
2. **Verify Sender Email:** Verify `diamondacc.project@gmail.com` in AWS SES
3. **Test OTP Sending:** Register a new user and check email
4. **Deploy to Production:** Set `DEVELOPMENT_MODE=false` and deploy

---

**Integration Complete! Your AWS SES OTP system is ready for production use.**

