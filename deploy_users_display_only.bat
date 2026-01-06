@echo off
echo === Deploy Users Display Fix (No Delete Feature) ===
echo.
echo Uploading users.html with Full Name display and Edit button...
scp app\templates\users.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/users.html
if %errorlevel% neq 0 (echo Upload failed && pause && exit /b 1)

echo.
echo === SUCCESS ===
echo Changes:
echo   - Column changed from Username to Name
echo   - Display full_name instead of username
echo   - Edit button visible
echo   - Delete button visible (but won't work - need auth.py fix later)
echo.
echo Check: https://m-coder.flazinsight.com/users
pause
