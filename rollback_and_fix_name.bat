@echo off
echo === ROLLBACK - Restore working template ===
echo.
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git checkout HEAD -- app/templates/users.html && supervisorctl restart mcoder-markplus"
echo.
echo Done! App should be working again.
echo But we lost the Name change. Let me re-apply just that.
echo.
pause

echo.
echo Re-applying Name fix only...
ssh root@145.79.10.104 "sed -i '23s/Username/Name/' /opt/markplus/mcoder-markplus/app/templates/users.html && sed -i '37s/{{ user.username }}/{{ user.full_name or user.username }}/' /opt/markplus/mcoder-markplus/app/templates/users.html && supervisorctl restart mcoder-markplus"

echo.
echo === Done ===
echo Check: https://m-coder.flazinsight.com/users
pause
