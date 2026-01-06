# Deploy Classification Improvements Only (NO DATABASE)
# Safe deployment of multiple variables + normalization features

Write-Host "=== Deploying Classification Improvements ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will deploy:" -ForegroundColor Yellow
Write-Host "  - Multiple variables support (E1+E2+E3 in 1 file)" -ForegroundColor Gray
Write-Host "  - Category normalization (only 'Lainnya')" -ForegroundColor Gray
Write-Host "  - Duration format (minutes/seconds)" -ForegroundColor Gray
Write-Host "  - Label simplification ('Coded')" -ForegroundColor Gray
Write-Host "  - Fixed progress page duplicate files" -ForegroundColor Gray
Write-Host ""
Write-Host "This will NOT deploy database features (safe)" -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "Continue deployment? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Deployment cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[1/4] Uploading excel_classifier.py..." -ForegroundColor Yellow
scp excel_classifier.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[2/4] Uploading openai_classifier.py..." -ForegroundColor Yellow
scp openai_classifier.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

Write-Host ""
Write-Host "[3/4] Uploading classification_progress.html..." -ForegroundColor Yellow
scp app/templates/classification_progress.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

Write-Host ""
Write-Host "[4/4] Clearing cache and restarting..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; find . -name '*.pyc' -delete 2>/dev/null; supervisorctl restart mcoder-markplus && sleep 5 && supervisorctl status mcoder-markplus"

Write-Host ""
Write-Host "=== Deployment Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Test classification with multiple variables:" -ForegroundColor Yellow
Write-Host "  1. Go to https://m-coder.flazinsight.com/classify" -ForegroundColor Cyan
Write-Host "  2. Upload your test files" -ForegroundColor Cyan
Write-Host "  3. Select multiple variables (e.g., E1, E2, E3)" -ForegroundColor Cyan
Write-Host "  4. Check output: All coded columns in 1 file" -ForegroundColor Cyan
Write-Host "  5. Verify: No 'Other' category (only 'Lainnya')" -ForegroundColor Cyan
Write-Host ""
Write-Host "If any error, rollback with: .\emergency_rollback_now.ps1" -ForegroundColor Gray
