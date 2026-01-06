# Get Recent Error from Production Log

Write-Host "=== Checking Recent Production Errors ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Filtering for Traceback and Error lines..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "cat /var/log/mcoder/gunicorn.log | grep -A 30 'Traceback\|AttributeError\|TypeError\|NameError' | tail -60"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "If no error above, checking last 30 lines of log..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 "tail -30 /var/log/mcoder/gunicorn.log"
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
