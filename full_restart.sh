#!/bin/bash
# Full Application Restart

cd /opt/markplus/mcoder-markplus

echo "============================================================"
echo "FULL APPLICATION RESTART"
echo "============================================================"
echo ""

echo "[1] Stopping application..."
supervisorctl stop mcoder-markplus

echo ""
echo "[2] Clearing all Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "[3] Verifying .env DATABASE_URL..."
grep "DATABASE_URL" .env

echo ""
echo "[4] Starting application (will reload .env)..."
supervisorctl start mcoder-markplus
sleep 5

echo ""
echo "[5] Checking worker status..."
supervisorctl status mcoder-markplus

echo ""
echo "[6] Testing PostgreSQL connection..."
source venv/bin/activate
python3 << 'EOPY'
import os
from app import create_app, db

# Print environment variable
print(f"DATABASE_URL from env: {os.environ.get('DATABASE_URL', 'NOT SET')}")

app = create_app()
with app.app_context():
    # Check database engine
    print(f"Database engine: {db.engine.name}")
    print(f"Database URL: {db.engine.url}")
    
    # Test query
    result = db.session.execute(db.text("SELECT version()"))
    version = result.scalar()
    print(f"✅ PostgreSQL version: {version[:50]}")
    
    from app.models import User
    user_count = User.query.count()
    print(f"✅ Users in database: {user_count}")
EOPY

echo ""
echo "[7] Checking recent logs..."
tail -20 /var/log/mcoder/gunicorn.log

echo ""
echo "============================================================"
echo "RESTART COMPLETE!"
echo "============================================================"
echo ""
