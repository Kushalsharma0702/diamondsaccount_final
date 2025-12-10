# Production Deployment Checklist - Firebase + AWS SES OTP Authentication

## Pre-Deployment Configuration

### 1. Environment Variables (.env file)

Create/update `client_side/.env` with production values:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# AWS SES Configuration (REQUIRED for email delivery)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=ca-central-1
AWS_SES_FROM_EMAIL=your-verified-email@domain.com

# Firebase Configuration (REQUIRED for Firebase Auth)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-service-account.json
FIREBASE_PROJECT_ID=taxease-ec35f

# Production Settings
DEVELOPMENT_MODE=false
DEVELOPER_OTP=123456  # Only works if DEVELOPMENT_MODE=true

# JWT Configuration
SECRET_KEY=your-strong-random-secret-key-here  # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration (Update with your production domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Admin Backend Sync (Optional)
ADMIN_BACKEND_URL=https://admin.yourdomain.com
```

### 2. AWS SES Setup

#### Step 1: Verify Sender Email
1. Go to [AWS SES Console](https://console.aws.amazon.com/ses/)
2. Select region: **ca-central-1**
3. Click **Verified identities** → **Create identity**
4. Choose **Email address**
5. Enter your sender email (e.g., `diamondacc.project@gmail.com`)
6. Verify the email by clicking the verification link

#### Step 2: Request Production Access (if in Sandbox)
1. In SES Console, click **Account dashboard**
2. Click **Request production access**
3. Fill out the form:
   - Mail Type: Transactional
   - Website URL: Your production URL
   - Use case: User authentication OTP emails
   - Expected sending volume: Estimate your daily emails
4. Submit request (usually approved within 24 hours)

#### Step 3: Verify Recipient Emails (Sandbox Mode Only)
- In sandbox mode, you can only send to verified emails
- Add recipient emails in **Verified identities**
- Or request production access to send to any email

#### Step 4: Configure IAM User
1. Create IAM user with `AmazonSESFullAccess` policy
2. Generate Access Key ID and Secret Access Key
3. Add to `.env` file

### 3. Firebase Setup

#### Step 1: Download Service Account Key
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: **taxease-ec35f**
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate new private key**
5. Save the JSON file securely
6. Update `FIREBASE_CREDENTIALS_PATH` in `.env`

#### Step 2: Verify Firebase Auth is Enabled
1. Go to **Authentication** → **Sign-in method**
2. Enable **Email/Password** provider
3. Enable **Google** provider (if using Google Sign-In)
4. Configure authorized domains

### 4. Database Setup

#### PostgreSQL Configuration
```sql
-- Ensure database exists
CREATE DATABASE taxease_production;

-- Run migrations (if using Alembic)
alembic upgrade head

-- Or create tables manually from models
```

### 5. Flutter Web Configuration

#### Update API Endpoint
Update `mobile-app/lib/core/constants/api_endpoints.dart`:
```dart
static const String BASE_URL = 'https://api.yourdomain.com/api/v1';
```

#### Update Google Sign-In Client ID
Update `mobile-app/web/index.html`:
```html
<meta name="google-signin-client_id" content="YOUR_WEB_CLIENT_ID.apps.googleusercontent.com">
```

## Deployment Steps

### Backend Deployment (FastAPI)

1. **Install Dependencies:**
   ```bash
   cd client_side
   pip install -r requirements.txt
   ```

2. **Set Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Run Database Migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start Application:**
   ```bash
   # Using uvicorn
   uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
   
   # Or using gunicorn (recommended for production)
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
   ```

5. **Set up Reverse Proxy (Nginx):**
   ```nginx
   server {
       listen 80;
       server_name api.yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

6. **Set up SSL (Let's Encrypt):**
   ```bash
   certbot --nginx -d api.yourdomain.com
   ```

### Frontend Deployment (Flutter Web)

1. **Build for Production:**
   ```bash
   cd mobile-app
   flutter build web --release
   ```

2. **Deploy to Web Server:**
   - Copy `build/web/` contents to your web server
   - Configure Nginx/Apache to serve static files
   - Enable HTTPS

3. **Configure Nginx:**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       
       location / {
           root /var/www/taxease/build/web;
           try_files $uri $uri/ /index.html;
       }
   }
   ```

## Post-Deployment Testing

### Test Email Delivery

1. **Test OTP Email:**
   ```bash
   # Use curl or Postman
   curl -X POST https://api.yourdomain.com/api/v1/auth/request-otp \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@yourdomain.com",
       "purpose": "email_verification",
       "firebase_id_token": "YOUR_FIREBASE_TOKEN"
     }'
   ```

2. **Check Email Inbox:**
   - Verify OTP email is received
   - Check spam folder if not received
   - Verify email formatting looks correct

### Test Authentication Flow

1. **Test Email/Password Login:**
   - User enters email + password
   - Firebase authenticates
   - Backend sends OTP via SES
   - User receives OTP email
   - User enters OTP
   - Backend returns JWT token
   - User accesses dashboard

2. **Test Google Sign-In:**
   - User clicks "Sign in with Google"
   - Google authentication popup appears
   - User selects account
   - Backend sends OTP via SES
   - User receives OTP email
   - User enters OTP
   - Backend returns JWT token

## Monitoring & Logging

### Check Logs

1. **Backend Logs:**
   ```bash
   # If using systemd service
   journalctl -u taxease-backend -f
   
   # Or check application logs
   tail -f /var/log/taxease/backend.log
   ```

2. **Email Delivery Logs:**
   - Check AWS CloudWatch for SES metrics
   - Monitor bounce/complaint rates
   - Set up SNS notifications for bounces

### Key Metrics to Monitor

- OTP generation rate
- Email delivery success rate
- OTP verification success rate
- Failed authentication attempts
- AWS SES sending quota usage

## Security Checklist

- [ ] HTTPS enabled for all endpoints
- [ ] CORS configured with specific origins
- [ ] JWT secret key is strong and unique
- [ ] Database credentials secured
- [ ] AWS credentials not in code (use environment variables)
- [ ] Firebase service account JSON secured
- [ ] OTP expiry set to 5 minutes
- [ ] Rate limiting implemented (if needed)
- [ ] Error messages don't leak sensitive information
- [ ] Input validation on all endpoints

## Troubleshooting

### OTP Email Not Received

1. **Check AWS SES Status:**
   - Verify sender email is verified
   - Check if account is in sandbox mode
   - Verify recipient email is verified (if in sandbox)

2. **Check Logs:**
   ```bash
   # Look for email sending errors
   grep "OTP email" /var/log/taxease/backend.log
   ```

3. **Test SES Directly:**
   ```python
   import boto3
   ses = boto3.client('ses', region_name='ca-central-1')
   ses.send_email(...)
   ```

### Firebase Authentication Fails

1. **Verify Firebase Credentials:**
   - Check service account JSON path
   - Verify JSON file is valid
   - Check Firebase project ID matches

2. **Check Firebase Console:**
   - Verify Authentication is enabled
   - Check authorized domains
   - Verify API keys are correct

### Database Connection Issues

1. **Test Connection:**
   ```python
   from sqlalchemy import create_engine
   engine = create_engine(DATABASE_URL)
   engine.connect()
   ```

2. **Check Connection Pool:**
   - Adjust pool size in database URL
   - Monitor connection usage

## Rollback Plan

1. Keep previous version ready
2. Maintain database backups
3. Document configuration changes
4. Test rollback procedure before deploying

## Support

For issues:
- Check application logs
- Review AWS CloudWatch metrics
- Verify environment variables
- Test endpoints individually
- Check Firebase Console for auth issues

