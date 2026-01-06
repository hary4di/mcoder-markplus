#!/bin/bash
# Force Update .env to PostgreSQL

set -e

cd /opt/markplus/mcoder-markplus

echo "============================================================"
echo "FORCING DATABASE_URL UPDATE"
echo "============================================================"
echo ""

echo "[1] Current .env DATABASE_URL:"
echo "-----------------------------------------------------------"
grep "DATABASE_URL" .env || echo "Not found"

echo ""
echo "[2] Reading PostgreSQL credentials..."
source .env.postgres
echo "PostgreSQL URL loaded"

echo ""
echo "[3] Backing up .env..."
cp .env .env.backup.force.$(date +%Y%m%d_%H%M%S)

echo ""
echo "[4] Removing ALL DATABASE_URL lines..."
sed -i '/DATABASE_URL/d' .env

echo ""
echo "[5] Adding PostgreSQL DATABASE_URL..."
echo "" >> .env
echo "# PostgreSQL Database (Production)" >> .env
echo "DATABASE_URL=postgresql://mcoder_app:MarkPlus25@localhost:5432/mcoder_production" >> .env

echo ""
echo "[6] Verifying new .env:"
echo "-----------------------------------------------------------"
grep "DATABASE_URL" .env

echo ""
echo "[7] Restarting application..."
supervisorctl restart mcoder-markplus
sleep 5

echo ""
echo "[8] Testing PostgreSQL connection..."
source venv/bin/activate
python3 << 'EOPY'
from app import create_app, db
app = create_app()
with app.app_context():
    result = db.session.execute(db.text("SELECT current_database()"))
    dbname = result.scalar()
    print(f"✅ Connected to: {dbname}")
    
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    print(f"✅ Database engine: {db.engine.name}")
    
    from app.models import User
    user_count = User.query.count()
    print(f"✅ Users count: {user_count}")
EOPY

echo ""
echo "[9] Supervisor status:"
supervisorctl status mcoder-markplus

echo ""
echo "============================================================"
echo "DATABASE_URL UPDATE COMPLETE!"
echo "============================================================"
echo ""
echo "✅ Now using: postgresql://mcoder_app:MarkPlus25@localhost:5432/mcoder_production"
echo ""
