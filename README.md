# TaxEase - Complete Tax Filing Solution

A comprehensive tax filing application with client-side mobile app (Flutter), admin dashboard (React), and multiple backend services (FastAPI).

## 📁 Project Structure

```
CA-final/
├── client_side/              # Client backend (FastAPI)
│   ├── main.py              # Main application
│   ├── shared/              # Shared modules
│   └── services/            # Microservices
│
├── tax-hub-dashboard/       # Admin dashboard
│   ├── src/                 # React frontend
│   └── backend/             # Admin backend (FastAPI)
│
├── frontend/                # Mobile client app
│   └── tax_ease-main/       # Flutter application
│
├── docs/                    # All documentation
│   ├── aws/                 # AWS integration docs
│   ├── authentication/      # Auth documentation
│   ├── integration/         # System integration
│   ├── admin/               # Admin panel docs
│   ├── testing/             # Testing guides
│   └── setup/               # Setup documentation
│
├── scripts/                 # All scripts
│   ├── setup/               # Setup scripts
│   ├── testing/             # Test scripts
│   ├── maintenance/         # Maintenance utilities
│   └── deployment/          # Deployment scripts
│
├── storage/                 # Local file storage
└── logs/                    # Application logs
```

## 🚀 Quick Start

### 1. Start All Services
```bash
./scripts/setup/start-all-services.sh
```

### 2. Run Tests
```bash
./scripts/testing/RUN_TEST_NOW.sh
```

### 3. Access Applications
- **Client Backend:** http://localhost:8001
- **Admin Backend:** http://localhost:8002
- **Admin Dashboard:** http://localhost:8080

## 📚 Documentation

All documentation is organized in the `docs/` directory:

- **Getting Started:** [Integration Guide](docs/integration/INTEGRATION_GUIDE.md)
- **Authentication:** [AWS Cognito](docs/aws/COGNITO_INTEGRATION_COMPLETE.md)
- **AWS Services:** [AWS SES](docs/aws/AWS_SES_COMPLETE_INTEGRATION.md)
- **Admin Panel:** [Admin Setup](docs/admin/BACKEND_SETUP.md)
- **Testing:** [Test Guide](docs/testing/TEST_SETUP_GUIDE.md)

See [docs/README.md](docs/README.md) for complete documentation index.

## 🛠️ Scripts

All scripts are organized in the `scripts/` directory:

- **Setup Scripts:** Service management and deployment
- **Testing Scripts:** Health checks and diagnostics
- **Maintenance Scripts:** Database sync and utilities

See [scripts/README.md](scripts/README.md) for complete script index.

## 🔧 Configuration

### Environment Variables

**Client Backend** (`client_side/.env`):
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/taxease_db
COGNITO_USER_POOL_ID=ca-central-1_FP2WE41eW
COGNITO_CLIENT_ID=504mgtvq1h97vlml90c3iibnt0
AWS_REGION=ca-central-1
```

**Admin Backend** (`tax-hub-dashboard/backend/.env`):
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/taxease_db
JWT_SECRET=your-secret-key
```

## 📋 Key Features

- ✅ User authentication with AWS Cognito
- ✅ OTP verification via AWS SES
- ✅ Tax form submission (T1 Personal)
- ✅ Document upload and management
- ✅ Admin dashboard with role-based access
- ✅ Real-time updates
- ✅ File encryption

## 🔐 Default Credentials

**Developer User:**
- Email: `Developer@aurocode.app`
- Password: `Developer@123`
- OTP Bypass: `123456`

**Admin Users:**
- Superadmin: `superadmin@taxease.ca` / `demo123`
- Admin: `admin@taxease.ca` / `demo123`

## 📖 More Information

- [Documentation Index](docs/README.md)
- [Scripts Index](scripts/README.md)
- [Integration Guide](docs/integration/INTEGRATION_GUIDE.md)

## 🆘 Support

For issues or questions, refer to:
- Authentication issues → `docs/authentication/`
- AWS setup → `docs/aws/`
- Integration help → `docs/integration/`

---

**Project organized and ready for development! 🚀**



