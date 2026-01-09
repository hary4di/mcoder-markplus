# Upload dashboard.html to VPS
$ErrorActionPreference = "Stop"

Write-Host "Uploading dashboard.html to VPS..." -ForegroundColor Cyan

scp "app\templates\dashboard.html" root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: dashboard.html uploaded successfully!" -ForegroundColor Green
    Write-Host "`nNow restart the application:" -ForegroundColor Yellow
    Write-Host "ssh root@145.79.10.104 'supervisorctl restart mcoder-markplus'" -ForegroundColor White
} else {
    Write-Host "ERROR: Upload failed!" -ForegroundColor Red
    exit 1
}
