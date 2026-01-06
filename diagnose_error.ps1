# Check Production Error
Write-Host "============================================================" -ForegroundColor Red
Write-Host "CHECKING PRODUCTION ERROR" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

Write-Host "Uploading diagnostic script..." -ForegroundColor Yellow
scp check_error.sh root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "Running diagnostics..." -ForegroundColor Yellow
ssh root@145.79.10.104 "chmod +x /opt/markplus/mcoder-markplus/check_error.sh && bash /opt/markplus/mcoder-markplus/check_error.sh"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "Analyzing logs above to determine fix..." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
