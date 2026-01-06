# Create Production Database with Flask-Migrate
# This will create mcoder.db with all required tables

Write-Host "=== Creating Production Database ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Creating database file..." -ForegroundColor Yellow
ssh root@145.79.10.104 @"
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
python << 'EOPY'
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'\nCreated tables: {", ".join(tables)}')
EOPY
"@

Write-Host ""
Write-Host "[2/4] Verifying database file exists..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && ls -lh instance/mcoder.db"

Write-Host ""
Write-Host "[3/4] Checking tables in database..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && sqlite3 instance/mcoder.db '.tables'"

Write-Host ""
Write-Host "[4/4] Running diagnostic script..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && source venv/bin/activate && python diagnose_production_db.py"

Write-Host ""
Write-Host "=== Database Created! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Database file: /opt/markplus/mcoder-markplus/instance/mcoder.db" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT: Upload new code with database support" -ForegroundColor Yellow
Write-Host "Run: .\fix_production_results.ps1" -ForegroundColor Gray
