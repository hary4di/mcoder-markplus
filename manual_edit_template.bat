@echo off
echo === Manual Template Fix via SSH ===
echo.
echo Connecting to VPS to edit template manually...
echo.
echo Instructions:
echo 1. Line 23: Change "Username" to "Name"
echo 2. Line 37: Change "{{ user.username }}" to "{{ user.full_name }}"
echo 3. Save and exit (Ctrl+X, Y, Enter)
echo.
pause
ssh root@145.79.10.104 "nano /opt/markplus/mcoder-markplus/app/templates/users.html"
