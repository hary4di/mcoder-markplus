@echo off
echo === Adding Edit Button (Safe Version - No is_super_admin) ===
echo.

echo Step 1: Download current template...
scp root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/users.html users_current.html
if %errorlevel% neq 0 (echo Download failed && pause && exit /b 1)

echo.
echo Template downloaded as users_current.html
echo Please check the file and confirm.
pause
