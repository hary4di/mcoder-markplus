#!/usr/bin/env python3
"""
Test if production can query ClassificationJob
"""
import sys
sys.path.insert(0, '/opt/markplus/mcoder-markplus')

print("Testing ClassificationJob query...")

try:
    from app import create_app
    from app.models import ClassificationJob
    
    app = create_app()
    with app.app_context():
        count = ClassificationJob.query.count()
        print(f"✅ Query successful: {count} jobs")
        
        # Try to get all jobs
        jobs = ClassificationJob.query.all()
        print(f"✅ Query all() successful: {len(jobs)} jobs")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("Database query working correctly!")
