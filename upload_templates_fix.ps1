# Upload missing template files to production
# Created: Jan 7, 2026

Write-Host "`n=== Uploading Template Files to Production ===`n" -ForegroundColor Cyan

$templates = @(
    "app/templates/base.html",
    "app/templates/classify.html",
    "app/templates/select_variables.html"
)

$allSuccess = $true

foreach ($template in $templates) {
    if (Test-Path $template) {
        $filename = Split-Path $template -Leaf
        $fileSize = [math]::Round((Get-Item $template).Length / 1KB, 2)
        
        Write-Host "Uploading $filename ($fileSize KB)..." -ForegroundColor Yellow
        scp $template root@145.79.10.104:/opt/markplus/mcoder-markplus/$template
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $filename uploaded successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to upload $filename" -ForegroundColor Red
            $allSuccess = $false
        }
    } else {
        Write-Host "✗ $template not found!" -ForegroundColor Red
        $allSuccess = $false
    }
    
    Write-Host ""
}

if ($allSuccess) {
    Write-Host "Restarting application..." -ForegroundColor Yellow
    ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus"
    
    Write-Host "`n✓ All templates uploaded and application restarted!" -ForegroundColor Green
} else {
    Write-Host "`n✗ Some uploads failed!" -ForegroundColor Red
}

Write-Host "`n=== Deployment Complete ===`n" -ForegroundColor Cyan
