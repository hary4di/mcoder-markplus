# EMERGENCY ROLLBACK - Database File Not Found
# Restore to pre-database version (before Jan 2, 2026)

Write-Host "=== EMERGENCY ROLLBACK ===" -ForegroundColor Red
Write-Host ""
Write-Host "Issue: Database file does not exist in production" -ForegroundColor Yellow
Write-Host "Solution: Rollback to session-based version (no database dependency)" -ForegroundColor Yellow
Write-Host ""

Write-Host "[1/5] Checking git status..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git log --oneline -5"

Write-Host ""
Write-Host "[2/5] Finding last working commit (before Jan 2 database update)..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git log --oneline --all --grep='Dec 27\|Dec 30\|Branding' | head -3"

Write-Host ""
Write-Host "[3/5] Restoring files to working state..." -ForegroundColor Yellow
Write-Host "Restoring: app/routes.py, app/models.py, app/templates/*.html" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git checkout HEAD app/routes.py app/models.py app/templates/results.html app/templates/classification_progress.html"

Write-Host ""
Write-Host "[4/5] Clearing Python cache..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; find . -name '*.pyc' -delete 2>/dev/null; echo 'Cache cleared'"

Write-Host ""
Write-Host "[5/5] Restarting service..." -ForegroundColor Yellow
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus && sleep 5 && supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "=== Rollback Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Test homepage: https://m-coder.flazinsight.com/" -ForegroundColor Cyan
Write-Host "✅ Test classify: https://m-coder.flazinsight.com/classify" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Create database file properly with Flask-Migrate" -ForegroundColor Gray
Write-Host "  2. Test database migration in development first" -ForegroundColor Gray
Write-Host "  3. Deploy database and new code together" -ForegroundColor Gray
