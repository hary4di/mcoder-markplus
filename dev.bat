@echo off
REM M-Code Pro - Windows Development Setup Wrapper
REM Run this to set up development environment

echo.
echo ============================================================
echo   M-Code Pro - Development Setup
echo   MarkPlus AI-Powered Classification System
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.11 or higher from python.org
    echo.
    pause
    exit /b 1
)

REM Run setup script
python setup_dev.py

if errorlevel 1 (
    echo.
    echo Setup encountered errors. Please review the messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
pause
