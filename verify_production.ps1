# Verify Production Database Features
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "VERIFYING PRODUCTION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Uploading verification script..." -ForegroundColor Yellow
scp verify_production.sh root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "Running verification..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && chmod +x verify_production.sh && bash verify_production.sh"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "MANUAL TEST NOW:" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Open: https://m-coder.flazinsight.com/results" -ForegroundColor Cyan
Write-Host "   Expected: Empty table with search box, bulk delete button" -ForegroundColor White
Write-Host ""
Write-Host "2. Go to: https://m-coder.flazinsight.com/classify" -ForegroundColor Cyan
Write-Host "   Run new classification (upload files, select variables)" -ForegroundColor White
Write-Host ""
Write-Host "3. Check /results again" -ForegroundColor Cyan
Write-Host "   Expected: Job appears in table with all details" -ForegroundColor White
Write-Host ""
Write-Host "4. Test features:" -ForegroundColor Cyan
Write-Host "   - Checkbox selection" -ForegroundColor White
Write-Host "   - Search box filtering" -ForegroundColor White
Write-Host "   - Expiry countdown badge" -ForegroundColor White
Write-Host "   - Download button (multiple times)" -ForegroundColor White
Write-Host "   - View details (eye icon)" -ForegroundColor White
Write-Host ""
