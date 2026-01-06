# Post-Rollback Verification & Root Cause Analysis

Write-Host "=== Post-Rollback Verification ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Checking service status..." -ForegroundColor Yellow
ssh root@145.79.10.104 "supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "[2/3] Checking last 30 lines of log..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "tail -30 /var/log/mcoder/gunicorn.log"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "[3/3] Looking for error that caused crash..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "grep -B 5 -A 20 'Traceback\|ImportError\|ModuleNotFoundError\|AttributeError' /var/log/mcoder/gunicorn.log | tail -50"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Verification Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Please test production manually:" -ForegroundColor Yellow
Write-Host "  - Homepage: https://m-coder.flazinsight.com/" -ForegroundColor Cyan
Write-Host "  - Dashboard: https://m-coder.flazinsight.com/dashboard" -ForegroundColor Cyan
Write-Host "  - Classify: https://m-coder.flazinsight.com/classify" -ForegroundColor Cyan
