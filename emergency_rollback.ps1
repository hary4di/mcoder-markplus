# SAFE ROLLBACK - Back to Session-Based Results
# Restore old working code without ClassificationJob

Write-Host "=== SAFE ROLLBACK TO WORKING VERSION ===" -ForegroundColor Red
Write-Host ""
Write-Host "This will restore old session-based results (pre-Jan 2 version)" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Rollback cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[1/4] Rolling back via git..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git status"

Write-Host ""
Write-Host "[2/4] Restoring old files..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git checkout HEAD app/"

Write-Host ""
Write-Host "[3/4] Clearing cache..." -ForegroundColor Yellow  
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null"

Write-Host ""
Write-Host "[4/4] Restarting service..." -ForegroundColor Yellow
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus && sleep 5 && supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "=== Rollback Complete! ===" -ForegroundColor Green
Write-Host "Test: https://m-coder.flazinsight.com/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Production will use SESSION-BASED results (old version)" -ForegroundColor Yellow
Write-Host "To enable database-based results, we need to run Flask-Migrate first" -ForegroundColor Yellow
