# Test Production Upload Endpoint
# Created: Jan 7, 2026

Write-Host "`n=== Testing Production Upload Endpoint ===`n" -ForegroundColor Cyan

# Test with curl to see actual response
Write-Host "Testing /upload-files endpoint..." -ForegroundColor Yellow

$response = curl -X POST https://m-coder.flazinsight.com/upload-files `
    -H "Content-Type: multipart/form-data" `
    -F "kobo_system_file=@test.txt" `
    -F "raw_data_file=@test.txt" `
    -v 2>&1 | Out-String

Write-Host "`nResponse:" -ForegroundColor Green
Write-Host $response

Write-Host "`n=== Test Complete ===`n" -ForegroundColor Cyan
