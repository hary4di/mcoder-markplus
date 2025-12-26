@echo off
cd /d "%~dp0"

echo Setting up Git configuration...
git config --global user.name "hary4di"
git config --global user.email "hary4di@users.noreply.github.com"

echo Initializing Git repository...
git init

echo Creating .gitignore...
if not exist .gitignore (
    echo # Python> .gitignore
    echo __pycache__/>> .gitignore
    echo *.py[cod]>> .gitignore
    echo venv/>> .gitignore
    echo env/>> .gitignore
    echo.>> .gitignore
    echo # Flask>> .gitignore
    echo instance/>> .gitignore
    echo *.db>> .gitignore
    echo *.sqlite3>> .gitignore
    echo.>> .gitignore
    echo # Environment>> .gitignore
    echo .env>> .gitignore
    echo.>> .gitignore
    echo # Files>> .gitignore
    echo files/uploads/*>> .gitignore
    echo files/output/*>> .gitignore
    echo files/logo/*>> .gitignore
    echo files/logs/*.log>> .gitignore
    echo !files/*/.gitkeep>> .gitignore
    echo.>> .gitignore
    echo # OS ^& IDE>> .gitignore
    echo .DS_Store>> .gitignore
    echo Thumbs.db>> .gitignore
    echo .vscode/>> .gitignore
)

echo Adding files to Git...
git add .

echo Creating initial commit...
git commit -m "Initial commit: M-Coder Platform"

echo Adding remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/hary4di/mcoder-markplus.git

echo Setting main branch...
git branch -M main

echo Pushing to GitHub...
echo You will be prompted for username and password/token
git push -u origin main

echo.
echo ========================================
echo Git setup complete!
echo ========================================
pause
