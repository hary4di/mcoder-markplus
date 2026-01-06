# Upload and Run PostgreSQL Explorer

Write-Host "=== PostgreSQL Exploration ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Uploading explorer script..." -ForegroundColor Yellow
scp explore_postgres.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/2] Running exploration..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && python3 explore_postgres.py"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Complete ===" -ForegroundColor Green
