# Create Production Database - Simple Version

Write-Host "=== Creating Production Database ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Uploading database creation script..." -ForegroundColor Yellow
scp create_db.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/3] Running database creation script..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python create_db.py"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "[3/3] Verifying with diagnostic..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python diagnose_production_db.py"

Write-Host ""
Write-Host "=== Database Creation Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT: Upload new code with database support" -ForegroundColor Yellow
Write-Host "Run: .\fix_production_results.ps1" -ForegroundColor Cyan
