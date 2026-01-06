# Copy users.db to mcoder.db and verify

Write-Host "=== Setting Up Production Database ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Found existing users.db (56KB) in production" -ForegroundColor Yellow
Write-Host "Will copy to mcoder.db to preserve users" -ForegroundColor Yellow
Write-Host ""

Write-Host "[1/4] Copying users.db to mcoder.db..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus/instance && cp users.db mcoder.db"

Write-Host ""
Write-Host "[2/4] Verifying files..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus/instance && ls -lh"

Write-Host ""
Write-Host "[3/4] Checking tables in mcoder.db..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && sqlite3 instance/mcoder.db '.tables'"

Write-Host ""
Write-Host "[4/4] Running diagnostic..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python diagnose_production_db.py"

Write-Host ""
Write-Host "=== Database Ready! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Database file: /opt/markplus/mcoder-markplus/instance/mcoder.db" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT: Upload new code with database support" -ForegroundColor Yellow
Write-Host "Run: .\fix_production_results.ps1" -ForegroundColor Gray
