@echo off
echo === COMPREHENSIVE PRODUCTION DIAGNOSIS ===
echo.
echo Uploading diagnosis script...
scp diagnose_production.sh root@145.79.10.104:/tmp/
if %errorlevel% neq 0 (echo Upload failed && pause && exit /b 1)

echo.
echo Running full diagnosis on VPS...
echo This will check: error logs, syntax, routes, database, templates
echo.
ssh root@145.79.10.104 "chmod +x /tmp/diagnose_production.sh && /tmp/diagnose_production.sh"

echo.
echo.
echo === DIAGNOSIS COMPLETE ===
echo.
echo Please review the output above to identify root cause.
echo.
pause
