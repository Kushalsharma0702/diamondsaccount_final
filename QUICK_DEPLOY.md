# EC2 Deployment Quick Reference

## Files Created
- ✅ `deploy_ec2.sh` - Main deployment script (11 automated steps)
- ✅ `pre_deploy_check.sh` - Pre-deployment validation
- ✅ `DEPLOYMENT_GUIDE.md` - Comprehensive deployment documentation
- ✅ `backend/requirements.txt` - Complete Python dependencies (30 packages)

## Quick Deployment Steps

### Option 1: Automated Deployment (Recommended)
```bash
# 1. Run pre-deployment checks locally
./pre_deploy_check.sh

# 2. Upload to EC2
scp -r . ubuntu@YOUR_EC2_IP:/home/ubuntu/taxease

# 3. SSH to EC2
ssh ubuntu@YOUR_EC2_IP

# 4. Run deployment script
cd /home/ubuntu/taxease
sudo ./deploy_ec2.sh
```

### Option 2: Manual Step-by-Step
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed manual deployment.

## Current Configuration

### Database (AWS RDS)
- **Host**: 16.52.182.106:5432
- **Database**: postgres
- **Connection**: ✅ Verified and migrated

### Services
- **Admin API**: Port 8001 (FastAPI)
- **Client API**: Port 8002 (FastAPI)
- **Admin Dashboard**: Port 8080 (React/Vite)

### Backend URLs (After EC2 Deployment)
Update frontend `.env` with:
```env
VITE_ADMIN_API_URL=http://YOUR_EC2_IP:8001/api/v1
VITE_CLIENT_API_URL=http://YOUR_EC2_IP:8002/api/v1
```

## EC2 Security Group Requirements
| Port | Service | Protocol | Source |
|------|---------|----------|--------|
| 22 | SSH | TCP | Your IP |
| 80 | HTTP | TCP | 0.0.0.0/0 |
| 443 | HTTPS | TCP | 0.0.0.0/0 |
| 8001 | Admin API | TCP | 0.0.0.0/0 |
| 8002 | Client API | TCP | 0.0.0.0/0 |
| 8080 | Dashboard | TCP | 0.0.0.0/0 |

## Post-Deployment Verification

### Check Services
```bash
# Check service status
sudo systemctl status taxease-admin-api
sudo systemctl status taxease-client-api

# View logs
sudo journalctl -u taxease-admin-api -f
sudo journalctl -u taxease-client-api -f
```

### Test APIs
```bash
# Admin API health check
curl http://localhost:8001/health

# Client API health check  
curl http://localhost:8002/health

# Test login
curl -X POST http://localhost:8001/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@taxease.ca","password":"admin123"}'
```

### Check Nginx
```bash
sudo nginx -t
sudo systemctl status nginx
```

## Troubleshooting Commands

### Service Management
```bash
# Restart services
sudo systemctl restart taxease-admin-api
sudo systemctl restart taxease-client-api
sudo systemctl restart nginx

# Stop services
sudo systemctl stop taxease-admin-api
sudo systemctl stop taxease-client-api

# View full logs
sudo journalctl -u taxease-admin-api --no-pager
sudo journalctl -u taxease-client-api --no-pager
```

### Database Issues
```bash
# Test database connection
PGPASSWORD=Diamondaccount321 psql -h 16.52.182.106 -U postgres -d postgres -c "SELECT version();"

# Check tables
PGPASSWORD=Diamondaccount321 psql -h 16.52.182.106 -U postgres -d postgres -c "\dt"
```

### Port Issues
```bash
# Check if ports are listening
sudo netstat -tuln | grep -E ':(8001|8002|8080)'

# Check what's using a port
sudo lsof -i :8001
sudo lsof -i :8002
```

### Process Management
```bash
# Kill stuck processes
sudo pkill -f "uvicorn.*8001"
sudo pkill -f "uvicorn.*8002"

# Check Python processes
ps aux | grep uvicorn
```

## Environment Variables Check
```bash
# Verify .env is loaded
cat .env | grep -E '(DB_HOST|DB_NAME|JWT_SECRET|DATABASE_URL)'

# Test environment in Python
cd /home/ubuntu/taxease
source venv/bin/activate
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DB_HOST:', os.getenv('DB_HOST'))"
```

## Performance Monitoring
```bash
# CPU and Memory
top
htop  # if installed

# Disk usage
df -h
du -sh /home/ubuntu/taxease/*

# Service resource usage
systemctl status taxease-admin-api | grep -E '(Memory|CPU)'
```

## Important Paths
```
/home/ubuntu/taxease/                    # Project root
/home/ubuntu/taxease/venv/               # Virtual environment
/home/ubuntu/taxease/logs/               # Application logs
/etc/systemd/system/taxease-*.service    # Service files
/etc/nginx/sites-available/taxease       # Nginx config
/var/log/nginx/                          # Nginx logs
```

## Support Files
- **Full Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **API Docs**: [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
- **Testing Guide**: [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)

## Common Issues

### Issue: Services won't start
```bash
# Check permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/taxease

# Check virtual environment
source /home/ubuntu/taxease/venv/bin/activate
python3 -c "import uvicorn; print(uvicorn.__version__)"
```

### Issue: Database connection fails
```bash
# Verify AWS RDS security group allows EC2 IP
# Check EC2's public IP
curl http://checkip.amazonaws.com

# Test from EC2
PGPASSWORD=Diamondaccount321 psql -h 16.52.182.106 -U postgres -d postgres
```

### Issue: Frontend can't connect to backend
1. Check EC2 security groups allow ports 8001, 8002
2. Verify frontend .env has correct EC2 public IP
3. Test from browser: `http://YOUR_EC2_IP:8001/docs`

### Issue: Nginx 502 Bad Gateway
```bash
# Check backend services are running
curl http://localhost:8001/health
curl http://localhost:8002/health

# Check Nginx config
sudo nginx -t

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

## Deployment Checklist
- [ ] Run `./pre_deploy_check.sh` locally
- [ ] Upload project to EC2
- [ ] Run `sudo ./deploy_ec2.sh` on EC2
- [ ] Configure EC2 security groups (ports 80, 8001, 8002, 8080)
- [ ] Update frontend `.env` with EC2 IP
- [ ] Test API endpoints from browser
- [ ] Verify admin login works
- [ ] Check document upload/download
- [ ] Monitor service logs for 10 minutes
- [ ] Setup CloudWatch alarms (optional)
- [ ] Configure SSL with Let's Encrypt (optional)

## Next Steps After Deployment
1. **SSL Certificate**: Use certbot for HTTPS
2. **Domain Setup**: Point domain to EC2 IP
3. **Monitoring**: Setup CloudWatch or Datadog
4. **Backups**: Configure automated database backups
5. **Auto-scaling**: Consider ECS/EKS for production scale
