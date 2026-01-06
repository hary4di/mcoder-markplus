@echo off
echo === Checking Production Error Logs ===
echo.
echo 1. Gunicorn Error Log (last 50 lines):
echo =========================================
ssh root@145.79.10.104 "tail -50 /var/log/mcoder/gunicorn_error.log 2>/dev/null || tail -50 /opt/markplus/mcoder-markplus/logs/gunicorn_error.log 2>/dev/null || echo 'Log file not found'"
echo.
echo.
echo 2. Supervisor Log (last 30 lines):
echo =========================================
ssh root@145.79.10.104 "tail -30 /var/log/supervisor/mcoder-markplus-stderr*.log 2>/dev/null || echo 'No supervisor log'"
echo.
pause
