# Emergency: Check and Restart Application
Write-Host "Checking application status..." -ForegroundColor Red

ssh root@145.79.10.104 @"
echo "=== Checking error logs ==="
tail -30 /var/log/mcoder/error.log

echo ""
echo "=== Trying to start application ==="
cd /opt/markplus/mcoder-markplus
supervisorctl start mcoder-markplus
sleep 3
supervisorctl status mcoder-markplus

echo ""
echo "=== If still error, check syntax ==="
source venv/bin/activate
python3 -c 'from app import create_app; print(\"Import OK\")'
"@
