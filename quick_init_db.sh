#!/bin/bash
# Quick database initialization script
# Usage: ./quick_init_db.sh

set -e

cd "$(dirname "$0")"

echo "🚀 Starting quick database initialization..."
echo ""

python3 init_database.py --yes --test-data

echo ""
echo "✅ Database initialized!"
echo ""
echo "Next: Run backend with:"
echo "  cd ~/Documents/Projects/CA-final"
echo "  source backend/venv/bin/activate"
echo "  export PYTHONPATH=\$PWD"
echo "  uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001"
