# Starting the Tax Hub Dashboard Application

## Quick Start Commands

### 1. Start Backend Server

```bash
cd tax-hub-dashboard/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or using the startup script:
```bash
cd tax-hub-dashboard/backend
./start.sh
```

Or run in background:
```bash
cd tax-hub-dashboard/backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

### 2. Start Frontend Server

```bash
cd tax-hub-dashboard
npm run dev
```

Or run in background:
```bash
cd tax-hub-dashboard
nohup npm run dev > frontend.log 2>&1 &
```

## Service URLs

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend Dashboard**: http://localhost:5173

## Login Credentials

- **Email**: superadmin@taxease.ca
- **Password**: demo123

## Testing

Run the API test script:
```bash
cd tax-hub-dashboard
./test_api.sh
```

## Check Status

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:5173

# Check processes
ps aux | grep uvicorn
ps aux | grep vite
```

## Stop Services

```bash
# Stop backend
pkill -f "uvicorn app.main:app"

# Stop frontend
pkill -f "vite"
```

## Troubleshooting

### Backend Issues

1. **Database connection error**: Check PostgreSQL is running and DATABASE_URL in `.env`
2. **Redis connection error**: Check Redis is running (`redis-cli ping`)
3. **Port 8000 in use**: Kill existing process or use different port

### Frontend Issues

1. **Port 5173 in use**: Vite will automatically use next available port
2. **API connection error**: Check VITE_API_BASE_URL in `.env` file
3. **CORS errors**: Check CORS_ORIGINS in backend `.env`

## Logs

- Backend logs: `tax-hub-dashboard/backend/backend.log`
- Frontend logs: Console output or `tax-hub-dashboard/frontend.log`




