# Tax Hub Dashboard Backend Setup Guide

Complete setup guide for the Python FastAPI backend with Redis caching.

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Node.js 18+ (for frontend)

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd tax-hub-dashboard/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```sql
-- Create PostgreSQL database
CREATE DATABASE taxhub_db;

-- Or using psql command line
createdb taxhub_db
```

### 3. Redis Setup

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 4. Environment Configuration

Create a `.env` file in the `backend/` directory:

```bash
# Application
DEBUG=False
APP_NAME=Tax Hub Dashboard API

# Database - Update with your credentials
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/taxhub_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_CACHE_TTL=3600

# Security - Generate a new secret key!
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS - Add your frontend URLs
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:5174"]
FRONTEND_URL=http://localhost:5173

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

**Generate a secure secret key:**
```bash
openssl rand -hex 32
```

### 5. Initialize Database and Create Superadmin

```bash
# Create superadmin user
python create_superadmin.py
```

This will create:
- Email: `superadmin@taxease.ca`
- Password: `demo123`

**Important:** Change the password after first login in production!

### 6. Start the Backend Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 7. Frontend Configuration

Update the frontend to connect to the backend:

1. Create `.env` file in `tax-hub-dashboard/` directory:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

2. Update `vite.config.ts` if needed to proxy API requests.

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login with email/password
- `GET /api/v1/auth/me` - Get current user (requires auth)

### Clients
- `GET /api/v1/clients?page=1&page_size=20&status=...&year=...&search=...`
- `GET /api/v1/clients/{id}`
- `POST /api/v1/clients`
- `PATCH /api/v1/clients/{id}`
- `DELETE /api/v1/clients/{id}`

### Admin Users (Superadmin only)
- `GET /api/v1/admin-users`
- `GET /api/v1/admin-users/{id}`
- `POST /api/v1/admin-users`
- `PATCH /api/v1/admin-users/{id}`
- `DELETE /api/v1/admin-users/{id}`

### Documents
- `GET /api/v1/documents?status=...&search=...&client_id=...`
- `POST /api/v1/documents`
- `DELETE /api/v1/documents/{id}`

### Payments
- `GET /api/v1/payments?client_id=...`
- `POST /api/v1/payments`

### Analytics
- `GET /api/v1/analytics` - Dashboard analytics

### Audit Logs (Superadmin only)
- `GET /api/v1/audit-logs?page=1&page_size=50&entity_type=...&action=...`

## Testing the API

### Using curl:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@taxease.ca","password":"demo123"}'

# Get clients (use token from login)
curl -X GET http://localhost:8000/api/v1/clients \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using the Swagger UI:

Visit http://localhost:8000/docs for interactive API documentation.

## Troubleshooting

### Database Connection Issues

1. Verify PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

2. Check database exists:
```bash
psql -U postgres -l | grep taxhub_db
```

3. Verify connection string in `.env`

### Redis Connection Issues

1. Check Redis is running:
```bash
redis-cli ping
```

2. Verify Redis host/port in `.env`

3. Check Redis logs:
```bash
redis-cli monitor
```

### Port Already in Use

If port 8000 is in use:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process or use different port
uvicorn app.main:app --port 8001
```

### Import Errors

Make sure you're in the virtual environment:
```bash
which python  # Should show venv path
pip list      # Should show installed packages
```

## Production Deployment

### Environment Variables

Set all environment variables properly:
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- Never commit `.env` files to version control
- Use different databases for dev/staging/prod

### Database Migrations

For production, use Alembic migrations:

```bash
# Initialize (if not done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Performance Tuning

1. **Database Connection Pooling:**
   - Adjust `pool_size` and `max_overflow` in `database.py`

2. **Redis Caching:**
   - Adjust `REDIS_CACHE_TTL` for different data types
   - Use Redis Cluster for high availability

3. **Worker Processes:**
   - Use `--workers 4` for CPU-bound operations
   - Consider using Gunicorn with Uvicorn workers

### Security Checklist

- [ ] Change default superadmin password
- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS/TLS
- [ ] Configure proper CORS origins
- [ ] Set DEBUG=False
- [ ] Use environment variables for secrets
- [ ] Enable database SSL
- [ ] Set up rate limiting
- [ ] Enable request logging
- [ ] Set up monitoring/alerting

## Architecture Notes

### Redis Caching Strategy

- Analytics data cached for 1 hour
- Client lists can be cached (invalidated on updates)
- Admin user data cached (invalidated on updates)
- Cache invalidation on mutations

### Database Models

- AdminUser: Admin accounts with role-based permissions
- Client: Tax filing clients
- Document: Client documents
- Payment: Payment records
- AuditLog: Action tracking
- CostEstimate: Cost estimates
- Note: Client notes

### Security

- JWT tokens with expiration
- Bcrypt password hashing
- Role-based access control (RBAC)
- Audit logging for all actions
- SQL injection protection via ORM
- CORS protection

## Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review logs for errors
3. Check database/Redis connectivity
4. Verify environment variables

## Next Steps

1. Create additional admin users via API or admin panel
2. Import initial client data
3. Configure Flutter frontend API endpoints
4. Set up CI/CD pipeline
5. Configure monitoring and logging




