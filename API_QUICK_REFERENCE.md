# API Quick Reference Card

## Base URLs
- **Local**: `http://localhost:8001`
- **API Base**: `http://localhost:8001/api/v1`

## Authentication

### Client Auth
| Endpoint | Method | Path |
|----------|--------|------|
| Register | POST | `/api/v1/auth/register` |
| Login | POST | `/api/v1/auth/login` |
| Request OTP | POST | `/api/v1/auth/request-otp` |
| Verify OTP | POST | `/api/v1/auth/verify-otp` |

### Admin Auth
| Endpoint | Method | Path |
|----------|--------|------|
| Login | POST | `/api/v1/admin/auth/login` |
| Register | POST | `/api/v1/admin/auth/register` |
| Get Me | GET | `/api/v1/admin/auth/me` |
| Logout | POST | `/api/v1/admin/auth/logout` |
| Refresh Session | POST | `/api/v1/admin/auth/refresh-session` |

## Client Endpoints

| Endpoint | Method | Path | Auth |
|----------|--------|------|------|
| Get My Info | GET | `/api/v1/client/me` | ✅ |
| Add Client | POST | `/api/v1/client/add` | ✅ Admin |
| Delete Client | DELETE | `/api/v1/client/{id}` | ✅ Admin |

## Admin Endpoints

| Endpoint | Method | Path | Auth |
|----------|--------|------|------|
| Get Clients | GET | `/api/v1/admin/clients` | ✅ Admin |
| Get Client Detail | GET | `/api/v1/admin/clients/{id}` | ✅ Admin |
| Update Client | PATCH | `/api/v1/admin/clients/{id}` | ✅ Admin |
| Delete Client | DELETE | `/api/v1/admin/clients/{id}` | ✅ Admin |
| Get Documents | GET | `/api/v1/admin/documents` | ✅ Admin |
| Update Document | PATCH | `/api/v1/admin/documents/{id}` | ✅ Admin |
| Get Payments | GET | `/api/v1/admin/payments` | ✅ Admin |
| Create Payment | POST | `/api/v1/admin/payments` | ✅ Admin |
| Get Analytics | GET | `/api/v1/admin/analytics` | ✅ Admin |
| Get Admin Users | GET | `/api/v1/admin/admin-users` | ✅ Admin |

## Chat Endpoints

| Endpoint | Method | Path | Auth |
|----------|--------|------|------|
| Send Message | POST | `/api/v1/chat/send` | ❌ |
| Get Messages | GET | `/api/v1/chat/{client_id}` | ❌ |
| Mark Read | PUT | `/api/v1/chat/{client_id}/mark-read` | ❌ |
| Unread Count | GET | `/api/v1/chat/{client_id}/unread-count` | ❌ |

## Document Endpoints

| Endpoint | Method | Path | Auth |
|----------|--------|------|------|
| Upload | POST | `/api/v1/documents/upload` | ✅ |
| Download | GET | `/api/v1/documents/{id}/download` | ✅ |
| Get Client Docs | GET | `/api/v1/documents/client/{id}` | ✅ |
| Delete | DELETE | `/api/v1/documents/{id}` | ✅ |

## T1 Form Endpoints

| Endpoint | Method | Path | Auth |
|----------|--------|------|------|
| Submit | POST | `/api/v1/t1/tax-return` | ✅ |
| Get Form | GET | `/api/v1/t1/tax-return` | ✅ |

## Filing Status Endpoints

| Endpoint | Method | Path | Auth |
|----------|--------|------|------|
| Get Client Status | GET | `/api/v1/filing-status/client/{id}` | ✅ |
| Update Status | PUT | `/api/v1/filing-status/admin/{id}/status` | ✅ Admin |
| Get All Returns | GET | `/api/v1/filing-status/admin/returns` | ✅ Admin |

## Common Headers

```http
Content-Type: application/json
Authorization: Bearer <access_token>
```

## Universal OTP
**Static OTP for all verifications**: `123456`

## Demo Credentials

### Client
- Email: `client@example.com`
- Password: `password123`

### Admin
- Email: `admin@taxease.com`
- Password: `Admin123!`

### Superadmin
- Email: `superadmin@taxease.com`
- Password: `Super123!`

## Response Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Quick Test Commands

```bash
# Health Check
curl http://localhost:8001/

# Client Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"client@example.com","password":"password123"}'

# Admin Login
curl -X POST http://localhost:8001/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@taxease.com","password":"Admin123!"}'
```





