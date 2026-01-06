# Deploy Registration Fix
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEPLOYING REGISTRATION FIX" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Changes:" -ForegroundColor Yellow
Write-Host "  - Removed Username field from registration form" -ForegroundColor White
Write-Host "  - Username auto-generated from email" -ForegroundColor White
Write-Host "  - Simplified registration: Email + Password only" -ForegroundColor White
Write-Host ""

Write-Host "[1/2] Uploading auth.py..." -ForegroundColor Yellow
scp app/auth.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

Write-Host ""
Write-Host "[2/2] Uploading register.html..." -ForegroundColor Yellow
scp app/templates/register.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

Write-Host ""
Write-Host "Clearing cache and restarting..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null ; supervisorctl restart mcoder-markplus && sleep 3 && supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "FIXED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Registration sekarang:" -ForegroundColor Yellow
Write-Host "  - TIDAK ada field Username (dihilangkan)" -ForegroundColor Green
Write-Host "  - Username otomatis dari email (sebelum @)" -ForegroundColor White
Write-Host "  - Langsung bisa login setelah register" -ForegroundColor White
Write-Host ""
Write-Host "Test: https://m-coder.flazinsight.com/auth/register" -ForegroundColor Cyan
Write-Host ""
