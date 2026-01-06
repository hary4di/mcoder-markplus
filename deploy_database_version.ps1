# Deploy Database Version with Proper Error Handling

Write-Host "=== Deploying Database-Based Results ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will enable:" -ForegroundColor Yellow
Write-Host "  - Job history table (persistent results)" -ForegroundColor Gray
Write-Host "  - Bulk delete with checkboxes" -ForegroundColor Gray
Write-Host "  - Search by filename" -ForegroundColor Gray
Write-Host "  - Expiry countdown (24h)" -ForegroundColor Gray
Write-Host "  - Download multiple times" -ForegroundColor Gray
Write-Host ""
Write-Host "Requirements:" -ForegroundColor Yellow
Write-Host "  - Database must exist: /opt/markplus/mcoder-markplus/instance/mcoder.db" -ForegroundColor Gray
Write-Host "  - Tables must exist: classification_jobs, classification_variables" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Continue deployment? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Deployment cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[1/6] Verifying database exists..." -ForegroundColor Yellow
ssh root@145.79.10.104 "ls -lh /opt/markplus/mcoder-markplus/instance/mcoder.db"

Write-Host ""
Write-Host "[2/6] Uploading app/routes.py..." -ForegroundColor Yellow
scp app/routes.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

Write-Host ""
Write-Host "[3/6] Uploading app/models.py..." -ForegroundColor Yellow
scp app/models.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

Write-Host ""
Write-Host "[4/6] Uploading app/templates/results.html..." -ForegroundColor Yellow
scp app/templates/results.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

Write-Host ""
Write-Host "[5/6] Clearing cache and restarting..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; find . -name '*.pyc' -delete 2>/dev/null; supervisorctl restart mcoder-markplus && sleep 5 && supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "[6/6] Testing if app started correctly..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "Checking last 20 lines of log..." -ForegroundColor Gray
ssh root@145.79.10.104 "tail -20 /var/log/mcoder/gunicorn.log"

Write-Host ""
Write-Host "=== Deployment Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "IMMEDIATELY TEST:" -ForegroundColor Red
Write-Host "  1. Homepage: https://m-coder.flazinsight.com/" -ForegroundColor Cyan
Write-Host "  2. Dashboard: https://m-coder.flazinsight.com/dashboard" -ForegroundColor Cyan
Write-Host "  3. Results: https://m-coder.flazinsight.com/results" -ForegroundColor Cyan
Write-Host ""
Write-Host "If ANY page shows error, IMMEDIATELY run:" -ForegroundColor Red
Write-Host "  .\emergency_rollback_now.ps1" -ForegroundColor Yellow
