@echo off
echo === Check Actual Application Error ===
echo.
scp check_actual_error.sh root@145.79.10.104:/tmp/
ssh root@145.79.10.104 "chmod +x /tmp/check_actual_error.sh && /tmp/check_actual_error.sh"
echo.
pause
