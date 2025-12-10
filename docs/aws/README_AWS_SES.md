# AWS SES OTP Integration - Complete Guide

## 🎯 Overview

This integration adds production-ready AWS SES email sending for OTP (One-Time Password) authentication. The system generates 6-digit OTPs, stores them securely, and sends professional emails via AWS Simple Email Service (SES).

---

## ✅ Implementation Summary

### **Files Created:**
1. **`client_side/shared/aws_ses_service.py`** - AWS SES email service implementation

### **Files Updated:**
1. **`client_side/shared/utils.py`** - Updated `EmailService` class to use AWS SES
2. **`client_side/main.py`** - Updated OTP expiry to 5 minutes

### **Features:**
✅ 6-digit numeric OTP (cryptographically secure)  
✅ 5-minute expiry (configurable)  
✅ AWS SES integration (production-ready)  
✅ Professional HTML email template  
✅ Comprehensive error handling  
✅ Development mode support  
✅ No breaking changes to existing code  

---

## 🚀 Quick Start (3 Steps)

### Step 1: Configure Environment Variables

Add to `client_side/.env`:

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

### Step 2: Verify Sender Email in AWS SES

1. Go to: https://console.aws.amazon.com/ses
2. Select region: **ca-central-1**
3. Navigate to: **Verified identities → Create identity**
4. Select **"Email address"**
5. Enter: `diamondacc.project@gmail.com`
6. Click **"Create identity"**
7. Check email inbox and click verification link

### Step 3: Install Dependencies

```bash
cd client_side
pip install boto3 botocore python-decouple
```

---

## 📧 Email Template

**Subject:** Your TaxEase Login OTP

**Content:**
- Professional HTML design with branded header
- Large, readable 6-digit OTP code display
- Clear 5-minute expiry notice
- Security disclaimer
- Plain text fallback for email clients

---

## 🔄 How It Works

### Signup Flow:
```
1. User registers → account created
2. OTP generated (6 digits, random) → stored in DB
3. Email sent via AWS SES → user receives OTP
4. User verifies OTP → account activated
```

### OTP Generation:
- **Length:** Exactly 6 digits (enforced)
- **Type:** Numeric only
- **Security:** Uses `secrets.choice()` for cryptographically strong randomness
- **Storage:** PostgreSQL database (`otps` table)
- **Expiry:** 5 minutes (configurable via `OTP_EXPIRY_MINUTES`)

### OTP Verification:
- Validates OTP code against database
- Checks expiry time (5 minutes)
- Marks OTP as used after verification
- Supports developer bypass (`123456` for testing)

---

## 🧪 Testing

### Development Mode (No AWS Required):
```env
DEVELOPMENT_MODE=true
```
When enabled, OTP is logged to console instead of being sent via email.

### Test OTP Sending:
```bash
# 1. Start backend
cd client_side
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001

# 2. Register user (OTP will be sent)
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

---

## 🔒 Security Features

1. **Cryptographically Secure OTP Generation**
   - Uses `secrets.choice()` for unpredictable randomness
   - Not guessable or predictable

2. **Single-Use OTPs**
   - Marked as used after verification
   - Prevents replay attacks

3. **Short Expiry Time**
   - 5-minute expiry prevents long-term abuse
   - Configurable via environment variable

4. **Email Validation**
   - Validates email format before sending
   - Checks AWS SES sending quota

5. **Error Handling**
   - Generic error messages (don't reveal if email exists)
   - Detailed logging server-side only

---

## 🐛 Troubleshooting

### OTP Email Not Received:

1. **Check AWS SES Console:**
   - Go to: AWS SES → Account dashboard
   - Check sending statistics
   - View rejected/bounced emails

2. **Verify Sender Email:**
   - Ensure `diamondacc.project@gmail.com` is verified
   - Check verification status in SES console

3. **Check Sandbox Mode:**
   - If in sandbox mode, can only send to verified emails
   - Request production access in SES console

4. **Review Backend Logs:**
   ```bash
   # Look for AWS SES errors
   grep -i "ses\|otp\|email" client_side/server.log
   ```

### Common Error Messages:

- **`MessageRejected`**: Email address not verified in SES sandbox mode
  - **Solution:** Verify recipient email in SES or request production access

- **`MailFromDomainNotVerified`**: Sender email/domain not verified
  - **Solution:** Verify sender email (`diamondacc.project@gmail.com`) in SES

- **`AccountSendingPausedException`**: Account sending is paused
  - **Solution:** Check AWS SES console and resume sending if needed

- **`InvalidCredentials`**: AWS credentials are incorrect
  - **Solution:** Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`

---

## 📋 API Endpoints

### Request OTP:
```
POST /api/v1/auth/request-otp
```
**Body:**
```json
{
  "email": "user@example.com",
  "purpose": "email_verification"
}
```

### Verify OTP:
```
POST /api/v1/auth/verify-otp
```
**Body:**
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

---

## 🎯 Production Checklist

- [ ] AWS SES sender email verified
- [ ] Production access requested (if in sandbox mode)
- [ ] Environment variables configured
- [ ] `DEVELOPMENT_MODE=false` in production
- [ ] AWS credentials secured (use environment variables or AWS Secrets Manager)
- [ ] Error monitoring set up for SES failures
- [ ] Rate limiting implemented (optional but recommended)
- [ ] OTP expiry set to 5 minutes
- [ ] Backend logs configured for debugging

---

## 📝 Configuration Options

### Environment Variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key | - | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | Yes |
| `AWS_REGION` | AWS region for SES | `ca-central-1` | No |
| `AWS_SES_FROM_EMAIL` | Sender email address | `diamondacc.project@gmail.com` | No |
| `OTP_EXPIRY_MINUTES` | OTP expiry time in minutes | `5` | No |
| `OTP_LENGTH` | OTP code length | `6` | No |
| `DEVELOPMENT_MODE` | Enable development mode | `false` | No |
| `DEVELOPER_OTP` | Developer bypass OTP | `123456` | No |

---

## 🚀 Next Steps

1. ✅ Configure environment variables in `.env`
2. ✅ Verify sender email in AWS SES console
3. ✅ Test OTP sending (use development mode first)
4. ✅ Request production access (if in sandbox mode)
5. ✅ Deploy to production (`DEVELOPMENT_MODE=false`)
6. ✅ Monitor AWS SES sending statistics

---

## 📚 Additional Resources

- **AWS SES Documentation:** https://docs.aws.amazon.com/ses/
- **AWS SES Console:** https://console.aws.amazon.com/ses
- **Boto3 SES Documentation:** https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html

---

**Integration Complete! 🎉**

Your AWS SES OTP system is now ready for production use. All existing authentication logic has been preserved, and the integration is backward compatible.

For detailed technical documentation, see: `AWS_SES_COMPLETE_INTEGRATION.md`

