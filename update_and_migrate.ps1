# Update PostgreSQL Password to MarkPlus25
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "UPDATING POSTGRESQL PASSWORD" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "New Password: MarkPlus25" -ForegroundColor Yellow
Write-Host ""

Write-Host "[1/2] Uploading update script..." -ForegroundColor Yellow
scp update_postgres_password.sh root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/2] Executing update..." -ForegroundColor Yellow
Write-Host "This will:" -ForegroundColor White
Write-Host "  - Update PostgreSQL user password" -ForegroundColor White
Write-Host "  - Update .env.postgres" -ForegroundColor White
Write-Host "  - Update .env" -ForegroundColor White
Write-Host "  - Restart application" -ForegroundColor White
Write-Host ""

ssh root@145.79.10.104 "chmod +x /opt/markplus/mcoder-markplus/update_postgres_password.sh && bash /opt/markplus/mcoder-markplus/update_postgres_password.sh"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "PASSWORD UPDATED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "New Credentials:" -ForegroundColor Yellow
Write-Host "   Database: mcoder_production" -ForegroundColor White
Write-Host "   User: mcoder_app" -ForegroundColor White
Write-Host "   Password: MarkPlus25" -ForegroundColor Green
Write-Host "   Connection: postgresql://mcoder_app:MarkPlus25@localhost:5432/mcoder_production" -ForegroundColor Gray
Write-Host ""
Write-Host "Now running migration with new password..." -ForegroundColor Yellow
Write-Host ""

# Continue with migration
.\continue_migration.ps1
