# Migrate Production Database - Add Missing Tables
# This is SAFE - will not delete existing users

Write-Host "=== Migrating Production Database ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Adding ClassificationJob and ClassificationVariable tables..." -ForegroundColor Yellow
Write-Host "(User table will be preserved)" -ForegroundColor Gray
Write-Host ""

Write-Host "[1/2] Uploading migration script..." -ForegroundColor Yellow
scp migrate_db.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/2] Running migration..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python migrate_db.py"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Migration Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT: Upload new code with database support" -ForegroundColor Yellow
Write-Host "Run: .\fix_production_results.ps1" -ForegroundColor Cyan
