# 🚀 Quick Start Guide

## Start All Services

Use the convenience script to start everything:

```bash
cd tax-hub-dashboard
./start-all.sh
```

Or manually:

### 1. Start Backend
```bash
cd tax-hub-dashboard/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend (in another terminal)
```bash
cd tax-hub-dashboard
npm run dev
```

## Access Points

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Login Credentials

- **Email**: `superadmin@taxease.ca`
- **Password**: `demo123`

## Stop All Services

```bash
./stop-all.sh
```

Or manually:
```bash
pkill -f uvicorn
pkill -f vite
```

## Verify Everything is Working

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Login**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"superadmin@taxease.ca","password":"demo123"}'
   ```

3. **Check Database Connection**:
   ```bash
   PGPASSWORD=Kushal07 psql -U postgres -h localhost -d taxhub_db -c "SELECT COUNT(*) FROM clients;"
   ```

## Features

✅ **Real Database Connection** - All data from PostgreSQL  
✅ **No Mock Data** - Everything is dynamic  
✅ **Full CRUD Operations** - Create, Read, Update, Delete  
✅ **Authentication** - JWT-based auth  
✅ **Real-time Updates** - Changes reflect immediately  

## Troubleshooting

### Backend not starting?
- Check if port 8000 is already in use
- Verify virtual environment is activated
- Check `backend/backend.log` for errors

### Frontend not starting?
- Check if port 8080 is already in use
- Run `npm install` if needed
- Check `frontend.log` for errors

### Database connection issues?
- Verify PostgreSQL is running: `pg_isready`
- Check database credentials in `backend/.env`
- Verify database exists: `psql -U postgres -l`

### CORS errors?
- Backend CORS is configured for port 8080
- If using different port, update `backend/.env` CORS_ORIGINS

## Current Status

All mock data has been removed. The application now:
- ✅ Connects to real PostgreSQL database
- ✅ Uses FastAPI backend for all operations
- ✅ Provides dynamic data on all pages
- ✅ Supports full CRUD operations
- ✅ Persists all changes to database

---

**Ready for testing with real data!** 🎉





