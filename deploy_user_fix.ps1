Write-Host "Deploying user management fixes..." -ForegroundColor Cyan

# Upload fixed files
Write-Host "`n1. Uploading auth.py..." -ForegroundColor Yellow
scp "app/auth.py" root@145.79.10.104:/opt/markplus/mcoder-markplus/app/auth.py
if ($LASTEXITCODE -ne 0) { Write-Host "Failed to upload auth.py" -ForegroundColor Red; exit 1 }

Write-Host "2. Uploading users.html..." -ForegroundColor Yellow
scp "app/templates/users.html" root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/users.html
if ($LASTEXITCODE -ne 0) { Write-Host "Failed to upload users.html" -ForegroundColor Red; exit 1 }

# Restart application
Write-Host "`n3. Restarting application..." -ForegroundColor Yellow
ssh root@145.79.10.104 "find /opt/markplus/mcoder-markplus -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; supervisorctl restart mcoder-markplus"
if ($LASTEXITCODE -ne 0) { Write-Host "Failed to restart" -ForegroundColor Red; exit 1 }

Write-Host "`n=== DEPLOYMENT COMPLETE ===" -ForegroundColor Green
Write-Host "Changes:" -ForegroundColor Cyan
Write-Host "  ✓ Removed csrf_exempt decorator from delete_user route" -ForegroundColor Green
Write-Host "  ✓ Added CSRF token to JavaScript fetch request" -ForegroundColor Green
Write-Host "  ✓ Delete user button now functional" -ForegroundColor Green
Write-Host "`nTest: https://m-coder.flazinsight.com/auth/users" -ForegroundColor Cyan
