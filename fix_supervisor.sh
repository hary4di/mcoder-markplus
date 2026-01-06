#!/bin/bash
# Fix Supervisor to Load .env

cd /opt/markplus/mcoder-markplus

echo "============================================================"
echo "FIXING SUPERVISOR CONFIGURATION"
echo "============================================================"
echo ""

echo "[1] Current supervisor config:"
cat /etc/supervisor/conf.d/mcoder-markplus.conf

echo ""
echo "[2] Creating new config with .env support..."
cat > /etc/supervisor/conf.d/mcoder-markplus.conf << 'EOF'
[program:mcoder-markplus]
command=/opt/markplus/mcoder-markplus/venv/bin/gunicorn -c /opt/markplus/mcoder-markplus/gunicorn.conf.py run_app:app
directory=/opt/markplus/mcoder-markplus
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/mcoder/gunicorn.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=/var/log/mcoder/error.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10

# IMPORTANT: Load environment from .env file
environment=LANG="en_US.UTF-8",LC_ALL="en_US.UTF-8",DATABASE_URL="postgresql://mcoder_app:MarkPlus25@localhost:5432/mcoder_production"

startsecs=5
stopsignal=TERM
stopwaitsecs=30
priority=999
EOF

echo "✅ New config created"

echo ""
echo "[3] Reloading supervisor..."
supervisorctl reread
supervisorctl update

echo ""
echo "[4] Restarting application..."
supervisorctl restart mcoder-markplus
sleep 5

echo ""
echo "[5] Testing PostgreSQL connection..."
source venv/bin/activate
python3 << 'EOPY'
import os
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")

from app import create_app, db
app = create_app()
with app.app_context():
    print(f"Database engine: {db.engine.name}")
    if db.engine.name == 'postgresql':
        result = db.session.execute(db.text("SELECT version()"))
        version = result.scalar()
        print(f"✅ PostgreSQL: {version[:80]}")
        
        from app.models import User
        user_count = User.query.count()
        print(f"✅ Users: {user_count}")
    else:
        print(f"❌ Still using: {db.engine.name}")
EOPY

echo ""
echo "[6] Final status:"
supervisorctl status mcoder-markplus

echo ""
echo "============================================================"
echo "FIX COMPLETE!"
echo "============================================================"
echo ""
