# Test Database Query

Write-Host "=== Testing Production Database Query ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Uploading test script..." -ForegroundColor Yellow
scp test_query.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/2] Running test..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python test_query.py"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
