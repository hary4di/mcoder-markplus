# Emergency Rollback Auth.py
Write-Host "EMERGENCY ROLLBACK - Removing Delete User Feature" -ForegroundColor Red
scp emergency_rollback_auth.sh root@145.79.10.104:/tmp/
ssh root@145.79.10.104 "bash /tmp/emergency_rollback_auth.sh"
Write-Host ""
Write-Host "Test: https://m-coder.flazinsight.com/" -ForegroundColor Cyan
