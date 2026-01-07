# T1 API Quick Reference Guide

## 🚀 Quick Start

### 1. Start the API
```bash
cd /home/cyberdude/Documents/Projects/CA-final
pkill -f uvicorn && sleep 2
export PYTHONPATH="${PWD}:${PYTHONPATH}"
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/taxease-api.log 2>&1 &
```

### 2. Check Health
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","redis":"ok","database":"ok"}
```

### 3. View API Documentation
Open browser: http://localhost:8000/docs

---

## 📋 Database Info

**Connection:**
- Host: localhost:5432
- Database: CA_Project
- User: postgres
- Password: Kushal07

**Tables:**
```sql
-- List all T1 tables
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('t1_forms', 't1_answers', 't1_sections_progress', 'email_threads', 'email_messages');
```

---

## 🔑 Authentication Flow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Test@123","first_name":"John","last_name":"Doe","phone":"+1234567890"}'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Test@123"}' | jq -r '.access_token')

# 3. Use token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me
```

---

## 📝 T1 Form Flow

### ⚠️ IMPORTANT: Filing ID Must Be a Valid UUID

The mobile app must first create a filing to get a valid UUID. Do NOT use custom IDs like `T1_1736180000000`.

```bash
# ❌ WRONG - Will get 400 error:
curl -X POST "http://localhost:8000/api/v1/t1-forms/T1_1736180000000/answers" ...
# Error: {"code": "INVALID_FILING_ID", "hint": "First create a filing via POST /api/v1/filings"}

# ✅ CORRECT - Create filing first, then use returned UUID:
```

### Complete Flow:

```bash
# 1. Create filing (REQUIRED FIRST STEP)
FILING_ID=$(curl -X POST http://localhost:8000/api/v1/filings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filing_year":2024}' | jq -r '.id')
# Returns UUID like: "a141864f-8906-47bd-965a-16c75936c4c6"

# 2. Get T1 structure (optional)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/t1-forms/structure | jq '.formName'

# 3. Save draft (use the UUID from step 1)
curl -X POST "http://localhost:8000/api/v1/t1-forms/$FILING_ID/answers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answers":{"firstName":"John","lastName":"Doe","SIN":"123456789"}}'

# 4. Fetch draft
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/t1-forms/$FILING_ID"

# 5. Get required docs
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/t1-forms/$FILING_ID/required-documents"

# 6. Submit
curl -X POST "http://localhost:8000/api/v1/t1-forms/$FILING_ID/submit" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 Debugging

### Check API Logs
```bash
tail -f /tmp/taxease-api.log
```

### Check Recent Requests
```bash
tail -100 /tmp/taxease-api.log | grep "REQUEST:"
```

### Check Errors
```bash
tail -100 /tmp/taxease-api.log | grep "ERROR"
```

### Database Queries
```bash
PGPASSWORD="Kushal07" psql -h localhost -U postgres -d CA_Project

# List all T1 forms
SELECT id, filing_id, status, is_locked, completion_percentage FROM t1_forms;

# Count answers per form
SELECT t1_form_id, COUNT(*) FROM t1_answers GROUP BY t1_form_id;

# View user info
SELECT id, email, email_verified, is_active FROM users;
```

---

## 📊 Common Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Health check |
| POST | /api/v1/auth/register | Create account |
| POST | /api/v1/auth/login | Login |
| POST | /api/v1/filings | Create filing |
| GET | /api/v1/t1-forms/structure | Get form structure |
| POST | /api/v1/t1-forms/{filing_id}/answers | Save draft |
| GET | /api/v1/t1-forms/{filing_id} | Get draft |
| POST | /api/v1/t1-forms/{filing_id}/submit | Submit form |
| GET | /api/v1/t1-forms/{filing_id}/required-documents | Get docs |

---

## 🛠️ Troubleshooting

### API not starting
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
pkill -f uvicorn

# Check logs
tail -50 /tmp/taxease-api.log
```

### Redis connection error
```bash
# Check Redis status
redis-cli ping

# Should return: PONG

# Start Redis if needed
sudo systemctl start redis
```

### Database connection error
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
PGPASSWORD="Kushal07" psql -h localhost -U postgres -d CA_Project -c "SELECT 1;"
```

### Email verification required
```bash
# Bypass in dev (set email_verified=true)
PGPASSWORD="Kushal07" psql -h localhost -U postgres -d CA_Project -c "UPDATE users SET email_verified=TRUE WHERE email='user@test.com';"
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| T1_API_DOCUMENTATION.md | Complete API reference (600+ lines) |
| T1_IMPLEMENTATION_SUMMARY.md | Technical summary |
| T1_QUICK_REFERENCE.md | This file |
| backend/test_t1_endpoints.py | Test suite |
| backend/migrations/t1_tables_v2.sql | Database schema |

---

## 🎯 Testing Checklist

- [ ] API health check passing
- [ ] User registration works
- [ ] User login works  
- [ ] Email verification bypassed (dev)
- [ ] Filing creation works
- [ ] T1 structure loads
- [ ] Draft save works
- [ ] Draft fetch works
- [ ] Required documents computed
- [ ] Submission validates properly
- [ ] Admin endpoints (requires admin user)

---

## 🔐 Admin Testing

Admin endpoints require admin role. Create admin user:

```bash
# Option 1: Use existing create_admin_user.py script
cd backend
python create_admin_user.py

# Option 2: SQL insert
PGPASSWORD="Kushal07" psql -h localhost -U postgres -d CA_Project << EOF
INSERT INTO admins (id, email, password_hash, first_name, last_name, role)
VALUES (
  gen_random_uuid(),
  'admin@test.com',
  -- Use a pre-hashed password or create via API first
  '\$2b\$12\$...',
  'Admin',
  'User',
  'admin'
);
EOF
```

---

## 💡 Pro Tips

1. **Save tokens:** Export TOKEN variable for reuse
2. **Use jq:** Pretty-print JSON responses
3. **Watch logs:** `tail -f /tmp/taxease-api.log` in separate terminal
4. **Swagger UI:** Best for interactive testing
5. **Database direct:** Quick way to verify data

---

## 🚨 Known Issues

1. **Performance:** Auth endpoints slow (~600s+) - under investigation
2. **Duplicate warning:** SAWarning in schemas_v2.py - cosmetic only
3. **Email verification:** Bypass needed in dev environment

---

**Last Updated:** 2026-01-06
