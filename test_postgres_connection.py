"""
Test PostgreSQL connection from local to production
"""
import os
from dotenv import load_dotenv
load_dotenv()

print("Testing PostgreSQL connection...")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    try:
        # Test connection
        engine_name = db.engine.name
        print(f"\n✅ Connected to: {engine_name}")
        
        # Query users
        users = User.query.all()
        print(f"\n✅ Found {len(users)} users:")
        for u in users:
            role = "Super Admin" if u.is_super_admin else ("Admin" if u.is_admin else "User")
            print(f"  - {u.full_name or u.username} ({u.email}) [{role}]")
        
        print("\n✅ Local development now connected to production PostgreSQL!")
        print("You can now test edit/delete features locally before deploying.")
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check VPS firewall allows port 5432")
        print("2. Check PostgreSQL pg_hba.conf allows remote connections")
        print("3. Check password: MarkPlus25")
