@echo off
echo Deploying user management fixes...

echo.
echo 1. Uploading auth.py...
scp app\auth.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/auth.py
if %errorlevel% neq 0 (echo Failed && exit /b 1)

echo 2. Uploading users.html...
scp app\templates\users.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/users.html
if %errorlevel% neq 0 (echo Failed && exit /b 1)

echo.
echo 3. Restarting application...
ssh root@145.79.10.104 "find /opt/markplus/mcoder-markplus -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; supervisorctl restart mcoder-markplus"

echo.
echo === DEPLOYMENT COMPLETE ===
echo Changes:
echo   - Removed csrf_exempt decorator
echo   - Added CSRF token to fetch request
echo   - Delete button now functional
echo.
echo Test at: https://m-coder.flazinsight.com/auth/users
pause
