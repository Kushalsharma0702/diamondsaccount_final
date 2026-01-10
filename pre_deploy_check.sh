#!/bin/bash

##############################################################################
# Pre-Deployment Checklist Script
# Run this before deploying to EC2 to ensure everything is ready
##############################################################################

echo "=========================================================================="
echo "Tax-Ease EC2 Pre-Deployment Checklist"
echo "=========================================================================="
echo ""

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1 exists"
        return 0
    else
        echo "❌ $1 missing"
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo "✅ $1 directory exists"
        return 0
    else
        echo "❌ $1 directory missing"
        return 1
    fi
}

all_good=true

echo "1. Checking required files..."
check_file ".env" || all_good=false
check_file "backend/requirements.txt" || all_good=false
check_file "services/admin-api/requirements.txt" || all_good=false
check_file "deploy_ec2.sh" || all_good=false

echo ""
echo "2. Checking directories..."
check_directory "backend" || all_good=false
check_directory "services/admin-api" || all_good=false
check_directory "database" || all_good=false

echo ""
echo "3. Checking .env configuration..."

if [ -f ".env" ]; then
    # Check critical variables
    source .env
    
    [ -z "$DB_HOST" ] && echo "❌ DB_HOST not set" && all_good=false || echo "✅ DB_HOST set"
    [ -z "$DB_NAME" ] && echo "❌ DB_NAME not set" && all_good=false || echo "✅ DB_NAME set"
    [ -z "$DB_USER" ] && echo "❌ DB_USER not set" && all_good=false || echo "✅ DB_USER set"
    [ -z "$DB_PASSWORD" ] && echo "❌ DB_PASSWORD not set" && all_good=false || echo "✅ DB_PASSWORD set"
    [ -z "$JWT_SECRET" ] && echo "❌ JWT_SECRET not set" && all_good=false || echo "✅ JWT_SECRET set"
    [ -z "$DATABASE_URL" ] && echo "❌ DATABASE_URL not set" && all_good=false || echo "✅ DATABASE_URL set"
    
    # Check JWT_SECRET length
    if [ ! -z "$JWT_SECRET" ] && [ ${#JWT_SECRET} -lt 32 ]; then
        echo "⚠️  JWT_SECRET should be at least 32 characters"
        all_good=false
    fi
fi

echo ""
echo "4. Testing database connectivity..."
if [ ! -z "$DB_HOST" ] && [ ! -z "$DB_USER" ] && [ ! -z "$DB_PASSWORD" ] && [ ! -z "$DB_NAME" ]; then
    if command -v psql &> /dev/null; then
        if PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &> /dev/null; then
            echo "✅ Database connection successful"
        else
            echo "❌ Cannot connect to database"
            echo "   Host: $DB_HOST"
            echo "   Database: $DB_NAME"
            echo "   User: $DB_USER"
            all_good=false
        fi
    else
        echo "⚠️  psql not installed, skipping database test"
    fi
else
    echo "⚠️  Database credentials not complete, skipping test"
fi

echo ""
echo "5. Checking Python requirements..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    echo "✅ Python $PYTHON_VERSION installed"
    
    if [[ "$(printf '%s\n' "3.9" "$PYTHON_VERSION" | sort -V | head -n1)" == "3.9" ]]; then
        echo "✅ Python version is >= 3.9"
    else
        echo "❌ Python version must be >= 3.9"
        all_good=false
    fi
else
    echo "❌ Python 3 not installed"
    all_good=false
fi

echo ""
echo "6. Checking deployment script..."
if [ -f "deploy_ec2.sh" ]; then
    if [ -x "deploy_ec2.sh" ]; then
        echo "✅ deploy_ec2.sh is executable"
    else
        echo "⚠️  deploy_ec2.sh not executable, fixing..."
        chmod +x deploy_ec2.sh
        echo "✅ Made deploy_ec2.sh executable"
    fi
else
    echo "❌ deploy_ec2.sh not found"
    all_good=false
fi

echo ""
echo "=========================================================================="
if [ "$all_good" = true ]; then
    echo "✅ All checks passed! Ready for deployment."
    echo ""
    echo "Next steps:"
    echo "1. Upload project to EC2: scp -r . ubuntu@your-ec2-ip:/home/ubuntu/taxease"
    echo "2. SSH to EC2: ssh ubuntu@your-ec2-ip"
    echo "3. Run deployment: cd /home/ubuntu/taxease && sudo ./deploy_ec2.sh"
    exit 0
else
    echo "❌ Some checks failed. Please fix the issues above before deploying."
    exit 1
fi
echo "=========================================================================="
