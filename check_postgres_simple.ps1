# PostgreSQL Quick Check - Simple Version

Write-Host "=== Quick PostgreSQL Check ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking PostgreSQL setup..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

ssh root@145.79.10.104 @"
echo ""
echo "=== PostgreSQL Installation ==="
which psql && psql --version || echo "PostgreSQL not installed"

echo ""
echo "=== PostgreSQL Service ==="
systemctl is-active postgresql 2>/dev/null || echo "Service check failed"

echo ""
echo "=== Existing Databases ==="
sudo -u postgres psql -l 2>/dev/null | grep -E "Name|postgres|template" | head -10

echo ""
echo "=== Disk Space ==="
df -h / | grep -E "Filesystem|/"

echo ""
echo "=== PostgreSQL Users ==="
sudo -u postgres psql -c '\du' 2>/dev/null | head -10

echo ""
echo "=== Check Complete ==="
"@

Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
Write-Host ""
Write-Host "Analysis complete. Review output above." -ForegroundColor Green
