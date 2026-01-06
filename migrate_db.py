#!/usr/bin/env python3
"""
Add ClassificationJob and ClassificationVariable tables to existing database
This will NOT delete existing User table
"""
import sys
sys.path.insert(0, '/opt/markplus/mcoder-markplus')

print("Adding missing tables to production database...")
print()

from app import create_app, db

app = create_app()
with app.app_context():
    # This will create ONLY missing tables, won't touch existing ones
    db.create_all()
    
    print("SUCCESS! Checking tables...")
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"Total tables: {len(tables)}")
    for table in tables:
        print(f"  - {table}")
    
    # Check if ClassificationJob exists
    if 'classification_job' in tables:
        print()
        print("✅ classification_job table created!")
    else:
        print()
        print("❌ classification_job table NOT found")
        sys.exit(1)
    
    if 'classification_variable' in tables:
        print("✅ classification_variable table created!")
    else:
        print("❌ classification_variable table NOT found")
        sys.exit(1)
    
    # Verify User table still intact
    from app.models import User
    user_count = User.query.count()
    print()
    print(f"✅ User table preserved: {user_count} users")

print()
print("=" * 60)
print("DATABASE MIGRATION COMPLETE!")
print("=" * 60)
