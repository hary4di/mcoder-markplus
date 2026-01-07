# Add Development IP to PostgreSQL pg_hba.conf
# Created: Jan 7, 2026

Write-Host "`n=== Adding Development IP to PostgreSQL Access ===`n" -ForegroundColor Cyan

$devIP = "114.8.205.190"
Write-Host "Development IP: $devIP" -ForegroundColor Yellow

Write-Host "`nConnecting to production server..." -ForegroundColor Yellow

# SSH command to add IP to pg_hba.conf
$sshCommand = @"
echo 'host    mcoder_production    mcoder_app    $devIP/32    md5' >> /etc/postgresql/16/main/pg_hba.conf && systemctl reload postgresql && echo 'PostgreSQL access updated!'
"@

ssh root@145.79.10.104 $sshCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Development IP added successfully!" -ForegroundColor Green
    Write-Host "`nTesting connection..." -ForegroundColor Yellow
    
    # Test connection dari local
    python -c "import psycopg2; conn = psycopg2.connect('postgresql://mcoder_app:MarkPlus25@145.79.10.104:5432/mcoder_production'); print('✓ Connection successful!'); conn.close()"
    
} else {
    Write-Host "`n✗ Failed to update pg_hba.conf" -ForegroundColor Red
}

Write-Host "`n=== Complete ===`n" -ForegroundColor Cyan
