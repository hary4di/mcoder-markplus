# Continue PostgreSQL Migration (Steps 3-7)
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CONTINUING POSTGRESQL MIGRATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Uploading fixed script..." -ForegroundColor Yellow
scp continue_migration.sh root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/2] Executing migration (Steps 3-7)..." -ForegroundColor Yellow
Write-Host "This will:" -ForegroundColor White
Write-Host "  - Update .env with PostgreSQL" -ForegroundColor White
Write-Host "  - Create database tables" -ForegroundColor White
Write-Host "  - Migrate users from SQLite" -ForegroundColor White
Write-Host "  - Restart application" -ForegroundColor White
Write-Host ""

ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && chmod +x continue_migration.sh && bash continue_migration.sh"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "DONE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "TEST NOW:" -ForegroundColor Yellow
Write-Host "   https://m-coder.flazinsight.com/" -ForegroundColor Cyan
Write-Host "   Login and Check /results page" -ForegroundColor White
Write-Host ""
