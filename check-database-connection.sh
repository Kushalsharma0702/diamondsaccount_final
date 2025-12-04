#!/bin/bash

# Check database connection and show table structure

DB_NAME="taxease_db"
DB_USER="postgres"
DB_PASSWORD="Kushal07"

echo "🔍 Checking database connection and structure..."
echo ""

# Check if PostgreSQL is running
if ! pg_isready -U $DB_USER > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running!"
    echo "Please start PostgreSQL: sudo systemctl start postgresql"
    exit 1
fi

echo "✅ PostgreSQL is running"
echo ""

# Check if database exists
export PGPASSWORD=$DB_PASSWORD
if psql -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "✅ Database '$DB_NAME' exists"
else
    echo "⚠️  Database '$DB_NAME' does not exist. Creating..."
    createdb -U $DB_USER $DB_NAME
    echo "✅ Database created"
fi
echo ""

# List tables
echo "📊 Tables in database:"
psql -U $DB_USER -d $DB_NAME -c "\dt" 2>/dev/null || echo "No tables found or error connecting"

echo ""
echo "📋 Client-side tables should include:"
echo "  - users"
echo "  - files"
echo "  - t1_personal_forms"
echo ""
echo "📋 Admin-side tables should include:"
echo "  - admin_users"
echo "  - clients"
echo "  - documents"
echo "  - payments"
echo ""


