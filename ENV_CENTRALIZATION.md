# Centralized Environment Configuration

## Overview

All services in the Tax-Ease project now use **ONE centralized `.env` file** located at the project root:

```
/home/cyberdude/Documents/Projects/CA-final/.env
```

## Benefits

- ✅ Single source of truth for all configuration
- ✅ No duplicate environment variables across services
- ✅ Easy to manage and update
- ✅ Consistent configuration across backend, admin-api, and client-api

## How It Works

### Backend Services

All backend services automatically load the centralized `.env` file:

1. **Backend (`backend/app/`)**: Uses `load_dotenv()` with explicit path to project root
2. **Database Schema (`database/schemas.py`)**: Loads from project root
3. **All Route Files**: Load `.env` from project root before accessing environment variables

### Example Usage

```python
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (2-3 levels up from current file)
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Now use os.getenv() as normal
import os
DB_HOST = os.getenv("DB_HOST", "localhost")
```

## Environment Variables

See `.env.example` at project root for all available variables.

### Key Variables

- **Database**: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- **JWT**: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- **OTP**: `STATIC_OTP`, `DEVELOPER_OTP`
- **Storage**: `STORAGE_PATH`, `MAX_FILE_SIZE_MB`
- **Email**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`

## Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual values:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **All services will automatically use this file** - no need to create separate `.env` files in subdirectories.

## Migration from Multiple .env Files

If you previously had separate `.env` files in:
- `services/admin-api/.env`
- `services/client-api/.env`
- `backend/.env`

**Action Required:**
1. Review those files and copy any unique variables to the centralized `.env`
2. Delete the old `.env` files (they're now ignored)
3. Restart your services

## Verification

To verify the centralized `.env` is being loaded:

```bash
# Check backend logs
tail -f backend/server.log

# Test database connection
python3 database/schemas.py

# Run API tests
python3 backend/test_api.py
```

All services should connect to the same database and use the same configuration.










