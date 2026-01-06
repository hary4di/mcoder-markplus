@echo off
echo === DEPLOYING USER MANAGEMENT FEATURES (Tested Version) ===
echo.
echo This will deploy:
echo   1. app/templates/users.html (Name, Edit, Delete)
echo   2. app/auth.py (edit_user and delete_user routes)
echo.
pause

echo.
echo Step 1: Uploading users.html...
scp app\templates\users.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/users.html
if %errorlevel% neq 0 (echo Failed && pause && exit /b 1)

echo.
echo Step 2: Uploading auth.py...
scp app\auth.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/auth.py
if %errorlevel% neq 0 (echo Failed && pause && exit /b 1)

echo.
echo Step 3: Clear Python cache and restart...
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null ; supervisorctl restart mcoder-markplus"

echo.
echo Wait 5 seconds for application to start...
timeout /t 5

echo.
echo === DEPLOYMENT COMPLETE ===
echo.
echo Features deployed:
echo   ✅ Name column (Full Name display)
echo   ✅ Edit button (pencil icon)
echo   ✅ Edit user functionality
echo   ✅ Delete button (trash icon)
echo   ✅ Delete with modal confirmation
echo.
echo Test at: https://m-coder.flazinsight.com/users
echo.
echo If any errors occur, rollback script is ready:
echo   .\rollback_users.bat
pause
