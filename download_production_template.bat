@echo off
echo === Downloading Production users.html ===
echo.
scp root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/users.html users_production.html
if %errorlevel% neq 0 (echo Download failed && pause && exit /b 1)

echo.
echo File saved as: users_production.html
echo Opening in notepad...
notepad users_production.html
