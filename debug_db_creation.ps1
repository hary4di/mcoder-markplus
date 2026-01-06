# Debug Database Creation Issue

Write-Host "=== Debugging Database Creation ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] Check if instance directory exists..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && ls -la instance/ 2>&1"

Write-Host ""
Write-Host "[2/6] Create instance directory if missing..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && mkdir -p instance && chmod 755 instance && ls -la instance/"

Write-Host ""
Write-Host "[3/6] Check Python can import app..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python -c 'from app import create_app; print(\"Import successful\")'"

Write-Host ""
Write-Host "[4/6] Try to create database manually..." -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
ssh root@145.79.10.104 @"
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
python -c "
from app import create_app, db
app = create_app()
print('App created')
with app.app_context():
    print('App context active')
    db.create_all()
    print('Database tables created!')
    import os
    db_path = 'instance/mcoder.db'
    if os.path.exists(db_path):
        print(f'Database file exists: {os.path.abspath(db_path)}')
        print(f'File size: {os.path.getsize(db_path)} bytes')
    else:
        print(f'ERROR: Database file not created at {os.path.abspath(db_path)}')
"
"@
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray

Write-Host ""
Write-Host "[5/6] List files in instance directory..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && ls -lh instance/"

Write-Host ""
Write-Host "[6/6] Run diagnostic..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python diagnose_production_db.py"

Write-Host ""
Write-Host "=== Debug Complete ===" -ForegroundColor Cyan
