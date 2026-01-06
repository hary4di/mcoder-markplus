# Rollback Production to Last Working State
# Issue: All pages showing Internal Server Error after update

Write-Host "=== EMERGENCY ROLLBACK ===" -ForegroundColor Red
Write-Host ""

Write-Host "[1/3] Rolling back to previous version..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git checkout HEAD~1 app/routes.py app/models.py app/templates/results.html"

Write-Host ""
Write-Host "[2/3] Clearing cache..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; find . -name '*.pyc' -delete 2>/dev/null"

Write-Host ""
Write-Host "[3/3] Restarting service..." -ForegroundColor Yellow
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus && sleep 3 && supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "=== Rollback Done! ===" -ForegroundColor Cyan
Write-Host "Test URL: https://m-coder.flazinsight.com/" -ForegroundColor Green
