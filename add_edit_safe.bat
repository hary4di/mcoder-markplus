@echo off
echo === Adding Edit Button via sed (Safe - no is_super_admin) ===
echo.

echo Adding Edit button before Delete button...
ssh root@145.79.10.104 "sed -i 's|<button class=\"btn btn-sm btn-outline-danger\"|<a href=\"{{ url_for('\''auth.edit_user'\'', user_id=user.id) }}\" class=\"btn btn-sm btn-outline-primary me-1\" title=\"Edit user\"><i class=\"bi bi-pencil\"></i></a>\n                                <button class=\"btn btn-sm btn-outline-danger\"|g' /opt/markplus/mcoder-markplus/app/templates/users.html"

echo.
echo Restarting application...
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus"

echo.
echo Wait 5 seconds...
timeout /t 5

echo.
echo === Done ===
echo Edit button should now appear (pencil icon before trash icon)
echo.
echo Refresh (Ctrl+F5): https://m-coder.flazinsight.com/users
pause
