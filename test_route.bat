@echo off
echo === Testing /users Route Directly ===
echo.
scp test_users_route.sh root@145.79.10.104:/tmp/
ssh root@145.79.10.104 "chmod +x /tmp/test_users_route.sh && /tmp/test_users_route.sh"
echo.
pause
