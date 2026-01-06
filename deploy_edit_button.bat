@echo off
echo === Deploying Edit Button Feature ===
echo.
echo Uploading users.html with Edit button...
scp users_production.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/users.html
if %errorlevel% neq 0 (echo Upload failed && pause && exit /b 1)

echo.
echo Restarting application...
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus"

echo.
echo Wait 5 seconds...
timeout /t 5

echo.
echo === SUCCESS ===
echo Changes:
echo   - Edit button added (pencil icon)
echo   - Shows for all users except Super Admin (unless you are Super Admin)
echo   - Delete button preserved
echo.
echo Refresh (Ctrl+F5): https://m-coder.flazinsight.com/users
pause
