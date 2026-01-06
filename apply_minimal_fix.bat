@echo off
echo === Applying Minimal Template Fix ===
echo.
echo Uploading fix script...
scp minimal_fix_template.sh root@145.79.10.104:/tmp/
if %errorlevel% neq 0 (echo Upload failed && pause && exit /b 1)

echo.
echo Running fix on production...
ssh root@145.79.10.104 "chmod +x /tmp/minimal_fix_template.sh && /tmp/minimal_fix_template.sh"

echo.
echo === Done ===
echo Refresh page (Ctrl+F5): https://m-coder.flazinsight.com/users
echo.
echo Should now display:
echo   - Column: Name (not Username)
echo   - Display: Full Name (Haryadi, Noor Aisyah Amini, Zainal Mutaqin)
echo.
pause
