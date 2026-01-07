#!/bin/bash

# Quick start script for API v2
# Starts the main backend API server

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Starting Tax-Ease API v2${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if database exists
echo -e "${YELLOW}Checking database...${NC}"
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw CA_Project; then
    echo -e "${GREEN}✅ Database CA_Project exists${NC}"
else
    echo -e "${YELLOW}Creating database CA_Project...${NC}"
    sudo -u postgres psql -c "CREATE DATABASE \"CA_Project\";"
    echo -e "${GREEN}✅ Database created${NC}"
fi

# Initialize tables
echo -e "${YELLOW}Initializing database tables...${NC}"
python -c "from backend.app.database import init_db; init_db()"
echo -e "${GREEN}✅ Tables initialized${NC}"
echo ""

# Check Redis
echo -e "${YELLOW}Checking Redis...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}⚠️  Redis is not running. Token blacklist will be disabled.${NC}"
    echo -e "${YELLOW}To start Redis: sudo systemctl start redis${NC}"
fi
echo ""

# Start backend
echo -e "${GREEN}Starting Backend API on http://localhost:8000${NC}"
echo -e "${YELLOW}API Documentation: http://localhost:8000/docs${NC}"
echo ""

# Set PYTHONPATH to include project root and run from project root
export PYTHONPATH="${BASE_DIR}:${PYTHONPATH}"
cd "$BASE_DIR"
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
