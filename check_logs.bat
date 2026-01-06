@echo off
echo === Checking Error Logs ===
echo.
ssh root@145.79.10.104 "tail -100 /var/log/mcoder/gunicorn_error.log"
pause
