## Tax-Ease Backend (Dummy Auth + Client/Admin Operations)

This backend provides minimal endpoints to:

- Register/login clients with email/password (stored in existing `users` table).
- Use a **static OTP** (`123456`) for verification.
- Add/delete client records (linked to users) and list them in the admin dashboard.

### Centralized Environment Configuration

**All services use ONE centralized `.env` file at the project root:**

```
/home/cyberdude/Documents/Projects/CA-final/.env
```

The backend automatically loads environment variables from this file. No need to create separate `.env` files in subdirectories.

**Key Environment Variables:**
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - PostgreSQL connection
- `JWT_SECRET_KEY` - JWT token signing key
- `STATIC_OTP` - Static OTP code (default: `123456`)
- `STORAGE_PATH` - Local filesystem path for document uploads

See `.env.example` at project root for all available variables.

### Endpoints

- `POST /api/v1/auth/register` – create `users` row.
- `POST /api/v1/auth/login` – dummy login, returns JWT.
- `POST /api/v1/auth/request-otp` – always issues OTP `123456`.
- `POST /api/v1/auth/verify-otp` – accepts OTP `123456`, marks email verified.
- `POST /api/v1/client/add` – create `clients` row mapped to a user.
- `DELETE /api/v1/client/{client_id}` – delete a client row.
- `GET /api/v1/admin/clients` – list all clients for admin dashboard.

### Running Locally

1. **Configure `.env` file** (at project root):
   ```bash
   # Copy example if needed
   cp .env.example .env
   # Edit .env with your database credentials
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001
   ```

4. **Run tests:**
   ```bash
   python3 backend/test_api.py
   ```

Use the Flutter client/admin dashboard pointed at `http://localhost:8001/api/v1`.

### Architecture

- **Monolith FastAPI backend** - Single application, no microservices
- **PostgreSQL database** - Using existing `CA_Project` database
- **Local filesystem storage** - Documents saved to `storage/uploads/`
- **JWT authentication** - Token-based auth with refresh tokens
- **Static OTP** - For development/testing (always `123456`)

### Database Schema

The backend uses existing tables:
- `users` - Client user accounts
- `clients` - Client records linked to users
- `admins` - Admin/superadmin accounts
- `otps` - One-time passwords
- `chat_messages` - Client ↔ Admin chat
- `documents` - Uploaded document metadata
- `t1_returns_flat` - T1 tax form data

See `database/schemas.py` for full schema definitions.
