# Deploy Database-Based Code to Production
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEPLOYING DATABASE FEATURES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will deploy:" -ForegroundColor Yellow
Write-Host "  - app/routes.py (database-based results)" -ForegroundColor White
Write-Host "  - app/models.py (ClassificationJob + ClassificationVariable)" -ForegroundColor White
Write-Host "  - app/templates/results.html (job history table)" -ForegroundColor White
Write-Host "  - app/templates/view_result.html (detail view)" -ForegroundColor White
Write-Host ""

# Upload files
Write-Host "[1/5] Uploading routes.py..." -ForegroundColor Yellow
scp app/routes.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

Write-Host ""
Write-Host "[2/5] Uploading models.py..." -ForegroundColor Yellow
scp app/models.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

Write-Host ""
Write-Host "[3/5] Uploading results.html..." -ForegroundColor Yellow
scp app/templates/results.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

Write-Host ""
Write-Host "[4/5] Uploading view_result.html..." -ForegroundColor Yellow
scp app/templates/view_result.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

Write-Host ""
Write-Host "[5/5] Clearing Python cache and restarting..." -ForegroundColor Yellow
ssh root@145.79.10.104 @"
cd /opt/markplus/mcoder-markplus
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
supervisorctl restart mcoder-markplus
sleep 3
supervisorctl status mcoder-markplus
"@

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEW FEATURES ENABLED:" -ForegroundColor Yellow
Write-Host "  - Job History Table (not session-based)" -ForegroundColor Green
Write-Host "  - Bulk Delete with Checkboxes" -ForegroundColor Green
Write-Host "  - Search Box (real-time filtering)" -ForegroundColor Green
Write-Host "  - Expiry Countdown (24h tracker)" -ForegroundColor Green
Write-Host "  - Persistent Results (database-backed)" -ForegroundColor Green
Write-Host ""
Write-Host "TEST NOW:" -ForegroundColor Cyan
Write-Host "  1. Refresh: https://m-coder.flazinsight.com/results" -ForegroundColor White
Write-Host "  2. Should show empty table (no session data)" -ForegroundColor White
Write-Host "  3. Run new classification to test" -ForegroundColor White
Write-Host ""
Write-Host "NOTE: Previous session-based result will be gone" -ForegroundColor Gray
Write-Host "      (not saved to database yet)" -ForegroundColor Gray
Write-Host ""
