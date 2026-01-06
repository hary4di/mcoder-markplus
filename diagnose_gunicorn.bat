@echo off
echo === Deep Gunicorn Diagnosis ===
echo.
scp diagnose_gunicorn.sh root@145.79.10.104:/tmp/
ssh root@145.79.10.104 "chmod +x /tmp/diagnose_gunicorn.sh && /tmp/diagnose_gunicorn.sh"
echo.
pause
