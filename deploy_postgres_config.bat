@echo off
echo === Enable PostgreSQL Remote Access ===
echo.
echo Uploading config script...
scp enable_postgres_remote.sh root@145.79.10.104:/tmp/
if %errorlevel% neq 0 (echo Upload failed && pause && exit /b 1)

echo.
echo Running configuration on VPS...
ssh root@145.79.10.104 "chmod +x /tmp/enable_postgres_remote.sh && /tmp/enable_postgres_remote.sh"

echo.
echo === Configuration Complete ===
echo.
echo Now test connection from local:
echo python test_postgres_connection.py
pause
