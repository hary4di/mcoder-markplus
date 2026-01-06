#!/bin/bash
echo "=== GUNICORN DEEP DIAGNOSIS ==="
echo ""

echo "1. Supervisor detailed status:"
supervisorctl status mcoder-markplus

echo ""
echo "2. Check process tree:"
ps aux | grep gunicorn | grep -v grep

echo ""
echo "3. Check what's listening on port 5000:"
netstat -tlnp | grep 5000

echo ""
echo "4. Check gunicorn.conf.py:"
cat /opt/markplus/mcoder-markplus/gunicorn.conf.py

echo ""
echo "5. Last 50 lines of stdout log:"
tail -50 /var/log/mcoder/gunicorn.log 2>/dev/null || echo "Not found"

echo ""
echo "6. Last 50 lines of stderr log:"
tail -50 /var/log/mcoder/gunicorn_error.log 2>/dev/null || echo "Not found"

echo ""
echo "7. Try to manually start gunicorn:"
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
gunicorn -c gunicorn.conf.py run_app:app --timeout 5 2>&1 &
GUNICORN_PID=$!
sleep 2
echo "Gunicorn PID: $GUNICORN_PID"
curl -s -o /dev/null -w "HTTP Status after manual start: %{http_code}\n" http://localhost:5000/
kill $GUNICORN_PID 2>/dev/null
echo ""
echo "=== END ==="
