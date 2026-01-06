# Deploy Delete User Feature
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEPLOYING DELETE USER FEATURE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "New Features:" -ForegroundColor Yellow
Write-Host "  - Delete user button now functional" -ForegroundColor Green
Write-Host "  - Confirmation modal before delete" -ForegroundColor White
Write-Host "  - Super Admin can delete all users" -ForegroundColor White
Write-Host "  - Cannot delete your own account" -ForegroundColor White
Write-Host "  - Cannot delete Super Admin (unless you're Super Admin)" -ForegroundColor White
Write-Host ""

Write-Host "[1/2] Uploading auth.py (delete route)..." -ForegroundColor Yellow
scp app/auth.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

Write-Host ""
Write-Host "[2/2] Uploading users.html (with delete modal)..." -ForegroundColor Yellow
scp app/templates/users.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

Write-Host ""
Write-Host "Clearing cache and restarting..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null ; supervisorctl restart mcoder-markplus && sleep 3 && supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "DELETE USER FEATURE READY!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Test di: https://m-coder.flazinsight.com/users" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cara kerja:" -ForegroundColor Yellow
Write-Host "  1. Klik tombol Delete (trash icon) di user" -ForegroundColor White
Write-Host "  2. Popup konfirmasi akan muncul" -ForegroundColor White
Write-Host "  3. Klik 'Delete User' untuk konfirmasi" -ForegroundColor White
Write-Host "  4. User akan dihapus dari database" -ForegroundColor White
Write-Host "  5. Page auto-reload dengan success message" -ForegroundColor White
Write-Host ""
