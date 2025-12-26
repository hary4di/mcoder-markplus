@echo off
echo ========================================
echo M-Coder Quick Deploy to Production
echo ========================================
echo.

REM Step 1: Git status
echo [1/5] Checking git status...
git status --short

REM Step 2: Add all changes
echo.
echo [2/5] Adding all changes...
git add -A

REM Step 3: Commit
echo.
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Quick deploy update

echo [3/5] Committing: %commit_msg%
git commit -m "%commit_msg%"

REM Step 4: Push to GitHub
echo.
echo [4/5] Pushing to GitHub...
git push

REM Step 5: Deploy to VPS
echo.
echo [5/5] Deploying to VPS...
echo.
echo Please run this command on VPS:
echo.
echo ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git pull && supervisorctl restart mcoder-markplus && supervisorctl status mcoder-markplus"
echo.
echo Copy the command above and paste in your terminal
echo.

pause
