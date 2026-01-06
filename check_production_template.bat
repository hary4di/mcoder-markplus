@echo off
echo === Checking Production users.html ===
echo.
ssh root@145.79.10.104 "head -40 /opt/markplus/mcoder-markplus/app/templates/users.html"
pause
