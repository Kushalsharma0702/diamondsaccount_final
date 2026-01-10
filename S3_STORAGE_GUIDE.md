# S3 Storage Integration Guide

## Overview
Your Tax-Ease application now supports AWS S3 for document storage with automatic encryption.

## Configuration

### Environment Variables (Already set in `.env`)
```env
# AWS Configuration
AWS_REGION=ca-central-1
S3_BUCKET_NAME=taxease-prod-documents

# Enable S3 storage
USE_S3_STORAGE=true

# AWS Credentials (optional if using EC2 IAM role)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

## Features

### ✅ Automatic Storage Selection
- **S3 Mode**: When `USE_S3_STORAGE=true` - uploads to S3 bucket
- **Local Mode**: When `USE_S3_STORAGE=false` - uploads to `./storage/uploads`

### ✅ End-to-End Encryption
- Files are encrypted **before** upload using your `FILE_ENCRYPTION_KEY`
- S3 server-side encryption (AES256) adds an extra layer
- Files stored as `*.enc` to indicate encryption

### ✅ Seamless Migration
- Existing local files continue to work
- New uploads go to S3 automatically
- No code changes needed in API consumers

## S3 Bucket Setup (AWS Console)

### 1. Create S3 Bucket
```bash
aws s3 mb s3://taxease-prod-documents --region ca-central-1
```

### 2. Configure Bucket Policy (if using EC2 IAM role)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR-ACCOUNT-ID:role/YOUR-EC2-ROLE"
            },
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::taxease-prod-documents/*",
                "arn:aws:s3:::taxease-prod-documents"
            ]
        }
    ]
}
```

### 3. Enable Server-Side Encryption
```bash
aws s3api put-bucket-encryption \
    --bucket taxease-prod-documents \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'
```

### 4. Block Public Access (Recommended)
```bash
aws s3api put-public-access-block \
    --bucket taxease-prod-documents \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

## EC2 IAM Role Setup (Recommended)

Instead of storing AWS credentials in `.env`, use an IAM role:

### 1. Create IAM Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::taxease-prod-documents/*",
                "arn:aws:s3:::taxease-prod-documents"
            ]
        }
    ]
}
```

### 2. Create IAM Role
- AWS Console → IAM → Roles → Create Role
- Trusted entity: EC2
- Attach the policy created above
- Name: `TaxEase-EC2-S3-Access`

### 3. Attach Role to EC2
- EC2 Console → Select your instance → Actions → Security → Modify IAM role
- Select `TaxEase-EC2-S3-Access`

### 4. Update `.env` on EC2
```env
# Remove or leave empty when using IAM role
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
USE_S3_STORAGE=true
```

## API Endpoints (No Changes)

Your existing API endpoints work without modification:

```bash
# Upload document (automatically goes to S3)
curl -X POST http://localhost:8002/api/v1/documents/upload \
  -F "file=@document.pdf" \
  -F "client_id=123" \
  -F "section=income"

# Download document (automatically fetches from S3)
curl http://localhost:8002/api/v1/documents/{document_id}/download

# Delete document (automatically deletes from S3)
curl -X DELETE http://localhost:8002/api/v1/documents/{document_id}
```

## File Structure in S3

```
s3://taxease-prod-documents/
  └── documents/
      ├── 550e8400-e29b-41d4-a716-446655440000.pdf.enc
      ├── 6ba7b810-9dad-11d1-80b4-00c04fd430c8.jpg.enc
      └── 7c9e6679-7425-40de-944b-e07fc1f90ae7.docx.enc
```

## Testing S3 Integration

### 1. Test Upload
```bash
# Upload a test file
curl -X POST http://localhost:8002/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf" \
  -F "client_id=test-client-id" \
  -F "section=test"
```

### 2. Verify in S3
```bash
# List files in bucket
aws s3 ls s3://taxease-prod-documents/documents/

# Download a file to verify
aws s3 cp s3://taxease-prod-documents/documents/FILENAME.enc ./test.enc
```

### 3. Test Download
```bash
curl http://localhost:8002/api/v1/documents/{document_id}/download \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output downloaded.pdf
```

## Monitoring & Costs

