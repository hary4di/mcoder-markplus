# Simple PostgreSQL Migration - Run Directly on Server

Write-Host "=== PostgreSQL Migration ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Uploading scripts..." -ForegroundColor Yellow
scp setup_postgres.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp migrate_to_postgresql.sh root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "Running migration on server..." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && chmod +x migrate_to_postgresql.sh && bash migrate_to_postgresql.sh"
Write-Host "============================================================" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "TEST NOW:" -ForegroundColor Yellow
Write-Host "  https://m-coder.flazinsight.com/" -ForegroundColor Cyan
