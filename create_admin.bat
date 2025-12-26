@echo off
echo ================================================
echo   Create Admin User
echo ================================================
echo.

REM Activate virtual environment if exists
if exist "venv\" (
    call venv\Scripts\activate.bat
)

REM Run create-admin command
py run_app.py create-admin

pause
