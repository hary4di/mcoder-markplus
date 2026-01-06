# Setup PostgreSQL for M-Code Pro

Write-Host "=== PostgreSQL Database Setup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  1. Create database: mcoder_production" -ForegroundColor Gray
Write-Host "  2. Create user: mcoder_app (with strong password)" -ForegroundColor Gray
Write-Host "  3. Grant privileges" -ForegroundColor Gray
Write-Host "  4. Save credentials to .env.postgres" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Setup cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[1/2] Uploading setup script..." -ForegroundColor Yellow
scp setup_postgres.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/2] Running PostgreSQL setup..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && python3 setup_postgres.py"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Configure Flask to use PostgreSQL" -ForegroundColor Yellow
