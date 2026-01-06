@echo off
echo === Checking Nginx Configuration ===
echo.
scp check_nginx.sh root@145.79.10.104:/tmp/
ssh root@145.79.10.104 "chmod +x /tmp/check_nginx.sh && /tmp/check_nginx.sh"
echo.
pause
