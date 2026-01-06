#!/bin/bash
# Check gunicorn stdout log for actual error

echo "=== Gunicorn STDOUT log (actual errors here) ==="
tail -100 /var/log/mcoder/gunicorn.log

echo ""
echo "=== Try to start manually to see error ==="
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
gunicorn -c gunicorn.conf.py run_app:app 2>&1 | head -50
