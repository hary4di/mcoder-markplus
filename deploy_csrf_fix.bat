@echo off
echo === DEPLOYING CSRF FIX ===
echo.
echo Uploading fixed users.html...
scp app\templates\users.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/users.html
if %errorlevel% neq 0 (echo Failed && pause && exit /b 1)

echo.
echo Restarting application...
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus"

echo.
echo Wait 5 seconds...
timeout /t 5

echo.
echo === DONE ===
echo.
echo Fixed: Removed undefined csrf_token() fallback
echo Now using: Meta tag with error handling
echo.
echo Test: https://m-coder.flazinsight.com/users
pause
