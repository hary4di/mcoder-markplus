#!/bin/bash
# Verify Production Database Features

set -e

cd /opt/markplus/mcoder-markplus
source venv/bin/activate

echo "============================================================"
echo "VERIFYING DATABASE FEATURES"
echo "============================================================"
echo ""

echo "[1/5] Checking PostgreSQL connection..."
python3 << 'EOPY'
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.session.execute(db.text("SELECT 1"))
        print("✅ PostgreSQL connection: OK")
    except Exception as e:
        print(f"❌ PostgreSQL connection: {e}")
        exit(1)
EOPY

echo ""
echo "[2/5] Checking tables..."
python3 << 'EOPY'
from app import create_app, db
from sqlalchemy import inspect
app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"✅ Tables found: {', '.join(tables)}")
    
    required = ['users', 'classification_jobs', 'classification_variables']
    missing = [t for t in required if t not in tables]
    if missing:
        print(f"❌ Missing tables: {', '.join(missing)}")
        exit(1)
EOPY

echo ""
echo "[3/5] Checking models..."
python3 << 'EOPY'
from app import create_app, db
from app.models import User, ClassificationJob, ClassificationVariable
app = create_app()
with app.app_context():
    user_count = User.query.count()
    job_count = ClassificationJob.query.count()
    var_count = ClassificationVariable.query.count()
    print(f"✅ Users: {user_count}")
    print(f"✅ Classification Jobs: {job_count}")
    print(f"✅ Classification Variables: {var_count}")
EOPY

echo ""
echo "[4/5] Checking application status..."
supervisorctl status mcoder-markplus

echo ""
echo "[5/5] Checking recent logs..."
tail -20 /var/log/mcoder/gunicorn.log

echo ""
echo "============================================================"
echo "VERIFICATION COMPLETE!"
echo "============================================================"
echo ""
echo "🔍 MANUAL TESTS REQUIRED:"
echo "   1. Open: https://m-coder.flazinsight.com/results"
echo "   2. Should show empty table with 'No classification history'"
echo "   3. Run new classification"
echo "   4. Check if job appears in table"
echo "   5. Test bulk delete, search, expiry features"
echo ""
