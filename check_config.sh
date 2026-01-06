#!/bin/bash
# Check Configuration

cd /opt/markplus/mcoder-markplus

echo "============================================================"
echo "CHECKING CONFIGURATION"
echo "============================================================"
echo ""

echo "[1] DATABASE_URL in .env:"
grep "DATABASE_URL" .env

echo ""
echo "[2] config.py contents:"
cat config.py

echo ""
echo "[3] app/__init__.py database initialization:"
grep -A 5 "SQLALCHEMY_DATABASE_URI" app/__init__.py || echo "Not found"

echo ""
echo "[4] Check if psycopg2-binary installed:"
source venv/bin/activate
pip list | grep psycopg2

echo ""
