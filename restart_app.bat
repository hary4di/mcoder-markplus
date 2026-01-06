@echo off
echo === Restarting Application to Apply Template Changes ===
echo.
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus"
echo.
echo Done! Wait 5 seconds and check: https://m-coder.flazinsight.com/users
timeout /t 5
pause
