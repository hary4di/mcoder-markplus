@echo off
echo === Updating User Full Names in Production ===
echo.
echo 1. Uploading script...
scp update_user_fullnames.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
if %errorlevel% neq 0 (echo Upload failed && pause && exit /b 1)

echo.
echo 2. Running database update...
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python update_user_fullnames.py"

echo.
echo === Done! ===
echo Refresh page: https://m-coder.flazinsight.com/users
echo.
echo If still showing username, the production template might display username field instead of full_name.
pause
