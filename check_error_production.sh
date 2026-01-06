#!/bin/bash
# Check error logs

echo "Checking supervisor logs..."
tail -50 /var/log/supervisor/supervisord.log

echo ""
echo "Checking gunicorn error log..."
tail -50 /var/log/mcoder/error.log

echo ""
echo "Testing Python syntax..."
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
python3 -m py_compile app/auth.py 2>&1 || echo "SYNTAX ERROR in auth.py"

echo ""
echo "Testing import..."
python3 -c "from app import create_app; print('OK')" 2>&1
