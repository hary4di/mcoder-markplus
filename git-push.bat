@echo off
cd /d "%~dp0"

echo Adding files...
git add .

echo Committing...
git commit -m "Add VPS setup script"

echo Pushing to GitHub...
git push

echo Done!
pause
