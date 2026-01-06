# Complete PostgreSQL Migration - One Script Does All

Write-Host "=== M-Code Pro PostgreSQL Migration ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will perform ALL steps automatically:" -ForegroundColor Yellow
Write-Host "  1. Create PostgreSQL database and user" -ForegroundColor Gray
Write-Host "  2. Install psycopg2-binary" -ForegroundColor Gray
Write-Host "  3. Update .env configuration" -ForegroundColor Gray
Write-Host "  4. Create tables in PostgreSQL" -ForegroundColor Gray
Write-Host "  5. Migrate users from SQLite" -ForegroundColor Gray
Write-Host "  6. Deploy database-based code" -ForegroundColor Gray
Write-Host "  7. Restart application" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  BACKUP: .env will be backed up automatically" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Proceed with complete migration? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Migration cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[1/3] Uploading migration scripts..." -ForegroundColor Yellow
scp setup_postgres.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp migrate_to_postgresql.sh root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/3] Making script executable..." -ForegroundColor Yellow
ssh root@145.79.10.104 "chmod +x /opt/markplus/mcoder-markplus/migrate_to_postgresql.sh"

Write-Host ""
Write-Host "[3/3] Running complete migration..." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && ./migrate_to_postgresql.sh"
Write-Host "============================================================" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Migration Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "IMMEDIATELY TEST:" -ForegroundColor Red
Write-Host "  1. https://m-coder.flazinsight.com/" -ForegroundColor Cyan
Write-Host "  2. Login with your credentials" -ForegroundColor Cyan
Write-Host "  3. Check /results page" -ForegroundColor Cyan
Write-Host ""
Write-Host "If ANY error, rollback with:" -ForegroundColor Yellow
Write-Host "  .\emergency_rollback_now.ps1" -ForegroundColor Gray
