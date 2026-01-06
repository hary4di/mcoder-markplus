#!/bin/bash
# Comprehensive diagnosis script for production errors

echo "========================================"
echo "PRODUCTION DIAGNOSIS REPORT"
echo "========================================"
echo ""

echo "1. APPLICATION STATUS"
echo "----------------------------------------"
supervisorctl status mcoder-markplus
echo ""

echo "2. LAST 30 LINES OF ERROR LOG"
echo "----------------------------------------"
tail -30 /var/log/mcoder/gunicorn_error.log 2>/dev/null || tail -30 /opt/markplus/mcoder-markplus/logs/gunicorn_error.log 2>/dev/null || echo "No error log found"
echo ""

echo "3. PYTHON SYNTAX CHECK - auth.py"
echo "----------------------------------------"
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
python -m py_compile app/auth.py 2>&1 || echo "Syntax error in auth.py"
echo ""

echo "4. PYTHON SYNTAX CHECK - models.py"
echo "----------------------------------------"
python -m py_compile app/models.py 2>&1 || echo "Syntax error in models.py"
echo ""

echo "5. CHECK ROUTES REGISTRATION"
echo "----------------------------------------"
python -c "
from app import create_app
app = create_app()
print('Routes in auth blueprint:')
for rule in app.url_map.iter_rules():
    if 'auth' in rule.endpoint:
        print(f'  {rule.endpoint} -> {rule.rule} [{rule.methods}]')
" 2>&1
echo ""

echo "6. CHECK auth.py STRUCTURE"
echo "----------------------------------------"
echo "Lines with @auth_bp.route:"
grep -n "@auth_bp.route" app/auth.py | head -20
echo ""
echo "Lines with def delete_user:"
grep -n "def delete_user" app/auth.py
echo ""
echo "Lines with def edit_user:"
grep -n "def edit_user" app/auth.py
echo ""

echo "7. CHECK FOR DUPLICATE DECORATORS"
echo "----------------------------------------"
echo "Checking for duplicate @auth_bp.route decorators..."
awk '/@auth_bp.route.*delete_user/ {count++} END {print "delete_user route defined", count, "times"}' app/auth.py
awk '/@auth_bp.route.*edit_user/ {count++} END {print "edit_user route defined", count, "times"}' app/auth.py
echo ""

echo "8. DATABASE CONNECTION TEST"
echo "----------------------------------------"
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    print(f'Database engine: {db.engine.name}')
    print(f'Database URL: {db.engine.url}')
    from app.models import User
    users = User.query.count()
    print(f'Users count: {users}')
" 2>&1
echo ""

echo "9. CHECK TEMPLATE FILE"
echo "----------------------------------------"
echo "users.html exists:"
ls -lh app/templates/users.html
echo ""
echo "First 10 lines of users.html:"
head -10 app/templates/users.html
echo ""

echo "========================================"
echo "END OF DIAGNOSIS REPORT"
echo "========================================"
