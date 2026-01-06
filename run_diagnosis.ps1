# Diagnose Production Database Issue
# Upload and run diagnostic script to identify root cause

Write-Host "=== Production Database Diagnostic ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Uploading diagnostic script..." -ForegroundColor Yellow
scp diagnose_production_db.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Script uploaded" -ForegroundColor Green
} else {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] Running diagnostic..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python diagnose_production_db.py"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "[3/3] Checking current error in log..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "tail -30 /var/log/mcoder/gunicorn.log | grep -A 10 'Error\|Traceback' | tail -20"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "=== Diagnostic Complete ===" -ForegroundColor Cyan
