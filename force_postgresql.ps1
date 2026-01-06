# Force Update to PostgreSQL
Write-Host "============================================================" -ForegroundColor Red
Write-Host "FORCING POSTGRESQL CONNECTION" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

Write-Host "Problem: App still using SQLite (not PostgreSQL)" -ForegroundColor Yellow
Write-Host "Solution: Force update DATABASE_URL in .env" -ForegroundColor Yellow
Write-Host ""

Write-Host "Uploading fix script..." -ForegroundColor Yellow
scp force_postgresql.sh root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "Executing fix..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && chmod +x force_postgresql.sh && bash force_postgresql.sh"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "FIXED! TEST NOW:" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "https://m-coder.flazinsight.com/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Should work now with PostgreSQL backend!" -ForegroundColor White
Write-Host ""
