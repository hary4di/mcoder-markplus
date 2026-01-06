# PostgreSQL Exploration & Setup for M-Code Pro

Write-Host "=== Exploring PostgreSQL Setup on VPS ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/8] Check if PostgreSQL is installed..." -ForegroundColor Yellow
ssh root@145.79.10.104 "which psql && psql --version"

Write-Host ""
Write-Host "[2/8] Check PostgreSQL service status..." -ForegroundColor Yellow
ssh root@145.79.10.104 "systemctl status postgresql || service postgresql status"

Write-Host ""
Write-Host "[3/8] List existing databases..." -ForegroundColor Yellow
ssh root@145.79.10.104 "sudo -u postgres psql -l"

Write-Host ""
Write-Host "[4/8] Check PostgreSQL version and config..." -ForegroundColor Yellow
ssh root@145.79.10.104 "sudo -u postgres psql -c 'SHOW data_directory;' -c 'SHOW config_file;'"

Write-Host ""
Write-Host "[5/8] Check current disk usage..." -ForegroundColor Yellow
ssh root@145.79.10.104 "df -h | grep -E 'Filesystem|/$'"

Write-Host ""
Write-Host "[6/8] Check existing PostgreSQL users..." -ForegroundColor Yellow
ssh root@145.79.10.104 "sudo -u postgres psql -c '\du'"

Write-Host ""
Write-Host "[7/8] Check PostgreSQL listen addresses..." -ForegroundColor Yellow
ssh root@145.79.10.104 "sudo -u postgres psql -c 'SHOW listen_addresses;' -c 'SHOW port;'"

Write-Host ""
Write-Host "[8/8] Check existing connections..." -ForegroundColor Yellow
ssh root@145.79.10.104 "sudo -u postgres psql -c 'SELECT datname, usename, client_addr FROM pg_stat_activity;'"

Write-Host ""
Write-Host "=== Exploration Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Analysis will be provided based on results above..." -ForegroundColor Yellow
