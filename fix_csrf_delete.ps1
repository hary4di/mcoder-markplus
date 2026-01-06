# Fix CSRF Error - Delete User
Write-Host "Fixing CSRF error..." -ForegroundColor Yellow
scp app/auth.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/
scp app/templates/users.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null ; supervisorctl restart mcoder-markplus && sleep 3 && supervisorctl status mcoder-markplus"
Write-Host "FIXED! Try delete user again." -ForegroundColor Green
