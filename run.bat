@echo off
REM Batch script untuk menjalankan Kobo Classification
REM Otomatis install dependencies dan run main.py

echo ============================================================
echo Kobo Survey Classification Automation
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo.
    echo Silakan install Python terlebih dahulu dari:
    echo https://www.python.org/downloads/
    echo.
    echo Pastikan centang "Add Python to PATH" saat install
    echo.
    pause
    exit /b 1
)

echo [Step 1] Checking Python version...
python --version

echo.
echo [Step 2] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [Step 3] Running classification automation...
echo.
python main.py

echo.
echo ============================================================
echo Process completed!
echo ============================================================
pause
