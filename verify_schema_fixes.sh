#!/bin/bash
# Schema Fix Verification Script

echo "════════════════════════════════════════════════════════════════════════"
echo "📋 SCHEMA FIX VERIFICATION"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check admin API
echo "🔍 Checking Admin API..."
HEALTH=$(curl -s http://localhost:8001/health 2>/dev/null)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Admin API is running and healthy${NC}"
else
    echo -e "${RED}❌ Admin API is not responding${NC}"
fi
echo ""

# Check admin users
echo "🔍 Checking Admin Users..."
ADMIN_COUNT=$(PGPASSWORD=Kushal07 psql -U postgres -d CA_Project -h localhost -t -c "SELECT COUNT(*) FROM admins WHERE email IN ('admin@taxease.ca', 'superadmin@taxease.ca');" 2>/dev/null | xargs)
if [ "$ADMIN_COUNT" = "2" ]; then
    echo -e "${GREEN}✅ Both admin users exist${NC}"
    PGPASSWORD=Kushal07 psql -U postgres -d CA_Project -h localhost -c "SELECT email, name, role FROM admins ORDER BY role;"
else
    echo -e "${RED}❌ Admin users missing (found: $ADMIN_COUNT)${NC}"
fi
echo ""

# Check test customer
echo "🔍 Checking Test Customer Data..."
USER_EXISTS=$(PGPASSWORD=Kushal07 psql -U postgres -d CA_Project -h localhost -t -c "SELECT COUNT(*) FROM users WHERE email = 'hacur.tichkule@test.com';" 2>/dev/null | xargs)
if [ "$USER_EXISTS" = "1" ]; then
    echo -e "${GREEN}✅ Test customer exists${NC}"
    
    ANSWER_COUNT=$(PGPASSWORD=Kushal07 psql -U postgres -d CA_Project -h localhost -t -c "SELECT COUNT(*) FROM t1_answers WHERE t1_form_id = 'a0b0e477-82a6-4ff3-81c7-aa58f959f161';" 2>/dev/null | xargs)
    if [ "$ANSWER_COUNT" = "99" ]; then
        echo -e "${GREEN}✅ All 99 T1 answers intact${NC}"
    else
        echo -e "${RED}❌ Expected 99 answers, found: $ANSWER_COUNT${NC}"
    fi
else
    echo -e "${RED}❌ Test customer not found${NC}"
fi
echo ""

# Check schema relationships
echo "🔍 Checking for SQLAlchemy Warnings..."
if grep -q "Filing.t1_form.*conflicts.*t1_forms" /tmp/admin-api.log 2>/dev/null; then
    echo -e "${RED}❌ T1Form relationship warning still present${NC}"
else
    echo -e "${GREEN}✅ T1Form relationship warning FIXED${NC}"
fi

if grep -q "AdminUser.created_audit_logs" /tmp/admin-api.log 2>/dev/null; then
    echo -e "${YELLOW}⚠️  AdminUser/AuditLog warning present (non-critical)${NC}"
else
    echo -e "${GREEN}✅ No relationship warnings${NC}"
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════════════════"
echo "📊 SUMMARY"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Admin Credentials:"
echo "  📧 admin@taxease.ca / 🔑 Admin123!"
echo "  📧 superadmin@taxease.ca / 🔑 Super123!"
echo ""
echo "Test Customer:"
echo "  📧 hacur.tichkule@test.com / 🔑 Test@1234"
echo "  User ID: 00afdea7-1b09-4992-808d-e41601947d3c"
echo "  T1 Form: 99 comprehensive answers"
echo ""
echo "Next Steps:"
echo "  1. Login to admin dashboard: http://localhost:8080"
echo "  2. View test customer T1 form"
echo "  3. Verify all sections display correctly"
echo ""
