# Tax-Ease EC2 Deployment Guide

This guide helps you deploy the Tax-Ease backend services on an AWS EC2 instance.

## Prerequisites

- AWS EC2 instance (Ubuntu 20.04 or later recommended)
- At least 2GB RAM and 10GB storage
- PostgreSQL database (can be RDS or self-hosted)
- Security group allowing inbound traffic on ports 80, 8001, 8002

## Quick Start

### 1. Connect to EC2 Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Clone Repository

```bash
cd /home/ubuntu
git clone <your-repo-url>
cd CA-final
```

Or upload using SCP:

```bash
scp -i your-key.pem -r ./CA-final ubuntu@your-ec2-ip:/home/ubuntu/
```

### 3. Configure Environment

Create or update the `.env` file with your settings:

```bash
nano .env
```

**Required environment variables:**

```env
# Database Configuration (use your AWS RDS or EC2 PostgreSQL)
DB_HOST=16.52.182.106
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# JWT Secret (generate a strong random string)
JWT_SECRET=your-jwt-secret-min-32-chars-long
JWT_SECRET_KEY=your-jwt-secret-min-32-chars-long

# Encryption Key
ENCRYPTION_KEY=base64-encoded-32-byte-encryption-key

# CORS Origins (add your frontend URLs)
CORS_ORIGINS=http://localhost:8080,https://your-frontend-domain.com

# Optional: Redis for caching
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 4. Run Deployment Script

Make the script executable and run it:

```bash
chmod +x deploy_ec2.sh
sudo ./deploy_ec2.sh
```

The script will:
- ✅ Check system requirements
- ✅ Install dependencies
- ✅ Set up virtual environment
- ✅ Install Python packages
- ✅ Configure systemd services
- ✅ Start all services
- ✅ Set up Nginx reverse proxy
- ✅ Perform health checks

## Manual Deployment (Alternative)

If you prefer manual deployment:

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev \
    build-essential libpq-dev postgresql-client redis-server \
    nginx supervisor git curl
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
pip install -r services/admin-api/requirements.txt
```

### 4. Start Services Manually

**Admin API:**
```bash
cd services/admin-api
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Client API:**
```bash
cd /path/to/project
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8002
```

## Service Management

### Systemd Commands

```bash
# Start services
sudo systemctl start taxease-admin-api
sudo systemctl start taxease-client-api

# Stop services
sudo systemctl stop taxease-admin-api
sudo systemctl stop taxease-client-api

# Restart services
sudo systemctl restart taxease-admin-api
sudo systemctl restart taxease-client-api

# Check status
sudo systemctl status taxease-admin-api
sudo systemctl status taxease-client-api

# View logs
sudo journalctl -u taxease-admin-api -f
sudo journalctl -u taxease-client-api -f

# Enable services to start on boot
sudo systemctl enable taxease-admin-api
sudo systemctl enable taxease-client-api
```

## API Endpoints

After deployment, your APIs will be available at:

- **Admin API:** `http://your-ec2-ip:8001`
- **Client API:** `http://your-ec2-ip:8002`
- **Nginx Proxy:** `http://your-ec2-ip/api/v1/`

### API Documentation

- Admin API Docs: `http://your-ec2-ip:8001/docs`
- Client API Docs: `http://your-ec2-ip:8002/docs`

## Connecting Frontend

Update your frontend environment variables to point to the EC2 backend:

```javascript
// For React/Vue/Angular
VITE_API_BASE_URL=http://your-ec2-ip:8001/api/v1
REACT_APP_API_URL=http://your-ec2-ip:8001/api/v1

// Or use Nginx proxy
VITE_API_BASE_URL=http://your-ec2-ip/api/v1/admin
```

## Security Group Configuration

Ensure your EC2 security group allows:

| Type | Protocol | Port Range | Source |
|------|----------|------------|--------|
| HTTP | TCP | 80 | 0.0.0.0/0 |
| Custom TCP | TCP | 8001 | 0.0.0.0/0 |
| Custom TCP | TCP | 8002 | 0.0.0.0/0 |
| SSH | TCP | 22 | Your IP |

## Database Migration

If you need to migrate your local database to AWS RDS:

```bash
# Export from local
pg_dump -h localhost -U postgres -d CA_Project > backup.sql

# Import to RDS
psql -h your-rds-endpoint -U postgres -d postgres -f backup.sql
```

## Nginx Configuration

The deployment script sets up Nginx as a reverse proxy. Configuration file:

```bash
sudo nano /etc/nginx/sites-available/taxease
```

Reload Nginx after changes:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring & Logs

### Log Files

- Admin API: `/var/log/taxease/admin-api.log`
- Client API: `/var/log/taxease/client-api.log`
- Nginx: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

### View Real-time Logs

```bash
# Admin API logs
tail -f /var/log/taxease/admin-api.log

# Client API logs
tail -f /var/log/taxease/client-api.log

# All services
sudo journalctl -u taxease-* -f
```

## Troubleshooting

### Services won't start

1. Check logs:
   ```bash
   sudo journalctl -u taxease-admin-api -n 50
   sudo journalctl -u taxease-client-api -n 50
   ```

2. Verify database connection:
   ```bash
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME
   ```

3. Check port availability:
   ```bash
   sudo lsof -i :8001
   sudo lsof -i :8002
   ```

### Database connection errors

- Verify database credentials in `.env`
- Check security groups allow PostgreSQL port (5432)
- Ensure database is accessible from EC2

### Permission errors

```bash
sudo chown -R $USER:$USER /opt/taxease
sudo chown -R $USER:$USER /var/log/taxease
```

### Restart all services

```bash
sudo systemctl restart taxease-admin-api taxease-client-api nginx redis-server
```

## Performance Tuning

### Increase Workers

Edit systemd service files:

```bash
sudo nano /etc/systemd/system/taxease-admin-api.service
```

Change `--workers 2` to `--workers 4` (based on CPU cores)

```bash
sudo systemctl daemon-reload
sudo systemctl restart taxease-admin-api
```

### Enable HTTPS

Use Certbot for Let's Encrypt SSL:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Updating Deployment

To update after code changes:

```bash
cd /opt/taxease
git pull origin main

# Reinstall dependencies if requirements.txt changed
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r services/admin-api/requirements.txt

# Restart services
sudo systemctl restart taxease-admin-api taxease-client-api
```

## Environment-Specific Settings

### Production

Update `.env`:

```env
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=https://your-production-domain.com
```

### Staging

```env
DEBUG=true
ENVIRONMENT=staging
```

## Backup & Recovery

### Backup Database

```bash
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$(date +%Y%m%d).sql
```

### Backup Configuration

```bash
tar -czf taxease-config-backup.tar.gz /opt/taxease/.env /etc/systemd/system/taxease-*
```

## Support

For issues or questions:
- Check logs first
- Review this documentation
- Contact system administrator

## License

Copyright © 2026 Tax-Ease. All rights reserved.
