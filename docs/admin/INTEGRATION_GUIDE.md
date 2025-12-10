# Tax Hub Dashboard - Backend Integration Guide

This guide explains how the Python FastAPI backend integrates with both the React admin dashboard and the Flutter mobile app.

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Dashboard│◄───────►│  FastAPI Backend │◄───────►│ Flutter Mobile  │
│  (TypeScript)   │         │   (Python)       │         │   (Dart)        │
│                 │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │                  │
                          │   PostgreSQL     │
                          │   + Redis        │
                          │                  │
                          └──────────────────┘
```

## Backend API Endpoints

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: Configure via `VITE_API_BASE_URL` environment variable

### Common Endpoints (Both Frontends)

#### Authentication
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/register` - Register (Flutter only, via existing auth service)
- `POST /api/v1/auth/request-otp` - Request OTP (Flutter)
- `POST /api/v1/auth/verify-otp` - Verify OTP (Flutter)

#### Files
- `POST /api/v1/files/upload` - Upload files (Flutter)

## React Dashboard Integration

### API Service

The React dashboard uses the `apiService` located at:
- `src/services/api.ts`

### Configuration

1. Create `.env` file in `tax-hub-dashboard/`:
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

2. The API service automatically handles:
   - Token storage in localStorage
   - Authorization headers
   - Error handling
   - Response parsing

### Authentication Flow

1. User enters credentials in Login page
2. `AuthContext.login()` calls `apiService.login()`
3. API returns JWT tokens and user data
4. Tokens stored in localStorage
5. User data stored in context and localStorage
6. All subsequent requests include `Authorization: Bearer <token>` header

### Using the API Service

```typescript
import { apiService } from '@/services/api';

// Get clients
const { clients, total } = await apiService.getClients({
  page: 1,
  page_size: 20,
  status: 'documents_pending',
  year: 2024,
  search: 'John'
});

// Create client
const newClient = await apiService.createClient({
  name: 'John Doe',
  email: 'john@example.com',
  phone: '(416) 555-0000',
  filing_year: 2024
});

// Get analytics
const analytics = await apiService.getAnalytics();
```

### Dashboard-Specific Endpoints

#### Admin Users (Superadmin only)
- `GET /api/v1/admin-users` - List all admins
- `POST /api/v1/admin-users` - Create admin
- `PATCH /api/v1/admin-users/{id}` - Update admin
- `DELETE /api/v1/admin-users/{id}` - Delete admin

#### Clients
- `GET /api/v1/clients` - List clients (paginated, filtered)
- `GET /api/v1/clients/{id}` - Get client details
- `POST /api/v1/clients` - Create client
- `PATCH /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

#### Documents
- `GET /api/v1/documents` - List documents
- `POST /api/v1/documents` - Create document
- `DELETE /api/v1/documents/{id}` - Delete document

#### Payments
- `GET /api/v1/payments` - List payments
- `POST /api/v1/payments` - Create payment

#### Analytics
- `GET /api/v1/analytics` - Get dashboard analytics

#### Audit Logs (Superadmin only)
- `GET /api/v1/audit-logs` - List audit logs

## Flutter Mobile App Integration

The Flutter app connects to the backend for:
1. User authentication (via existing auth service in `heyhey/`)
2. File uploads
3. Tax form submissions

### API Configuration

The Flutter app uses the base URL defined in:
- `lib/core/constants/api_endpoints.dart`

Update the `BASE_URL` constant:

```dart
static const String BASE_URL = 'http://localhost:8000/api/v1';
// Or production URL
static const String BASE_URL = 'https://api.yourdomain.com/api/v1';
```

### Flutter-Specific Endpoints

The Flutter app primarily uses endpoints from the existing `heyhey/` backend:
- Authentication endpoints
- File upload endpoints
- T1 form endpoints

The admin dashboard backend can share these endpoints or act as a gateway.

## Backend Features

### Redis Caching

The backend implements Redis caching for:
- Analytics data (1 hour TTL)
- Client lists (invalidated on updates)
- Admin user data (invalidated on updates)

Cache keys follow pattern: `{prefix}:{resource}:{id}`

Example:
```python
# In routes, use cache decorator
@cache_result("analytics", ttl=3600)
async def get_analytics():
    # Analytics logic
    pass
```

### Authentication & Authorization

- JWT tokens with 24-hour expiration
- Refresh tokens with 30-day expiration
- Role-based access control:
  - Superadmin: All permissions
  - Admin: Configurable permissions

### Permissions

Available permissions:
- `add_edit_payment`
- `add_edit_client`
- `request_documents`
- `assign_clients`
- `view_analytics`
- `approve_cost_estimate`
- `update_workflow`

### Audit Logging

All mutations are logged:
- Client CRUD operations
- Payment creation
- Admin user management
- Document management

Audit logs include:
- Action performed
- Entity type and ID
- Old and new values
- Performed by (admin user)
- Timestamp

## Data Models

### AdminUser
- id (UUID)
- email (unique)
- name
- password_hash
- role (superadmin/admin)
- permissions (array)
- is_active
- created_at, updated_at

### Client
- id (UUID)
- name, email, phone
- filing_year
- status (documents_pending, under_review, etc.)
- payment_status (pending, partial, paid, overdue)
- assigned_admin_id
- total_amount, paid_amount
- created_at, updated_at

### Document
- id (UUID)
- client_id
- name, type
- status (pending, complete, missing)
- version
- uploaded_at
- notes

### Payment
- id (UUID)
- client_id
- amount
- method (E-Transfer, Credit Card, etc.)
- created_by_id
- created_at

## Error Handling

All API errors follow standard format:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `204` - No Content (successful delete)
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Testing

### Using curl

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@taxease.ca","password":"demo123"}'

# Get clients (replace TOKEN with actual token)
curl http://localhost:8000/api/v1/clients \
  -H "Authorization: Bearer TOKEN"
```

### Using Swagger UI

Visit `http://localhost:8000/docs` for interactive API documentation.

## Deployment

### Development
```bash
cd backend
uvicorn app.main:app --reload
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables

Set all required environment variables (see `BACKEND_SETUP.md`):
- `DATABASE_URL`
- `REDIS_HOST`, `REDIS_PORT`
- `SECRET_KEY`
- `CORS_ORIGINS`
- etc.

## Next Steps

1. ✅ Backend API created
2. ✅ React dashboard integrated
3. ⏭️ Update Flutter app API endpoints
4. ⏭️ Deploy backend to production
5. ⏭️ Set up CI/CD pipeline
6. ⏭️ Configure monitoring and logging

## Support

For setup issues, see:
- `BACKEND_SETUP.md` - Complete backend setup guide
- `backend/README.md` - Backend API documentation

For API documentation:
- Visit `/docs` endpoint when server is running
- Check route files in `backend/app/api/v1/`




