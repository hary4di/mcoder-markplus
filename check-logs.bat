@echo off
echo Checking M-Coder logs on VPS...
echo.
ssh root@145.79.10.104 "tail -100 /var/log/mcoder/gunicorn.log | grep -A5 -B5 'MAIN\|Error\|Exception\|Traceback'"
pause