### S3 Storage Costs (ca-central-1)
- **Storage**: ~$0.0255/GB/month
- **PUT requests**: $0.0055 per 1,000 requests
- **GET requests**: $0.00044 per 1,000 requests

### Example Cost for 1,000 documents (5MB average)
- Storage: 5GB × $0.0255 = **$0.13/month**
- Uploads: 1,000 × $0.0000055 = **$0.006**
- Downloads: 5,000 × $0.00000044 = **$0.002**
- **Total: ~$0.14/month**

### CloudWatch Metrics
Monitor S3 usage:
```bash
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name BucketSizeBytes \
    --dimensions Name=BucketName,Value=taxease-prod-documents \
    --start-time 2026-01-01T00:00:00Z \
    --end-time 2026-01-31T23:59:59Z \
    --period 86400 \
    --statistics Average
```

## Troubleshooting

### Issue: "Access Denied" errors
**Solution**: Check IAM role permissions or AWS credentials in `.env`

```bash
# Test AWS credentials
aws sts get-caller-identity

# Test bucket access
aws s3 ls s3://taxease-prod-documents/
```

### Issue: "Bucket does not exist"
**Solution**: Create the bucket first

```bash
aws s3 mb s3://taxease-prod-documents --region ca-central-1
```

### Issue: Files uploading to local storage instead of S3
**Solution**: Verify `USE_S3_STORAGE=true` in `.env`

```bash
# Check environment variable
grep USE_S3_STORAGE .env
```

### Issue: "No credentials found"
**Solution**: Either set AWS credentials in `.env` or attach IAM role to EC2

## Migration from Local to S3

### Option 1: Sync Existing Files
```bash
# Upload existing local files to S3
aws s3 sync ./storage/uploads s3://taxease-prod-documents/documents/

# Update database file_path from local to S3 keys
# Run SQL migration (see below)
```

### SQL Migration Script
```sql
-- Update file_path from local paths to S3 keys
UPDATE documents
SET file_path = CONCAT('documents/', 
    SUBSTRING(file_path FROM '[^/]+$'))
WHERE file_path LIKE './storage/uploads/%';
```

### Option 2: Keep Existing, New to S3
- Leave existing documents in local storage
- New uploads automatically go to S3
- The storage service handles both transparently

## Security Best Practices

1. ✅ **Use IAM Roles** - Don't store credentials in `.env`
2. ✅ **Enable Encryption** - Both application-level and S3 SSE
3. ✅ **Block Public Access** - Keep bucket private
4. ✅ **Versioning** - Enable S3 versioning for backup
5. ✅ **Lifecycle Policies** - Archive old files to Glacier
6. ✅ **Access Logging** - Monitor bucket access
7. ✅ **VPC Endpoint** - Use S3 VPC endpoint for private traffic

### Enable S3 Versioning
```bash
aws s3api put-bucket-versioning \
    --bucket taxease-prod-documents \
    --versioning-configuration Status=Enabled
```

### Enable Access Logging
```bash
aws s3api put-bucket-logging \
    --bucket taxease-prod-documents \
    --bucket-logging-status '{
        "LoggingEnabled": {
            "TargetBucket": "taxease-logs",
            "TargetPrefix": "s3-access/"
        }
    }'
```

## Deployment Checklist

- [ ] Create S3 bucket: `taxease-prod-documents`
- [ ] Enable server-side encryption (AES256)
- [ ] Block public access
- [ ] Create IAM role with S3 permissions
- [ ] Attach IAM role to EC2 instance
- [ ] Update `.env` with `USE_S3_STORAGE=true`
- [ ] Install boto3: `pip install boto3`
- [ ] Restart backend services
- [ ] Test file upload/download
- [ ] Monitor S3 bucket in AWS Console
- [ ] Setup CloudWatch alarms for storage costs
- [ ] Enable S3 versioning (optional)
- [ ] Configure lifecycle policies (optional)

## Support

For issues, check logs:
```bash
# Backend logs
sudo journalctl -u taxease-client-api -f | grep -i s3

# Python shell test
python3
>>> from backend.app.utils.s3_storage import get_storage_service
>>> storage = get_storage_service()
>>> print(storage.use_s3)
>>> print(storage.bucket_name)
```
