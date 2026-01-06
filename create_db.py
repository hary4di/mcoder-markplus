#!/usr/bin/env python3
"""
Create database tables in production
"""
import sys
sys.path.insert(0, '/opt/markplus/mcoder-markplus')

from app import create_app, db

print("=" * 60)
print("CREATING PRODUCTION DATABASE")
print("=" * 60)
print()

app = create_app()
with app.app_context():
    print("[1/3] Creating all tables...")
    db.create_all()
    print("✅ Tables created successfully!")
    
    print()
    print("[2/3] Verifying tables...")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"✅ Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table}")
    
    print()
    print("[3/3] Checking User table...")
    from app.models import User
    user_count = User.query.count()
    print(f"✅ User table has {user_count} users")

print()
print("=" * 60)
print("DATABASE CREATED SUCCESSFULLY!")
print("=" * 60)
print()
print("Database location: /opt/markplus/mcoder-markplus/instance/mcoder.db")
print()
print("NEXT: Upload new code with database support")
print("Run: .\\fix_production_results.ps1")
