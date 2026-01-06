#!/usr/bin/env python3
"""
Production Database Diagnostic Script
Check if ClassificationJob table exists and is accessible
"""

import sys
import os

# Add app to path
sys.path.insert(0, '/opt/markplus/mcoder-markplus')

print("=" * 60)
print("PRODUCTION DATABASE DIAGNOSTIC")
print("=" * 60)
print()

# Test 1: Check if database file exists
print("[1/5] Checking database file...")
db_path = '/opt/markplus/mcoder-markplus/instance/mcoder.db'
if os.path.exists(db_path):
    print(f"✅ Database file exists: {db_path}")
    print(f"   Size: {os.path.getsize(db_path)} bytes")
else:
    print(f"❌ Database file NOT FOUND: {db_path}")
    sys.exit(1)

print()

# Test 2: Check tables using sqlite3
print("[2/5] Checking tables in database...")
import sqlite3
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    print(f"✅ Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table[0]}")
    conn.close()
except Exception as e:
    print(f"❌ Error checking tables: {e}")
    sys.exit(1)

print()

# Test 3: Check if ClassificationJob table exists
print("[3/5] Checking if 'classification_job' table exists...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classification_job';")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        print(f"✅ Table 'classification_job' EXISTS")
    else:
        print(f"❌ Table 'classification_job' DOES NOT EXIST")
        print()
        print("🔍 ROOT CAUSE IDENTIFIED:")
        print("   Production database is missing the 'classification_job' table")
        print("   This table was added in the Jan 2 update (database integration)")
        print()
        print("SOLUTION OPTIONS:")
        print("  1. Rollback to session-based version (no database)")
        print("  2. Run Flask-Migrate to create missing tables")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()

# Test 4: Try to import Flask app
print("[4/5] Testing Flask app import...")
try:
    from app import create_app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Failed to import Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: Try to import and query ClassificationJob
print("[5/5] Testing ClassificationJob model...")
try:
    from app.models import ClassificationJob
    print("✅ ClassificationJob model imported")
    
    app = create_app()
    with app.app_context():
        count = ClassificationJob.query.count()
        print(f"✅ Query successful: {count} jobs in database")
except Exception as e:
    print(f"❌ Error with ClassificationJob: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("🔍 This confirms the issue is with the database schema")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL CHECKS PASSED - Database is working correctly!")
print("=" * 60)
