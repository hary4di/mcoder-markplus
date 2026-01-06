#!/bin/bash
# Test PostgreSQL Connection

cd /opt/markplus/mcoder-markplus
source venv/bin/activate

python3 << 'EOPY'
from app import create_app, db
app = create_app()
with app.app_context():
    print(f"✅ Database Engine: {db.engine.name}")
    print(f"✅ Database URL: {db.engine.url}")
    
    if db.engine.name == 'postgresql':
        result = db.session.execute(db.text("SELECT version()"))
        version = result.scalar()
        print(f"✅ PostgreSQL Version: {version[:80]}")
        
        from app.models import User
        user_count = User.query.count()
        print(f"✅ Users in Database: {user_count}")
        print("")
        print("="*60)
        print("SUCCESS! Application is using PostgreSQL!")
        print("="*60)
    else:
        print(f"❌ ERROR: Still using {db.engine.name}")
        print("="*60)
        exit(1)
EOPY
