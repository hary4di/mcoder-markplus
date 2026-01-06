@echo off
echo === EMERGENCY ROLLBACK - Users Page Error ===
echo.
echo Rolling back auth.py and users.html...
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git checkout HEAD -- app/auth.py app/templates/users.html && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && supervisorctl restart mcoder-markplus"
echo.
echo Application restored. Check: https://m-coder.flazinsight.com
pause
