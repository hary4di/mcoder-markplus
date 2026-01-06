#!/bin/bash
# Check Production Error Logs

echo "============================================================"
echo "CHECKING ERROR LOGS"
echo "============================================================"
echo ""

echo "[1] Last 50 lines of gunicorn log:"
echo "-----------------------------------------------------------"
tail -50 /var/log/mcoder/gunicorn.log

echo ""
echo "[2] Last 50 lines of error log:"
echo "-----------------------------------------------------------"
tail -50 /var/log/mcoder/error.log 2>/dev/null || echo "No error.log found"

echo ""
echo "[3] Supervisor status:"
echo "-----------------------------------------------------------"
supervisorctl status mcoder-markplus

echo ""
echo "[4] Check if app can import:"
echo "-----------------------------------------------------------"
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
python3 -c "from app import create_app; print('✅ App can be imported')" 2>&1 || echo "❌ Import failed"

echo ""
echo "[5] Check database connection:"
echo "-----------------------------------------------------------"
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.session.execute(db.text('SELECT 1')); print('✅ Database connected')" 2>&1 || echo "❌ Database connection failed"

echo ""
