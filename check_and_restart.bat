@echo off
echo === Check if fix applied, then restart ===
echo.
echo 1. Checking line 37 in production...
ssh root@145.79.10.104 "sed -n '37p' /opt/markplus/mcoder-markplus/app/templates/users.html"

echo.
echo 2. Restarting application...
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus"

echo.
echo Wait 5 seconds...
timeout /t 5

echo.
echo === Done ===
echo Refresh with Ctrl+F5: https://m-coder.flazinsight.com/users
pause
