# Fix Production Results Page Error
# Issue: 'builtin_function_or_method' object is not iterable
# Cause: OLD templates still in production - missing results.html update

Write-Host "=== Fixing Production Results Page Error ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload ALL modified files (routes.py + templates + classifiers)
Write-Host "[1/7] Uploading app/routes.py..." -ForegroundColor Yellow
scp app/routes.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

Write-Host "[2/7] Uploading app/templates/results.html..." -ForegroundColor Yellow
scp app/templates/results.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

Write-Host "[3/7] Uploading app/templates/classification_progress.html..." -ForegroundColor Yellow
scp app/templates/classification_progress.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

Write-Host "[4/7] Uploading app/models.py..." -ForegroundColor Yellow
scp app/models.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

Write-Host "[5/7] Uploading excel_classifier.py..." -ForegroundColor Yellow
scp excel_classifier.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host "[6/7] Uploading openai_classifier.py..." -ForegroundColor Yellow
scp openai_classifier.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All files uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some uploads may have failed, but continuing..." -ForegroundColor Yellow
}

# Step 2: Clear Python cache
Write-Host ""
Write-Host "[7/7] Clearing cache and restarting..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; find . -name '*.pyc' -delete 2>/dev/null; supervisorctl restart mcoder-markplus && sleep 3 && supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "=== Done! ===" -ForegroundColor Cyan
Write-Host "Test URL: https://m-coder.flazinsight.com/results" -ForegroundColor Green
Write-Host ""
Write-Host "Jika masih error, cek log dengan:" -ForegroundColor Yellow
Write-Host 'ssh root@145.79.10.104 "tail -50 /var/log/mcoder/gunicorn.log"' -ForegroundColor Gray
