# Production Database Check & Fix
# Check if ClassificationJob table exists

Write-Host "=== Checking Production Database ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Checking tables in database..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && sqlite3 instance/mcoder.db '.tables'"

Write-Host ""
Write-Host "[2/2] Checking if ClassificationJob exists..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && sqlite3 instance/mcoder.db 'SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"classification_job\";'"

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
