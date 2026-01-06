@echo off
echo === EMERGENCY ROLLBACK ===
echo.
echo Rolling back to working version...
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git checkout HEAD -- app/auth.py app/templates/users.html && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && supervisorctl start mcoder-markplus"
echo.
echo Done! Check: https://m-coder.flazinsight.com
pause
