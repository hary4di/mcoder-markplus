# Upload routes.py fix to production
# Created: Jan 7, 2026

Write-Host "`n=== Uploading app/routes.py to Production ===`n" -ForegroundColor Cyan

# Check file exists
if (!(Test-Path "app/routes.py")) {
    Write-Host "ERROR: app/routes.py not found!" -ForegroundColor Red
    exit 1
}

# Get file size
$fileSize = (Get-Item "app/routes.py").Length / 1KB
Write-Host "Local file size: $([math]::Round($fileSize, 2)) KB" -ForegroundColor Green

# Upload file
Write-Host "`nUploading..." -ForegroundColor Yellow
scp app/routes.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Upload successful!" -ForegroundColor Green
    
    # Restart application
    Write-Host "`nRestarting application..." -ForegroundColor Yellow
    ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus && supervisorctl status mcoder-markplus"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Application restarted successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n✗ Failed to restart application" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n✗ Upload failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Deployment Complete ===`n" -ForegroundColor Cyan
